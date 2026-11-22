# Start, cost transactions and combat declarations
Implemented and audited 2026-11-22. Coverage: src/crucible_core/coverage.py v1.
Canonical mechanics remain in RULES_DRAFT.md; this file records implementation.

## Changes
- resources.py: immutable capacity/available/own-Start counters and exact payment
  validation against controlled token IDs/values. No implicit token selection.
- match.py: opt-in managed turns execute Start maintenance, Start triggers, normal
  Draw/duel skip, phase windows and Recharge. Registered Start expiration
  consequences precede refill; subsequent own Starts grow natural capacity.
- Registered source abilities validate Main/reaction timing, priority, resource
  payment, exhaust eligibility and per-turn limits before committing. Registered
  effect parameters stay locked. Costs remain spent if the pending item is lost.
  This is the source-ability transaction slice; hand-card play remains separate.
- combat_flow.py: attack commitment, post-declaration responses, private complete
  defender locks, simultaneous reveal, controller-specific damage orders and final
  responses. Intervening concession cleanup invalidates lock/order batches.
- combat.py: extracted validation/shared damage kernel; legacy fresh-attack API
  remains an adapter. Committed callers never flip readiness flags for admission.
- match_combat_view projects only combat data; other players/public cannot observe
  another defender's unrevealed lock. General player/bot views remain next work.

## Focused audit and fixes (single-agent review)
1. Damage resolution initially exhausted committed attackers again. Fixed: a
   reaction that readies an attacker stays effective; attack usage remains spent.
2. Legacy snapshot commands could bypass the new flow. Fixed: managed matches
   reject that adapter; declarations/orders must complete through the new path.
3. Depletion during a reaction could jump to End before declared combat completed.
   Fixed: the existing "after pending work" rule includes already committed combat;
   no new voluntary active-player actions open after exhaustion/refill.
4. Lock/order choices must not survive intervening public cleanup. Tested fresh
   lock requirements after concessions, including during order collection.
5. Tested controller/target changes, lost Challenge permission after declaration,
   missing targets, explicit no-block choices, stale/duplicate locks, invalid
   payments, unavailable sources, once-per-turn limits and cancelled paid items.
6. Four complete managed turns verify rotation, per-seat growth and single Start
   maintenance. Recharge and exhausted-Start refill take their separate paths.
No independent reviewer approval is implied by this self-review.

## Validation
Windows Python 3.14.3, PYTHONPATH=src:
- python -m unittest discover -s tests -q: 148 passing, including 34 new tests.
- python scripts/check_combat_equivalence.py --baseline 2458747: 36,214 exact
  legacy outcomes match (1,156 matrix plus 35,058 mixed/subset budget-2 cases).
  The harness loads only a trusted local Git baseline; it writes no game data.
- Additional committed-versus-legacy tests compare 16 shield/exhaustion/attack/
  Breakthrough combinations; Challenge/order/readiness cases have exact fixtures.
- git diff --check; design handoff regenerated and manifest hashes checked.

## Compatibility and rollback
No save/checkpoint/report/catalog schema changed and no match save was introduced.
The combat source fingerprint changes, so use fresh checkpoints with this engine;
retain the old build/source for earlier reports. Never rewrite stored hashes.
See COMBAT_LAB_QUICKSTART.md for the existing build/replay compatibility procedure.
Rollback is a source revert; preserve existing checkpoints/reports and older builds.
The portable executable was not rebuilt by this backend-only change.

Implementation gates are listed once in coverage.py. Detailed rule choices remain
in RULES_DRAFT.md rather than repeated here. PROJECT_STATE.md owns the next step.
