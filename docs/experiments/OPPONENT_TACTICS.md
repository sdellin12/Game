# Unravel policy evaluation
2026-11-23. Deterministic, permitted-view scenarios; no hidden-state policy access.

## Reproduce
Set PYTHONPATH=src, then run `python -m crucible_play.tactics`.
It builds twenty-one real engine states, projects only player A's view, asks the policy
for a command, and checks both legality and the scenario's explicit decision intent.
The result is bounded JSON; exit code 2 means an expectation failed.

## Before/after
The 556aa51 policy met 17/21 expectations in the expanded suite; all 21 moves
were legal. The updated policy meets 21/21, still all legal. The four failures
involved a distracting large Challenge, two wards aimed at safe blockers, and a
cheap ward spent on an idle creature instead of preventing lethal player damage.
The fourteen earlier combat/tempo/nested-negation scenarios continue to pass.

Scenarios: prefer permanent token removal over bouncing an idle body; avoid duplicate
removal; stop an attacker threatening self; reserve resources during others' fight;
hold when a revealed ready blocker safely absorbs the attack; stop Breakthrough;
remove a blocker for own Breakthrough; hold against a zero-attack body with no own
attackers. Six additional scenarios cover removal with zero through four nested
negates and a negated return effect. The policy walks the public chain newest first,
ignoring cancelled items, before judging whether removal is already committed.
Tests drain those chains through the engine to check the final outcome.
Seven additional scenarios cover multiple attackers, player survival versus a
Challenge, safely blocked threats, aggregate lethal damage, effective cheaper
wards, unavailable expensive responses, ineffective cheap wards and exact owned
token payments. Tests play the choices through actual combat and verify survival
and remaining resources.
Tests also resolve chosen commands, reverse hidden deck order, and reverse
public object order to check execution, permitted information and deterministic ties.

For final responses, the policy reconstructs the public combat snapshot and reuses
combat_flow.resolve_committed, including exhausted blockers, shields, orders and
blocked memory. It compares survival, player damage and preserved own creatures,
then breaks equal-value choices by lower cost and stable IDs. Earlier windows
retain the simpler public threat scores.
It retains exact resource payments and never queries the engine's authoritative state.
Only combat response windows were added to the previous empty-chain play conditions.
Unravel favors token removal and leader tempo; Banish favors permanent ordinary-card
removal because a leader returns to reserve instead of staying exiled. A separate
real-state regression checks that distinction.

## Progress and limits
Final pack-v8 2/3/4-seat practice runs completed in 327/829/1867 commands and
17/36/74 turns. The existing three-seat under-1500-command regression still passes.
Scenario scores measure these twenty-one decisions, not general strength or game balance.
Evaluation does not search future responses or hidden cards. Final-response
comparison falls back to earlier heuristics when pending non-removal effects would
change the forecast. This is not a general search or a win-rate claim.

Focused tests: test_opponent_tactics.py, test_opponent.py, test_exile.py and test_recovery.py.
Next evaluation work: future responses and triggered changes during reaction payments.
