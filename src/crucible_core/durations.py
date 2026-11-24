"""Original-seat boundary clocks and typed duration records."""
from dataclasses import dataclass


@dataclass(frozen=True)
class BoundaryCount:
    player_id: str
    starts: int = 0
    ends: int = 0


@dataclass(frozen=True)
class TimedEffect:
    duration_id: int
    controller: str
    anchor_player: str
    boundary: str
    occurrence: int
    target_id: str | None = None
    shield_id: str | None = None
    expiration_steps: tuple = ()


def expiry_rank(seats, effect):
    return (effect.occurrence-1)*2*len(seats)+2*seats.index(effect.anchor_player)+(effect.boundary=='End')


def initial_counts(seats, active, phase):
    index=seats.index(active)
    return tuple(BoundaryCount(p,int(i<index or (i==index and phase!='Start')),int(i<index)) for i,p in enumerate(seats))
