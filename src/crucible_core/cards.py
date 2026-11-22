"""Experimental match-only card definitions/instances; not the household catalog format."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CardDefinition:
    key: str
    kind: str  # creature, permanent, action, reaction
    cost: int
    steps: tuple = ()
    attack: int = 0
    health: int = 0
    keywords: tuple[str, ...] = ()
    capacity_bonus: int = 0
    target_kind: str | None = None  # player, creature, effect
    target_relation: str = 'any'  # any, friendly, enemy


@dataclass(frozen=True)
class CardInstance:
    instance_id: str
    definition_key: str
    owner: str


@dataclass(frozen=True)
class PendingCard:
    card_id: str
    effect_id: int
    controller: str
