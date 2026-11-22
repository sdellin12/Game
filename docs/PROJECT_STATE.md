# The Crucible — Resume Here
Updated 2026-11-22. First combat-only core/CLI implemented. No full-match simulations, desktop GUI, target-PC benchmarks or family playtests yet.

## Read
1. REQUIREMENTS.md — current confirmed product/UX/content.
2. RULES_DRAFT.md — current mechanics and remaining engineering specifications.
3. BALANCE_TESTER_PLAN.md — completed four-specialist tester design/implementation plan.
4. BUILD_PLAN.md — proposed tester and full-game stages.
5. Game_Lore.md — current fiction; architecture/UX as needed.
ANSWERS.md and DISCOVERY.md are historical and superseded; do not reread full interview by default.

## Latest accepted baseline
- No player revival. Permanent elimination at health<=0/failed required draw/concede; no final revival window.
- No universal defense stat. ATK/HP only; persistent damage; block doesn't exhaust; one blocker per attacker, multiple blockers allowed.
- Breakthrough overflow after lethal allocations; Pierce deferred. Challenge allows direct creature fight, no blockers/player overflow; group retaliation once; challenged creature cannot also block.
- Exhausted-blocker damage ceil1.5 before prevention; ordinary blocked status persists even if blockers leave.
- Start2 resources, natural base grows1/own turn to10, separate permanent bonuses beyond10; refill, stored spend-directly tokens. Green growth/Silver reserves.
- 40 singleton+leader, one color+generic,5 opening/partial redraw,1 draw/own turn,7 end hand,30 playerHP. First-player draw skip duel only.
- Main before/after combat, fixed turns; chain responses newest first untimed. Exact priority/cross-controller triggers/terminal sequencing require engine spec.
- Leader reserve reset/recovery until next own start, cumulative+2 per battlefield removal; negated summon no increase, retries allowed; accumulated increase undiscountable. No leader copy/control/combine.
- Transform/combine proportional HP roundUP actual whole numbers, no hidden fractions; no entry/departure from assembly; compatibility and disassembly rules in rules doc.
- Ten color identities, all offer easy-to-pilot decks incl Silver/Gold. Mostly0–1 creature abilities; initial24 creatures/10 actions-reactions/6 persistent.
- Ability-free candidate ATK/HP: cost1=2/1,1/2,0/3; cost2=3/2,2/3,1/4; cost3=4/3,3/4,2/5. Finite combat scenarios enumerated; full balance not established.
- Theme-first builder, leader choices, guided roles, private draft practice, shared permanent card catalog, independent optional shared deck copies.
- Permanent earned-only cosmetics/achievements, no real money EVER. All art retained, per-instance public treatments, no in-match changes.
- Desktop local test lab requested: no per-test AI, CSV/JSON/HTML, reproducible seeds/replays/multiple policy skill levels; mobile report companion later proposal.

## Current user request
User authorized moving ahead with tester implementation. First slice: pure immutable combat state/commands, nine candidate profiles, simultaneous blocking, Challenge/Breakthrough/shields, strict scenario validation and local JSON/CSV/HTML exporter/replay checker. 27 tests passed; 1,156 exact matrix encounters and worked Breakthrough example exported/replayed; two deliberately broken-rule mutants caught. Linux Python3.12 validation, not actual Windows validation. See COMBAT_LAB_QUICKSTART.md and experiments/FIRST_COMBAT_SLICE.md.
Next stage: equal-budget group enumeration, bounded job runner/checkpoints and desktop shell; full-match mode remains gated on complete turn/response/resource/elimination implementation. Existing plan records later stages. UI/LLM/policy/random-seed infrastructure not falsely claimed by deterministic combat slice.
Four-specialist plan remains in BALANCE_TESTER_PLAN.md; read its status update before historical planning statements.
User authorizes sensible tests/candidate numbers without approval for each fixture; ask consequential tradeoffs with selectable options+optional text.
TCG references can inform costs/wording/archetypes, but keep other games' rules separate and prefer curated official links/card/deck examples over indiscriminate full-database copies. Not required for first slice. No external card corpus imported.

## Known gates
Windows PC Ryzen5/GTX1650 (RAM/VRAM unknown), Linux home server previously discussed but deployment not verified. Tester CPU work independent of art/GPU/mobile install.
Actual iPads under Screen Time require restriction-safe delivery test; web accepted, weekly native fallback. Both Roku/GoogleTV required completed game. No paid art API; unattended ChatGPT Plus worker path unverified.
No estimates/claims of balanced cards before evidence. Bots see legal information only; full-game coverage cannot be inferred from combat-only simulation.

## Codex continuation � Windows checkpoint runner
Existing 27 tests passed on Windows. Added sequential bounded matrix batches,
atomic SQLite completion checkpoints, replay validation on resume and partial
reports through the `batch` CLI. See quickstart. Equal-budget creature groups,
parallel workers and desktop shell remain pending.

## Equal-budget group continuation
Added budget 1–3 exact-cost profile groups, all-attack directional encounters,
all legal ordinary blocker assignments/orders, including unblocked attacks.
32 tests pass on Windows; budget-1 CLI exported/replayed 18 encounters.
Group scenarios are full-health/ready/no-shield numeric fixtures; deployment,
optional attack subsets and group checkpoints remain pending. Repeated numeric
profiles do not establish singleton deck legality or equal card economy.


## Group checkpoint continuation
Equal-budget groups now use the same bounded SQLite runner via
`batch --experiment groups --budget 3`. Existing matrix checkpoint pins/schema
are preserved; changed inputs reject without discarding progress. Windows:
34 tests pass, including resumed groups versus uninterrupted results, changed
input rejection, and CLI partial export/replay. Runner remains sequential with
in-memory input enumeration and resume validation. Parallel workers, failure
attempt history and desktop controls remain pending.


## Batch progress and failure reporting
Added an atomic per-attempt SQLite history and structured progress in batch
JSON/HTML reports. Failed simulation jobs remain retryable and errors survive
successful retries. CLI reports errors, periodic progress and unresolved-failure
exit status. Legacy checkpoint results/pins are preserved with an additive table;
old attempt history is unavailable. Abrupt interruptions remain pending jobs.
Windows validation: 36 tests pass, including injected failure/retry/history and
legacy checkpoint compatibility. No worker pool or desktop shell yet.

## Cooperative pause/cancel controls
Runner accepts pause/cancel requests between combat jobs, preserving committed
results for resume. CLI exposes --control-file; exports distinguish pause,
cancel, batch-limit and completion. Cancel exits 130; pending jobs remain pending.
No checkpoint schema changes. Existing input generation/resume validation and
export are not interruptible by the cooperative control. Windows: 38 tests pass,
including stop after two jobs/resume equivalence and zero-attempt cancellation
with accurate partial report counts. Desktop interface remains pending.

## First desktop shell
Added Tkinter experiment/checkpoint selection, run/resume, pause/cancel, child
process logs and latest-report opening. Computation runs in a separate Python
process. Closing requests pause and waits for export. Launch: py -3 run_desktop.py.
Windows: 40 tests pass; Tk construction and window-to-child two-combat run,
completion log and report availability smoke checks pass. No visual layout review,
packaged executable, full-match mode or advanced replay inspector yet.

## Desktop review and comparison summaries
Visually reviewed the default Windows layout. Added readable completion/pending/
error status and a minimum window size. Automated real-child-process checks cover
pause, cancel, resume, close waiting for export, report link invocation and bad
checkpoint recovery. Reports now show per-board observed damage/loss ranges and
encounter denominators, including partial-run caveats. No policy win estimates.
45 Windows tests pass; full budget-3 export/replay: 18,445 exact encounters.

## Replay inspector, portable package and PR review
Added asynchronous verified export loading, searchable encounter selection,
public before/after boards and simultaneous damage details. Added reproducible
Windows one-folder build + ZIP and frozen-worker dispatch with bundled content.
Source/packaged engine hashes may differ; use new checkpoints per build, preserve
older builds for replay. No checkpoint schema migration. Windows tests and build
smokes are recorded in docs/experiments/PR1_REVIEW.md. PR remains open for merge
review; full-match mode, clean-machine package testing and signing remain pending.
