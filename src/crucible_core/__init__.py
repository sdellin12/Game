"""Pure deterministic rules, without UI, I/O, global randomness or match bots."""

from .combat import (
    Attack, CombatError, CombatResult, CombatState, Creature, DamageEvent,
    Player, Shield, resolve_combat,
)

__all__ = [
    "Attack", "CombatError", "CombatResult", "CombatState", "Creature",
    "DamageEvent", "Player", "Shield", "resolve_combat",
]
