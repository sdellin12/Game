# PR #1 review and Windows package evidence

Scope: combat-only engine, finite experiments, resumable runner, desktop reports
and replay inspection. Reviewed source paths crucible_core/combat.py,
crucible_sim/{cli,batch,groups,comparisons}.py and crucible_lab/{desktop,replay}.py.
This is a focused self-review, not an independent reviewer approval.

## Findings
No blocking finding identified within the declared subset. Combat tests specify
simultaneous retaliation, exhaustion-before-prevention, ordered multiblocking,
Challenge, Breakthrough and illegal assignments. Checkpoints reject changed pins,
commit results/attempts together, preserve prior errors and resume unfinished jobs.
Reports distinguish unfinished work and error attempts from completed encounters;
comparison ranges are descriptive, not win estimates or jointly optimal outcomes.
Desktop computation uses a child process; replay verification uses a background
thread, and Tk updates stay on the UI thread. Reference datasets are excluded
from the executable. No paid service or runtime API call is introduced.

## Evidence
- Source suite: 48 tests on Windows Python 3.14.3, including tamper rejection,
  inspector filtering/selection, async desktop load/error handling, pause/cancel,
  resume, report links, malformed checkpoints and close waiting for export.
- Full budget-3 source export/replay: 18,445 exact encounters (prior step).
- PyInstaller 6.22.0 build succeeds with pinned requirements-build.txt.
- Packaged worker: groups budget1, limit3; resume advances 3 -> 6 encounters;
  both exports verify using the packaged engine with PYTHONPATH removed.
- Source desktop driving packaged worker produces a two-encounter report.
- Packaged GUI and source replay inspector visually inspected on Windows.
- No required CI checks or external review approvals were observed during review.

## Limits and rollback
No full-match rules, bots, process-worker pool, hidden-information projections,
installer, signing or clean-machine portability claim. Inspector/export input is
in memory; cooperative stopping waits through validation/export. One writer per
checkpoint. SQLite schema additions preserve existing results; prior attempts
cannot be reconstructed. Frozen/source engine hashes can differ and intentionally
reject cross-build resume/replay. Retain prior builds/source to reproduce old data.
To roll back, retain experiment data separately and return to the previous source
revision/build. New inspector fields do not rewrite exported inputs or results.

Recommendation: ready for owner merge review within the above scope. Actual merge
is a separate explicit action; this review does not assert independent approval.
