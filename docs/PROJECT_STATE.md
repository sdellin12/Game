# The Crucible - Resume Here
Updated: 2026-11-22

## Current checkpoint
- Branch: feature/combat-coverage-and-timing; draft PR #2.
- Latest implementation: private views, command routing and hand-card transactions.
- Combat lab: desktop, portable build, checkpoint runner and replay inspector.
- Card templates: standard/full-art v1 complete; design/cards contains sources.
- Engine: managed turns, costs, combat, private projections and pending-card zones.
- Validation: 179 Windows tests; previous 36,214 combat equivalence cases unchanged.
- Full-match mode remains disabled pending the integration work below.

## Next implementation
Completed both selected slices; see experiments/PRIVATE_VIEWS_HAND_PLAY.md.
Recommended next: a small local playable harness using these same views/commands.
Then: lobby/opening hands and a validated content pack; leaders/durations remain gates.
Versioned implementation coverage: src/crucible_core/coverage.py v2.

## Read only the relevant entry
Start here, then read one spec/source directly relevant to the current task.
- Product decisions: REQUIREMENTS.md.
- Gameplay rules: RULES_DRAFT.md (canonical; avoid duplicate baseline summaries).
- Timing implementation: FULL_MATCH_TIMING_SPEC.md.
- Current engine evidence/audit: experiments/PRIVATE_VIEWS_HAND_PLAY.md.
- Card design/handoff: CARD_DESIGN.md.
- Lab operation: COMBAT_LAB_QUICKSTART.md.
Expand reads only when a concrete dependency requires it.
Do not read ANSWERS.md, DISCOVERY.md or design/cards/output/* unless asked.
CHANGELOG.md preserves older checkpoints; do not read it by default.

## Working constraints
Keep this file under 50 lines; replace stale status and archive older history.
Edit generators/fixtures, then regenerate artifacts; do not edit generated output.
Default to one agent; scope architecture/timing audits separately when needed.
Batch at most 2-3 questions when blocked; keep changes and summaries focused.
No saved-match schema exists; design migrations before adding persisted state.

## Verification and handoff
Tests: set PYTHONPATH=src, then python -m unittest discover -s tests -q.
Design bundle: python design/cards/make_handoff.py.
Bundle location: dist/CardTemplate-Handoff-v1.zip (local ignored artifact).
Offer concise multiple-choice next steps at completion.
