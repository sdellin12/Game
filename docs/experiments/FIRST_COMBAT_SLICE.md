# First Combat Slice — Validation Record

2026-11-22. Implemented on feature/balance-lab-combat-core. No full-game balance
conclusions are claimed.

## Delivered

- Pure immutable combat state, explicit commands and structured damage events.
- Simultaneous damage, ordered multiblocking, persistent wounds, exhaustion and
  readiness checks, Challenge groups, Breakthrough and numeric prevention.
- Nine approved ability-free creature test profiles as packaged JSON data.
- Strict JSON scenario loader: unknown fields/keywords/mechanics reject.
- Local command-line matrix and scenario runner with JSON/JSONL/CSV/HTML exports.
- Manifest core/content hashes, complete scenario inputs and replay verification.
- Standalone source launcher and dependency-free runtime; pyproject packaging.

## Evidence

Validated on Linux with Python3.12.14:

- 27 unittest tests pass, including independent expected combat examples,
  simultaneous retaliation, invalid blocker reuse, zero attack, exhausted lethal
  thresholds over 60 health/shield pairs, unsupported input rejection, safe HTML,
  repeatability, export/replay and tamper detection.
- Full finite profile matrix: 1,156 unique encounters, exported and replayed
  identically. Inputs: nine profiles in both directional roles, full/1-health
  states where distinct, ready/exhausted blockers and 0/2 prevention.
- Worked Breakthrough fixture: attack8 vs HP3+2 ->3 player damage, attacker
  takes4 simultaneous retaliation and remains4HP. Export/replay verified.
- Mutation check1: removing exhausted-blocker amplification caused combat tests
  to fail. Original source restored.
- Mutation check2: suppressing defeated blockers' retaliation caused combat
  tests to fail. Original source restored.
- Python wheel built without runtime dependencies, installed in an isolated
  target directory, and its packaged profile data loaded successfully. Installed
  package exported/replayed the same 1,156 encounters.

These verify implementation behavior within the declared subset. They do not
establish which profile/deck is strongest or whether matches are enjoyable.

## Limits

No full turns/matches, resources, reactions, leaders, triggers, form/assembly,
elimination cleanup or bots. No large-scale scheduling/checkpoint/resume or GUI.
No native Windows executable or actual Windows smoke test yet. No target-PC
throughput benchmark. No imported external TCG corpus or paid API use.

See [quickstart](../COMBAT_LAB_QUICKSTART.md) for commands and explicit experimental
assumptions. Full report outputs are generated locally under ignored lab-runs/;
do not commit bulk histories or interpret exact scenarios as statistical games.
