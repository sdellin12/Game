# Private save format and rollback plan
Version 1, implemented 2026-11-23. Applies only to the local play harness.

## Before implementation: data/compatibility decision
There is no existing match-save format to migrate. Keep the catalog, combat lab
SQLite checkpoints and reports unchanged. Add a separate `.crucible.json` format
and ignore saves/backups in Git. No autosave or automatic conversion is introduced.

A save holds the complete frozen LobbyState/MatchState plus computer roles,
including opening locks, hidden zones, seeds/shuffle counters, priority/passes,
resolving cursor/refill choice, combat locks/orders, leaders and duration clocks.
Do not store the current human viewer or tentative UI selections. Files are private
plaintext snapshots, not public replays or encrypted/account-authenticated storage.

## Version/validation policy
- Envelope: fixed format ID, schema version 1, runtime fingerprint, frozen content
  hash, payload and canonical SHA256 checksum. The checksum detects corruption;
  it does not authenticate a file against intentional editing.
- JSON only, explicit allowlisted dataclass/tuple/byte tags; never pickle or dynamic
  imports selected by file content. Reject duplicate keys, unknown tags/fields,
  nonfinite numbers, oversized files, deep nesting and invalid record field types.
- Validate setup provenance/conservation and the engine's current state invariants
  before installation. Definitions remain embedded/frozen rather than replaced
  with the current default practice pack. Runtime/rules compatibility must match.
- No previous version is assumed. Unknown/newer versions and incompatible builds
  fail closed without rewriting files. A later converter needs an explicit schema
  mapping, fixtures and new-output-file migration; retain the original save/build.

## Durable write and rollback
Validate/encode before filesystem changes. Write a temporary file in the target
directory, flush/fsync and atomically replace. Before replacing an existing valid
save, preserve its exact bytes in a uniquely named backup; never overwrite/delete
older backups. Refuse non-save/corrupt destinations and symlink targets. A failed
write leaves the previous save intact and cleans up only its own temporary file.
No data migration is run on startup or on load. Rollback is source/build rollback
plus opening the retained matching save/backup; do not edit stored fingerprints.

## Resume behavior and verification
Load into a separate candidate session first; a failed load preserves the current
session. Restore paused, hide all private widgets and stop computer automation.
Explicit Resume re-enables commands/computers; privacy handoff is still required.
Save/load file pickers suspend computer stepping during the operation.

18 persistence tests cover exact round trips at lobby/opening/priority/refill/combat locks/
orders/trigger choices and duration boundaries; the same subsequent command must
produce the same authoritative state after resume. They also cover unsupported schemas,
corruption, wrong builds, unknown types, collection/card conservation, atomic-write
failure and backups. Desktop tests cover paused loads, private UI reset, rejected
loads and explicit resume. Fixtures are synthetic; no existing user data is used.
Gameplay visual review verified the paused public table, resume, seat handoff,
private hand/leader controls and corrected leader summon details.
