# Fixed-controller authored rewards

Permanent own-draw/own-hand-discard abilities accept positive integer
GrantResources, HealPlayer and GrantCapacity steps, targeting `$controller` only.
Binding uses the resolved permanent's controller; no target selection is added.
Existing whole-effect timing, safe boundaries and optional-decision privacy apply.
Draw rewards remain excluded to avoid authored recursive draw loops.

Healing respects the engine's life cap and elimination rules. Capacity increases
permanent_bonus without increasing available resources until a Start refill.
Granted capacity survives source departure; ongoing printed capacity does not.
Mixed steps resolve together; Use/Skip applies to the entire effect.

Practice pack v9 replaces plain Memory Well with Archive Well (cost 5, ongoing
capacity 1, optional own-discard permanent capacity +1). Recurring healing is
supported for authoring/tests only, pending a separate cost/life-generation review.
No household collection data or card-template assets change.

Save schema remains v5 / compatibility 1; see SAVE_FORMAT.md for compatibility and
rollback. New typed authored reward hashes carry an additive discriminator while
old resource-only hashes stay identical. A native-v5 partially decided optional
trigger fixture verifies direct load, original hash and exact next-command result.

Regression tests cover mixed rewards, capped healing, delayed capacity, source
departure, optional skip, invalid targets/amounts, distinct reward hashes and
accurate desktop text. Hand-pressure evidence is in HAND_PRESSURE.md.

Pack-v9 verification: 397 Windows tests pass; tactics 21/21; mixed-client smoke
completes at 327/835/1751 commands for 2/3/4 seats. All nine all-computer seeds
complete below 4000 commands (1391/886/924, 1917/1697/1864, 2868/2366/2344).
They record 19 Lantern, 16 Battery and 18 Archive Well entries, 271 queued draw
items and zero discard items. Archive Well's natural reward value remains
unmeasured; adding a permanent did not make the existing policy create pressure.
