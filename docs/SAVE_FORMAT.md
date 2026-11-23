# Private save format and rollback policy
Schema v3 / gameplay compatibility 1, implemented 2026-11-23.
Applies only to the local play harness; catalog and combat-lab formats are unchanged.

## Stored state and privacy
A save holds the complete frozen LobbyState/MatchState plus computer roles,
including opening locks, hidden zones, seeds/shuffle counters, priority/passes,
resolving cursor/refill choice, combat locks/orders, leaders and duration clocks.
The current human viewer and tentative UI selections are omitted. Files are private
plaintext snapshots, not public replays or encrypted/account-authenticated storage.
Saves/backups are ignored by Git. There is no autosave or automatic conversion.

## Schema and gameplay compatibility
- Envelope: fixed format ID, schema version, gameplay compatibility version,
  Python runtime, source runtime fingerprint, frozen content hash, payload and
  canonical SHA256 checksum. The checksum detects corruption, not intentional editing.
- Schema v3 retains `compatibility_version: 1`, introduced by v2. Source runtime and frozen lobby rules
  hashes record provenance; they no longer require identical engine source bytes.
  Frozen definitions stay embedded rather than being replaced by the default pack.
- A compatibility version promises unchanged interpretation of existing state,
  instructions and shuffle algorithms. Additive instructions/UI changes may retain
  it after archived old-save/next-command regression checks. Incompatible semantics
  require a new compatibility version and an explicit reviewed converter.
- Python implementation and major.minor version must match because shuffles use
  the standard library. Source-build compatibility does not grant Python upgrades.
- JSON uses explicit allowlisted dataclass/tuple/byte records, never pickle or
  file-selected dynamic imports. Reject duplicate keys, unknown records/fields,
  wrong field types, nonfinite numbers, oversized files and deep nesting.
- Validate setup provenance/conservation, frozen content hashes and engine state
  invariants before installing a candidate. Unknown schema/compatibility versions
  fail closed without modifying the input or active session.

## Explicit v1/v2 conversion
The migration/rollback design was recorded before schema changes. The converter
supports the published 9b0f7f5 CPython 3.14 build: recorded deployed-workspace,
Git LF and Git CRLF hashes only. Unknown v1 builds retain their original runtime.
Only records that existed in that build may enter the v1 conversion path.
V2 input uses its recorded gameplay compatibility and Python version; its source
hash is provenance. Reject unknown compatibility versions and wrong Python.

From the Game repository directory:
```powershell
$env:PYTHONPATH='src'
python -m crucible_play.migrate "old.crucible.json" "converted.crucible.json"
```
The converter checks checksum, source/rules provenance, payload, frozen content and
state before publishing a separate v3 file. It preserves the original bytes and
refuses occupied destinations, including the input and concurrently created files.
Load the new file normally. Plain Load does not silently convert schema v1/v2.

## Schema v3 field mapping and rollback plan
The plan and synthetic v2 priority/refill/pending-Unravel snapshots were recorded
before changing state. V3 adds `MatchState.exiled: tuple[str, ...]`, empty by default,
and includes it in card conservation and allowlisted projections. Exile gameplay
is canonical in RULES_DRAFT.md. Gameplay compatibility stays 1 because existing
instructions and zones retain their meaning.

For each v1/v2 MatchState, add only an empty tagged exile tuple. Preserve every
other payload field, embedded pack, seed, cursor, lock, revision and event. Reject
legacy payloads that already declare the new field or instruction; enforce each
legacy record allowlist, then validate the complete current state. Keep the input
bytes and publish only to a new destination. This is never an in-place migration.

## Additive discard-recovery record
Recovery adds the allowlisted `RecoverDiscardCard` record and `discard` target kind,
without changing existing record fields, state layout or instruction semantics.
Schema v3 / compatibility 1 therefore stays unchanged. Archived pre-recovery v3
snapshots (exile/refill and nested counters) load directly and reproduce their exact
next-command states. Snapshots containing a new record require a reader that knows
it; older readers fail closed. Retain earlier files/builds for rollback.

## Durable writes and rollback
Regular saving validates/encodes first, writes a same-folder temporary file,
flushes/fsyncs, and atomically replaces the destination. Before replacement, retain
the exact previous valid envelope in a uniquely named backup; never overwrite/delete
older backups. Refuse corrupt/non-save destinations and symlink targets.
Conversion publishes a complete temporary file without replacing a destination
(Windows non-replacing rename; POSIX exclusive hard link). Failed publication
cleans up only its own temporary file. No startup data migration occurs.
For rollback, retain original v1/v2 files and the matching old build. V3 cannot be
opened by old v1/v2 readers; never edit stored fingerprints to force compatibility.

## Resume and evidence
Load validates a separate candidate before asking to replace the current session.
Restore paused, hide private widgets and stop computers. Explicit Resume enables
commands/computers; private hands still require seat acknowledgement. File pickers
suspend computer stepping.

18 persistence tests cover exact round trips and same-next-command state across
lobby/opening, priority, refill, combat locks/orders, trigger choices, leaders,
durations and terminal states, plus corruption, size/type limits, backups and
injected replacement failure. 14 migration tests cover archived synthetic v1/v2
next-command results (priority, refill, private blockers, pending Unravel), opening
locks, source/newline variants, unknown builds/versions, wrong Python, premature
exile data, occupied/concurrent outputs and failed publication. Desktop tests
cover paused loads, privacy reset and the public exile table. Return-to-hand and
exile and recovery instructions round-trip in pending cards and refill cursors.
