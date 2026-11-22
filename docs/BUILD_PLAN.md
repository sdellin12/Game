# Build Plan — Proposed Delivery Sequence
Updated 2026-11-22. Planning only; no implementation, benchmarks, automated simulations or family playtests performed.

## Current authorized work
Consolidate all conversation decisions in GitHub, then specialist team design/plan a local rigorous balance tester. Do not begin implementation merely from this planning request. Tester may start independently of mobile/TV platform gates.

## Tracks
| Stage | Deliverable | Exit evidence |
|---|---|---|
| B0 | Current product/rules/lore and tester plan | Canonical docs agree, decisions vs proposals clear |
| B1 | Reusable deterministic headless combat engine | Exact expected fixtures, invalid-action checks, regression coverage |
| B2 | Local batch scenario runner | Seeded reproducibility, exports, coverage/assumption manifest |
| B3 | Basic full-match engine and several policies | Legal hidden-safe bots, endings, reproducible replay, seat rotation |
| B4 | Desktop balance dashboard | Start/cancel/resume batches, comparisons, readable reports and replay inspection |
| G1 | Actual-device delivery feasibility | Android/iPad Screen Time/Google TV/Roku install/update/public-card proof |
| G2 | Local multiplayer battle slice | Private state projections, reactions, leaders, pause/save/reconnect on required devices |
| G3 | Family playtests | Simple aggression vs defense/setup, 40–60min target and elimination downtime evidence |
| G4 | Creation/catalog and artwork worker | Supported effects, guided decks, art queue/review/reuse, safe asset retention |
| G5 | Progression and complete client delivery | Earned-only cosmetics, practice/hints, backups, installation instructions |

Ten colors defined; first numeric comparisons ability-free, then contrasting aggro/defense/endurance/assembly and Gold multiplayer, expanding coverage. Intermediate subsets aren't completed ten-color offering.
Initial starter mix24 creatures/10 actions-reactions/6 persistent; 1-resource2/1,1/2,0/3; 2-resource3/2,2/3,1/4; 3-resource4/3,3/4,2/5. Candidates only.

## Tester principles
Same rules core game/tester/bots/hints; no per-match LLM. Deterministic code computes results, AI reviews compact summaries/outlier replays. CSV/JSON/HTML with seeds/rules/content/policy versions and assumptions. Test small-vs-large, attack-defense persistent/exhaustion, first-seat bias, policy skill, matchups. Never equate self-play win rates with proven human balance. Full test plan after requested specialist synthesis.

## Platform/art gates remain
Actual old-iPad OS and Screen Time standalone/navigation/camera/TTS/reconnect checks; preserve browser restrictions, weekly native fallback accepted, annual fee unapproved. Both Roku and GoogleTV remain required for completed game. Existing source references retained in ARCHITECTURE_PROPOSAL.md, reverify before implementation.
Ryzen5/GTX1650 known, RAM/VRAM unknown; art benchmark necessary; subscription-backed unattended image generation unverified. No paid fallback.
No independent simulator/game rules forks; schemas/effects registered/versioned, match definitions frozen, migrations/backup required. Future mechanic packages reject unsupported features rather than approximate silently.

## Workflow
Use focused docs and concise test summaries. User authorizes reasonable candidate stats and tests without repetitive approvals. Ask consequential unresolved experience choices; give selectable options+optional text. No claims of changing model or real credentialed experts; subagents supply independent specialist perspectives. All previous player-revival/full-defense bypass plans superseded.
