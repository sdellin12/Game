# Priority foundation — implementation and verification

2026-11-22. Implements only the approved response-window mechanics, not a playable
match engine or replacement combat algorithm.

## API

- `new_priority(seats, active_player)` opens an immutable window for fixed active seats.
- `add_effect(..., expected_revision=...)` records an opaque effect key/controller
  after the caller validates card timing, costs and targets. It clears passes and
  advances priority to the next seat.
- `pass_priority` advances fixed-order passes; all seats passing hands off exactly
  the newest item for resolution, or closes an empty window.
- `finish_resolution` is a coordinator-only transition after effect evaluation,
  mandatory cleanup and trigger-choice collection. It appends chosen trigger
  groups in active-seat-first order and resets priority to the active player.
- `reopen_priority` opens a subsequent window after an empty closure. Revision and
  effect counters persist, so stale earlier-window commands reject.

The resolving state blocks ordinary add/pass commands. Trigger order within each
controller's group is supplied after choice confirmation, oldest to newest. The
last seat group's newest trigger resolves first. No wall clock, I/O, randomness,
private card data or executable prose is used.

## Tests and limits

Ten unit tests independently assert three-seat newest-first resolution, pass reset,
revision/holder validation, immutable rejection, resolution gating and ID checks,
empty-window closure/reopen, trigger seat rotation and chosen internal order,
atomic invalid-trigger rejection, single-seat passing, invalid states and ID
continuity. Full validation on Windows Python 3.14.3: 70 tests pass, including these ten.
PowerShell commands:

```powershell
$env:PYTHONPATH = "src"
py -3 -m unittest discover -s tests -q
```

`git diff --check` passes. Existing
combat/runner/desktop tests remain regression coverage.

No costs, effect registry/evaluator, health, eliminated-seat changes, terminal
victory, initial-phase trigger collection, draw/refill/Recharge, private projections,
match persistence or UI hookup. Do not expose coordinator transitions as player
commands. An elimination during resolution needs the later atomic match coordinator;
this fixed-seat module must not silently invent cleanup rules.

No database/report/checkpoint schema migration. Existing combat engine hashes and
baseline scenarios are unchanged. Full-match coverage remains disabled. Future
match saves require explicit schema/version compatibility tests. Rollback removes
this isolated module/tests and retains existing experiment data unchanged.
