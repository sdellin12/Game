"""An isolated, already-declared combat step, NOT a full match engine.

All combat groups assign damage using the same pre-damage snapshot. A creature
may participate in only one group (several challengers may share one target).
Resolution assumes response windows have closed. Only the supported fields in
these immutable types participate; no card prose or arbitrary callbacks run.
"""

from dataclasses import dataclass, replace


class CombatError(ValueError):
    """Rejected scenario/command; the immutable input remains unchanged."""


def natural(value: int, label: str, minimum: int = 0) -> None:
    if type(value) is not int or value < minimum:
        raise CombatError(f"{label} must be an integer >= {minimum}")


@dataclass(frozen=True)
class Shield:
    shield_id: str
    amount: int
    expiry_rank: int = 0


@dataclass(frozen=True)
class Creature:
    instance_id: str
    controller: str
    attack: int
    health: int
    max_health: int
    exhausted: bool = False
    attack_eligible: bool = True
    attack_used: bool = False
    keywords: tuple[str, ...] = ()
    shields: tuple[Shield, ...] = ()


@dataclass(frozen=True)
class Player:
    player_id: str
    health: int = 30


@dataclass(frozen=True)
class CombatState:
    players: tuple[Player, ...]
    creatures: tuple[Creature, ...]


@dataclass(frozen=True)
class Attack:
    attacker_id: str
    target_player: str
    blockers: tuple[str, ...] = ()
    was_blocked: bool = False
    challenge_target: str | None = None


@dataclass(frozen=True)
class DamageEvent:
    source_ids: tuple[str, ...]
    target_id: str
    target_kind: str
    raw: int
    modified: int
    prevented: int
    health_damage: int


@dataclass(frozen=True)
class CombatResult:
    state: CombatState
    defeated_creatures: tuple[str, ...]
    lethal_players: tuple[str, ...]
    events: tuple[DamageEvent, ...]
    misses: tuple[str, ...]


def validate_state(state: CombatState) -> None:
    if type(state.players) is not tuple or type(state.creatures) is not tuple:
        raise CombatError("state collections must be tuples")
    players = [p.player_id for p in state.players]
    creatures = [c.instance_id for c in state.creatures]
    if any(not isinstance(i, str) or not i for i in players + creatures):
        raise CombatError("IDs must be nonempty strings")
    if len(set(players + creatures)) != len(players + creatures):
        raise CombatError("player and creature IDs must be globally unique")
    for p in state.players:
        natural(p.health, "player health", 1)
    for c in state.creatures:
        if c.controller not in players:
            raise CombatError("creature controller must exist")
        natural(c.attack, "attack")
        natural(c.max_health, "maximum health", 1)
        natural(c.health, "health", 1)
        if c.health > c.max_health:
            raise CombatError("health exceeds maximum")
        if any(type(b) is not bool for b in
               (c.exhausted, c.attack_eligible, c.attack_used)):
            raise CombatError("readiness flags must be booleans")
        if type(c.keywords) is not tuple or any(
            k not in ("breakthrough", "challenge") for k in c.keywords
        ) or len(set(c.keywords)) != len(c.keywords):
            raise CombatError("unsupported or duplicate keyword")
        if type(c.shields) is not tuple:
            raise CombatError("shields must be a tuple")
        ids = set()
        for shield in c.shields:
            if not isinstance(shield.shield_id, str) or not shield.shield_id:
                raise CombatError("shield ID required")
            if shield.shield_id in ids:
                raise CombatError("duplicate shield ID")
            ids.add(shield.shield_id)
            natural(shield.amount, "shield amount")
            natural(shield.expiry_rank, "shield expiry rank")


def _modified(raw: int, exhausted_blocker: bool) -> int:
    return (3 * raw + 1) // 2 if exhausted_blocker else raw


def _lethal_raw(c: Creature, exhausted_blocker: bool) -> int:
    # Smallest D with ceil(1.5 D) - shields >= HP, using integer arithmetic.
    needed = c.health + sum(s.amount for s in c.shields)
    return (2 * (needed - 1)) // 3 + 1 if exhausted_blocker else needed


def resolve_combat(
    state: CombatState,
    attacks: tuple[Attack, ...],
    challenge_orders: tuple[tuple[str, tuple[str, ...]], ...] = (),
) -> CombatResult:
    """Resolve legal final combat assignments simultaneously.

    Blocker tuples are attacker-selected order. challenge_orders supplies the
    target controller's chosen retaliation order; default is declaration order
    (experimental deterministic fallback, recorded by the scenario runner).
    Missing Challenge targets miss; removed normal blockers are represented by
    an empty blocker tuple plus was_blocked=True. Dangling blocker IDs reject.
    Lethal players are reported, not cleaned up/declared winners: full-match
    elimination, response and trigger processing are outside this kernel.
    """
    return _resolve_damage(state, attacks, challenge_orders)


def _validate_assignments(state, attacks, challenge_orders=(), *, require_fresh=True):
    validate_state(state)
    if type(attacks) is not tuple or type(challenge_orders) is not tuple:
        raise CombatError("combat commands must be tuples")
    by_id = {c.instance_id: c for c in state.creatures}
    player_ids = {p.player_id for p in state.players}
    attackers: set[str] = set()
    blockers: set[str] = set()
    groups: dict[str, list[str]] = {}
    acting_controller = None
    for a in attacks:
        if type(a.blockers) is not tuple or type(a.was_blocked) is not bool:
            raise CombatError("invalid blocker command")
        if a.attacker_id not in by_id or a.attacker_id in attackers:
            raise CombatError("missing or duplicate attacker")
        c = by_id[a.attacker_id]
        if require_fresh and (c.exhausted or not c.attack_eligible or c.attack_used):
            raise CombatError("attacker cannot attack")
        if acting_controller is None:
            acting_controller = c.controller
        if c.controller != acting_controller:
            raise CombatError("all attackers must share the active controller")
        if a.target_player not in player_ids or a.target_player == c.controller:
            raise CombatError("invalid defending player")
        attackers.add(a.attacker_id)
        if a.challenge_target is not None:
            if not isinstance(a.challenge_target, str) or not a.challenge_target:
                raise CombatError("invalid Challenge target ID")
            if (require_fresh and "challenge" not in c.keywords) or a.blockers or a.was_blocked:
                raise CombatError("Challenge requires permission and no blockers")
            if a.challenge_target in player_ids:
                raise CombatError("Challenge targets creatures, not players")
            target = by_id.get(a.challenge_target)
            if require_fresh and target is not None and target.controller != a.target_player:
                raise CombatError("Challenge target belongs to another controller")
            groups.setdefault(a.challenge_target, []).append(a.attacker_id)
        for blocker_id in a.blockers:
            if blocker_id not in by_id or blocker_id in blockers:
                raise CombatError("missing blocker or blocker assigned twice")
            if by_id[blocker_id].controller != a.target_player:
                raise CombatError("ordinary blocker must belong to defender")
            blockers.add(blocker_id)
    if attackers & blockers or attackers & groups.keys() or blockers & groups.keys():
        raise CombatError("creature participates in incompatible combat groups")
    orders: dict[str, tuple[str, ...]] = {}
    for target_id, order in challenge_orders:
        if target_id in orders or target_id not in groups or type(order) is not tuple:
            raise CombatError("invalid Challenge retaliation order")
        if len(order) != len(groups[target_id]) or set(order) != set(groups[target_id]):
            raise CombatError("Challenge order must contain every challenger once")
        orders[target_id] = order

    return by_id, player_ids, attackers, groups, orders


def _resolve_damage(state, attacks, challenge_orders=(), *, require_fresh=True):
    """Shared damage kernel; committed-flow callers already paid attack usage."""
    by_id, player_ids, attackers, groups, orders = _validate_assignments(
        state, attacks, challenge_orders, require_fresh=require_fresh)
    events: list[DamageEvent] = []
    damage: dict[str, int] = {}
    shields_after: dict[str, tuple[Shield, ...]] = {}
    player_damage = {p: 0 for p in player_ids}
    misses: list[str] = []

    def hit(sources: tuple[str, ...], target: Creature, raw: int,
            penalty: bool = False) -> None:
        modified = _modified(raw, penalty)
        remaining = modified
        retained = []
        for s in sorted(target.shields, key=lambda s: (s.expiry_rank, s.shield_id)):
            used = min(remaining, s.amount)
            remaining -= used
            if s.amount > used:
                retained.append(replace(s, amount=s.amount - used))
        shields_after[target.instance_id] = tuple(retained)
        damage[target.instance_id] = remaining
        events.append(DamageEvent(sources, target.instance_id, "creature", raw,
                                  modified, modified - remaining, remaining))

    def hit_player(source: str, target: str, amount: int) -> None:
        player_damage[target] += amount
        events.append(DamageEvent((source,), target, "player", amount,
                                  amount, 0, amount))

    for a in attacks:
        c = by_id[a.attacker_id]
        if a.challenge_target is not None:
            continue
        budget = c.attack
        if not a.blockers and not a.was_blocked:
            hit_player(c.instance_id, a.target_player, budget)
            continue
        for blocker_id in a.blockers:
            target = by_id[blocker_id]
            assigned = min(budget, _lethal_raw(target, target.exhausted))
            budget -= assigned
            hit((c.instance_id,), target, assigned, target.exhausted)
        if "breakthrough" in c.keywords:
            hit_player(c.instance_id, a.target_player, budget)
        if a.blockers:
            hit(a.blockers, c, sum(by_id[b].attack for b in a.blockers))

    for target_id, challengers in groups.items():
        target = by_id.get(target_id)
        if target is None:
            misses.extend(challengers)
            continue
        hit(tuple(challengers), target, sum(by_id[c].attack for c in challengers))
        budget = target.attack
        for challenger_id in orders.get(target_id, tuple(challengers)):
            c = by_id[challenger_id]
            assigned = min(budget, _lethal_raw(c, False))
            budget -= assigned
            hit((target_id,), c, assigned)

    survivors, defeated = [], []
    for c in state.creatures:
        hp = max(0, c.health - damage.get(c.instance_id, 0))
        if hp == 0:
            defeated.append(c.instance_id)
        else:
            survivors.append(replace(
                c, health=hp, shields=shields_after.get(c.instance_id, c.shields),
                exhausted=c.exhausted or (require_fresh and c.instance_id in attackers),
                attack_used=c.attack_used or c.instance_id in attackers,
            ))
    players = tuple(replace(p, health=max(0, p.health - player_damage[p.player_id]))
                    for p in state.players)
    return CombatResult(CombatState(players, tuple(survivors)), tuple(defeated),
                        tuple(p.player_id for p in players if p.health == 0),
                        tuple(events), tuple(misses))
