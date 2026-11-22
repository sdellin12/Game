"""Atomic typed-effect coordinator for a deliberately restricted match subset.

Server-internal state only; no client projections or production save schema.
Effects are registered immutable instructions, never arbitrary prose/callbacks.
"""
from dataclasses import dataclass, replace
from .combat import Creature, CombatState, Player, resolve_combat, validate_state
from .priority import PriorityState, PendingEffect, add_effect, pass_priority, validate_priority
from .turns import (DrawPlayer, TurnFlow, RefillPolicy, DrawState, begin_required_draw,
                    accept_refill, decline_refill, open_turn, request_end_turn,
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


@dataclass(frozen=True)
class MatchPlayer:
    cards: DrawPlayer
    max_health: int = 30
    eliminated: bool = False
    causes: tuple[str, ...] = ()


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
        if type(step) in (DamagePlayer, HealPlayer):
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
    for o in state.battlefield:
        if (type(o) is not MatchObject or not _name(o.object_id)
                or o.owner not in state.seat_order or o.controller not in state.seat_order):
            raise MatchError('invalid battlefield object')
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
            if (type(t) is not TriggerSpec or t.event not in ('defeat','departure','turn_end')
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


def new_match(players, battlefield, effects, policy, *, active_player, phase='MainBefore', end_cleanup=()):
    """Fixture/coordinator factory; no deck/lobby setup or full-match mode implied."""
    seats=tuple(p.cards.player_id for p in players)
    state=MatchState(seats,players,battlefield,effects,policy,TurnFlow(active_player,1,phase=phase),
                     PriorityState(seats,active_player,active_player),end_cleanup=end_cleanup)
    validate_match(state)
    if any(p.eliminated or p.cards.health <= 0 for p in players):
        raise MatchError('initial players must be alive')
    return state


def _check(state, revision):
    validate_match(state)
    if type(revision) is not int or revision != state.revision:
        raise MatchError('stale match revision')
    if state.result is not None:
        raise MatchError('match already ended')


def _blocked(state):
    return state.pending is not None or bool(state.triggers) or state.discard_needed > 0


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
                own = source.controller==event.subject if event.kind=='turn_end' else source.object_id==event.subject
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


def _stabilize(state):
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
        if type(step) in (DamagePlayer,HealPlayer,DrawCards):
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
    ending=active.eliminated or active.cards.end_turn_requested or state.turn.end_requested or state.turn.phase in ('End','Finished')
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
        state=replace(state,turn=turn,end_stage='none',end_cleanup=())
        state=_priority_after_cleanup(state)
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
    if state.turn.phase!='Combat' or _blocked(state) or state.priority is None or state.priority.chain or state.priority.status!='closed':
        raise MatchError('combat snapshot requires Combat phase and a closed empty response window')
    by_id={o.object_id:o for o in state.battlefield}
    if type(attacks) is not tuple or any(a.attacker_id not in by_id or by_id[a.attacker_id].controller!=state.turn.active_player for a in attacks):
        raise MatchError('combat attacks must belong to the active player')
    snapshot=CombatState(tuple(Player(p.cards.player_id,p.cards.health) for p in state.players if not p.eliminated),
                         tuple(o.creature for o in state.battlefield if o.creature))
    result=resolve_combat(snapshot,attacks,challenge_orders)
    for p in result.state.players:
        old=_player(state,p.player_id)
        state=_set_player(state,replace(old,cards=replace(old.cards,health=p.health)))
    survivors={c.instance_id:c for c in result.state.creatures}
    battlefield=tuple(replace(o,creature=survivors.get(o.object_id,replace(o.creature,health=0))) if o.creature else o for o in state.battlefield)
    state=replace(state,battlefield=battlefield,revision=state.revision+1)
    return _quiescent(_stabilize(state))
