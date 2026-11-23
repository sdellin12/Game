# Practice opponent and leaders
Implemented 2026-11-23. Coverage v4; practice content pack v2.

## Changes and trust boundaries
- opponent.py is a deterministic, one-view policy. It can select opening redraws,
  play affordable supported cards, respond, block with its own creatures, order
  choices and use leaders. It has no server-state, opponent-hand or deck-order
  parameter. Exact payment considers only its controlled public resources/tokens.
- HarnessSession schedules at most one computer command at a time, including setup.
  It never readies/redraws/passes for humans. The desktop advances computers through
  scheduled callbacks, preserves human decisions and disables computer hand buttons.
  A burst cap halts diagnostics without fabricating a result. Opponent errors stop
  automation with a visible message; no failed command is silently converted to a pass.
- leaders.py stores definitions and outside-deck leader state. match.py integrates
  summon transactions, negation, reserve return, cost/recovery and location-specific
  abilities into existing priority/atomic cleanup. Public views/command routing and
  the UI expose those operations. Card-definition validation was extracted unchanged
  into a reusable helper for authored leader abilities.
- All forty ordinary card instances remain separate from designated leaders. The
  practice pack validates matching public identity/definition data and contains one
  reserve and one battle ability per leader. Existing catalog/save formats are not
  read or rewritten. No new runtime dependencies or paid services are involved.
- Canonical leader mechanics remain in RULES_DRAFT.md. Transform/copy/control/combine
  and custom cost/form rules are not approximated; remaining gates live in coverage.py.

## Verification and focused review
Windows Python 3.14.3: `$env:PYTHONPATH='src'; python -m unittest discover -s tests -q`
passes 236 tests, including 33 new tests for this slice.

Leader fixtures cover paid/pending entry, negated retry with costs spent, repeated
removal costs above ten, exact payments, recovery only at own Start, full-health
reentry/attack wait, reserve-versus-battle abilities, exhaust/usage restrictions,
already-pending abilities surviving departure, reserve reactions during pending
summons, elimination, Challenge retaliation and simultaneous leader/owner loss.
The last case proves exactly one removal charge and ordinary attachment cleanup.

Opponent fixtures prove hidden-state noninterference, own-view input, refusal to
act through another player's required choice, exact owned-token payments, private
blocker legality, human setup/priority barriers and a completed practice game.
Widget tests cover disabled computer seats, real scheduled computer readiness and
leader summon inspection. Existing handoff, payment and geometry tests still pass.

A three-seat stress run initially hit the 4,000-command diagnostic cap. Review found
repeated small-wound healing and premature exhaust abilities prolonging play. The
policy now reserves healing for low life and preserves readiness before combat.
A regression test locks completion below 1,500 commands for that fixed seed.

Repeatable checks (same default seed, scripted human client):
`python -m crucible_play.smoke --practice --players 2` -> 213 commands / 11 turns.
`python -m crucible_play.smoke --practice --players 3` -> 815 commands / 37 turns.
`python -m crucible_play.smoke --practice --players 4` -> 1,637 commands / 65 turns.
These demonstrate legal bounded completion, not opponent strength or win-rate gains.

Full visual review remains outstanding; current UI checks are owned Tk widget tests.
No portable executable rebuild or match persistence was introduced. Rollback is a
source revert; keep existing experiment data. PROJECT_STATE.md owns the next step.
