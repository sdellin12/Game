# Historical project checkpoints

Archived 2026-11-22 from PROJECT_STATE.md. Historical statements may be
superseded. Do not read by default; use Git history for exact code changes.

# The Crucible — Resume Here
Updated 2026-11-22. Combat lab/desktop/portable build implemented; isolated priority
core foundation added. No complete full-match engine, match simulations or family
playtests yet. Current rules include paid draw-time refill and Recharge; cost20 is
provisional. See DECK_REFILL_DESIGN.md and FULL_MATCH_TIMING_SPEC.md.

## Current next step
The atomic coordinator foundation is now implemented and tested; see the latest
continuation below and experiments/ATOMIC_COORDINATOR.md. Recommended next slice:
automatic Start/resource maintenance and legal action-cost transactions.

Standard/full-art v1 layouts are complete in design/cards with shared fixtures,
SVG outputs, offline gallery and local PNG references. docs/CARD_DESIGN.md is the
current design/handoff source; the ZIP bundle is dist/CardTemplate-Handoff-v1.zip.
Illustrations remain clearly marked placeholders; no final game art is claimed.

Steve authorized moving directly into priority-core edge-case review and pure
turn/required-draw/refill state after both templates. Use explicit test-cost
parameters; do not adopt a final refill price, repeated Recharge debt or bypass
interactions without specification. No saved-match schema migration is authorized
by the design files. See the later continuation record for implementation status.

## Read
1. REQUIREMENTS.md — current confirmed product/UX/content.
2. RULES_DRAFT.md — current mechanics and remaining engineering specifications.
3. BALANCE_TESTER_PLAN.md — completed four-specialist tester design/implementation plan.
4. BUILD_PLAN.md — proposed tester and full-game stages.
5. Game_Lore.md — current fiction; architecture/UX as needed.
ANSWERS.md and DISCOVERY.md are historical and superseded; do not reread full interview by default.

## Latest accepted baseline
- No player revival. Permanent elimination at health<=0/unrecovered failed required draw/concede; no final revival window.
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

## Implementation history (older status statements are superseded above)

## Codex continuation — Windows checkpoint runner
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
smokes are recorded in docs/experiments/PR1_REVIEW.md. PR #1 was merged 2026-11-22; full-match mode, clean-machine package testing and signing remain pending.


## Current continuation: expanded coverage and full-match timing draft
PR #1 merged at 029b0fe; follow-up branch feature/combat-coverage-and-timing.
Group conditions now include baseline, all-wounded, exhausted defenders and
shielded defenders. Existing baseline scenarios/checkpoints are preserved.
Reports include counted joint outcomes and example replay IDs, not win estimates.
Windows: 53 tests; 558 exported/replayed budget-2 encounters per condition,
2,232 total. See experiments/GROUP_CONDITIONS.md for evidence.

FULL_MATCH_TIMING_SPEC.md is draft 1, with confirmed constraints separated from
proposals and 18 acceptance scenarios. Proposed priority/trigger ordering,
atomicity and concession windows require review/approval before implementation.
Recommend Astra for that review. No full-match rule code is enabled. The existing
combat API needs declaration/damage separation before match response integration.

## Timing review approvals and broader combat choices
Reviewed timing draft2 against canonical rules. Steve approved fixed priority/
trigger order, whole-effect player-health checks and safe-boundary concessions.
Remaining sequencing proposals are explicitly marked in FULL_MATCH_TIMING_SPEC.md;
no executable full-match engine is enabled and no independent Astra review claimed.

Added optional attacker subsets including no attacks, and independent mixed
creature-state fixtures bounded to budgets1–2. Old default inputs retain the prior
budget2 digest; incompatible new options reject checkpoint resume. Reports include
no-attack outcomes, with orientation labels. DESKTOP_WALKTHROUGH.md walks through
a complete 27-encounter run, joint outcomes and verified replay selection.

Validation for this continuation: 60 Windows tests; full mixed/subset budget2
export/replay 35,058 encounters; rebuilt package mixed/subset budget1 export/replay
165 encounters. Baseline compatibility and held-attacker readiness are tested.


Timing follow-up: Steve approved Start/End and eliminated-seat duration boundaries.
Failed required draw and multiplayer blocker disclosure await examples and a
subsequent decision; neither is adopted. Documentation-only update.


Owner follow-up: simultaneous private blocker lock/reveal approved. New accepted
intent: costly fixed-life discard-to-deck refill, with repeat use relying on a
life-gain plan. Standard action vs card ability vs emergency timing still needs
selection; 20 life is a test candidate, not an approved/balanced price. Failed-draw
handling remains unresolved; no rescue/revival inferred. See DECK_REFILL_DESIGN.md.


Latest owner decisions: required draws finish after successful paid refill;
unrecoverable/declined required-draw refill eliminates. Own-turn depletion/refill
ends that turn; next empty Start can refill then end. Off-turn refill makes next
own turn Recharge (automatic Start/End, no normal draw/voluntary plays/Combat).
Own-turn refill does not additionally consume the following turn. Off-turn defense
and reactions remain. Canonical timing/lore consolidated in DECK_REFILL_DESIGN.md;
old Main-only proposal superseded. Price20 remains provisional; repeated Recharge
stacking/bypass interactions are not invented. Documentation-only; no engine code.


Latest continuation: consolidated approved refill/Recharge timing and Core-recharge
lore, superseding Main-phase-only refill. Added isolated crucible_core.priority
with immutable response windows, revision/holder checks, one-item resolution
handoff, active-first trigger batches and monotonic IDs. Ten focused tests pass;
full-suite evidence is recorded in experiments/PRIORITY_FOUNDATION.md. No game save
format changes or new full-match claims. Price and repeat/bypass rules remain open.


Current card-template detour: proposed CARD_INFORMATION_CONTRACT.md authored from
focused canonical requirements. Common name/color/type/access/art/rules regions;
conditional creature/leader/trait/form content; live state overlays and optional
catalog/flavor data are separate. No new mechanics, card schemas, renderer or tests
added. Pending priority review and turn/draw implementation remain queued.


Latest card-template decisions: Steve approved the shared information contract and
requested filled examples. Added CARD_CONTENT_EXAMPLES.md, covering base/ability
creatures, zero ATK, Action, Reaction, Upgrade, other persistent, Leader with two
ability locations, two linked transform faces, Combined Form/components, creature
and resource tokens, plus live wounds/status overlays. Same content feeds both
styles; example abilities/costs/trait vocabulary are not approved game content.
Documentation only, no tests or schema changes. Priority review/turn-draw work
remain queued behind the template task as requested.


Latest completed work: standard/full-art template v1,15 content fixtures/30 SVGs,
offline preview, five local PNG reference pairs and verified50-file LLM handoff ZIP.
CARD_DESIGN.md is the design source of truth. SVG information-parity/capacity tests
pass; character art remains placeholder. Firefox computer-use URL enforcement was
unsupported, so visual QA used local resvg rendering without automating Firefox.

Then completed focused priority-core self-review and added crucible_core.turns:
immutable phase flow, partial required draws, explicit refill choice/payment and
recorded shuffle, own-turn end intent, off-turn Recharge and stale-command guards.
No final refill cost adopted. Repeated Recharge/bypass interactions fail closed.
No full-match coordinator, automatic Start/End effects, resources, elimination or
saved-match schema is claimed. See experiments/TURN_DRAW_FOUNDATION.md.
Next implementation recommendation: integrate these primitives through an atomic
match coordinator with cleanup/elimination fixtures before enabling full-match mode.

Final validation for template/turn foundation: 89 Windows tests pass; paired SVGs
regenerate deterministically; 50-file design ZIP SHA256 manifest verified. No core
combat changes or saved-format migrations. Full-match mode remains disabled.


## Latest continuation � atomic coordinator foundation
Added crucible_core.match: immutable typed effects, suspended refill choices,
whole-effect health checks, simultaneous cleanup/permanent elimination, original
seat rotation, controlled pending-item cancellation, lifecycle trigger ordering,
serial safe-boundary concessions and deferred terminal checks. End intent retains
the final response window; triggers, seven-card hand checks and supplied expiration
consequences settle before advancement. Existing combat kernel has a restricted
closed-window snapshot adapter. 25 new tests; full Windows suite: 114 passing.
See experiments/ATOMIC_COORDINATOR.md for the exact scope and trust boundary.

Full-match mode remains disabled. Resources/automatic Start, production action
legality, attack/block declaration, hidden projections, leaders/combined forms and
general duration anchors remain separate gates. No persisted state/catalog/report
format changed. Standard/full-art layouts are unchanged; CARD_DESIGN.md and the
portable design ZIP have updated engine-status notes for another LLM.
Recommended next: Start/resource maintenance and legal cost transactions, then
attack/block flow and private projections.
