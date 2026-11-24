# Local match screen
Updated 2026-11-24. This is a usable-screen implementation slice, not a
family-test readiness signoff. Human testing remains deferred in REQUIREMENTS.md.

## Flow and information placement
1. The lobby guides seat selection, reserve identity/deck application and Ready.
   Status cards name who is still waiting; only the host can deal once all seats
   are ready. Opening hands use private card tiles with replacement checkboxes,
   a live selection count and an explicit lock. Unmarked cards are kept. Hiding
   or switching seats clears tentative marks; locked choices cannot be changed.
2. The match opens on one scrollable table. The fixed header names the active
   player, phase, priority holder and next required action. Pass/continue and End
   turn use the existing command path and availability checks. Fixed shortcuts
   jump to battlefield, hand, required choice, effects and history. The selected
   location restores after refresh for that viewer; new required choices take
   precedence. Hand navigation requires an acknowledged seat. Wheel scrolling is
   bound only to the current table, not other windows or the whole application.
3. Required private choices appear first, followed by public combat and pending
   effects. Each player has a fixed zone showing life, available resources, hand
   and deck counts, leader location and battlefield cards.
4. The acknowledged viewer's hand uses three-column card tiles. Inspection opens
   a private payment/target review; it never submits a move. Hide, seat change or
   any view refresh closes review dialogs and destroys stale private widgets.
5. Public discards, exile, durations and recent events follow the hand. Use the
   vertical scrollbar for a large board/hand. Computer seats remain inaccessible.

## Payment and target review
The scrollable review shows cost, available ordinary resources, token choices,
exact total and remaining ordinary resources, with confirmation/cancel below it.
Ordinary payment starts at the lesser of cost and available resources; tokens are
never selected automatically and are explicitly marked as consumed. Invalid,
unavailable, short or excess payments disable confirmation.

Targeted plays require explicit selection from the existing permitted target
projection. Public player life and effect labels aid selection; identifiers
distinguish duplicate creature/discard names. No first target is silently selected.
No-target, paused, unavailable timing/priority or stale actor/revision reviews
cannot submit. Leader abilities use projected availability. The engine still
validates the final command; rejection remains visible in the review. Cancel
changes no game state. No legal-target or payment rule moved into the UI.

## Combat selection
Eligible attackers appear as cards with Stay back, player targets and any Challenge
targets. Each eligible blocker has Do not block and named incoming attackers;
short identifiers distinguish duplicate names. Challenged creatures are excluded
from ordinary blocking. A live count tracks selected attackers/blockers. Selecting
targets changes only local widgets; explicit confirmation submits the complete
batch through existing engine validation, including empty/no-block batches.
Blocker assignments remain private until the engine reveals them. Paused combat
controls cannot submit; locked defenders see a waiting message. Damage-order and
trigger-order forms retain their previous controls.

## Runtime card content
Tiles use permitted engine metadata: name, kind, cost, creature attack/health,
keywords, rules text and a short instance reference. Battlefield creatures also
show current/max health, exhaustion, attack readiness and prevention. Resource
tokens and capacity permanents display their values. These are app presentation
tiles, not replacements for standard/full-art print templates. Artwork, collection
metadata and unpublished local card-editor assets are not integrated here.

## Implementation and verification
- `src/crucible_play/match_screen.py`, `setup_screen.py`, `combat_selection.py`
  and `confirmation.py` own presentation only; desktop.py retains seat privacy,
  other required choices, developer controls and command dispatch.
- Default launch: `python run_play.py`; developer fallback: `python run_play.py --debug-ui`.
- `tests/test_match_screen.py` checks privacy, non-mutating inspection, actual
  payment submission, priority/paused controls and large-hand geometry using hidden
  Tk windows. `test_setup_combat_ui.py` checks actual setup/redraw transactions,
  eligibility and assignment packets, a real no-attack engine command, paused
  controls, private mark reset and thirty-creature scroll geometry. Existing
  developer-screen tests remain in test_play_desktop.py.
- `test_navigation_confirmation.py` checks navigation restoration/privacy, cancel,
  exact mixed payments, controlled-token filtering, explicit enemy targeting,
  absent targets, paused controls and stale confirmation rejection.
- No rule, save-schema, pack, bot-policy or card-template changes are involved.
  Rollback is selecting --debug-ui or reverting the presentation change.

## Next slice
Improve damage/trigger ordering and required discard/refill choices, then visual
hierarchy and keyboard guidance. The UI still uses native widgets; some required
choice forms remain engineering controls. Visual review, accessibility,
mouse/touch interactions and real device checks remain outstanding before deciding
whether a family session is appropriate. Automated widget checks are not that review.
