# The Crucible - Resume Here
Updated: 2026-11-22

## Current checkpoint
- Branch: feature/combat-coverage-and-timing; draft PR #2.
- Latest implementation: Start/resources, ability costs and committed combat flow.
- Combat lab: desktop, portable build, checkpoint runner and replay inspector.
- Card templates: standard/full-art v1 complete; design/cards contains sources.
- Engine: managed turns, exact ability costs, private blocker locks and atomic cleanup.
- Validation: 148 Windows tests; 36,214 unchanged legacy combat outcomes.
- Full-match mode remains disabled pending the integration work below.

## Next implementation
Completed all three selected slices; see experiments/START_COST_COMBAT.md.
Recommended next: general private player/bot projections and command routing.
Then: hand-card play/zone transitions; leaders and duration scheduling remain gates.
Versioned implementation coverage: src/crucible_core/coverage.py.

## Read only the relevant entry
Start here, then read one spec/source directly relevant to the current task.
- Product decisions: REQUIREMENTS.md.
- Gameplay rules: RULES_DRAFT.md (canonical; avoid duplicate baseline summaries).
- Timing implementation: FULL_MATCH_TIMING_SPEC.md.
- Current engine evidence/audit: experiments/START_COST_COMBAT.md.
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
