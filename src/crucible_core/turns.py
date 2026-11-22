"""Pure turn sequencing and required-draw/refill primitives.

Not a match coordinator: effect legality, Start/End effects, priority, terminal
cleanup and saved-match schemas remain external. No global RNG or simulator fork.
"""
from dataclasses import dataclass, replace


class TurnError(ValueError):
    """Invalid/stale command; original immutable state is unchanged."""


class UnsupportedTurnRule(TurnError):
    """An unresolved Recharge/bypass interaction was requested."""


PHASES = ('Start', 'Draw', 'MainBefore', 'Combat', 'MainAfter', 'End', 'Finished')


@dataclass(frozen=True)
class DrawPlayer:
    player_id: str
    health: int
    deck: tuple[str, ...]
    discard: tuple[str, ...]
    hand: tuple[str, ...] = ()
    recharge_due: bool = False
    end_turn_requested: bool = False


@dataclass(frozen=True)
class TurnFlow:
    active_player: str
    turn_id: int
    phase: str = 'Start'
    recharge: bool = False
    end_requested: bool = False
    revision: int = 0


@dataclass(frozen=True)
class RefillPolicy:
    # Required experiment parameters, NOT adopted default prices/payment floors.
    life_cost: int
    minimum_health_after_payment: int


@dataclass(frozen=True)
class DrawState:
    player: DrawPlayer
    turn: TurnFlow
    policy: RefillPolicy
    request_id: int
    remaining: int
    status: str  # needs_refill, complete, failed
    reason: str = 'required_draw'
    failure: str | None = None
    shuffles: tuple[tuple[str, ...], ...] = ()
    revision: int = 1


def _integer(value, minimum=0):
    return type(value) is int and value >= minimum


def _name(value):
    return type(value) is str and bool(value.strip())


def _validate_player(player):
    if type(player) is not DrawPlayer or not _name(player.player_id) or not _integer(player.health, 1):
        raise TurnError('expected a living DrawPlayer with positive health')
    if any(type(flag) is not bool for flag in (player.recharge_due, player.end_turn_requested)):
        raise TurnError('invalid player timing flags')
    zones = (player.deck, player.discard, player.hand)
    if any(type(zone) is not tuple or any(not _name(card) for card in zone) for zone in zones):
        raise TurnError('zones must be tuples of stable card-instance IDs')
    cards = player.deck + player.discard + player.hand
    if len(set(cards)) != len(cards):
        raise TurnError('card-instance IDs must be unique across zones')


def _validate_turn(turn):
    if (type(turn) is not TurnFlow or not _name(turn.active_player)
            or not _integer(turn.turn_id, 1) or not _integer(turn.revision)
            or turn.phase not in PHASES
            or any(type(flag) is not bool for flag in (turn.recharge, turn.end_requested))):
        raise TurnError('invalid turn flow')
    if turn.recharge and turn.phase not in ('Start', 'End', 'Finished'):
        raise TurnError('Recharge skips normal Draw/Main/Combat phases')


def _validate_policy(policy):
    if (type(policy) is not RefillPolicy or not _integer(policy.life_cost, 1)
            or not _integer(policy.minimum_health_after_payment, 1)):
        raise TurnError('explicit positive refill cost and payment floor required')


def open_turn(player, *, turn_id):
    """Coordinator-only: consume one approved Recharge obligation at own Start."""
    _validate_player(player)
    turn = TurnFlow(player.player_id, turn_id, recharge=player.recharge_due)
    _validate_turn(turn)
    return replace(player, recharge_due=False, end_turn_requested=False), turn


def _check_turn(turn, expected_turn_id, expected_revision):
    _validate_turn(turn)
    if (type(expected_turn_id) is not int or expected_turn_id != turn.turn_id
            or type(expected_revision) is not int or expected_revision != turn.revision):
        raise TurnError('stale turn ID/revision')
    if turn.phase == 'Finished':
        raise TurnError('turn already finished')


def request_end_turn(turn, *, expected_turn_id, expected_revision):
    """Mark the request; never truncate the currently resolving effect/chain."""
    _check_turn(turn, expected_turn_id, expected_revision)
    return replace(turn, end_requested=True, revision=turn.revision + 1)


def advance_at_boundary(turn, *, expected_turn_id, expected_revision):
    """Coordinator-only AFTER mandatory effects, priority and cleanup have settled.

    This does not run Start recovery/resources, End triggers/discards/expiry or
    choose the next surviving seat. The caller must do those before advancing.
    """
    _check_turn(turn, expected_turn_id, expected_revision)
    if turn.phase == 'End':
        phase = 'Finished'
    elif turn.end_requested or turn.recharge:
        phase = 'End'
    else:
        phase = PHASES[PHASES.index(turn.phase) + 1]
    return replace(turn, phase=phase, revision=turn.revision + 1)


def may_take_main_action(turn, actor):
    _validate_turn(turn)
    return (actor == turn.active_player and turn.phase in ('MainBefore', 'MainAfter')
            and not turn.recharge and not turn.end_requested)


def _refill_failure(player, policy):
    if not player.discard:
        return 'no_refill_cards'
    if player.health - policy.life_cost < policy.minimum_health_after_payment:
        return 'cannot_pay_refill'
    return None


def _advance_draw(state):
    player, remaining = state.player, state.remaining
    while remaining and player.deck:
        card, rest = player.deck[0], player.deck[1:]
        player = replace(player, deck=rest, hand=player.hand + (card,),
                         end_turn_requested=player.end_turn_requested or (
                             not rest and player.player_id == state.turn.active_player))
        remaining -= 1
    state = replace(state, player=player, remaining=remaining)
    if not remaining:
        return replace(state, status='complete', failure=None)
    failure = _refill_failure(player, state.policy)
    if failure:
        return replace(state, status='failed', failure=failure)
    if player.player_id != state.turn.active_player and player.recharge_due:
        raise UnsupportedTurnRule('multiple off-turn refills before Recharge need a stacking rule')
    return replace(state, status='needs_refill', failure=None)


def begin_required_draw(player, turn, count, policy, *, request_id):
    _validate_player(player); _validate_turn(turn); _validate_policy(policy)
    if not _integer(count) or not _integer(request_id, 1) or turn.phase == 'Finished':
        raise TurnError('invalid draw count/request or finished turn')
    if count and player.player_id == turn.active_player and turn.recharge:
        raise UnsupportedTurnRule('mandatory draw during Recharge is not specified yet')
    state = DrawState(player, turn, policy, request_id, count, 'complete')
    return _advance_draw(state)


def begin_start_refill(player, turn, policy, *, request_id):
    _validate_player(player); _validate_turn(turn); _validate_policy(policy)
    if (turn.phase != 'Start' or turn.active_player != player.player_id or player.deck
            or not _integer(request_id, 1)):
        raise TurnError('Start refill requires the active player with an empty deck')
    if turn.recharge:
        raise UnsupportedTurnRule('empty-deck refill during Recharge needs a rule')
    failure = _refill_failure(player, policy)
    return DrawState(player, turn, policy, request_id, 0,
                     'failed' if failure else 'needs_refill', reason='start_refill', failure=failure)


def _check_choice(state, request_id, revision):
    if type(state) is not DrawState:
        raise TurnError('expected DrawState')
    _validate_player(state.player); _validate_turn(state.turn); _validate_policy(state.policy)
    if (not _integer(state.request_id, 1) or not _integer(state.remaining)
            or not _integer(state.revision, 1) or state.reason not in ('required_draw', 'start_refill')):
        raise TurnError('invalid draw state')
    if (type(request_id) is not int or request_id != state.request_id
            or type(revision) is not int or revision != state.revision):
        raise TurnError('stale draw request/revision')
    if (state.status != 'needs_refill' or state.player.deck
            or _refill_failure(state.player, state.policy)):
        raise TurnError('no payable refill choice is pending')


def accept_refill(state, shuffled_discard, *, expected_request_id, expected_revision):
    """Explicit recorded shuffle outcome, not a global RNG or arbitrary callback."""
    _check_choice(state, expected_request_id, expected_revision)
    if (type(shuffled_discard) is not tuple or any(not _name(c) for c in shuffled_discard)
            or len(shuffled_discard) != len(state.player.discard)
            or set(shuffled_discard) != set(state.player.discard)):
        raise TurnError('shuffle must be a permutation of the eligible discard IDs')
    off_turn = state.player.player_id != state.turn.active_player
    if off_turn and state.player.recharge_due:
        raise UnsupportedTurnRule('multiple off-turn refills before Recharge need a stacking rule')
    player = replace(state.player, health=state.player.health - state.policy.life_cost,
                     deck=shuffled_discard, discard=(),
                     recharge_due=state.player.recharge_due or off_turn,
                     end_turn_requested=state.player.end_turn_requested or not off_turn)
    state = replace(state, player=player, revision=state.revision + 1,
                    shuffles=state.shuffles + (shuffled_discard,))
    return _advance_draw(state)


def decline_refill(state, *, expected_request_id, expected_revision):
    _check_choice(state, expected_request_id, expected_revision)
    return replace(state, status='failed', failure='refill_declined', revision=state.revision + 1)
