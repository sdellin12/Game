# Local match screen
Updated 2026-11-24. This is the first usable-screen implementation slice, not a
family-test readiness signoff. Human testing remains deferred in REQUIREMENTS.md.

## Flow and information placement
1. Select a human seat, acknowledge the handoff, select a deck/leader and ready.
   Existing lobby and opening-hand controls remain unchanged in this slice.
2. The match opens on one scrollable table. The fixed header names the active
   player, phase, priority holder and next required action. Pass/continue and End
   turn use the existing command path and availability checks.
3. Required private choices appear first, followed by public combat and pending
   effects. Each player has a fixed zone showing life, available resources, hand
   and deck counts, leader location and battlefield cards.
4. The acknowledged viewer's hand uses three-column card tiles. Inspection opens
   the existing payment/target confirmation dialog; it never submits a move.
   Hide or seat change closes inspection dialogs and destroys private widgets.
5. Public discards, exile, durations and recent events follow the hand. Use the
   vertical scrollbar for a large board/hand. Computer seats remain inaccessible.

## Runtime card content
Tiles use permitted engine metadata: name, kind, cost, creature attack/health,
keywords, rules text and a short instance reference. Battlefield creatures also
show current/max health, exhaustion, attack readiness and prevention. Resource
tokens and capacity permanents display their values. These are app presentation
tiles, not replacements for standard/full-art print templates. Artwork, collection
metadata and unpublished local card-editor assets are not integrated here.

## Implementation and verification
- `src/crucible_play/match_screen.py` owns presentation only; desktop.py retains
  seat privacy, confirmation dialogs, required choices and command dispatch.
- Default launch: `python run_play.py`; developer fallback: `python run_play.py --debug-ui`.
- `tests/test_match_screen.py` checks privacy, non-mutating inspection, actual
  payment submission, priority/paused controls and large-hand geometry using hidden
  Tk windows. Existing developer-screen tests remain in test_play_desktop.py.
- No rule, save-schema, pack, bot-policy or card-template changes are involved.
  Rollback is selecting --debug-ui or reverting the presentation change.

## Next slice
Reduce scrolling between hand and battlefield, improve lobby/opening guidance,
and replace combat's form rows with clearer card selection. Required-choice forms
and payment dialogs are still engineering controls. Visual review, accessibility,
mouse/touch interactions and real device checks remain outstanding before deciding
whether a family session is appropriate. Automated widget checks are not that review.
