"""Atomic typed-effect coordinator for a deliberately restricted match subset.

Server-internal state only; no client projections or production save schema.
Effects are registered immutable instructions, never arbitrary prose/callbacks.
"""
from dataclasses import dataclass, replace
from .combat import Creature, CombatState, Player, resolve_combat, validate_state
from .combat_flow import (CombatFlow, commit_attacks, begin_blocking, lock_blockers,
                          required_orders, choose_order, resolve_committed, combat_view, validate_flow)
from .resources import ResourcePool, Payment, validate_pool, start_resources, pay_resources
from .priority import PriorityState, PendingEffect, add_effect, pass_priority, validate_priority
from .turns import (DrawPlayer, TurnFlow, RefillPolicy, DrawState, begin_required_draw,
                    accept_refill, decline_refill, begin_start_refill, open_turn, request_end_turn,
                    _validate_player, _validate_turn, _validate_policy)


class MatchError(ValueError):
    pass


class UnsupportedMatchRule(MatchError):
    pass


@dataclass(frozen=True)
class DamagePlayer:
    target: str
    amount: int


@dataclass(frozen=True)
class HealPlayer:
    target: str
    amount: int


@dataclass(frozen=True)
class DrawCards:
    target: str
    count: int


@dataclass(frozen=True)
class DestroyCreature:
    target: str


@dataclass(frozen=True)
class GrantCapacity:
    target: str
    amount: int


@dataclass(frozen=True)
class GrantResources:
    target: str
    amount: int


@dataclass(frozen=True)
class ActionSpec:
    key: str
    effect_key: str
    source_id: str
    resource_cost: int = 0
    timing: str = 'main'
    exhaust_source: bool = False
    once_per_turn: bool = False


@dataclass(frozen=True)
class EffectSpec:
    key: str
    controller: str
    steps: tuple
    source_id: str | None = None


@dataclass(frozen=True)
class TriggerSpec:
    event: str  # defeat, departure, turn_end
    effect_key: str
    watch: str = 'self'  # self or any


@dataclass(frozen=True)
class MatchObject:
    object_id: str
    owner: str
    controller: str
    kind: str  # creature, creature_token, permanent, resource_token
    creature: Creature | None = None
    attached_to: str | None = None
    triggers: tuple[TriggerSpec, ...] = ()
    resource_value: int = 1
    capacity_bonus: int = 0


@dataclass(frozen=True)
class MatchPlayer:
    cards: DrawPlayer
    max_health: int = 30
    eliminated: bool = False
    causes: tuple[str, ...] = ()
    resources: ResourcePool = ResourcePool()


@dataclass(frozen=True)
class MatchEvent:
    event_id: int
    kind: str
    subject: str
    cause: str


@dataclass(frozen=True)
class TriggerCandidate:
    trigger_id: int
    event_id: int
    controller: str
    source_id: str
    effect_key: str


@dataclass(frozen=True)
class Resolution:
    steps: tuple
    index: int = 0
    draw: DrawState | None = None
    cleanup: bool = False


@dataclass(frozen=True)
class MatchResult:
    kind: str  # win or draw
    winner: str | None = None


@dataclass(frozen=True)
class MatchState:
    seat_order: tuple[str, ...]
    players: tuple[MatchPlayer, ...]
    battlefield: tuple[MatchObject, ...]
    effects: tuple[EffectSpec, ...]
    policy: RefillPolicy
    turn: TurnFlow
    priority: PriorityState | None
    revision: int = 0
    pending: Resolution | None = None
    failed_draws: tuple[str, ...] = ()
    destroyed: tuple[str, ...] = ()
    concedes: tuple[str, ...] = ()
    triggers: tuple[TriggerCandidate, ...] = ()
    trigger_orders: tuple[tuple[str, tuple[int, ...]], ...] = ()
    events: tuple[MatchEvent, ...] = ()
    next_event_id: int = 1
    next_trigger_id: int = 1
    end_cleanup: tuple = ()  # registered expiration consequences for THIS turn
    end_stage: str = 'none'  # none, triggers, discard, cleanup, done
    discard_needed: int = 0
    draw_records: tuple[DrawState, ...] = ()  # internal debug/replay; private card order!
    result: MatchResult | None = None
    actions: tuple[ActionSpec, ...] = ()
    action_uses: tuple[tuple[str, int], ...] = ()
    managed_turns: bool = False
    starting_player: str | None = None
    start_cleanup: tuple = ()
    start_stage: str = 'pending'
    combat: CombatFlow | None = None


def _name(value):
    return type(value) is str and bool(value.strip())


def _natural(value):
    return type(value) is int and value >= 0


def _living(state):
    return tuple(p.cards.player_id for p in state.players if not p.eliminated)


def _player(state, player_id):
    return next(p for p in state.players if p.cards.player_id == player_id)


def _set_player(state, player):
    return replace(state, players=tuple(player if p.cards.player_id == player.cards.player_id else p for p in state.players))


def _steps_valid(steps, seats, objects):
    if type(steps) is not tuple:
        raise MatchError('effect steps must be a tuple')
    for step in steps:
        if type(step) in (DamagePlayer, HealPlayer, GrantCapacity, GrantResources):
            valid = step.target in seats and _natural(step.amount)
        elif type(step) is DrawCards:
            valid = step.target in seats and _natural(step.count)
        elif type(step) is DestroyCreature:
            valid = _name(step.target)  # may be absent when an item resolves
        else:
            raise UnsupportedMatchRule('unregistered instruction type')
        if not valid:
            raise MatchError('invalid instruction target/quantity')


def validate_match(state):
    if type(state) is not MatchState or type(state.seat_order) is not tuple or not state.seat_order:
        raise MatchError('expected match state with original seats')
    if any(not _name(p) for p in state.seat_order) or len(set(state.seat_order)) != len(state.seat_order):
        raise MatchError('invalid original seat order')
    if any(type(value) is not tuple for value in (state.players,state.battlefield,state.effects)):
        raise MatchError('match collections must be tuples')
    if any(type(p) is not MatchPlayer or type(p.cards) is not DrawPlayer for p in state.players):
        raise MatchError('invalid player record')
    if any(type(e) is not EffectSpec for e in state.effects) or any(type(o) is not MatchObject for o in state.battlefield):
        raise MatchError('invalid effect/object record')
    if tuple(p.cards.player_id for p in state.players) != state.seat_order:
        raise MatchError('player records must preserve original seat order')
    _validate_turn(state.turn); _validate_policy(state.policy)
    if state.turn.active_player not in state.seat_order or not _natural(state.revision):
        raise MatchError('invalid turn/revision')
    ids = list(state.seat_order)
    for p in state.players:
        if type(p) is not MatchPlayer or type(p.eliminated) is not bool or type(p.max_health) is not int or p.max_health < 1:
            raise MatchError('invalid player record')
        validate_pool(p.resources)
        _validate_player(p.cards, allow_nonpositive_health=True)
        if p.cards.health > p.max_health:
            raise MatchError('health exceeds maximum')
        ids.extend(p.cards.deck + p.cards.discard + p.cards.hand)
    definitions = {e.key:e for e in state.effects}
    if len(definitions) != len(state.effects):
        raise MatchError('duplicate registered effect key')
    object_ids = {o.object_id for o in state.battlefield}
    for e in state.effects:
        if type(e) is not EffectSpec or not _name(e.key) or e.controller not in state.seat_order:
            raise MatchError('invalid registered effect')
        _steps_valid(e.steps,state.seat_order,object_ids)
    _steps_valid(state.end_cleanup,state.seat_order,object_ids)
    _steps_valid(state.start_cleanup,state.seat_order,object_ids)
    if state.combat is not None:
        validate_flow(state.combat,state.seat_order)
        if state.combat.active_player!=state.turn.active_player or state.turn.phase not in ('Combat','MainAfter','End','Finished'):
            raise MatchError('combat/turn mismatch')
    if state.starting_player is not None and state.starting_player not in state.seat_order:
        raise MatchError('invalid starting seat')
    if (type(state.action_uses) is not tuple or any(type(u) is not tuple or len(u)!=2 or
            type(u[0]) is not str or not _natural(u[1]) for u in state.action_uses)
            or len(set(state.action_uses))!=len(state.action_uses)):
        raise MatchError('invalid action usage records')
    if type(state.managed_turns) is not bool or state.start_stage not in ('pending','cleanup','done'):
        raise MatchError('invalid managed turn state')
    if type(state.actions) is not tuple or any(type(a) is not ActionSpec for a in state.actions):
        raise MatchError('invalid action registry')
    if len({a.key for a in state.actions})!=len(state.actions):
        raise MatchError('duplicate action key')
    for a in state.actions:
        if (not _name(a.key) or not _name(a.source_id) or a.effect_key not in definitions
                or not _natural(a.resource_cost) or a.timing not in ('main','reaction')
                or type(a.exhaust_source) is not bool or type(a.once_per_turn) is not bool):
            raise UnsupportedMatchRule('unsupported action definition')
    for o in state.battlefield:
        if (type(o) is not MatchObject or not _name(o.object_id)
                or o.owner not in state.seat_order or o.controller not in state.seat_order):
            raise MatchError('invalid battlefield object')
        if (not _natural(o.capacity_bonus) or type(o.resource_value) is not int or o.resource_value<1
                or (o.kind!='resource_token' and o.resource_value!=1)):
            raise MatchError('invalid capacity/token value')
        if o.kind not in ('creature','creature_token','permanent','resource_token'):
            raise UnsupportedMatchRule('leader/combined/unknown object not covered')
        if o.kind in ('creature','creature_token'):
            if (type(o.creature) is not Creature or o.creature.instance_id != o.object_id
                    or o.creature.controller != o.controller or type(o.creature.health) is not int):
                raise MatchError('creature/object identity mismatch')
            # Validate a positive-HP view; zero is only allowed transiently until cleanup.
            validate_state(CombatState(tuple(Player(p) for p in state.seat_order),
                                      (replace(o.creature,health=max(1,o.creature.health)),)))
        elif o.creature is not None:
            raise MatchError('non-creature cannot contain creature stats')
        if o.attached_to is not None and (o.kind != 'permanent' or o.attached_to not in object_ids or o.attached_to == o.object_id):
            raise MatchError('invalid structural attachment')
        if type(o.triggers) is not tuple or len(set(o.triggers)) != len(o.triggers):
            raise MatchError('invalid/duplicate trigger specs')
        for t in o.triggers:
            if (type(t) is not TriggerSpec or t.event not in ('defeat','departure','turn_end','turn_start')
                    or t.watch not in ('self','any') or t.effect_key not in definitions
                    or definitions[t.effect_key].controller != o.controller):
                raise MatchError('invalid registered trigger')
        ids.append(o.object_id)
    if len(set(ids)) != len(ids):
        raise MatchError('instance IDs must be globally unique across players/zones/battlefield')
    if state.priority is None and state.result is None and _living(state):
        raise MatchError('surviving nonterminal state needs priority')
    if state.result is not None:
        alive=_living(state)
        expected=MatchResult('draw') if not alive else MatchResult('win',alive[0])
        if len(alive)>1 or state.result!=expected or state.pending or state.triggers or state.discard_needed or state.priority is not None:
            raise MatchError('invalid terminal checkpoint')
    if state.priority is not None:
        validate_priority(state.priority)
        if state.priority.seats != _living(state):
            raise MatchError('priority seats must match surviving seats')
        for effect in state.priority.chain + ((state.priority.resolving,) if state.priority.resolving else ()):
            if effect.effect_key not in definitions or definitions[effect.effect_key].controller != effect.controller:
                raise MatchError('pending item does not match registered controller')
    if state.end_stage not in ('none','triggers','discard','cleanup','done') or not _natural(state.discard_needed):
        raise MatchError('invalid boundary stage')


def new_match(players, battlefield, effects, policy, *, active_player, phase='MainBefore', end_cleanup=(),
              actions=(), managed_turns=False, start_cleanup=()):
    """Fixture/coordinator factory; no deck/lobby setup or full-match mode implied."""
    seats=tuple(p.cards.player_id for p in players)
    state=MatchState(seats,players,battlefield,effects,policy,TurnFlow(active_player,1,phase=phase),
                     PriorityState(seats,active_player,active_player),end_cleanup=end_cleanup,actions=actions,managed_turns=managed_turns,
                     starting_player=active_player,start_cleanup=start_cleanup)
    validate_match(state)
    if any(p.eliminated or p.cards.health <= 0 for p in players):
        raise MatchError('initial players must be alive')
    if managed_turns and phase!='Start':
        raise MatchError('managed matches begin at Start')
    return _begin_start(state) if managed_turns else state


def _check(state, revision):
    validate_match(state)
    if type(revision) is not int or revision != state.revision:
        raise MatchError('stale match revision')
    if state.result is not None:
        raise MatchError('match already ended')


def _blocked(state):
    return (state.pending is not None or bool(state.triggers) or state.discard_needed > 0
            or (state.combat is not None and state.combat.stage in ('blocking','ordering')))


def queue_effect(state, actor, key, *, expected_revision):
    """Internal commit for an already-authorized fixture effect, not card play legality."""
    _check(state,expected_revision)
    if _blocked(state) or state.priority is None:
        raise MatchError('resolution/mandatory choice is pending')
    e=next((e for e in state.effects if e.key==key),None)
    if e is None or e.controller != actor or actor not in _living(state):
        raise MatchError('unregistered or wrong-controller effect')
    if e.source_id is not None and not any(o.object_id==e.source_id and o.controller==actor for o in state.battlefield):
        raise MatchError('effect source is no longer controlled on battlefield')
    if actor == state.turn.active_player and (state.turn.recharge or _player(state,actor).cards.end_turn_requested):
        raise MatchError('active player cannot take voluntary actions while ending/Recharging')
    p=add_effect(state.priority,actor,key,expected_revision=state.priority.revision)
    return replace(state,priority=p,revision=state.revision+1)


def request_match_end(state, actor, *, expected_revision):
    """Record own-turn ending intent without truncating pending work."""
    _check(state,expected_revision)
    if actor != state.turn.active_player or actor not in _living(state):
        raise MatchError('only the living active player can end their turn')
    if state.combat is not None and state.combat.stage!='done':
        raise MatchError('committed combat must finish before ending intent')
    turn=request_end_turn(state.turn,expected_turn_id=state.turn.turn_id,expected_revision=state.turn.revision)
    return _quiescent(replace(state,turn=turn,revision=state.revision+1))


def pass_match(state, actor, *, expected_revision):
    _check(state,expected_revision)
    if _blocked(state) or state.priority is None:
        raise MatchError('resolution/mandatory choice is pending')
    p=pass_priority(state.priority,actor,expected_revision=state.priority.revision)
    return _quiescent(replace(state,priority=p,revision=state.revision+1))


def _emit(state, kind, subject, cause):
    event=MatchEvent(state.next_event_id,kind,subject,cause)
    return replace(state,events=state.events+(event,),next_event_id=state.next_event_id+1),event


def _capture(state, sources, events):
    candidates=list(state.triggers)
    next_id=state.next_trigger_id
    for event in events:
        for source in sources:
            for trigger in source.triggers:
                own = source.controller==event.subject if event.kind in ('turn_end','turn_start') else source.object_id==event.subject
                if trigger.event==event.kind and (trigger.watch=='any' or own):
                    candidates.append(TriggerCandidate(next_id,event.event_id,source.controller,source.object_id,trigger.effect_key))
                    next_id+=1
    return replace(state,triggers=tuple(candidates),next_trigger_id=next_id)


def _depart(state, ids, cause, *, genuine=False):
    sources=state.battlefield
    events=[]
    for o in sources:
        if o.object_id not in ids:
            continue
        if genuine:
            state,e=_emit(state,'defeat',o.object_id,cause);events.append(e)
        state,e=_emit(state,'departure',o.object_id,cause);events.append(e)
        if o.kind not in ('creature_token','resource_token'):
            owner=_player(state,o.owner)
            owner=replace(owner,cards=replace(owner.cards,discard=owner.cards.discard+(o.object_id,)))
            state=_set_player(state,owner)
    state=_capture(state,sources,events)
    return replace(state,battlefield=tuple(o for o in sources if o.object_id not in ids))


def _priority_after_cleanup(state):
    alive=_living(state)
    if not alive:
        return replace(state,priority=None,triggers=(),trigger_orders=())
    active=state.turn.active_player
    if active not in alive:
        start=state.seat_order.index(active)
        active=next(p for p in state.seat_order[start+1:]+state.seat_order[:start+1] if p in alive)
    old=state.priority
    chain=tuple(e for e in old.chain if e.controller in alive) if old else ()
    p=PriorityState(alive,active,active,chain=chain,
                    revision=old.revision+1 if old else 0,next_effect_id=old.next_effect_id if old else 1)
    return replace(state,priority=p,triggers=tuple(t for t in state.triggers if t.controller in alive),trigger_orders=())


def _stabilize(state, *, reset_priority=True):
    if reset_priority and state.combat is not None and state.combat.stage in ('blocking','ordering'):
        state=replace(state,combat=replace(state.combat,stage='attack_responses',locks=(),orders=()))
    # Genuine defeats are recorded before elimination ownership cleanup.
    defeated={o.object_id for o in state.battlefield if o.object_id in state.destroyed or (o.creature and o.creature.health<=0)}
    if defeated:
        state=_depart(state,defeated,'genuine_defeat',genuine=True)
    losing={p.cards.player_id for p in state.players if not p.eliminated and
            (p.cards.health<=0 or p.cards.player_id in state.failed_draws)}
    # One recorded concession per safe boundary; terminal checks precede the next.
    concession=state.concedes[:1]
    losing.update(p for p in concession if not _player(state,p).eliminated)
    for player_id in state.seat_order:
        if player_id not in losing:
            continue
        p=_player(state,player_id)
        causes=tuple(c for yes,c in ((p.cards.health<=0,'health'),(player_id in state.failed_draws,'failed_draw'),(player_id in concession,'concede')) if yes)
        p=replace(p,eliminated=True,causes=causes)
        state=_set_player(state,p)
        state,_=_emit(state,'elimination',player_id,'+'.join(causes))
    while True:
        alive=_living(state)
        ids={o.object_id for o in state.battlefield}
        removed={o.object_id for o in state.battlefield if o.owner not in alive or o.controller not in alive
                 or (o.attached_to is not None and o.attached_to not in ids)}
        if not removed:
            break
        state=_depart(state,removed,'elimination_or_attachment_cleanup')
    state=replace(state,failed_draws=(),destroyed=(),concedes=state.concedes[1:],
                  discard_needed=0 if _player(state,state.turn.active_player).eliminated else state.discard_needed)
    if reset_priority:
        state=_priority_after_cleanup(state)
    return _flush_triggers(state)


def _flush_triggers(state):
    if not state.triggers:
        return state
    groups={}
    for t in state.triggers:
        groups.setdefault(t.controller,[]).append(t)
    orders=dict(state.trigger_orders)
    if any(len(group)>1 and controller not in orders for controller,group in groups.items()):
        return state
    p=state.priority
    start=p.seats.index(p.active_player)
    seats=p.seats[start:]+p.seats[:start]
    chain=list(p.chain);next_id=p.next_effect_id
    for controller in seats:
        candidates=groups.get(controller,[])
        by_id={t.trigger_id:t for t in candidates}
        order=orders.get(controller,tuple(by_id))
        for trigger_id in order:
            t=by_id[trigger_id]
            chain.append(PendingEffect(next_id,controller,t.effect_key));next_id+=1
    return replace(state,priority=replace(p,chain=tuple(chain),holder=p.active_player,passes=(),
                   status='priority',revision=p.revision+1,next_effect_id=next_id),triggers=(),trigger_orders=())


def choose_trigger_order(state, actor, order, *, expected_revision):
    _check(state,expected_revision)
    own=tuple(t.trigger_id for t in state.triggers if t.controller==actor)
    if (type(order) is not tuple or any(type(i) is not int for i in order) or not own or len(order)!=len(own) or set(order)!=set(own)
            or actor in dict(state.trigger_orders)):
        raise MatchError('invalid or already-confirmed trigger order')
    state=replace(state,trigger_orders=state.trigger_orders+((actor,order),),revision=state.revision+1)
    return _quiescent(_flush_triggers(state))


def resolve_current(state, *, expected_revision):
    _check(state,expected_revision)
    if _blocked(state) or state.priority is None or state.priority.status!='resolving':
        raise MatchError('no newly resolving effect')
    effect=next(e for e in state.effects if e.key==state.priority.resolving.effect_key)
    return _run(replace(state,pending=Resolution(effect.steps),revision=state.revision+1))


def _record_draw(state, draw):
    p=_player(state,draw.player.player_id)
    state=_set_player(state,replace(p,cards=draw.player))
    if draw.status=='needs_refill':
        return replace(state,pending=replace(state.pending,draw=draw))
    failures=state.failed_draws
    if draw.status=='failed' and draw.player.player_id not in failures:
        failures+= (draw.player.player_id,)
    return replace(state,failed_draws=failures,draw_records=state.draw_records+(draw,),
                   pending=replace(state.pending,index=state.pending.index+1,draw=None))


def _run(state):
    while state.pending and state.pending.index<len(state.pending.steps):
        if state.pending.draw is not None:
            return state
        step=state.pending.steps[state.pending.index]
        if type(step) in (DamagePlayer,HealPlayer,DrawCards,GrantCapacity,GrantResources):
            p=_player(state,step.target)
            if p.eliminated:
                state=replace(state,pending=replace(state.pending,index=state.pending.index+1));continue
            if type(step) is DrawCards:
                draw=begin_required_draw(p.cards,state.turn,step.count,state.policy,
                        request_id=state.next_event_id,defer_health_check=True)
                state,_=_emit(state,'required_draw',step.target,str(step.count))
                if draw.status=='needs_refill' and step.target in state.concedes:
                    draw=decline_refill(draw,expected_request_id=draw.request_id,expected_revision=draw.revision)
                state=_record_draw(state,draw)
                if state.pending.draw is not None:
                    return state
                continue
            if type(step) in (GrantCapacity,GrantResources):
                field='permanent_bonus' if type(step) is GrantCapacity else 'available'
                pool=replace(p.resources,**{field:getattr(p.resources,field)+step.amount})
                state=_set_player(state,replace(p,resources=pool))
                state=replace(state,pending=replace(state.pending,index=state.pending.index+1))
                continue
            health=p.cards.health-step.amount if type(step) is DamagePlayer else min(p.max_health,p.cards.health+step.amount)
            state=_set_player(state,replace(p,cards=replace(p.cards,health=health)))
            state,_=_emit(state,'damage' if type(step) is DamagePlayer else 'heal',step.target,str(step.amount))
        else:  # validated DestroyCreature; absent targets do not cancel independent instructions
            obj=next((o for o in state.battlefield if o.object_id==step.target),None)
            if obj and obj.creature:
                state=replace(state,destroyed=state.destroyed+(obj.object_id,))
        state=replace(state,pending=replace(state.pending,index=state.pending.index+1))
    cleanup=state.pending.cleanup
    state=replace(state,pending=None)
    if cleanup:
        state=replace(state,end_stage='done')
    state=_stabilize(state)
    if state.start_stage=='cleanup':
        return _finish_start(state)
    return _quiescent(state)


def choose_refill(state, actor, *, pay, shuffled_discard=(), expected_request_id, expected_revision):
    _check(state,expected_revision)
    draw=state.pending.draw if state.pending else None
    if draw is None or draw.player.player_id!=actor or type(pay) is not bool or type(expected_request_id) is not int or expected_request_id!=draw.request_id:
        raise MatchError('wrong or absent refill choice')
    if pay:
        draw=accept_refill(draw,shuffled_discard,expected_request_id=draw.request_id,expected_revision=draw.revision)
    else:
        draw=decline_refill(draw,expected_request_id=draw.request_id,expected_revision=draw.revision)
    state=replace(state,revision=state.revision+1)
    return _run(_record_draw(state,draw))


def concede(state, actor, *, expected_revision):
    _check(state,expected_revision)
    if actor not in _living(state):
        raise MatchError('player is not active')
    if actor in state.concedes:
        raise MatchError('concession already recorded')
    state=replace(state,concedes=state.concedes+(actor,),revision=state.revision+1)
    state,_=_emit(state,'concede_request',actor,'confirmed')
    if state.pending or (state.priority and state.priority.status=='resolving'):
        if state.pending and state.pending.draw and state.pending.draw.player.player_id==actor:
            draw=state.pending.draw
            draw=decline_refill(draw,expected_request_id=draw.request_id,expected_revision=draw.revision)
            return _run(_record_draw(state,draw))
        return state
    return _quiescent(_stabilize(state))


def _quiescent(state):
    if state.pending:
        return state
    if state.triggers or state.discard_needed or (state.priority and (state.priority.chain or state.priority.status=='resolving')):
        return _quiescent(_stabilize(state)) if state.concedes else state
    active=_player(state,state.turn.active_player)
    # Empty-chain phase progression still needs every surviving seat to pass.
    # Terminal checks have no extra empty-chain reaction window.
    if len(_living(state))>1 and state.priority and state.priority.status!='closed':
        return _quiescent(_stabilize(state)) if state.concedes else state
    committed_combat=state.combat is not None and state.combat.stage!='done' and not active.eliminated
    ending=active.eliminated or (not committed_combat and (active.cards.end_turn_requested or state.turn.end_requested or state.turn.phase in ('End','Finished')))
    if ending and state.end_stage=='none':
        state=replace(state,turn=replace(state.turn,phase='End',end_requested=True,revision=state.turn.revision+1),end_stage='triggers')
        if not active.eliminated:
            state,event=_emit(state,'turn_end',active.cards.player_id,'normal_end')
            state=_flush_triggers(_capture(state,state.battlefield,(event,)))
            if state.triggers or (state.priority and state.priority.chain):
                return state
    if ending and state.end_stage in ('triggers','discard'):
        excess=max(0,len(active.cards.hand)-7) if not active.eliminated else 0
        state=replace(state,end_stage='discard',discard_needed=excess)
        if excess:
            return state
        state=replace(state,end_stage='cleanup')
        if state.end_cleanup:
            return _run(replace(state,pending=Resolution(state.end_cleanup,cleanup=True)))
        state=replace(state,end_stage='done',turn=replace(state.turn,phase='Finished',revision=state.turn.revision+1))
    if ending and state.end_stage=='done' and not active.eliminated:
        excess=max(0,len(active.cards.hand)-7)
        if excess:
            return replace(state,discard_needed=excess)
    alive=_living(state)
    if len(alive)<=1:
        return replace(state,result=MatchResult('draw') if not alive else MatchResult('win',alive[0]),priority=None,concedes=())
    if state.concedes:
        return _quiescent(_stabilize(state))
    if ending and state.end_stage=='done':
        index=state.seat_order.index(state.turn.active_player)
        next_player=next(p for p in state.seat_order[index+1:]+state.seat_order[:index+1] if p in alive)
        p=_player(state,next_player)
        cards,turn=open_turn(p.cards,turn_id=state.turn.turn_id+1)
        state=_set_player(state,replace(p,cards=cards))
        state=replace(state,turn=turn,end_stage='none',end_cleanup=(),combat=None,
                      start_stage='pending',start_cleanup=(),action_uses=())
        state=_priority_after_cleanup(state)
        if state.managed_turns:
            return _begin_start(state)
    if state.combat is not None and not ending:
        if state.combat.stage=='attack_responses':
            flow=begin_blocking(_combat_snapshot(state),state.combat)
            return _open_final_if_ordered(replace(state,combat=flow))
        if state.combat.stage=='final_responses':
            result=resolve_committed(_combat_snapshot(state),state.combat)
            state=_apply_combat_result(state,result)
            state=replace(state,combat=replace(state.combat,stage='done'),
                          turn=replace(state.turn,phase='MainAfter',revision=state.turn.revision+1))
            return _quiescent(_stabilize(state))
    if state.managed_turns and not ending:
        return _advance_managed(state)
    return state


def choose_end_discards(state, actor, cards, *, expected_revision):
    _check(state,expected_revision)
    p=_player(state,state.turn.active_player)
    if (actor!=p.cards.player_id or state.discard_needed<=0 or type(cards) is not tuple
            or len(cards)!=state.discard_needed or len(set(cards))!=len(cards)
            or any(card not in p.cards.hand for card in cards)):
        raise MatchError('invalid end-hand-limit choice')
    player=replace(p,cards=replace(p.cards,hand=tuple(c for c in p.cards.hand if c not in cards),discard=p.cards.discard+cards))
    state=_set_player(state,player)
    return _quiescent(replace(state,discard_needed=0,revision=state.revision+1))


def resolve_combat_snapshot(state, attacks, challenge_orders=(), *, expected_revision):
    """Atomic final-snapshot adapter, NOT full-match attack/block declaration windows."""
    _check(state,expected_revision)
    if state.managed_turns or state.combat is not None or state.turn.phase!='Combat' or _blocked(state) or state.priority is None or state.priority.chain or state.priority.status!='closed':
        raise MatchError('combat snapshot requires Combat phase and a closed empty response window')
    by_id={o.object_id:o for o in state.battlefield}
    if type(attacks) is not tuple or any(a.attacker_id not in by_id or by_id[a.attacker_id].controller!=state.turn.active_player for a in attacks):
        raise MatchError('combat attacks must belong to the active player')
    snapshot=CombatState(tuple(Player(p.cards.player_id,p.cards.health) for p in state.players if not p.eliminated),
                         tuple(o.creature for o in state.battlefield if o.creature))
    result=resolve_combat(snapshot,attacks,challenge_orders)
    return _quiescent(_stabilize(_apply_combat_result(replace(state,revision=state.revision+1),result)))


def _combat_snapshot(state):
    return CombatState(tuple(Player(p.cards.player_id,p.cards.health) for p in state.players if not p.eliminated),
                       tuple(o.creature for o in state.battlefield if o.creature))


def _apply_combat_result(state, result):
    for p in result.state.players:
        old=_player(state,p.player_id)
        state=_set_player(state,replace(old,cards=replace(old.cards,health=p.health)))
    survivors={c.instance_id:c for c in result.state.creatures}
    battlefield=tuple(replace(o,creature=survivors.get(o.object_id,replace(o.creature,health=0))) if o.creature else o for o in state.battlefield)
    state=replace(state,battlefield=battlefield)
    for damage in result.events:
        state,_=_emit(state,'combat_damage',damage.target_id,str(damage.health_damage))
    for attacker in result.misses:
        state,_=_emit(state,'combat_miss',attacker,'invalid_challenge_target')
    return state


def declare_match_attacks(state, actor, attacks, *, expected_revision):
    _check(state,expected_revision)
    if (actor not in _living(state) or actor!=state.turn.active_player or state.turn.phase!='Combat' or state.turn.recharge
            or state.turn.end_requested or _blocked(state) or state.combat is not None
            or state.priority is None or state.priority.status!='closed'):
        raise MatchError('not a fresh closed Combat declaration boundary')
    snapshot,flow=commit_attacks(_combat_snapshot(state),actor,attacks)
    updated={c.instance_id:c for c in snapshot.creatures}
    state=replace(state,battlefield=tuple(replace(o,creature=updated[o.object_id]) if o.creature else o for o in state.battlefield),
                  combat=flow,revision=state.revision+1)
    state,_=_emit(state,'attacks_declared',actor,str(len(attacks)))
    return _priority_after_cleanup(state)


def _open_final_if_ordered(state):
    if state.combat.stage=='ordering' and not required_orders(_combat_snapshot(state),state.combat):
        state=replace(state,combat=replace(state.combat,stage='final_responses'))
        return _priority_after_cleanup(state)
    return state


def lock_match_blockers(state, actor, assignments, *, expected_revision):
    _check(state,expected_revision)
    if state.combat is None or state.pending or state.triggers:
        raise MatchError('blocker batch unavailable')
    flow=lock_blockers(_combat_snapshot(state),state.combat,actor,assignments)
    state=replace(state,combat=flow,revision=state.revision+1)
    if flow.stage=='ordering':
        state,_=_emit(state,'blockers_revealed',state.turn.active_player,'all_defenders_locked')
    return _open_final_if_ordered(state)


def choose_match_combat_order(state, actor, subject, order, *, expected_revision):
    _check(state,expected_revision)
    if state.combat is None or state.pending or state.triggers:
        raise MatchError('combat order unavailable')
    flow=choose_order(_combat_snapshot(state),state.combat,actor,subject,order)
    return _open_final_if_ordered(replace(state,combat=flow,revision=state.revision+1))


def match_combat_view(state, viewer=None):
    if viewer is not None and viewer not in _living(state):
        raise MatchError('viewer is not an active player')
    return combat_view(state.combat,viewer) if state.combat is not None else None


def submit_action(state, actor, key, payment, *, expected_revision):
    """Confirm a registered source ability and exact costs as one transaction."""
    _check(state,expected_revision)
    if _blocked(state) or state.priority is None or state.priority.status!='priority' or state.priority.holder!=actor:
        raise MatchError('actor does not hold an actionable response window')
    action=next((a for a in state.actions if a.key==key),None)
    effect=next((e for e in state.effects if action and e.key==action.effect_key),None)
    source=next((o for o in state.battlefield if action and o.object_id==action.source_id),None)
    if action is None or effect.controller!=actor or source is None or source.controller!=actor or actor not in _living(state):
        raise MatchError('unavailable action/source/controller')
    active=actor==state.turn.active_player
    if active and (state.turn.recharge or _player(state,actor).cards.end_turn_requested):
        raise MatchError('active player is ending/Recharging')
    if action.timing=='main' and (not active or state.turn.phase not in ('MainBefore','MainAfter')
            or state.turn.end_requested or state.priority.chain):
        raise MatchError('ordinary abilities require own Main with an empty chain')
    if action.once_per_turn and (key,state.turn.turn_id) in state.action_uses:
        raise MatchError('per-turn ability already used')
    if action.exhaust_source and (source.creature is None or source.creature.exhausted or not source.creature.attack_eligible):
        raise MatchError('source cannot pay exhaust cost')
    if effect.source_id is not None and effect.source_id!=source.object_id:
        raise MatchError('registered effect/source mismatch')
    owner=_player(state,actor)
    tokens=tuple((o.object_id,o.resource_value) for o in state.battlefield if o.kind=='resource_token' and o.controller==actor)
    pool=pay_resources(owner.resources,action.resource_cost,payment,tokens)
    # All checks precede the first replacement; rejected commands leave every ID intact.
    priority=add_effect(state.priority,actor,effect.key,expected_revision=state.priority.revision)
    state=_set_player(state,replace(owner,resources=pool))
    if action.exhaust_source:
        state=replace(state,battlefield=tuple(replace(o,creature=replace(o.creature,exhausted=True)) if o.object_id==source.object_id else o for o in state.battlefield))
    state=replace(state,priority=priority,revision=state.revision+1,
                  action_uses=state.action_uses+(((key,state.turn.turn_id),) if action.once_per_turn else ()))
    if payment.token_ids:
        state=_depart(state,set(payment.token_ids),'cost_payment')
    state,_=_emit(state,'action_committed',actor,key)
    return _quiescent(_stabilize(state,reset_priority=False))


def _phase_window(state, phase):
    turn=replace(state.turn,phase=phase,revision=state.turn.revision+1)
    return _priority_after_cleanup(replace(state,turn=turn))


def _begin_start(state):
    if state.start_stage!='pending' or state.turn.phase!='Start':
        raise MatchError('Start maintenance already applied')
    state=replace(state,start_stage='cleanup')
    if state.start_cleanup:
        return _run(replace(state,pending=Resolution(state.start_cleanup)))
    return _finish_start(state)


def _finish_start(state):
    active=_player(state,state.turn.active_player)
    state=replace(state,start_stage='done',start_cleanup=())
    if active.eliminated:
        return _quiescent(state)
    bonus=sum(o.capacity_bonus for o in state.battlefield if o.controller==active.cards.player_id)
    active=replace(active,resources=start_resources(active.resources,bonus))
    state=_set_player(state,active)
    state=replace(state,battlefield=tuple(replace(o,creature=replace(o.creature,exhausted=False,
                  attack_eligible=True,attack_used=False)) if o.controller==active.cards.player_id and o.creature else o
                  for o in state.battlefield))
    state,event=_emit(state,'turn_start',active.cards.player_id,str(active.resources.own_starts))
    state=_capture(state,state.battlefield,(event,))
    return _quiescent(_stabilize(state))


def _advance_managed(state):
    phase=state.turn.phase
    active=_player(state,state.turn.active_player)
    if phase=='Start':
        if state.turn.recharge:
            return _quiescent(replace(state,turn=replace(state.turn,end_requested=True)))
        if not active.cards.deck:
            draw=begin_start_refill(active.cards,state.turn,state.policy,request_id=state.next_event_id)
            state,_=_emit(state,'start_refill',active.cards.player_id,'empty_deck')
            state=replace(state,pending=Resolution((DrawCards(active.cards.player_id,0),)))
            return _run(_record_draw(state,draw))
        state=_phase_window(state,'Draw')
        skip=len(state.seat_order)==2 and active.cards.player_id==state.starting_player and active.resources.own_starts==1
        return _run(replace(state,pending=Resolution((DrawCards(active.cards.player_id,0 if skip else 1),))))
    if phase=='Draw':
        return _phase_window(state,'MainBefore')
    if phase=='MainBefore':
        return _phase_window(state,'Combat')
    if phase=='Combat':
        return state  # committed declaration workflow owns this phase
    if phase=='MainAfter':
        return _quiescent(replace(state,turn=replace(state.turn,end_requested=True)))
    return state
