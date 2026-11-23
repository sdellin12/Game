# The Crucible - Resume Here
Updated: 2026-11-23

## Current checkpoint
- Branch: feature/combat-coverage-and-timing; draft PR #2.
- Latest implementation: multi-attacker reaction choices and registered draw/discard observers.
- Combat lab: desktop, portable build, checkpoint runner and replay inspector.
- Card templates: standard/full-art v1 complete; design/cards contains sources.
- Launch the local harness: python run_play.py from the Game repository directory.
- Validation: 352 Windows tests; tactics 21/21, draw/discard observers and save checks pass.
- Local practice is playable; production full-match coverage remains gated.

## Next implementation
Multi-attacker resource scenarios and registered draw/discard triggers are complete.
Recommended next: design authored trigger-bearing cards with migration-safe defaults.
Alternative: stress-test multiplayer trigger chains before authored-card expansion.
Versioned implementation coverage: src/crucible_core/coverage.py v10; practice pack v6; save schema v3 / compatibility 1.

## Read only the relevant entry
Start here, then read one spec/source directly relevant to the current task.
- Product decisions: REQUIREMENTS.md.
- Gameplay rules: RULES_DRAFT.md (canonical; avoid duplicate baseline summaries).
- Timing implementation: FULL_MATCH_TIMING_SPEC.md.
- Harness usage: PLAY_HARNESS.md; persistence policy/evidence: SAVE_FORMAT.md.
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
Save compatibility and rollback: SAVE_FORMAT.md; preserve original v1/v2 saves/builds.

## Verification and handoff
Tests: set PYTHONPATH=src, then python -m unittest discover -s tests -q.
Design bundle: python design/cards/make_handoff.py.
Bundle location: dist/CardTemplate-Handoff-v1.zip (local ignored artifact).
Offer concise multiple-choice next steps at completion.
