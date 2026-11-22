"""Private blocker commitments and explicit orders, independent of UI/replay storage."""
from dataclasses import dataclass, replace
from .combat import Attack, CombatState, CombatError, _validate_assignments, _resolve_damage


@dataclass(frozen=True)
class CombatFlow:
    active_player: str
    attacks: tuple[Attack, ...]
    stage: str = 'attack_responses'
    defenders: tuple[str, ...] = ()
    locks: tuple = ()
    orders: tuple = ()


def commit_attacks(snapshot, active_player, attacks):
    if type(attacks) is not tuple or any(type(a) is not Attack or a.blockers or a.was_blocked for a in attacks):
        raise CombatError('declaration cannot preassign blockers or blocked memory')
    by_id={c.instance_id:c for c in snapshot.creatures}
    _validate_assignments(snapshot,attacks)
    if any(by_id[a.attacker_id].controller!=active_player or
           (a.challenge_target is not None and a.challenge_target not in by_id) for a in attacks):
        raise CombatError('declaration requires own attackers and existing Challenge targets')
    used={a.attacker_id for a in attacks}
    creatures=tuple(replace(c,exhausted=True,attack_used=True) if c.instance_id in used else c for c in snapshot.creatures)
    return replace(snapshot,creatures=creatures),CombatFlow(active_player,attacks)


def surviving_attacks(snapshot, flow):
    creatures={c.instance_id:c for c in snapshot.creatures}
    players={p.player_id for p in snapshot.players}
    return tuple(a for a in flow.attacks if a.attacker_id in creatures and
                 creatures[a.attacker_id].controller==flow.active_player and a.target_player in players)


def begin_blocking(snapshot, flow):
    attacks=surviving_attacks(snapshot,flow)
    defenders=tuple(p.player_id for p in snapshot.players if any(a.target_player==p.player_id and a.challenge_target is None for a in attacks))
    flow=replace(flow,attacks=attacks,stage='blocking',defenders=defenders,locks=(),orders=())
    return flow if defenders else replace(flow,stage='ordering')


def lock_blockers(snapshot, flow, actor, assignments):
    if flow.stage!='blocking' or actor not in flow.defenders or actor in dict(flow.locks):
        raise CombatError('no unlocked defender choice')
    own=tuple(a for a in flow.attacks if a.target_player==actor and a.challenge_target is None)
    if type(assignments) is not tuple or any(type(x) is not tuple or len(x)!=2 or type(x[0]) is not str or
            type(x[1]) is not tuple or any(type(i) is not str for i in x[1]) for x in assignments):
        raise CombatError('invalid blocker assignment')
    choices=dict(assignments)
    if len(choices)!=len(assignments) or set(choices)!={a.attacker_id for a in own}:
        raise CombatError('complete assignment required, including explicit empty blockers')
    challenged={a.challenge_target for a in flow.attacks if a.challenge_target is not None}
    if any(b in challenged for ids in choices.values() for b in ids):
        raise CombatError('challenged creatures cannot also block')
    # Validate this defender without inspecting any earlier private lock.
    proposed=tuple(replace(a,blockers=choices.get(a.attacker_id,()),was_blocked=bool(choices.get(a.attacker_id,()))) for a in flow.attacks)
    _validate_assignments(snapshot,proposed,require_fresh=False)
    flow=replace(flow,locks=flow.locks+((actor,assignments),))
    if len(flow.locks)!=len(flow.defenders):
        return flow
    revealed={key:ids for _,locked in flow.locks for key,ids in locked}
    attacks=tuple(replace(a,blockers=revealed.get(a.attacker_id,()),was_blocked=bool(revealed.get(a.attacker_id,()))) for a in flow.attacks)
    return replace(flow,attacks=attacks,stage='ordering')


def required_orders(snapshot, flow):
    creatures={c.instance_id:c for c in snapshot.creatures}
    choices=[(a.attacker_id,flow.active_player,a.blockers) for a in flow.attacks if len(a.blockers)>1]
    groups={}
    for a in flow.attacks:
        if a.challenge_target in creatures and creatures[a.challenge_target].controller==a.target_player:
            groups.setdefault(a.challenge_target,[]).append(a.attacker_id)
    choices.extend((target,creatures[target].controller,tuple(ids)) for target,ids in groups.items() if len(ids)>1)
    return tuple(choice for choice in choices if choice[0] not in dict(flow.orders))


def choose_order(snapshot, flow, actor, subject, order):
    if flow.stage!='ordering':
        raise CombatError('no damage order choice')
    choice=next((c for c in required_orders(snapshot,flow) if c[0]==subject),None)
    if choice is None or choice[1]!=actor or type(order) is not tuple or len(order)!=len(choice[2]) or set(order)!=set(choice[2]):
        raise CombatError('wrong controller or incomplete order')
    return replace(flow,orders=flow.orders+((subject,order),))


def resolve_committed(snapshot, flow):
    if flow.stage!='final_responses' or required_orders(snapshot,flow):
        raise CombatError('declarations/orders incomplete')
    creatures={c.instance_id:c for c in snapshot.creatures}
    orders=dict(flow.orders)
    attacks=[];misses=[]
    for a in surviving_attacks(snapshot,flow):
        if a.challenge_target is not None:
            target=creatures.get(a.challenge_target)
            if target is not None and target.controller!=a.target_player:
                misses.append(a.attacker_id);continue
        blockers=tuple(b for b in orders.get(a.attacker_id,a.blockers) if b in creatures and creatures[b].controller==a.target_player)
        attacks.append(replace(a,blockers=blockers))
    groups={}
    for a in attacks:
        if a.challenge_target is not None:
            groups.setdefault(a.challenge_target,[]).append(a.attacker_id)
    challenge_orders=tuple((target,tuple(i for i in orders.get(target,tuple(ids)) if i in ids)) for target,ids in groups.items())
    result=_resolve_damage(snapshot,tuple(attacks),challenge_orders,require_fresh=False)
    return replace(result,misses=result.misses+tuple(misses))


def combat_view(flow, viewer=None):
    """Explicit projection: locks never appear in another player's/public view."""
    revealed=flow.stage in ('ordering','final_responses','done')
    view={'stage':flow.stage,'attacks':tuple((a.attacker_id,a.target_player,a.challenge_target) for a in flow.attacks)}
    if revealed:
        view['blockers']=tuple((a.attacker_id,a.blockers) for a in flow.attacks)
        view['orders']=flow.orders
    elif flow.stage=='blocking':
        view['waiting']='Defenders are choosing blockers'
        if viewer in flow.defenders:
            view['own_lock']=dict(flow.locks).get(viewer)
    return view

def validate_flow(flow, seats):
    if (type(flow) is not CombatFlow or flow.active_player not in seats
            or flow.stage not in ('attack_responses','blocking','ordering','final_responses','done')
            or any(type(x) is not tuple for x in (flow.attacks,flow.defenders,flow.locks,flow.orders))):
        raise CombatError('invalid committed combat state')
    if any(type(a) is not Attack or type(a.attacker_id) is not str or not a.attacker_id or
           a.target_player not in seats or a.target_player==flow.active_player or
           type(a.blockers) is not tuple or type(a.was_blocked) is not bool or
           any(type(b) is not str or not b for b in a.blockers) or
           (a.challenge_target is not None and (type(a.challenge_target) is not str or not a.challenge_target or a.blockers or a.was_blocked))
           for a in flow.attacks):
        raise CombatError('invalid committed attack record')
    if len({a.attacker_id for a in flow.attacks})!=len(flow.attacks):
        raise CombatError('duplicate committed attacker')
    if any(p not in seats or p==flow.active_player for p in flow.defenders) or len(set(flow.defenders))!=len(flow.defenders):
        raise CombatError('invalid defender batch')
    for records in (flow.locks,flow.orders):
        if any(type(x) is not tuple or len(x)!=2 or type(x[0]) is not str or type(x[1]) is not tuple for x in records):
            raise CombatError('invalid lock/order records')
        if len(dict(records))!=len(records):
            raise CombatError('duplicate lock/order owner')
    if any(p not in flow.defenders for p,_ in flow.locks):
        raise CombatError('invalid lock controller')
