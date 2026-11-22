# The Crucible — Resume Here
Updated 2026-11-22. Planning only; no implementation, simulations, hardware benchmarks or family playtests performed.

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
- Ability-free candidate ATK/HP: cost1=2/1,1/2,0/3; cost2=3/2,2/3,1/4; cost3=4/3,3/4,2/5. Not tested.
- Theme-first builder, leader choices, guided roles, private draft practice, shared permanent card catalog, independent optional shared deck copies.
- Permanent earned-only cosmetics/achievements, no real money EVER. All art retained, per-instance public treatments, no in-match changes.
- Desktop local test lab requested: no per-test AI, CSV/JSON/HTML, reproducible seeds/replays/multiple policy skill levels; mobile report companion later proposal.

## Current user request
First sync everything discussed to GitHub, then relevant expert subagents discuss/plan design and implementation of tester. Documentation updates authorized on sdellin12/Game. Implementation not requested yet.
Core requirements/rules/build/UX/lore consolidated and verified. Four-specialist review completed: engine architecture, experimental statistics, hidden-safe bots/adversarial QA and Windows desktop UX/packaging. Synthesis saved in BALANCE_TESTER_PLAN.md. Recommended next work when implementation is requested: T0/T1 pure combat core, nine approved candidate profiles and independent expected fixtures; CLI runner before desktop UI. No coding or test runs yet.
User authorizes sensible tests/candidate numbers without approval for each fixture; ask consequential tradeoffs with selectable options+optional text.

## Known gates
Windows PC Ryzen5/GTX1650 (RAM/VRAM unknown), Linux home server previously discussed but deployment not verified. Tester CPU work independent of art/GPU/mobile install.
Actual iPads under Screen Time require restriction-safe delivery test; web accepted, weekly native fallback. Both Roku/GoogleTV required completed game. No paid art API; unattended ChatGPT Plus worker path unverified.
No estimates/claims of balanced cards before evidence. Bots see legal information only; full-game coverage cannot be inferred from combat-only simulation.
