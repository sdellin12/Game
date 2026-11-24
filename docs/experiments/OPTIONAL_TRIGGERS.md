# Optional Use/Skip choices
2026-11-23. Coverage v12; pack v8; save schema v5 / compatibility 1.

## Scope
Printed TriggeredAbility and registered TriggerSpec support optional=True. Capture
that flag on each TriggerCandidate, with an initially unset decision. First authored
scope remains own-draw/discard permanent resource rewards. Scholar's Lantern is
optional in new pack v8; Salvage Battery remains mandatory. Old packs are preserved.
Canonical timing/privacy and card wording: RULES_DRAFT.md and CARD_DESIGN.md.

The waiting controller receives a session-bound trigger_choice command with an exact
trigger ID and strict boolean Use/Skip. Collect decisions after the atomic effect,
including any refill, then order only accepted/mandatory effects. Each original
multi-trigger controller group confirms its selected list, including an empty list.
Otherwise the presence/absence of ordering would disclose private choices. Public
waiting-controller lists depend on original groups, not accepted counts. Retain
skipped metadata only until queueing; other seats see no decisions. No responses or
orders interleave with choices. Partial choices persist privately.
Skipping at End does not create an extra response window. Safe-boundary concessions
remove eliminated owners' candidates. Captured choices survive source departure.

Desktop controls appear only behind the owner's seat acknowledgement and disable
while paused. Shared play/end controls disable for any pending required choice.
Computer policy uses positive resource rewards and declines registered self-damage.

## Verification and migration
16 focused cases cover Use/Skip, irreversible mixed decisions, strict/stale IDs,
wrong actors, public/other-seat equality, controller order from each active seat,
partial draws, concession, source departure, computer policy, v4 mandatory fixtures,
partial private save/resume, impossible flags, End skip, premature legacy fields,
and public equality through the ordering barrier even when all effects are skipped.
A widget case confirms private/paused Use/Skip handlers, empty-selection confirmation
and actual resource outcomes. Empty-group ordering state also round-trips in saves.

V5 conversion preserves v4 abilities and hashes, adding optional=False/decision=None.
Older defaults still apply only to the schemas that lacked those fields. Conversion
writes a separate output. Full policy/command and rollback: SAVE_FORMAT.md.

Run with PYTHONPATH=src:
- python -m unittest discover -s tests -p test_optional_triggers.py -q
- python -m unittest discover -s tests -p test_play_desktop.py -q
