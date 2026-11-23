# Discard recovery integration
2026-11-23. Coverage v12; practice pack v8; save schema v5 / compatibility 1.

## Implementation
`RecoverDiscardCard` uses a registered ordinary card instance as its locked target.
Authored cards use `target_kind=discard` and friendly ownership; the existing payment,
pending-card and negation paths are reused. Resolution rechecks discard membership
and owner eligibility. Targets and recovered identities are allowlisted public data;
other hand contents stay private. Canonical behavior is in RULES_DRAFT.md.

Second Chance replaces Stored Momentum at spell-09 in new practice packs. It is a
three-resource Action. Old loaded packs retain their embedded definitions and names.
The desktop lists only the player's own registered discard cards. The opponent
prefers creatures and considers ordinary resources remaining for a separate replay.

## Evidence
13 focused tests cover paid confirmation and fresh-state replay; creature/Action/
Reaction/permanent recovery; invalid/foreign/hand/deck/exile/self targets; authored
metadata validation; negation; two recoveries choosing one card; refill moving the
locked target; eliminated owners; End hand-limit cleanup; public recovery history
versus private hands; exact native-v3 legacy states/next commands; pending practice
cards; and save cursors before or after recovery followed by a required draw.
A desktop widget test confirms the actual target-selection/payment handler.

Archived pre-recovery v3 fixtures include a nonempty exile zone/refill cursor and a
nested-negation chain. Both retain exact command results after explicit current-schema conversion with empty
trigger defaults. Existing v1/v2/v3 converters and
all prior persistence tests remain in the suite. Compatibility/rollback: SAVE_FORMAT.md.

Run with PYTHONPATH=src:
- python -m unittest discover -s tests -p test_recovery.py -q
- python -m unittest discover -s tests -p test_play_desktop.py -q
- python -m crucible_play.tactics

Current practice runs complete at 327/829/1867 commands and 17/36/74 turns for
2/3/4 seats. These check legal progress; tactical evidence is in OPPONENT_TACTICS.md.
