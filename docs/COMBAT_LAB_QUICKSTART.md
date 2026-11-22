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
