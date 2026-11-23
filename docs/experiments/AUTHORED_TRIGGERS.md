# Authored permanent triggers and multiplayer stress
2026-11-23. Coverage v12; practice pack v8; save schema v5 / compatibility 1.

## Authoring/entry
CardDefinition.triggered_abilities is an ordered tuple of TriggeredAbility records:
key, event, steps, watch, optional. First scope: permanent cards, mandatory/optional own card_drawn or
card_discarded events, and positive fixed GrantResources($controller, amount) rewards.
Any-watch authored rewards, targets and other reward instructions
remain gated. Canonical event semantics: RULES_DRAFT.md.

On resolved entry, source-length-prefixed keys bind printed rewards to that controller
and install registered TriggerSpecs/EffectSpecs. Negated plays install none. Retain
registered effects after departure for captured/queued triggers; re-entry reuses the
same definitions without duplicate installation. Conflicts reject before payment;
restored pending cards and live printed abilities must agree with the registry.

Scholar's Lantern (beacon-01) and Salvage Battery (beacon-02) replace the prior plain
capacity cards in new packs. Each costs four, grants one ongoing capacity, and grants
one available resource on its own draw or hand discard respectively. The Lantern
now says "may" in new pack v8; v4 saves retain their original mandatory wording. Old packs keep
their original identities/definitions. Inspection, battlefield and pending-trigger
labels show meaningful public text. Shared design panels: CARD_DESIGN.md.

## Verification
11 authored tests cover controller-specific rewards across all three seats, paid
pending entry, negation, both event types, retained effects after departure, re-entry,
invalid metadata/rewards, registry collision/missing bindings, v3 hash/default migration,
corrupt/premature legacy data, pending source saves and captured trigger-order saves.
A desktop test confirms the actual inspection/payment handler and public ability text.

Three stress methods exercise 54 draw/discard order combinations (2-4 players, 1-3
sources each, 1-3 cards), reversed confirmations and exact once-only reward counts.
Separate concession and bounded cascade cases check surviving candidates and refill.
All original observer, tactical and migration cases remain in the suite.

Schema-v4/v5 mapping and rollback were planned before model edits. Old definitions gain
empty trigger tuples; normalized pack hashing retains their original content hashes.
Original saves remain unchanged; conversion always writes a separate file.
Full policy/command: SAVE_FORMAT.md. Fixture provenance: tests/fixtures/README.md.

Run with PYTHONPATH=src:
- python -m unittest discover -s tests -p test_multiplayer_trigger_stress.py -q
- python -m unittest discover -s tests -p test_authored_triggers.py -q
- python -m unittest discover -s tests -p test_play_desktop.py -q

Pack-v7 2/3/4-seat practice runs complete in 327/829/1867 commands and 17/36/74 turns.
The existing three-seat under-1500-command regression remains unchanged.
