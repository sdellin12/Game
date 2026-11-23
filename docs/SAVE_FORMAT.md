# Private save format and rollback policy
Schema v4 / gameplay compatibility 1, implemented 2026-11-23.
Applies only to the local play harness; catalog and combat-lab formats are unchanged.

## Stored state and privacy
A save holds the full frozen lobby/match, embedded pack, roles, hidden zones,
seeds/shuffle counters, priority, partial draws/refill choices, combat locks/orders,
leaders, clocks, registered abilities and captured triggers. Human viewers and
tentative UI selections are omitted. These are private plaintext snapshots, not
public replays or encrypted/authenticated storage. Saves/backups are ignored by Git.
There is no autosave or automatic conversion.

## Schema and compatibility
The envelope contains format/schema/compatibility versions, Python runtime, source
fingerprint, frozen content hash, payload and canonical SHA256 checksum. Checksums
detect corruption, not intentional editing. Source/rules hashes are provenance;
Python implementation and major.minor must match for deterministic stdlib shuffles.
Gameplay compatibility 1 promises unchanged interpretation of existing instructions,
state and shuffle algorithms. Incompatible semantics require a new compatibility
version and a reviewed converter. Frozen definitions never silently receive the
current practice pack. Unknown records/versions and invalid fields fail closed.
JSON uses explicit allowlisted dataclass/tuple/byte records, never pickle or
file-selected imports. Duplicate keys, nonfinite values, excessive size/depth,
wrong types, invalid ownership/conservation and inconsistent state are rejected.

## V4 design and explicit conversion
The migration/rollback plan and a native-v3 observer/refill fixture were recorded
before changing models. V4 adds CardDefinition.triggered_abilities (empty tuple by
default) and the typed TriggeredAbility record. Native content includes mandatory
own-draw/own-hand-discard permanent abilities with fixed controller resource rewards.

From the Game repository directory:
```powershell
$env:PYTHONPATH='src'
python -m crucible_play.migrate "old.crucible.json" "converted.crucible.json"
```
Plain Load requires v4. The converter accepts known published v1 builds (9b0f7f5,
CPython 3.14, recorded workspace/LF/CRLF hashes) and compatible v2/v3 envelopes.
Unknown v1 builds retain their original runtime. Original checksum/provenance is
checked before conversion. Reject records, observer enums and fields that could
not exist in the claimed input schema.

Field mapping:
- V1/v2 MatchState gains only an empty exiled tuple; v3 retains its existing zone.
- Every legacy CardDefinition gains only an empty triggered_abilities tuple.
- All other payload values remain unchanged: names, definitions, seeds, revisions,
  locks, events, cursors and registered trigger candidates/effects.
- Canonical pack hashing omits empty trigger defaults, retaining old content hashes.
  Nonempty authored abilities participate fully in the content hash.

Validate the converted models, setup/frozen definitions, content hash and complete
state before publishing a new file. Tests compare exact old next-command results
with only these default fields added. Migration never overwrites the input or an
occupied/concurrently created destination. Keep the original bytes/build for rollback.
New v4 abilities are not retrofitted to old cards; v4 files cannot be read by older
schema readers. Never edit fingerprints or remove new fields to force compatibility.

## Observer and authored-registration invariants
Observer events materialize only for matching registered sources, preserving
listener-free legacy event/request IDs. Partial draws count only newly added cards;
candidates/ordering choices persist across pauses. Authored source-scoped effects
install at resolved entry, remain registered after departure for captured effects,
and are reused on re-entry. Validate printed abilities against live registration
and reject conflicting reserved keys before payment or restoring pending cards.

## Durable writes and resume
Validate/encode first, write a same-folder temporary file, flush/fsync and atomically
replace. Before regular replacement, retain exact previous valid bytes under a unique
backup name; never overwrite/delete older backups. Reject corrupt/non-save destinations
and symlink targets. Migration publishes complete bytes without replacement (Windows
non-replacing rename; POSIX exclusive hard link). Failure cleans only its own temp.
Load validates a separate candidate before asking to replace the active session.
Restore paused with hands hidden and computers stopped. Explicit Resume enables
commands; private hands still need seat acknowledgement. File pickers suspend bots.

## Evidence
Existing persistence/migration cases cover corruption, backups, interrupted/concurrent
writes, privacy, old v1/v2/v3 states and exact next-command results. New authored cases
cover empty defaults/content-hash preservation, rejected premature fields/records,
pending permanent entry, live registry invariants and captured-trigger order saves.
The pre-v4 v3 observer/refill fixture retains its nonempty candidates and request ID.
