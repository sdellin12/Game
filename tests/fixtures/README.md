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
