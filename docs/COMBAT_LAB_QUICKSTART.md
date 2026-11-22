# Combat Lab v0.1 — Run Locally

This is the first runnable slice, not the complete desktop app. Requires Python
3.11 or newer. It has no third-party runtime dependencies, API keys or network
calls. No GPU is used. Windows execution/packaging still needs actual Windows
validation; this slice has been exercised on Linux Python 3.12.

From a checkout of this branch, open a terminal in the repository directory.
Each command below is **one line**.

Windows:

```powershell
py -3 run_lab.py matrix --output lab-runs/first-matrix
```

macOS/Linux:

```bash
python3 run_lab.py matrix --output lab-runs/first-matrix
```

Open `lab-runs/first-matrix/report.html` in a browser. It is a local standalone
report, not a running web app. No internet connection is needed. Choose a new
output name each time; existing results are not overwritten.

Verify every exported result by recomputing its pinned input:

```powershell
py -3 run_lab.py verify lab-runs/first-matrix
```

Resolve the worked 8-attack Breakthrough example:

```powershell
py -3 run_lab.py run examples/breakthrough.json --output lab-runs/breakthrough
```

Substitute `python3` for `py -3` on Linux/macOS. Reports export `manifest.json`,
`summary.json`, `results.csv`, `results.jsonl`, and `report.html`. JSONL stores
each scenario input, exact damage events and result hashes for replay. All
information is public combat state; no full-match private hands exist yet.

## What the matrix actually measures

The nine approved cost1–3 ATK/HP profiles are compared in all 81 directional
pairs, using full/1 remaining health where distinct, ready/exhausted blockers,
and 0/2 prevention. This yields 1,156 unique exact single-block encounters.
These are finite scenarios, not 1,156 independent statistical games, and do not
establish win rates or prove cards balanced. Cost is metadata; no resources,
draws, deployment timing, deck construction or turns are simulated.

Core supports simultaneous ordinary combat, ordered multiblocking, Challenge
groups, Breakthrough, numeric shields, persistent wounds in reused snapshots,
readiness validation and spent attacks. Unsupported keywords/JSON fields reject
instead of becoming blank effects. Response windows are assumed already closed.
The CLI example exercises Breakthrough; the ability-free matrix doesn't add
abilities to its candidates. Exact fixture tests cover special interactions.

## Explicit limitations and experimental defaults

- Not yet implemented: full matches, bots, reactions/triggers, leaders, resources,
  forms/combination, player shields, elimination cleanup, multiprocessing,
  resumable jobs, desktop GUI or a packaged Windows executable.
- Lethal-player IDs are diagnostic only; the combat kernel never declares a winner.
- All damage resolves from the same pre-damage snapshot. Each creature belongs
  to one group; several challengers can share one target.
- Blocker order is explicit. Challenge retaliation order can be supplied through
  `challenge_orders`; otherwise declaration order is a labeled experimental
  fallback, not a new mandatory card-game rule.
- Numeric shields use supplied expiry ranks; tied ranks use shield IDs.
  Actual phase expiration and source-sensitive prevention remain unsupported.
- Input represents current final combat assignments. A previously blocked
  attacker with no blockers uses `was_blocked: true`. A vanished Challenge target
  uses its old target ID. Both rules have exact regression tests.
- Replay requires the same engine file hash. It detects edited results and
  record-count mismatches; hashes are reproducibility checks, not signatures.
- First exporter is synchronous/in-memory. Large-scale job scheduling and atomic
  checkpoints come in the next runner stage; interrupted exports aren't completed
  runs and must be rerun into a new directory.

## Tests

Windows PowerShell, two separate single-line commands:

```powershell
$env:PYTHONPATH = "src"
```

```powershell
py -3 -m unittest discover -s tests -v
```

Linux/macOS, one line:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Test sources independently specify expected outcomes, brute-force exhausted
lethal thresholds, reject illegal assignments, check serialization/replay and
escaped HTML. See the full [tester plan](BALANCE_TESTER_PLAN.md) for later stages.

## Bounded checkpoint batches

On Windows, run up to 100 new matrix combats and export the completed subset:

```powershell
py -3 run_lab.py batch --checkpoint lab-runs/matrix.sqlite --limit 100 --output lab-runs/batch-1
```

Repeat with the same checkpoint and a new output directory to resume. Each combat
commits atomically. Completed jobs are replay-checked before resuming; changed
engine/profile/input hashes reject. Reports contain completed combats only;
the CLI shows progress against all 1,156 encounters. These remain combat-only.
The checkpoint is local SQLite data, unrelated to family game saves. Keep it
for resume; deleting it restarts the experiment. This first runner is sequential;
process workers, equal-budget groups and GUI controls remain future work.

## Equal-budget creature groups

```powershell
py -3 run_lab.py groups --budget 3 --output lab-runs/groups-budget3
```

Budgets 1–3 enumerate exact-cost profile multisets (22 groups at budget 3),
both attack directions, all creatures attacking, and every blocker assignment
including unassigned blockers and each blocker order. Boards start at full HP,
ready, without shields or keywords. Group profile repetition represents numeric
fixtures, not a claim of singleton deck legality. Names retain each profile,
card count/board width and zero unused budget. Deployment turns, resources and
card advantage are not simulated. Optional attacks, wounds and exhausted group
variants remain future coverage. Reports are exact encounters, not policy win
rates. This command is finite and in-memory; group checkpoints are supported through the batch command below.


## Resume equal-budget groups

```powershell
py -3 run_lab.py batch --experiment groups --budget 3 --checkpoint lab-runs/groups.sqlite --limit 100 --output lab-runs/groups-part-1
```

Repeat with the same budget/checkpoint and a fresh output directory (for example,
`groups-part-2`). Each invocation completes at most 100 new encounters. Budget 3
has 18,445 encounters; progress uses the actual generated count. Reports include
all completed encounters so far, and the manifest experiment label records
completed/requested counts. Use `verify` on any exported directory as usual.
Changing budget, scenario ordering, profiles or engine rejects resume before
adding results. Existing matrix checkpoints keep their original format and work
with the default `batch` experiment. No checkpoint migration is required.
The runner still generates inputs and validates saved results in memory; the
limit bounds new combat jobs, not startup memory or validation work. One process
should use a given checkpoint at a time. No parallel scheduling is implemented.


## Batch progress and failures

Batch reports now include requested, completed and pending combat counts,
error-attempt counts and jobs awaiting retry in manifest.json, summary.json and
the standalone HTML report. Attempts retain job ordinal, UTC time, status and
error message. Every completed result and its attempt are committed together.
The CLI prints progress every 100 attempts and each simulation error immediately.
`--limit` bounds new attempts, including failures. A later invocation retries
unfinished jobs; earlier errors remain recorded. Exit code 2 indicates unresolved
failed jobs (or a rejected run); partial completion without errors returns 0.

Existing checkpoint files gain only an additive attempts table. Earlier results
are preserved; historical attempts cannot be reconstructed. No manual migration
is needed. To roll back runner code, the older runner ignores that extra table.
Checkpoint replay errors stop resume; database/storage errors stop the run and
are reported by the CLI. Abrupt process termination may leave an unfinished job
without an attempt record; resume reruns it. Progress counts do not label pending
jobs as draws. These reports still describe combat encounters only.

## Pause, cancel and resume

Add `--control-file lab-runs/control.txt` to a batch command. From another
PowerShell window, request a stop:

```powershell
Set-Content -Encoding utf8 lab-runs/control.txt pause
```

Use `cancel` instead to cancel this invocation. The runner checks the file
before each new combat, finishes and commits any combat already running, and
exports the completed subset. Reports record `paused`, `cancelled`, `batch_limit`
or `completed` separately from encounter results. Cancel returns exit code 130;
pause and ordinary batch limits return 0 unless unresolved simulation errors
require code 2. Neither action marks pending jobs as draws or deletes results.

To resume, clear the file before rerunning with the same checkpoint and a new
report directory:

```powershell
Set-Content -Encoding utf8 lab-runs/control.txt ''
```

A preexisting pause/cancel request stops before any new job. Unknown file contents
reject the invocation. The file is not deleted or cleared automatically. Stops
are checked after input generation and saved-result validation; they do not
interrupt startup validation or report export. This is a cooperative runner
control, not an in-game timer. Keyboard interruption remains abrupt; completed
checkpoint jobs survive, but that invocation may not export a report.

Future desktop controls can use the runner's `control` callback and existing
progress events without changing combat rules or the checkpoint schema.

## Desktop window

From the checkout:

```powershell
py -3 run_desktop.py
```

Requires Python with Tkinter (included with the tested Windows Python install).
Choose matrix or groups, budget and batch size, then choose a new `.sqlite`
checkpoint or an existing matching checkpoint. Click Run / Resume. Results go
into a fresh `reports/<unique-id>` directory beside the checkpoint. Open latest
report opens the standalone HTML in your browser. The window shows runner logs.
Pause/Cancel stop between combat jobs; Run / Resume starts the next batch.
Closing a running window requests pause and waits for report export before exit.
Startup validation and export can take time before a stop request is honored.
Use one window/process per checkpoint. The packaged entry point is `crucible-lab`
after installation; a standalone Windows executable is not built yet.

## Comparison summaries and desktop review
summary.json and report.html now group identical public starting boards and
attacking creature sets. Each row shows encounter count and observed ranges for
player damage, attacking creature losses and defending creature losses. Board
labels show ATK/current HP, exhaustion, shields and keywords. An example job ID
in JSON links a row to full inputs/results in results.jsonl. Ranges are separate
extrema and may not occur together. Counts are enumerated choices, not independent
trials or policy probabilities. Partial reports cover only jobs already completed.

Desktop review on Windows confirmed readable default layout, pause/cancel,
resume, report-link invocation, close-while-running and recovery from a malformed
checkpoint. No packaged executable or full-match simulation is supplied.

## Replay inspector

Click **Inspect exported replays...** and choose a report directory. Loading
recomputes its records against the current engine before opening. Verification
runs in a background thread so the desktop remains responsive. Search by scenario
name or job ID, select an encounter, and inspect the public before/after boards,
declarations and simultaneous damage calculations. A mismatched engine or altered
record is rejected. This is a single-combat inspector, not a turn-by-turn match
replay. Data is loaded into memory. No hidden hands or full-match state exist.

## Portable Windows app

The local build is `dist/CrucibleLab/CrucibleLab.exe`. Double-click it; Python
is bundled. Keep the entire folder including `_internal` together. A distributable
folder ZIP is `dist/CrucibleLab-Windows.zip`. Store checkpoints/reports outside
the app directory so replacing the app cannot replace experiment data.

To rebuild on Windows (tested Python 3.14.3):

```powershell
py -3 -m venv .venv-build
.\.venv-build\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv-build\Scripts\python.exe scripts/build_windows.py
```

Build dependencies are isolated; runtime has no per-simulation services. The
bundle contains the app, candidate profile JSON, Python and Tk, not the reference
corpora. PyInstaller one-folder distribution documentation:
https://pyinstaller.org/en/stable/usage.html

Source and frozen engine hashes can differ: use a new checkpoint for the packaged
build and inspect its reports with that same build. Keep old source/build copies
for old replays. Never edit hashes to force compatibility. Checkpoint schema is
unchanged. The app is unsigned, with no installer or automatic updates. It was
tested on this Windows machine, not a clean machine without Python installed.


## Group condition presets and joint outcomes

Choose a Group condition in the desktop, or use the CLI:

```powershell
py -3 run_lab.py groups --budget 2 --condition exhausted --output lab-runs/exhausted-2
py -3 run_lab.py batch --experiment groups --budget 2 --condition shielded --checkpoint lab-runs/shielded.sqlite --limit 100 --output lab-runs/shielded-part-1
```

- `baseline`: existing full-health ready groups, no shields (default; unchanged).
- `wounded`: every creature starts at 1 current HP with original maximum HP.
- `exhausted`: full health; every defender exhausted, attackers ready.
- `shielded`: full health and ready; each defender has 2 numeric prevention.

These are deliberately separate sensitivity presets, not all combinations of
individual statuses. All creatures attack as before; optional attack subsets
remain outside this enumerator. Conditions require the groups experiment.
Resume with the same condition, budget and checkpoint; a changed condition
rejects against the pinned inputs. Existing baseline checkpoints remain readable.

Comparison JSON and expandable HTML now retain joint `(player damage, attacker
losses, defender losses)` outcomes with encounter counts and example job IDs.
Counts are enumerated assignments, not probabilities. Search an ID in the replay
inspector to inspect an actual outcome. A partial report only describes completed
jobs; there is no guarantee that its ranges or outcomes cover all choices.

## Optional attacks and mixed boards

Both group commands accept `--attack-mode subsets` to enumerate every attacker
subset, including none. Default `all` preserves the earlier inputs/checkpoints.
Use `--condition mixed` (budgets1–2 only) to vary each attacker independently
between full/1 HP and each defender between full/1 HP, exhausted, or shielded2.
Duplicate creature states are removed. No individual exhausted+wounded+shielded
cross-product is claimed. Mixed budget2 with attack subsets has 35,058 encounters;
use bounded batches/checkpoints instead of a single large export when convenient.

The desktop exposes these options. No-attack comparison rows are included with
zero outcomes; boards are oriented by the first listed seat rather than claiming
an active attacker. Existing scenario schemas and checkpoint tables are unchanged.
See [the first-run walkthrough](DESKTOP_WALKTHROUGH.md) for a 27-encounter example.
