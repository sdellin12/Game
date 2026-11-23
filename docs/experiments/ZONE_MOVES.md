# Zone-move integration
2026-11-23. Source checkpoint: coverage v12; practice pack v8.

## Implementation scope
`ReturnCreatureToHand` and `ExileCreature` are registered instructions and authored
single-creature targets. It uses the existing paid pending-card, target-relation, negation and
resolution pipeline, plus allowlisted views and private save records. The desktop
renders readable text and a public exile table. Unravel replaces Thunder Pebble at
spell-02; pack v5 replaces Unmake with the six-resource Banish Action at spell-05.
Older loaded packs retain their exact definitions/names. Tactics evidence is in
OPPONENT_TACTICS.md.
Canonical mechanics remain in RULES_DRAFT.md (Payments/resources, Combat,
Healing/protection/upgrades, Leaders); this file records implementation evidence.

The departure helper now accepts selected hand/exile destinations, leaving default
discard callers unchanged. The move gathers structural attachments and removes
targeted prevention durations before any later instruction can pause for refill.
Exile uses registered ordinary-card instances, preserving owner identity separately
from battlefield control. Token/leader replacements do not populate that zone.
Own-discard recovery is implemented separately; see DISCARD_RECOVERY.md.
Deck moves, exile recovery and hand transfers remain gated.

## Verification
13 return-to-hand cases cover paid public pending cards; borrowed ownership and fresh
re-entry; tokens and attachments; leader reserve/cost/recovery; departure versus
defeat triggers; absent targets with independent instructions; illegal targets;
negation; blocked memory and Breakthrough; Challenge misses; source-independent
pending abilities; public known-card history versus hidden hand contents; and
private round trips during the new instruction/required draw.

14 exile cases cover paid pending cards, ownership/public visibility, zone
conservation, token/leader replacement, attachments/durations, departure triggers,
negation, missing/illegal targets, elimination privacy, refill exclusion, interrupted
save/resume, combat blocked memory and the ordinary-card-versus-leader policy.
The desktop widget check verifies displayed exile identity and effect text.

Archived v1 and v2 next-command states still match after explicit current-schema
conversion; legacy MatchState/CardDefinition records gain only documented empty defaults.
Practice-policy runs for 2/3/4 players completed in 327/829/1867 commands and
17/36/74 turns. These runs check legal progress, not strategic quality.

Run with PYTHONPATH=src:
- python -m unittest discover -s tests -p test_zone_moves.py -q
- python -m unittest discover -s tests -p test_exile.py -q
- python -m unittest discover -s tests -p test_save_migration.py -q
- python -m crucible_play.smoke --practice --players 2 (repeat 3 and 4)

Rollback: revert the source checkpoint. Keep original v1/v2 saves/builds and use the
non-destructive conversion policy in SAVE_FORMAT.md. Do not alter existing saves.
