"""Leader definitions and outside-deck state. No production save format."""
from dataclasses import dataclass


@dataclass(frozen=True)
class LeaderAbility:
    key: str
    cost: int
    steps: tuple
    timing: str = 'main'
    target_kind: str | None = None
    target_relation: str = 'any'
    exhaust_source: bool = False
    once_per_turn: bool = True


@dataclass(frozen=True)
class LeaderDefinition:
    key: str
    name: str
    color: str
    summon_cost: int
    attack: int
    health: int
    reserve_ability: LeaderAbility
    battle_ability: LeaderAbility
    keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class LeaderState:
    instance_id: str
    owner: str
    definition_key: str
    location: str = 'reserve'
    removals: int = 0
    recovering: bool = False
    pending_effect_id: int | None = None
