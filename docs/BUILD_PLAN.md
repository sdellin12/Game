# Implementation Plan — Proposed, Not Started
2026-11-17. Second expert planning team completed platform, rules and family-UX reviews. Canonical product brief: REQUIREMENTS.md. No coding/deployment, hardware benchmark or family playtest yet. No exact release date/effort estimate justified until feasibility gates pass.

## Critical path
1. Resolve native iPad installation tradeoff and actual device reach.
2. Make a minimal client/server transport proof on ALL four required platforms.
3. Close coherent combat, leader and revival rules for a playable ruleset.
4. Implement one battle slice, then family starter playtest.
5. Add creation/catalog and automated artwork queue.
6. Validate expanded color library and family usability; package first completed version.

Rules drafting can proceed while deferred hardware details unavailable; no need block independent design work. iPad-only web option explicitly allowed if secure/restriction-compatible; no silent global PWA substitution, Roku deferral or paid generator.

## Milestones and exit checks
| ID | Work | Reviewable exit |
|---|---|---|
| M0 | Canonical docs, decision register, unresolved gate list | Resume from PROJECT_STATE without full chat; accepted/proposed separated |
| M1 | Inventory and installation/generation feasibility | Real iPad/Android/GoogleTV/Roku install/update proof; Linux card fetched; PC sample art report or explicit backend blocker |
| M2 | Ruleset v0 draft and headless engine | Deterministic command/state model, worked response/combat/revival examples, selected proposals recorded |
| M3 | Connected battle slice | Four private seats, both TV viewers, turn/resource/draw/attack/block/response/pass, pause/reconnect; no hidden TV payload |
| M4 | Family starter playtest | Legal 40-card color decks and leaders, 30HP/5 opening/7 cap baseline; full win/loss including deck-out and bounded revival; record duration/comprehension |
| M5 | Creation and catalog | Wizard/archetype/full build, traits/validation, read-level text/TTS, camera/gallery, private drafts/shared finalize/copy/reuse |
| M6 | Art worker integration | Deck queue, incremental per-card results, cached assets, retry/restart/stale-result protection, tucked-away regen; zero paid fallback |
| M7 | First completed version | Both TVs + Android + actual older iPads, simple install/update docs, usable tutorials/creation, roughly-ten agreed identities, verified starter coverage and extension boundaries |

Milestones are proposed order; M1 art benchmark and M2 rules work can overlap. M4 may use placeholder art and a smaller selection of starter decks internally, but do not call that the completed requested ten-identity offering. Final roster and exact first-release starter count still require a concrete card plan.

## Proposed repository layout
- server/: rules engine, transport, library/storage and queue service
- clients/mobile/: candidate shared Android/iPad installed app
- clients/google-tv/: TV display implementation or proven shared Android target
- clients/roku/: native SceneGraph/BrightScript viewer
- workers/art/: local PC job runner and generation adapters
- shared/schemas/: versioned commands, public/private snapshots, cards/effects/content packs
- content/: rulesets, supported effects, draft starter cards; art binaries stored on home server, metadata in repo
- tests/: scenario fixtures, contract/visibility/recovery checks
- docs/: product, rules, architecture, UX, setup, playtest reports and next task
Do not create empty app scaffolding until stack/compatibility chosen.

## First proposed engineering work package (after planning choices)
M1 "public card viewer": minimal Linux service, versioned card JSON/art URL, installed read-only display on each platform, update sequence/reconnect, screenshots and reproducible setup. No battle UI, paid API keys or fake support matrix.
Dependencies: native iPad signing/build route, models/OS, Roku dev-mode approval/setup, Linux access. User deferred iPad details; don't repeatedly request until available.
Success: all required actual devices display same card/version and reconnect; install/update steps acceptable to household.
If iPad build route blocked, continue rules/UX/contracts and Android/TV spikes while clearly reporting M1 not complete.

## Rules decisions before full-match coding
See RULES_DRAFT.md:
- R01 revive participation/access/payment/limits/retained state and mill-defeat eligibility.
- R02 leader summon/resummon/passive timing.
- P05–P08 multi-block raw allocation, pooled versus separate retaliation, exhausted modifier, trample.
- Blocking exhausts or not, repeated allied blocking and one blocker per attacker constraints.
- Choose turn/priority defaults, including explicit pass burden in four-player games.
- Near-ten distinct color identities/relative specialties, card types and validated starter lists.
- Weakness tags/bonuses minimal and intuitive; no arbitrary color chart.
These are proposed rules work, not all requests for immediate interview questions. Review coherent examples one consequential choice at a time.

## Test and balance strategy
Use deterministic scenario fixtures that exercise genuine interactions: defenses/health, multi-block order, wounded transforms, combined damage ratio, trample/exhausted conversion, responses between resolutions, illegal commands, hidden-state projection, reconnect, milling/revival/final-window termination.
Test art worker idempotency/retry/stale-job protection with fake backend before consuming generation.
Cross-client protocol contract tests and actual installation/viewer checks. Test no opponent hand in TV payload or other-seat snapshots.
No need write tests mirroring trivial UI markup. Essential rules/privacy/recovery tests required.
Family sessions record duration, turns, hand churn, deck-out rate, revival count, player downtime, first/seat advantage, assistance use and rules questions. Compare archetypes/combos and near-duplicates, not only individual card budgets. Do not promise superb balance from research alone.
Later user-requested large comparative team for MTG/Pokemon/Elestrals/Yu-Gi-Oh! should have scoped official-source questions, synthesis and independent adversarial review; exact team size deferred. Simulation prioritizes likely exploits; actual mixed-age play essential.

## Art-provider feasibility criteria
Known PC Ryzen5/GTX1650, RAM/VRAM unverified. Measure supported local model's quality, latency, memory and queue recovery, not assume "lots of server storage" implies image compute.
Investigate official supported subscription-backed image tool routes/limits/result retrieval. Consumer Plus not equivalent to arbitrary free API. Stop when limits hit; no paid fallback authorized.
If neither integrated route works acceptably, return to user with concrete options (manual import already known but doesn't meet automated primary flow); do not label feature implemented.

## Extensibility and release discipline
Server effect registry, versioned rule profiles and cost schemas, registered readable descriptions, content-pack validator, art-provider adapters, compatible client capabilities. Unsupported effects rejected before match.
Pinned match rules/cards prevent editor changing live combat. Data migrations and backups before library changes. Optional later features do not alter existing matches silently.
Native mobile plugin restrictions handled through signed app updates; no universal executable plugin promise.

## Models and token economy
- GPT-6.1 Sol: interview synthesis, structured card drafts, normal coding/debug/docs.
- GPT-6 Astra: focused final rules/architecture adversarial review; optional, do not claim switched.
- Image models: lightest suitable actual backend; benchmark, no exact usage guarantee. Prompt assembly no model.
- Current expert agents inherited session model; three focused briefs, no large comparative team launched.
Read PROJECT_STATE then focused doc. Avoid default rereading 100KB historical ANSWERS. Record stable decisions and next tasks; specialists get scoped briefs/outputs. Re-review only after material changes or phase gates.

## Next user decision
iPad direction now permits secure/restriction-compatible home-screen web app; weekly native reinstalls accepted fallback. Next clarify how browser access is blocked (Screen Time vs managed profile). Test permitted full-screen client on actual iPad before selecting web or native path. Hardware/OS deferred; Mac build route necessary only if native fallback selected. No fee or restriction changes approved.

### M1 updated iPad gate
Prove web client launches after restoring existing browser restrictions and cannot open arbitrary browsing through game UI; verify hand privacy, camera/import, local connection, reconnect and read-aloud. Standalone icon alone insufficient. If blocked, evaluate accepted weekly native fallback. No general browser enablement or removal of parental controls as implicit prerequisite.
