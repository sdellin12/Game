# Unravel policy evaluation
2026-11-23. Deterministic, permitted-view scenarios; no hidden-state policy access.

## Reproduce
Set PYTHONPATH=src, then run `python -m crucible_play.tactics`.
It builds eight real engine states, projects only player A's view, asks the policy
for a command, and checks both legality and the scenario's explicit decision intent.
The result is bounded JSON; exit code 2 means an expectation failed.

## Before/after
The fbfdbd6 policy met 2/8 decision expectations; all 8 moves were legal. The new
policy meets 8/8, still all legal. Original weaknesses: sorting creature targets by
attack alone; duplicate pending removal; spending bounce on harmless bodies; and
skipping reactions in empty-chain combat response windows.

Scenarios: prefer permanent token removal over bouncing an idle body; avoid duplicate
removal; stop an attacker threatening self; reserve resources during others' fight;
hold when a revealed ready blocker safely absorbs the attack; stop Breakthrough;
remove a blocker for own Breakthrough; hold against a zero-attack body with no own
attackers. Tests also resolve chosen commands, reverse hidden deck order, and reverse
public object order to check execution, permitted information and deterministic ties.

The policy uses public combat declarations/revealed blockers and simple threat scores.
It retains exact resource payments and never queries the engine's authoritative state.
Only combat response windows were added to the previous empty-chain play conditions.
Unravel favors token removal and leader tempo; Banish favors permanent ordinary-card
removal because a leader returns to reserve instead of staying exiled. A separate
real-state regression checks that distinction.

## Progress and limits
Final pack-v5 2/3/4-seat practice runs completed in 327/1302/1747 commands and
17/61/69 turns. The existing three-seat under-1500-command regression still passes.
Scenario scores measure these eight decisions, not general strength or game balance.
The ready-block heuristic does not search future responses or hidden cards.

Focused tests: test_opponent_tactics.py, test_opponent.py and test_exile.py.
Next evaluation work: adversarial response chains and multi-attacker resource tradeoffs.
