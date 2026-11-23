# Unravel policy evaluation
2026-11-23. Deterministic, permitted-view scenarios; no hidden-state policy access.

## Reproduce
Set PYTHONPATH=src, then run `python -m crucible_play.tactics`.
It builds fourteen real engine states, projects only player A's view, asks the policy
for a command, and checks both legality and the scenario's explicit decision intent.
The result is bounded JSON; exit code 2 means an expectation failed.

## Before/after
The 1864642 policy met 11/14 expectations on the expanded suite; all 14 moves
were legal. The updated policy meets 14/14, still all legal. The three new failures
were passes caused by treating negated removal as certain to resolve. The original
eight combat/tempo scenarios continue to pass.

Scenarios: prefer permanent token removal over bouncing an idle body; avoid duplicate
removal; stop an attacker threatening self; reserve resources during others' fight;
hold when a revealed ready blocker safely absorbs the attack; stop Breakthrough;
remove a blocker for own Breakthrough; hold against a zero-attack body with no own
attackers. Six additional scenarios cover removal with zero through four nested
negates and a negated return effect. The policy walks the public chain newest first,
ignoring cancelled items, before judging whether removal is already committed.
Tests drain those chains through the engine to check the final outcome.
Tests also resolve chosen commands, reverse hidden deck order, and reverse
public object order to check execution, permitted information and deterministic ties.

The policy uses public combat declarations/revealed blockers and simple threat scores.
It retains exact resource payments and never queries the engine's authoritative state.
Only combat response windows were added to the previous empty-chain play conditions.
Unravel favors token removal and leader tempo; Banish favors permanent ordinary-card
removal because a leader returns to reserve instead of staying exiled. A separate
real-state regression checks that distinction.

## Progress and limits
Final pack-v6 2/3/4-seat practice runs completed in 327/1488/1569 commands and
17/73/61 turns. The existing three-seat under-1500-command regression still passes.
Scenario scores measure these fourteen decisions, not general strength or game balance.
The ready-block heuristic does not search future responses or hidden cards.

Focused tests: test_opponent_tactics.py, test_opponent.py, test_exile.py and test_recovery.py.
Next evaluation work: future responses, simultaneous threats and multi-attacker resource tradeoffs.
