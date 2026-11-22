# Priority review and turn/draw foundation

2026-11-22. Follow-up implementation after completing both card-template v1
layouts, as requested. These are reusable core primitives, not a simulator-only
rules fork and not a complete match engine.

## Priority-core focused review

Read priority.py against approved priority/trigger sequencing. No blocking issue
found within the fixed-seat response-window scope. Holder/revision guards reject
stale or out-of-order commands; pass sequences reset on additions; all-seat passes
hand off one newest item; explicit acknowledgement follows resolution/cleanup;
trigger groups are ordered active-seat first with last-added-first resolution.
Counters persist across reopened windows. This is a focused Sol self-review, not
independent Astra approval. Existing ten priority tests retain exact evidence.

Integration requirements remain: caller validates actual card timing/costs/targets
and authority; resolving effects must stabilize before acknowledgement; elimination
can change the surviving-seat set, which the current fixed-seat helper does not
support. Initial-phase trigger collection and choice persistence are not supplied.
Do not expose coordinator-only finish/reopen methods directly as player commands.
No review finding is disguised as a complete full-match legality implementation.

## New shared primitives: crucible_core.turns

- Immutable DrawPlayer zones and TurnFlow; unique card-instance IDs across zones.
- Normal Start/Draw/MainBefore/Combat/MainAfter/End/Finished flow. Recharge uses
  Start/End/Finished, consuming its pending obligation at own-turn open.
- End requests mark intent and block active Main actions; they do not truncate
  the resolving item or automatically bypass pending effects/End maintenance.
- begin_required_draw draws available cards in order and pauses at an eligible
  refill, retaining hand/remaining count and the own-turn depletion end request.
- begin_start_refill offers refill before the normal draw on an empty own Start;
  successful payment creates no bonus draw and requests end of that turn only.
- accept_refill validates a recorded permutation of the eligible discard, pays
  explicit policy life, shuffles into the empty deck and finishes remaining draws.
  The exact permutation is retained as replay data; no global RNG is used.
- Unavailable/declined/insufficient refill returns a failed-draw result for later
  atomic elimination processing, never a draw/victory or an immediate terminal win.
- Off-turn refill requests next-turn Recharge without ending the active turn.
  Required choices use stable request IDs/revisions; turn commands use turn IDs
  and revisions. Those IDs are assigned uniquely by the future match coordinator.

RefillPolicy requires explicit positive life_cost and minimum_health_after_payment;
there is no approved/default20. Tests exercise15/20/25 with floor1 as candidates.
Card-instance IDs model ordinary eligible cards; catalog/token/ownership validation
is a caller obligation. No database or existing saved schema has changed.

## Coordinator boundary

Before advancing a phase, the match coordinator must complete automatic Start
work, costs, priority, resolving instructions, mandatory triggers/cleanup, End
hand-limit/expiry and elimination as appropriate. advance_at_boundary is INTERNAL,
not a player action; this primitive does not assert those systems already exist.
After a complete DrawState, use its player.end_turn_requested to request active
turn end only after current/pending work. Failure needs atomic elimination before
any new action/turn is offered. No integration into the combat desktop is claimed.

begin/open helpers do not choose the next living seat or award victory. Opening
a turn assumes the coordinator has finished the previous turn and cleanup. They
do not handle initial duel draw skipping, opening hands/redraw, hidden projections,
resources, leader recovery, arbitrary healing, effect evaluation, damage or bots.

## Fail-closed unresolved cases

Multiple off-turn refills before Recharge, mandatory draw/refill during a Recharge
turn, and penalty-bypass cards remain unsupported. Requests that need those rules
raise UnsupportedTurnRule; initial full-match content must be validated against
that coverage before play. No stacking rule or silent skipped effect is invented.
If a refill itself leaves more required draws than all available cards, payment
stays spent and an unrecovered failure is returned once discard is empty.

## Tests / compatibility / rollback

Fourteen focused tests cover approved draw3/deck2 behavior; exact-last-card
own/off-turn differences; Start refill; decline/unavailable failures; insufficient
refill preserving payment; Recharge; phase sequencing/deferred end; stale turn/
request IDs; bad permutations; explicit candidate costs; unsupported interactions;
invalid zones/contexts; Start failures; and card conservation/recorded replay.
The original player/flow/pending-choice snapshots remain immutable on rejection.

Template tests and existing combat/runner/desktop tests remain regression coverage.
No old checkpoint/report/card-pack data is rewritten. Future persisted match state
will need versioned schema/defaults, migration fixtures and rollback plans before
these data classes are serialized as production saves. Rollback removes isolated
new modules/tests without deleting experiment data. Full-match mode stays disabled.


Final validation: `$env:PYTHONPATH = "src"` then
`py -3 -m unittest discover -s tests -q`: 89 tests pass on Windows Python 3.14.3.
This includes 14 turn/draw tests, five template tests and the prior 70 regression
tests. Template source generation and local PNG review export succeed; all 50
handoff ZIP file hashes match. `git diff --check` passes. No existing combat
matrix was rerun because its engine/scenarios were not changed by this slice.
