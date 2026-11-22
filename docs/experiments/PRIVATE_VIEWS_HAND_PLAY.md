# Private views, command routing and hand-card transactions
Implemented 2026-11-22. Current scope: crucible_core.coverage v2.

## Implementation
- views.py builds detached JSON-compatible allowlisted views for a living player,
  bots using that same player view, spectators, and eliminated sessions. It exposes
  public board/counts/resources/chain/discards and only the viewer's own hand and
  choices. No deck order, hidden instance registry, full effect registry, shuffle
  seed, draw replay records or raw event causes are serialized. Unknown event
  types default to omission. Unseen target IDs in source abilities are redacted.
- commands.py accepts a strict kind/revision/args envelope plus a separately
  trusted session actor. Payload identity/extra fields reject. Internal effect
  queueing, resolution and supplied shuffle outcomes have no client command.
  Server work resolves one selected chain item after all-seat passing. The router
  prevents End Turn from bypassing mandatory Start/Draw or pending choices.
- Refill shuffles use a caller-supplied private server seed and immutable counter.
  A local RNG produces recorded permutations; accepted paid commands advance the
  counter. Rejection changes no state/global RNG. Deterministic experiment replay
  is supported; production seed custody belongs to the future server transport.
- cards.py defines match-only immutable definitions/instances, separate from the
  household catalog format. Supported cards: plain creatures, capacity permanents,
  structured Actions/Reactions, and chosen player/creature/effect targets with
  authored relation constraints. Locked targets bind before payment. Negation is
  a structured effect against an existing pending effect ID, never a client cancel.
- Hand -> pending commits payment and public identity together. Resolution moves
  the same instance to battlefield/discard; negation/elimination cancel pending
  cards without refunds. Registered instances occupy exactly one zone. Creatures
  enter ready at full HP with attack/exhaust eligibility waiting for their next
  controller Start; blocking works immediately. Card text/ability entry extensions
  reject until covered. The approved pending/discard timing is canonical in
  RULES_DRAFT.md, not redefined here.

## Boundary review / verification
31 new tests, 179 total passing on Windows Python 3.14.3:
`$env:PYTHONPATH='src'; python -m unittest discover -s tests -q`.

Exact tests compare public/opponent views after hidden hand/deck/definition/seed
changes, prove no earlier blocker lock leak through full player projections,
check eliminated viewers, public reveal history and detached results, and reject spoofed actors, unknown
commands, stale revisions and client-chosen shuffles. Invalid foreign/unknown card
requests return the same error. Router-driven managed turns verify newly played
creatures can block before attack eligibility. Card fixtures cover payment before
responses, locked targets disappearing, negation, cancellation, duplicate/missing
zones, persistent entry and a draw card remaining unavailable to its own refill.

The existing combat kernel is unchanged by this slice; its previous 36,214-case
equivalence evidence remains applicable. Diff checks and the 50-file design
handoff hash manifest pass. PROJECT_STATE.md stays at 42 lines.

## Integration and rollback
These are pure internal boundaries, not a network service, authenticated session
implementation, saved-match schema, UI or bot policy. Transport must bind the
actor/viewer to the authenticated session, return project_match output only, and
keep raw MatchState private. Do not let clients select viewer IDs, provide server
seeds or call internal effect helpers. Supported command kinds are the allowlist
in commands.py; clients can inspect their own view without a legal-reaction signal
being emitted to opponents.

Existing catalog, checkpoint/report and saved-data formats are untouched. Legacy
fixtures may contain opaque unregistered IDs; those cards cannot be played. A
production content pack will need complete validated registration. Rollback is a
source revert; preserve existing experiment data. No executable rebuild was made.
PROJECT_STATE.md owns the next step; coverage.py owns remaining implementation gates.
