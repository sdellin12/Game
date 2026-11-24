# The Crucible - Resume Here
Updated: 2026-11-24

## Current checkpoint
- Branch: feature/combat-coverage-and-timing; draft PR #2.
- Latest checkpoint: card-based required choices, named order previews, visual hierarchy and keyboard guidance.
- Combat lab: desktop, portable build, checkpoint runner and replay inspector.
- Card templates: standard/full-art v1 complete; design/cards contains sources.
- Launch the local harness: python run_play.py from the Game repository directory.
- Validation: 475 Windows tests pass; 66 docs/links/versions pass; 98 Python sources parse; 44 state lines.
- Local practice is playable; production full-match coverage remains gated.

## Next implementation
Budgeted policy fixes both known losses; fresh case wins 6/18 vs baseline 4/18, with one regression; live bots stay baseline.
Owner deferred human testing: REQUIREMENTS.md; FAMILY_PLAYTEST.md is a future checklist.
Recommended next: guided walkthrough and whole-flow focus/small-window checks; MATCH_UI_FLOW.md owns UI scope/limits.
Versioned implementation coverage: coverage.py v14; default pack v9 / opt-in package v1; save schema v6 / compatibility 1.

## Read only the relevant entry
Start here, then read one spec/source directly relevant to the current task.
- AI continuation/source map: AI_HANDOFF.md; full document roles: DOCUMENTATION_INDEX.md.
- Product decisions: REQUIREMENTS.md.
- Gameplay rules: RULES_DRAFT.md (canonical; avoid duplicate baseline summaries).
- Timing implementation: FULL_MATCH_TIMING_SPEC.md.
- Harness usage: PLAY_HARNESS.md; persistence policy/evidence: SAVE_FORMAT.md.
- Card design/handoff: CARD_DESIGN.md.
- Proposed discard package: DISCARD_DRAW_PACKAGE.md; data: design/packages/discard_draw.json.
- Lab operation: COMBAT_LAB_QUICKSTART.md.
Expand reads only when a concrete dependency requires it.
Do not read ANSWERS.md, DISCOVERY.md or design/cards/output/* unless asked.
CHANGELOG.md preserves older checkpoints; do not read it by default.

## Working constraints
Keep this file under 50 lines; replace stale status and archive older history.
Edit generators/fixtures, then regenerate artifacts; do not edit generated output.
Default to one agent; scope architecture/timing audits separately when needed.
Batch at most 2-3 questions when blocked; keep changes and summaries focused.
Save compatibility and rollback: SAVE_FORMAT.md; preserve original v1-v5 saves/builds.

## Verification and handoff
Tests: set PYTHONPATH=src, then python -m unittest discover -s tests -q.
Design bundle: python design/cards/make_handoff.py.
Bundle location: dist/CardTemplate-Handoff-v1.zip (local ignored artifact).
Offer concise multiple-choice next steps at completion.
