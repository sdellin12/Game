# Project State — Resume Here
Updated 2026-11-17. Phase: discovery complete; expert build-planning draft complete; no implementation started.

## Read in order
1. [Confirmed requirements](REQUIREMENTS.md) — concise canonical product/gameplay brief.
2. [Build plan](BUILD_PLAN.md) — milestones, dependencies, validation and next work package.
3. Focused detail only as needed: [architecture](ARCHITECTURE_PROPOSAL.md), [rules](RULES_DRAFT.md), [UX/content](UX_CONTENT_PLAN.md).
4. ANSWERS.md is historical interview record with superseded brainstorms; do NOT read it all by default. DISCOVERY.md is original question queue, no longer current progress.

## Latest decisions
- One bounded final revival opportunity before last active player wins; exact procedure/eligibility still draft.
- Combination health = combinedMax × sumCurrentHP/sumMaxHP. All components destroyed when combined creature destroyed, except explicit survival effects.
- Leader resummon costs escalate and can include sacrifice/exile; outside effects recover owner's next turn.
- Baseline: four players,40–60min;40 singleton+leader,5 opening,1 draw/own turn,7 hand end turn,30HP provisional; one-color+generic.
- Full requirements and revisions consolidated in REQUIREMENTS.md; do not recover defaults from obsolete interview entries.

## Completed
Two user-requested expert teams: initial discovery; second platform/rules/UX planning. Their results saved in focused docs and synthesized into BUILD_PLAN. Parent verified official Apple/Roku/Android/Flutter sources. No code, installs, hardware benchmark or gameplay testing performed.
Later large comparative balance team is deferred and has NOT run.

## Current consequential question
Native iPad distribution: free Xcode Personal Team provisions expire7days/rebuild-reinstall; Apple Developer Program US$99/year offers other routes but exact route/device support still requires verification. Current TestFlight needs iPadOS16+ and builds expire90days. User prefers simple private installed apps, not web app. Ask whether they prefer exploring paid native route, free periodic maintenance, or explicit iPad-only web exception. No fees/purchases authorized. No-cost requirement previously applied to artwork generation; broader platform-fee budget wasn't decided.
Actual iPad models/OS intentionally deferred until available. Do not re-ask known PC specs (Ryzen5/GTX1650; RAM/VRAM unverified). Need current Mac/Xcode access later.

## Next actions after preference
1. Record iPad installation preference; maintain both Roku and Google TV requirements.
2. Close core rules draft via worked examples (revival R01, leader access R02, combat P05–P08, blocking exhaustion). Exact card costs user deferred; don't restart endless micro-interview.
3. Choose feasible installed-client stack after real-device spike. Proposed Python+SQLite Linux server, Flutter personal clients candidate, Android TV view, separate Roku SceneGraph.
4. Plan/start only when user requests implementation; current chat requested planning.
5. First proposed engineering slice: Linux public-card endpoint and installed viewers on all required actual platforms. Follow BUILD_PLAN acceptance gates.

## Working conventions
One consequential question at a time. Accepted requirements versus proposals labeled. Decisions saved to GitHub sdellin12/Game main; no Library mirror for repo items.
Use scoped briefs and compact canonical docs to conserve tokens; retain historical answers for provenance. New versions should update canonical requirements/state, not grow this file into interview transcript.
Models recommended: Sol ordinary work, Astra focused difficult review; agents inherited session model. No model switch claimed.
