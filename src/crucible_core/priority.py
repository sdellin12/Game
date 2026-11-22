"""Pure response-window transitions; no card effects, costs or turn engine.

The match coordinator must validate card/timing/cost legality before adding an
item, resolve/stabilize the requested item, and collect trigger choices before
finishing resolution. This module never evaluates effect prose or hidden cards.
"""
from dataclasses import dataclass, replace


class PriorityError(ValueError):
    """Rejected command; immutable state is unchanged."""


@dataclass(frozen=True)
class PendingEffect:
    effect_id: int
    controller: str
    effect_key: str


@dataclass(frozen=True)
class PriorityState:
    seats: tuple[str, ...]
    active_player: str
    holder: str | None
    chain: tuple[PendingEffect, ...] = ()  # oldest -> newest
    passes: tuple[str, ...] = ()
    status: str = 'priority'  # priority, resolving, closed
    resolving: PendingEffect | None = None
    revision: int = 0
    next_effect_id: int = 1


def _text(value):
    return type(value) is str and bool(value.strip())


def _next(seats, player):
    return seats[(seats.index(player) + 1) % len(seats)]


def validate_priority(state):
    if type(state) is not PriorityState:
        raise PriorityError('expected PriorityState')
    if (type(state.seats) is not tuple or not state.seats
            or any(not _text(p) for p in state.seats)
            or len(set(state.seats)) != len(state.seats)):
        raise PriorityError('seats must be a nonempty tuple of unique player IDs')
    if state.active_player not in state.seats:
        raise PriorityError('active player must be seated')
    if (type(state.revision) is not int or state.revision < 0
            or type(state.next_effect_id) is not int or state.next_effect_id < 1):
        raise PriorityError('invalid revision/effect counter')
    if type(state.chain) is not tuple or type(state.passes) is not tuple:
        raise PriorityError('chain and passes must be tuples')
    effects = state.chain + ((state.resolving,) if state.resolving is not None else ())
    for effect in effects:
        if (type(effect) is not PendingEffect or type(effect.effect_id) is not int
                or not 0 < effect.effect_id < state.next_effect_id
                or effect.controller not in state.seats or not _text(effect.effect_key)):
            raise PriorityError('invalid pending effect')
    ids = [e.effect_id for e in effects]
    if len(set(ids)) != len(ids) or ids != sorted(ids):
        raise PriorityError('duplicate or out-of-order live effect IDs')
    if state.status == 'priority':
        if state.holder not in state.seats or state.resolving is not None:
            raise PriorityError('priority window needs a holder and no resolving item')
        if len(state.passes) >= len(state.seats) or any(p not in state.seats for p in state.passes):
            raise PriorityError('invalid pass sequence')
        if len(set(state.passes)) != len(state.passes):
            raise PriorityError('duplicate passes')
        for first, second in zip(state.passes, state.passes[1:] + (state.holder,)):
            if _next(state.seats, first) != second:
                raise PriorityError('passes must follow seat order')
    elif state.status in ('resolving', 'closed'):
        if state.holder is not None or state.passes:
            raise PriorityError('inactive window cannot hold priority or passes')
        if state.status == 'resolving' and state.resolving is None:
            raise PriorityError('resolution requires an item')
        if state.status == 'closed' and (state.chain or state.resolving is not None):
            raise PriorityError('closed window must be empty')
    else:
        raise PriorityError('unsupported window status')


def new_priority(seats: tuple[str, ...], active_player: str) -> PriorityState:
    state = PriorityState(seats, active_player, active_player)
    validate_priority(state)
    return state


def _check(state, expected_revision, status, actor=None):
    validate_priority(state)
    if type(expected_revision) is not int or expected_revision != state.revision:
        raise PriorityError('stale or invalid state revision')
    if state.status != status:
        raise PriorityError(f'expected {status} window')
    if actor is not None and actor != state.holder:
        raise PriorityError('player does not hold priority')


def add_effect(state, actor, effect_key, *, expected_revision):
    """Internal commit after the caller validates timing, targets and payment."""
    _check(state, expected_revision, 'priority', actor)
    if actor not in state.seats or not _text(effect_key):
        raise PriorityError('invalid effect controller/key')
    effect = PendingEffect(state.next_effect_id, actor, effect_key)
    return replace(state, chain=state.chain + (effect,), passes=(),
                   holder=_next(state.seats, actor), revision=state.revision + 1,
                   next_effect_id=state.next_effect_id + 1)


def pass_priority(state, actor, *, expected_revision):
    _check(state, expected_revision, 'priority', actor)
    if actor not in state.seats:
        raise PriorityError('invalid player')
    passes = state.passes + (actor,)
    if len(passes) < len(state.seats):
        return replace(state, passes=passes, holder=_next(state.seats, actor),
                       revision=state.revision + 1)
    if state.chain:
        return replace(state, chain=state.chain[:-1], resolving=state.chain[-1],
                       holder=None, passes=(), status='resolving', revision=state.revision + 1)
    return replace(state, holder=None, passes=(), status='closed', revision=state.revision + 1)


def finish_resolution(state, effect_id, *, expected_revision, trigger_groups=()):
    """Coordinator-only: resolved/stabilized one item and collected trigger choices.

    trigger_groups contains (controller, tuple of effect keys oldest->newest).
    Groups append in active-seat-first order, so the last group's newest item
    resolves first. Seat elimination is not supported by this first slice.
    """
    _check(state, expected_revision, 'resolving')
    if type(effect_id) is not int or effect_id != state.resolving.effect_id:
        raise PriorityError('wrong resolving effect ID')
    if type(trigger_groups) is not tuple:
        raise PriorityError('trigger groups must be a tuple')
    groups = {}
    for group in trigger_groups:
        if type(group) is not tuple or len(group) != 2:
            raise PriorityError('invalid trigger group')
        controller, keys = group
        if (not _text(controller) or controller not in state.seats or controller in groups
                or type(keys) is not tuple or any(not _text(key) for key in keys)):
            raise PriorityError('invalid or duplicate trigger controller/keys')
        groups[controller] = keys
    start = state.seats.index(state.active_player)
    order = state.seats[start:] + state.seats[:start]
    chain = list(state.chain)
    next_id = state.next_effect_id
    for controller in order:
        for key in groups.get(controller, ()):
            chain.append(PendingEffect(next_id, controller, key))
            next_id += 1
    return replace(state, holder=state.active_player, resolving=None, passes=(),
                   status='priority', chain=tuple(chain), revision=state.revision + 1,
                   next_effect_id=next_id)


def reopen_priority(state, active_player, *, expected_revision):
    """Coordinator-only phase boundary; revisions and IDs never reset."""
    _check(state, expected_revision, 'closed')
    if active_player not in state.seats:
        raise PriorityError('active player must be seated')
    return replace(state, active_player=active_player, holder=active_player,
                   status='priority', revision=state.revision + 1)
