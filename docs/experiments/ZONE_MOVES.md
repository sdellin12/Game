# First zone-move integration
2026-11-23. Source checkpoint: coverage v7; practice pack v4.

## Implementation scope
`ReturnCreatureToHand` is a registered instruction and an authored single-creature
target. It uses the existing paid pending-card, target-relation, negation and
resolution pipeline, plus allowlisted views and private save records. The desktop
renders readable effect text; the view-only opponent uses its existing creature
target selection. Unravel replaces Thunder Pebble at spell-02 in new practice packs.
Loaded older packs retain their exact definitions/names instead of receiving v4.
Canonical mechanics remain in RULES_DRAFT.md (Payments/resources, Combat,
Healing/protection/upgrades, Leaders); this file records implementation evidence.

The departure helper now accepts selected hand destinations, leaving its default
discard callers unchanged. The move gathers structural attachments and removes
targeted prevention durations before any later instruction can pause for refill.
Other zone moves (exile, deck moves, discard recovery, hand transfers) remain gated.

## Verification
13 focused cases cover paid public pending cards; borrowed ownership and fresh
re-entry; tokens and attachments; leader reserve/cost/recovery; departure versus
defeat triggers; absent targets with independent instructions; illegal targets;
negation; blocked memory and Breakthrough; Challenge misses; source-independent
pending abilities; public known-card history versus hidden hand contents; and
private round trips during the new instruction/required draw.

The archived v1 priority/refill/private-blocker command results still match after
this additive engine change. Compatible snapshots preserve the old pack and state.
Practice-policy runs for 2/3/4 players completed in 327/1303/1749 commands and
17/61/69 turns. These runs check legal progress, not strategic quality.

Run with PYTHONPATH=src:
- python -m unittest discover -s tests -p test_zone_moves.py -q
- python -m unittest discover -s tests -p test_save_migration.py -q
- python -m crucible_play.smoke --practice --players 2 (repeat 3 and 4)

Rollback: revert the source checkpoint. Keep original v1 saves/builds and use the
non-destructive conversion policy in SAVE_FORMAT.md. Do not alter existing saves.
