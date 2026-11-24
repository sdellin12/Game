# The Crucible Balance Lab — Expert Design and Implementation Plan

Status: historical design synthesis, reviewed 2026-11-22. Its package layout,
proposed budgets and original first-slice sequence are planning provenance, not
current instructions. The combat lab, desktop/package and restricted local match
harness are now implemented. Use PROJECT_STATE.md for current work, AI_HANDOFF.md
for source boundaries and COMBAT_LAB_QUICKSTART.md for the lab. Original test counts
below belong to their checkpoints; no fresh balance claim is implied.

## Decision and purpose
Build a Windows-first desktop balance lab around the SAME deterministic Python rules core used later by the authoritative household server, practice opponents and previews/hints. Core -> command-line scenario/batch runner -> desktop shell. No per-simulation LLM/API use, no paid services or GPU requirement. PC Ryzen5/GTX1650; exact CPU/RAM and throughput unmeasured. Mobile report viewing is later optional scope, not a phone compute requirement.
Compute correctness/statistics locally; AI reads concise summaries, proposed changes and selected replay evidence. Human family play remains necessary for enjoyment, comprehension and real 40–60 minute duration.

## Specialist review and synthesis
Four independently scoped reviewers read current canonical repo docs:
1. Deterministic engine architect: reusable pure core, legal decisions/projections, versioned replay and fail-closed coverage.
2. Experimental design/statistics: finite enumeration first, seat/policy blocks, honest uncertainty/denominators and fresh-seed confirmation.
3. Bot design/adversarial QA: hidden-information-safe policies, competent simple play, exploit fixtures and invariant gates.
4. Desktop/product engineering: thin tkinter/ttk shell, process workers, single result writer, resumable exports and Windows packaging.
Integration cross-check: GUI remains replaceable; no simulator-only combat implementation. Multiple workers affect throughput only, not seed selection/results. Command replay separate from rerunning bots. No claim these agents are certified human judges or that external game numbers establish balance.

## Suggested package layout
| Package/path | Responsibility |
|---|---|
| src/crucible_core/ | State, legality, commands, resolution, costs, combat, triggers, observations, explicit randomness |
| src/crucible_content/ | Versioned rules/cards/decks/token schemas, validation, supported effect registry |
| src/crucible_sim/ | Experiments, scheduling, policies, metrics, checkpoints |
| src/crucible_reports/ | Aggregation, statistical summaries, CSV/JSON/HTML, replay tools |
| src/crucible_lab/ | Desktop UI and app entry point |
| content/rulesets/ and content/test_packs/ | Reviewed parameters and mechanical fixtures; no generated art required |
| tests/scenarios/ | Exact expected-state fixtures and interaction cases |
| tests/properties/ | Invariants, generated legal transitions, metamorphic/privacy checks |
| tests/replay/ | Recorded decisions/randomness and state hashes |
| docs/experiments/ | Small reviewed conclusions; not every generated run |
Future server imports core; no network/database/UI/clock/global RNG inside core. Large run outputs outside git in chosen local output directory. No Library duplication of repo-backed source. Production family database/currency never touched by simulator.
Begin ordinary Python modules, JSON, integer math, process workers and SQLite coordinator. Pin interpreter/dependencies at implementation; property-testing library optional after assessing usefulness. Avoid plugin framework or distributed cluster before measured need.

## Core API and data boundaries
Proposed contract:
- validate_pack(pack, supported_mechanics) -> structured errors/warnings.
- create_match(config, deck_definitions, seed_bundle) -> state.
- observe(state, seat) -> authorized observation, separate public observer view.
- legal_decisions(state, seat) -> parameterized decision specifications.
- submit(state, command) -> accepted transition/events or rejected with gameplay state unchanged.
- preview(observation, proposed_action) -> conditional public/own-information explanation.
Parameterized decisions constrain valid targets, X, payment, ordering and combinations instead of fully enumerating exponential action spaces. Preview validation must not consult hidden identities to reveal conclusions. Server later revalidates submitted commands.

Immutable definitions vs runtime instances:
- Stable mechanical/card/character IDs and rules/content hashes.
- Current phase/seat/turn/priority/consecutive passes and pending chain.
- Ordered zones with owner/controller, separate private identity visibility.
- ATK/currentHP/maxHP, exhaustion, last-control/entry/attack eligibility.
- Shields with source, remaining amount, expiry and deterministic tie-break.
- Leader reserve, recovery anchor, cumulative undiscountable increase.
- Natural capacity, permanent/source bonuses, available resources, stored tokens.
- Ability-use identities/reset anchors; transformation/component/upgrade links.
- Event IDs and randomness state.
Whole-number HP per approved rules. Use exact integer ceil_div(n,d)=(n+d-1)//d for positive denominators, validate domain; never float-round or retain hidden fractional HP. Rounding-healing risks are real findings to test, not silently fixed by changing accepted rules.

## Resolution model
Explicit transitions, not arbitrary callbacks:
1. Validate actor/timing/all choices/exact cost.
2. Commit choices and payment atomically.
3. Queue effect or apply permitted atomic operation.
4. Resolve one atomic effect/combat event.
5. Process simultaneous lethal/removal, snapshot last-known data for applicable triggers.
6. Collect allowed triggers/choices/order and reopen response opportunities.
7. Check terminal outcomes at the specified checkpoint, never midway through simultaneous work.
8. Yield a decision request or terminal record.
Precise priority/cross-player trigger/terminal ordering must be specified before affected fixtures. Preserve per-source damage attribution even with pooled totals. No approximate inference from card prose.

## Mechanics coverage and assumptions
Each experiment manifest lists implemented/excluded mechanics and experimental assumption IDs. Unsupported cards reject preflight, never become blank cards. UI/report prominent label: combat-only, partial-match, or full declared supported rules coverage.
Accepted design has no universal defense, no player revival, no mana/land cards. Start30HP,40singleton+leader,5opening,draw1,7hand; resources2 then natural+1 to10 plus permanent bonuses. Current rules include Challenge/Breakthrough and round-up forms.
Unsettled engineering items before affected implementation:
- Fixed priority starting/reset/pass sequence, optional autopass privacy behavior.
- Simultaneous cross-controller trigger order; last-known-source and damage-source allocation.
- Multi-draw loss/atomic defeat/terminal checkpoint with surviving pending effects.
- Challenge multiple attackers/other combat groups, order locks and modifier/shield tie semantics.
- Combined upgraded maxHP calculation before/after transfer/disassembly; cross-owner stolen components.
- Inherited/form-specific ability-use identity mapping.
- Expiry tied to eliminated player's next scheduled seat; removal of all eliminated effects.
- Safe finite representation of variable X/search space and unbounded effect expansion.
Resolve routine details as documented implementation proposals; test named alternative rulesets when consequential. Never silently promote them to accepted game rules. Ask user only material play-experience changes.

## Experimental ladder
### 1. Exact fixtures
Manually derived scenarios with expected state/events, not only implementation-vs-itself checks. Existing tests must fail on representative seeded mutations (e.g., multiplier after prevention instead of before). No balance statistics trusted until relevant correctness gates pass.
### 2. Finite combat enumeration
Approved no-ability candidates:
| Cost | Aggressive | Balanced | Defensive |
|---|---|---|---|
| 1 | 2/1 | 1/2 | 0/3 |
| 2 | 3/2 | 2/3 | 1/4 |
| 3 | 4/3 | 3/4 | 2/5 |
All ATK/HP, provisional not equal-power guarantees.
Enumerate both attack directions, legal blocker order, ready/exhausted, full/wounded health and representative shields for finite small groups. Compare equal-resource one-big/many-small groups while separately recording card count, deployment turns, board width and unused resources. Two cards are not economically identical to one even if resource totals equal.
No fictitious full singleton deck filled with illegal mechanical duplicates to force this test; scenario packs are explicitly non-deck combat fixtures.
### 3. Policy qualification/full-match subset
Only after setup/turn/resource/chain/end/elimination rules supported. Use supported draft mechanical packs and validate singleton; content production not assumed complete.
### 4. Matchup screening
Deck x opposing deck x acting policy x opposing policy x seat. Start selected contrasts, not every possible ten-color combination. Compare duels AND selected four-player lineups. FFA targeting/assistance distinct from duel.
### 5. Frozen confirmation
Freeze candidate rules/cards/policies then rerun flagged findings on untouched seeds. Controlled substitutions for causal hypotheses; played-card win correlation descriptive only.
### 6. Human validation
Measure comprehension, useful choices, satisfying simple attacks, enjoyment/assembly, elimination downtime and real minutes. Automated turns cannot establish human session duration.

## Bot architecture and policies
Dispatcher gives only authorized observation + legal decision specification + independently seeded policy RNG. NEVER full MatchState. Privileged evaluator separate.
| Policy | Purpose |
|---|---|
| Legal random | Rules exercise/fuzz, not balance authority |
| Eager attacker | Frequent legal development/attacks, simple choices |
| Preview-aware attacker | Straight attacking with obvious lethal/bad-trade checks |
| Cautious defender | Survival/favorable trades and stall stress |
| Resource-aware | Intermediate reserve/reaction/token budgeting |
| Bounded search later | Stronger limited-depth evaluation, information-safe hypotheses |
Simple policies model play styles, not a psychological simulation of a six-year-old. Compare two attacking variants so deliberate incompetence doesn't falsely condemn easy-pilot Silver/Gold.
Policies need passing, redraw, targets, payments, X, blockers/orders, sacrifice/trigger choices and assembly, not only card selection. Qualification scenarios test these separately. Decks rotate between policies so policy weakness isn't mislabeled deck weakness.
Search must sample hypothetical unknowns from permitted knowledge, not actual hidden hands/deck order; shared catalog doesn't reveal deck composition. Search enhancement optional after cost/value measurement. No LLM reasoning per decision.
Baseline FFA no scripted collusion; explicit assistance/coalition policies separate labeled experiments.

## Correctness and adversarial suite
- ATK0 defender, persistent wounds, blocking no exhaustion, readiness independent.
- One blocker assignment only; ordered multiblock and pooled simultaneous retaliation with source attribution.
- Exhausted HP2 needs1 raw lethal; HP5 needs3 raw (ceil1.5), before prevention. Do not use ceil(HP/1.5), which is wrong for some thresholds.
- Ready3HP+2shield needs5 raw; unused shield remains to expiry, earliest-first.
- Breakthrough raw budget conserved, no multiplier overflow; blocked status persists if blockers removed.
- Challenge missing target miss, no overflow/penalty, group target retaliates once and can't also block.
- Sources dying still deal simultaneous damage; <=0 checked before next response.
- Costs/X/discount floors, undiscountable leader increase, failures spend cost/usage, exact token payments.
- Leader reserve/recovery/tax, negated retry, uncopyable/unstealable, no player revival.
- Forms ratios ceil, repeated form loops quantify HP gain, no hidden precision; upgrades transfer/compatibility/disassembly, used eligibility not refreshed.
- Combine no ordinary enter/leave, component defeat triggers only genuine destruction, nested forbidden/copy no components.
- Elimination owned/borrowed effects and surviving pending chain; cleanup departure not defeat, skipped End triggers.
- Zero-cost activated loops, self-generating token/resource engines, identical state cycles.
Invariants: unique zone/instance linkage; legal domains; consumed tokens/eliminated seats can't act; no unauthorized projection; payment conservation; no eligibility/usage refresh by transformation/control; deterministic replay. Generated tests supplement independent expected examples.

## Experimental budgets and statistics (proposed defaults)
Benchmark small pilot first; default workers conservative 1–2, allow more after memory/CPU measurement while leaving desktop usable. No promised simulations/sec or GPU dependency.
Duel screen:200 seat-balanced games per selected matchup/policy pair (100 independent two-seat seed blocks).
Confirm:2,000 fresh seat-balanced games for frozen flagged comparisons (1,000 blocks). This is a practical budget, not guaranteed precision.
FFA screen:50 independent seed blocks x four cyclic assignments=200 games per selected lineup/policy setup. Confirm flagged cases with more blocks; cyclic assignments alone do not exhaust all opponent-order permutations, so add reverse/all permutations where seat/opponent order is implicated.
Predeclare fixed budgets or precision schedule, not stop when a desired result appears. Multi-parameter sweeps exploratory; confirm fresh seeds; report number of hypotheses examined.

Uncertainty:
- Shared-seed/seat-rotation games correlated: analyze independent SEED BLOCKS, block bootstrap/per-block differences primary.
- Wilson95% appropriate only for genuinely independent binary trials, not naïvely treating correlated matches as independent.
- Draw-half scores need appropriate block-score intervals, not binary win intervals.
- No universal +/-precision promise from raw game count. Report independent block count and method.
- Same-seed before/after enables paired blocks but diverging actions can change draws; does not mean identical hidden sequences. Explicit independent RNG streams and algorithm versions.
- Duel symmetrical reference50%, FFA equal entrants first-place25%; these are contextual references not universal target constraints.
- Show policy and seat strata; avoid one pooled strength number.

Metrics:
Outcomes/wins/draws/first-seat, elimination order and first-elimination turn, rounds/actions/response-chain length, remaining turns after elimination, empty-hand/non-progress cycles, resource use/growth payoff, creature deployment/trades/survival/player damage, Challenge/Breakthrough usage, deck-out, width and giant-vs-swarm. Record policy compute and throughput separately. Qualitative human satisfaction remains separate.

## Outcome classifications and denominators
completed_win, rules_draw, concession_scenario, detected_loop, turn_or_action_budget_truncation, policy_timeout, illegal_policy_action, unsupported_content, engine_error/invariant_failure, replay_divergence, cancelled, worker_failure.
Harness budgets are computational safeguards NOT player timers or new win conditions. Never convert truncation/error to draw or award victory by HP.
Display requested/started/completed/rules-valid/error/truncated/cancelled counts. Conditional completed-match win estimates clearly labeled; errors/truncations remain visible as share of attempted trials and can invalidate a conclusion. Do not silently discard inconvenient runs.

## Reproducibility and replay
Manifest: schema/experiment/jobID, engine commit/build+interpreter/dependency info, rules/content/deck/policy hashes, assumption/coverage IDs, master seed and derivation/RNG algorithm versions, per-game streams for game/policy random events, seat/start map, parameters/budgets/worker setting/machine metadata, timestamps.
Stable per-job seeds derive from job identity, never worker index/scheduling. Aggregate sorted job IDs. Pin definitions; source edits create a new experiment, never mutate in-flight state.
State replay uses recorded accepted commands/random outcomes and stable instance/event IDs, periodic canonical hashes. Policy rerun uses seeded bot decisions under pinned version; distinct reproducibility guarantee. Retain pinned content/config required to reproduce, not just hash without recoverable data.
Store ALL compact game summaries; full failure and representative/outlier traces configurable. Seed alone insufficient across code changes.
Public/player replay separate from clearly labeled omniscient developer debug; full debug contains hidden cards and must not be used for hints/bot observation. Test same-observation/different-hidden-state deterministic bot action equivalence.

## Desktop workflow
Five simple views:
1. Experiments: presets, versions, seeds, counts, coverage and assumption warnings.
2. Scenario editor: structured state/actions/expected result, no executable free text.
3. Runs: queue/progress/workers/elapsed, pause/cancel/resume, conservative measured ETA.
4. Results: uncertainty, matchup/policy/seat matrices, error/incomplete counts, flags.
5. Replay inspector: event timeline and compact board, explicit public/player/debug perspective.
Defaults let Steve start a preset without editing Python; advanced configuration expandable.
Recommend tkinter/ttk v1; rich tables/charts in standalone HTML exports. PySide6 if later interactive replay needs justify dependency; local web/mobile wrapper later, not required to run tests. No listening network service for desktop v1.

Main GUI thread, separate CPU processes. Coordinator only database writer; workers return isolated immutable result records. Bounded queues, no million-future allocation.
Pause stops scheduling new work and settles current bounded jobs; cancel cooperatively stops at safe action boundaries. Save completed jobs; interrupted jobs rerun from pinned seed/ID on resume. No promise arbitrary mid-match continuation in first tester. Retry/attempt history retained, idempotent completion keyed by jobID; avoid duplicate statistics.
SQLite checkpoints atomic, local app data separate from installed executable. Disk-full/worker-crash visible recoverable status. Simulation data cannot alter live achievements/currency.
Windows-first one-folder executable distribution after CLI/UI work; test clean Windows account and process spawning/frozen entry point. Packaging not yet built; source and acceptance test plan only.

## Exports
Experiment directory:
- manifest.json and pinned input definitions.
- results.csv / results.jsonl compact per-job metrics/status.
- summary.json with uncertainty, denominators/methods/flags.
- report.html standalone, no CDN/network dependency, escaped user-provided names/content.
- replays/ retained trace bundles with perspective labels.
- run.sqlite checkpoint/history.
Reports open without app installed. Offer optional share bundle excluding hidden/full-debug data by default. Include assumptions and coverage on first page, before recommendations. Never claim proven balanced.
Compact AI brief: experiment purpose/hash, counts and independent blocks, coverage, top findings/uncertainty, error/truncation rates, proposed next experiment, few selected replay links.

## Implementation work packages
| ID | Work | Acceptance gate |
|---|---|---|
| T0 | Rules ADRs, schema, supported mechanics manifest, fixture specification | No silent defaults; docs align no defense/revival; fixtures independently calculated |
| T1 | Definitions + deterministic combat core | Approved profile fixtures/invariants/illegal-action no mutation |
| T2 | Challenge/Breakthrough/prevention and finite scenario CLI | Boundary rounding, simultaneous/source cases correct; explicit coverage |
| T3 | Batch runner/checkpoints/reporting | Repeat same job hashes across worker counts; cancel/resume equals uninterrupted completed set; exports reopen |
| T4 | Minimal full-match rules + random/eager/preview-aware/defensive bots | Setup/endings/priority/privacy gates; no unsupported effects silently run |
| T5 | Leaders/upgrades/forms/assembly and resource-aware policies | Each mechanic fixture+interaction+replay coverage; loop flags |
| T6 | Windows desktop shell + packaging | Start/run/pause/cancel/resume/export without terminal; responsive GUI and clean-account smoke test |
| T7 | Screening and held-out confirmation | Block-aware results, explicit failures, frozen candidates; contrasting archetypes/FFA |
| T8 | Family validation and optional polish | Human timing/enjoyment, next reviewed card changes; optional advanced search/mobile reports |
T6 can wrap T3 scenario reports while T4–T5 progress, but full-match mode disabled until coverage gates. No hard timeline before benchmark/scoping. All stages proposed, no implementation performed.

## First concrete implementation slice (ready to begin when requested)
Create package skeleton with pure state/command types, nine approved ability-free definitions, scenario fixtures and headless CLI generating exact combat results and JSON/CSV manifest. Add first meaningful tests: persistent wounds, simultaneous multiblock, exhausted threshold, zero attack, invalid blocker assignment. No desktop scaffold/complete-match claims yet. Next implement Breakthrough/Challenge/shield pipeline, then runner exports, then UI.

## Official technical references reviewed by desktop specialist
Reverify chosen release/toolchain during implementation:
- Python Tkinter event model: https://docs.python.org/3/library/tkinter.html
- Python process execution: https://docs.python.org/3/library/concurrent.futures.html
- Qt Python alternative: https://doc.qt.io/qtforpython-6/
- PyInstaller distribution guidance: https://pyinstaller.org/en/stable/operating-mode.html

## Limits and status
The original planning task did not itself deliver code; subsequent implementation and experiment evidence is indexed in DOCUMENTATION_INDEX.md. No perfect-balance or throughput claim. This plan does not approve changing user rules to simplify engine work. Reports are evidence under named rules, coverage and policies; human family testing remains essential.
