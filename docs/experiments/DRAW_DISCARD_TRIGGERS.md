# Registered draw/discard observers
2026-11-23. Coverage v10; practice pack v6; save schema v3 / compatibility 1.

## Scope
This checkpoint adds mandatory `card_drawn` and `card_discarded` events to existing
registered battlefield TriggerSpec sources. It does not add trigger fields to
CardDefinition or author new trigger-bearing practice cards. Canonical event and
atomic-boundary behavior is in RULES_DRAFT.md.

Register an EffectSpec under the source controller, then attach a matching
TriggerSpec to that MatchObject. For these player events, `watch=self` observes
the source controller's card moves; `watch=any` observes all players. Existing
trigger ordering, responses, negation and eliminated-controller cleanup are reused.
Draw events reveal the player only, never the drawn card identity.

## Implementation and compatibility
_record_draw compares the newly recorded hand against the current player's hand,
so partial draws capture immediately and refill resumes count only additional cards.
Candidates wait through the atomic effect/refill, then use the existing trigger queue.
choose_end_discards observes confirmed hand discards and queues/requests ordering
before End proceeds. Triggered draws can require another hand-limit discard.

Observer events are materialized only when a matching registered source exists.
This keeps existing listener-free saves' event/request IDs unchanged; it does not
alter the existing required_draw journal. Native-v3 fixtures and v1/v2 migration
next-command tests continue to verify exact states. Legacy converters additionally
reject observer event names that did not exist in the old schema. No files migrate
in place; compatibility/rollback policy is SAVE_FORMAT.md.

## Evidence
16 tests cover per-card capture after atomic effects; partial refill without duplicate
counts; declined refill and surviving witnesses; own/any matching and zero draws;
End discard counts and order confirmation; hand-limit rechecks; non-discard zone
moves; cross-controller stack order; draw identity privacy; paused-refill snapshots;
invalid events; source departure before/after capture; normal draw and first-duel
skip; eliminated owners; negated trigger effects; and saved discard-order choices.

Run with PYTHONPATH=src:
- python -m unittest discover -s tests -p test_draw_discard_triggers.py -q
- python -m unittest discover -s tests -q

New practice-card authoring needs a separate explicit trigger data model, migration
plan, public ability text and entry registration. It remains gated in coverage.py.
