# Duration anchors and automatic expiration
Implemented 2026-11-23. Coverage v5; practice content pack v3.

## Implementation
- durations.py defines immutable original-seat Start/End counts and typed duration
  records. A duration locks its anchor seat, boundary and occurrence; elimination
  does not retarget that deadline. No wall-clock timer is used.
- match.py expires Start records before maintenance and End records after triggers/
  hand cleanup. It drains skipped original-seat boundaries before opening the next
  living turn. Dead seats receive no turn, resources, draw, readiness or recovery.
- Expiration removes records before running registered typed consequences, so
  nested stabilization cannot expire them twice. Resulting triggers/choices drain
  before progression/terminal checks. Skipped expiry work remains in the departing
  turn's End context until the next living turn is opened.
- Numeric creature prevention has timed shield IDs. Expiry rank uses the original
  schedule so the shared combat kernel consumes earliest-expiring protection first.
  Partial consumption is preserved; a consumed shield/removed target drops its
  timer. Source departure alone preserves a captured grant. Elimination cancels
  the eliminated controller's ongoing grants.
- A same-End grant made after expiration is due immediately at atomic cleanup,
  rather than leaking into the next turn. Public projections expose current
  prevention, locked deadlines and typed expiry events; no private replay fields.
- Practice pack v3 replaces two reaction fixtures with Brace for Impact and
  Enduring Ward. Both use the existing card/target/payment path. The forty-card
  count and ordinary card keys are retained, while the content version/hash changes.

## Verification
Windows Python 3.14.3: `$env:PYTHONPATH='src'; python -m unittest discover -s tests -q`
passes 253 tests (17 new duration fixtures plus 236 prior tests).

Cases include Start-versus-End order, exactly-once expiry, source/target/controller
lifetime, consumed/partly consumed shields, stale commands, real played Ward cards,
late-End grants, multiple simultaneous timers and malformed clock/record rejection.
Eliminated-anchor cases test both before and after that seat's first real turn.
They assert original occurrence counts without a resource refill or draw.

Mandatory expiry can eliminate the planned next seat; rotation finds the next
survivor without granting a dead turn. Start/End effects on a crossed dead position
can eliminate all survivors and produce a draw before a premature win. Abandoned
active-turn End expiration is also covered. Trigger effects finish before rotation.

Fixed-seed actual practice-policy checks complete for 2/3/4 seats in
213/1,472/1,640 commands and 11/73/65 turns. These are bounded command-path checks,
not balance/strength estimates. The combat kernel itself is unchanged by this slice. A fixed-delay computer-ready
widget check was replaced with bounded state polling after one load-dependent
false failure; the scheduler behavior was unchanged.

## Compatibility and remaining gates
Duration records and boundary queues are internal state, not a persisted schema.
Existing catalog/checkpoint/report data is untouched. Source revert is the rollback;
retain existing experiment data. No executable rebuild or new dependency was added.
Coverage.py owns unsupported duration forms, including continuous stat modifiers
and nested timed grants in registered expiration payloads. No arbitrary callbacks
or prose evaluation were introduced. Canonical mechanics remain in RULES_DRAFT.md;
PROJECT_STATE.md owns the next step.
