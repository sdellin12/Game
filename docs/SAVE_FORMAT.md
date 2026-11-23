# Private save format and rollback policy
Schema v5 / gameplay compatibility 1, implemented 2026-11-23.
Local harness only; catalog and combat-lab formats are unchanged.

## Storage and validation
A save contains frozen lobby/match/content, computer roles, hidden zones, seeds,
shuffle counters, priority, partial draws/refill, combat locks/orders, leaders,
clocks, registered/captured triggers and committed optional decisions. Human viewer
and tentative UI selections are omitted. Files are private plaintext snapshots,
not encrypted or authenticated replays. Saves/backups are ignored by Git. No autosave
or automatic conversion occurs.

Envelope: format/schema/compatibility versions, Python runtime, source fingerprint,
frozen content hash, payload and canonical SHA256 checksum. Checksums detect
corruption, not intentional editing. Source/rules hashes are provenance; Python
implementation and major.minor must match for deterministic stdlib shuffles.
Compatibility 1 preserves existing instruction/state/shuffle interpretation.
Frozen packs never silently receive the latest cards or optional wording.

Explicit allowlisted JSON dataclass/tuple/byte records only: no pickle, callbacks or
file-selected imports. Reject duplicate keys, wrong types, nonfinite values,
oversized/deep files, unknown records/versions, invalid ownership/conservation,
inconsistent bindings and impossible decision states before installing a candidate.

## V5 plan and mapping
The migration/rollback plan and v4 mandatory-source fixtures were recorded before
model changes. V5 adds optional=False to TriggeredAbility and TriggerSpec; captured
TriggerCandidate gains optional=False and decision=None. No MatchState fields change.

Explicit conversion from the Game repository directory:
```powershell
$env:PYTHONPATH='src'
python -m crucible_play.migrate "old.crucible.json" "converted.crucible.json"
```
Plain Load requires v5. The converter accepts known published v1 builds (9b0f7f5,
CPython 3.14, recorded workspace/LF/CRLF hashes), and compatible v2-v4 envelopes.
Unknown v1 builds retain their original runtime. Verify the original checksum,
provenance, content identity and legacy record/field permissions.

Apply only the relevant defaults:
- V1/v2 MatchState gains empty exile; v3/v4 retain their existing zone.
- V1-v3 CardDefinition gains empty triggered_abilities; preserve v4 authored lists.
- All earlier TriggeredAbility/TriggerSpec records gain optional=False.
- All earlier TriggerCandidate records gain optional=False and decision=None.
- Preserve every other field, including names, effects, seeds, event/request IDs,
  revisions, locks, cursors, captured candidates and ordering confirmations.

Canonical pack hashing omits empty trigger lists and optional=False defaults,
retaining v1-v4 content hashes; nonempty/optional abilities participate in hashing.
Reject premature optional/decision fields or records that could not exist in the
claimed input schema. Validate all converted models, frozen definitions and state
before publishing a separate file. Never overwrite input or an occupied/concurrently
created destination. Retain original bytes/builds; never edit fingerprints or strip
new fields to force downgrade. New v5 choices do not retrofit old mandatory cards.

## Optional-decision invariants
After atomic completion, the active-player/turn-order controller chooses each pending
optional candidate privately. Partial Use/Skip decisions persist and are irreversible.
No ordering or response interleaves. After decisions finish, only accepted/mandatory
effects appear in the owner's ordering list. Every original multi-trigger controller
group must confirm that list, even empty/singleton lists, so the ordering step does
not disclose Use/Skip outcomes. Retain skipped metadata privately until all groups
confirm, then queue accepted effects and clear the candidates.
Public views expose the waiting seat, not private decisions or future choices.
Only the currently eligible controller gets Use/Skip payloads. Ending/cleanup
continues through the existing safe boundaries; skipping adds no new response window.
Registry collisions reject before payment/restoring pending cards; live printed
abilities must match their registered sources. Retain effects after departure so
captured effects remain valid, and reuse definitions on re-entry.

## Writes, restore and evidence
Fixed-controller reward extension plan: reuse existing HealPlayer and GrantCapacity
records without adding fields or changing schema v5 / compatibility 1. Preserve the
archived native-v5 partial-decision fixture and its exact next-command result.
Hash newly authored healing/capacity steps with an instruction discriminator;
retain the existing encoding for resource-only authored rewards and all old packs.
Old saves load directly; old builds may reject new reward content. Roll back code
with its original saves/build, never rewrite a new-content save to force downgrade.

Validate/encode, write a same-folder temp, flush/fsync, then atomically replace.
Regular replacement retains exact previous valid bytes under a unique backup name.
Reject corrupt/non-save destinations and symlink targets. Conversion publishes
without replacement (Windows rename; POSIX exclusive hard link). On failure clean
only the operation's own temp. No startup migration runs.
Load validates a separate candidate before replacement; restore paused, hands hidden,
computers stopped. Resume enables commands; private seat acknowledgement remains.
File pickers suspend computers. Partial decisions never restore the old UI viewer.

Existing v1-v4 fixtures retain their content hashes and exact next-command results
with only defaults added. V4 fixtures include live mandatory authored sources,
partial refill/candidates and discard ordering. New tests cover partial private
choices, Use/Skip, stale/wrong-actor requests, End behavior, negation/elimination,
premature legacy fields, UI buttons and paused save/resume.
