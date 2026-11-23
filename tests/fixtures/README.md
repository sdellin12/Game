# Archived private-save fixtures
`save_v1_9b0f7f5.json.gz` contains synthetic snapshots made before engine edits,
using commit 9b0f7f5, CPython 3.14 and the test_persistence helpers. Each includes
a real schema-v1 envelope, one subsequent command and the original authoritative
result. Cases: partially passed priority, interrupted required draw/refill and
one locked multiplayer defender. No user saves are included. These immutable
regression inputs must not be regenerated from the newer runtime.

`save_v2_before_exile.json.gz` archives synthetic schema-v2 snapshots and original
next-command results before the exile state change: priority, refill and a pending
Unravel that resolves on the recorded command. Built from the fbfdbd6 engine/state
with the subsequent view-only policy fix (no state or command semantics changes).
Do not regenerate these from the schema-v3 runtime.

`save_v3_before_recovery.json.gz` archives synthetic schema-v3 snapshots and next
commands before adding the recovery instruction: exile plus interrupted refill, and
an Unravel chain with nested counters. Generated from the 1864642 state/engine with
the subsequent view-only nested-chain policy fix. No state layout changed. These
fixtures originally checked direct native-v3 compatibility. V4 now requires explicit
conversion with empty trigger defaults. Do not regenerate these archived inputs.

`save_v3_before_authored_triggers.json.gz` is a synthetic d36da74 observer/refill
snapshot with two captured triggers, frozen content hash and the original next
command/result, archived before the CardDefinition field change. Conversion adds
empty authored-trigger defaults while preserving that hash/cursor/candidate set.
