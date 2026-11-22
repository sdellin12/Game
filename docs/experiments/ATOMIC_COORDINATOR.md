# Atomic coordinator foundation
Updated 2026-11-22. Internal immutable experiment state, not a playable match or
production save format. Full-match mode remains disabled.

## Implemented subset
`crucible_core.match` coordinates the existing priority, turn/draw and combat
primitives. Registered effects contain typed player damage, healing, required
draw and creature-destruction instructions. Effects finish before player health
checks or permanent elimination. Intermediate signed health is preserved; a later
separate effect cannot rescue an eliminated player. Independent instructions
continue after a draw failure or an absent/eliminated target.

A required draw can suspend one resolving item for an actor/revision/request-bound
refill choice. Available draws and accepted payments stay committed. The supplied
shuffle must exactly permute the discard and is recorded; no global RNG is used.
The policy remains explicit experimental input: tests use cost20/floor1, not a
new adopted price. Own-turn exhaustion requests End after pending work; off-turn
refill records Recharge for the next own turn.

Stabilization records genuine simultaneous creature defeats first, captures
lifecycle witnesses before removal, then eliminates losing players and removes
objects they own or control. Ordinary borrowed cards go to their owners' discard;
tokens disappear. Structural orphan attachments depart. Cleanup departures never
manufacture defeat events. Eliminated controllers' pending items/triggers are
cancelled; surviving controllers' already queued items outlive their sources.
Mandatory lifecycle/End triggers group in active-first surviving seat order, with
the last group resolving first. A controller with multiple candidates explicitly
chooses their order before responses resume.

Confirmed concessions are recorded and processed serially at safe boundaries.
Terminal results stop later queued concessions; arrival batching cannot turn an
otherwise finished duel into an all-concede draw. A conceding refill chooser is
released without deadlocking the current effect. Abandoned active turns skip End
triggers, drain surviving pending work, apply supplied expiration consequences and
rotate in original seat order. Boundary expiration is an explicit registered tuple
for the current turn, not a general duration scheduler.

End intent preserves the all-seat final response window. End triggers run once,
then the hand limit is enforced, followed by expiration consequences and any
resulting triggers/hand-limit checks. Terminal results wait for valid pending work
and mandatory boundary choices. Rotation consumes a pending Recharge flag and
opens the next Start; automatic Start maintenance is still external.

The closed-window Combat-phase adapter calls the existing simultaneous damage
kernel. It accepts only active-player attacks and stabilizes the resulting whole
snapshot. It does not implement attack declarations, hidden blocker locks/reveal,
pre-damage reactions, or a second combat rules implementation.

## Trust boundary and remaining gates
This is an internal fixture/effect executor. `queue_effect` assumes an already
authorized instruction, not a legal-card-play endpoint. Resource costs, card
ownership/zone play legality, reactions versus main-action timing and hidden
information projections still require a production command layer. Do not expose
these dataclasses or private `draw_records` directly to players/bots.

Leaders, combined forms, continuous stat/capacity modifiers, arbitrary prose,
discard/draw event abilities, generic targeting/replacement/cost systems and a
full eliminated-seat duration scheduler are not covered. Unknown instruction and
object types reject. Repeated Recharge debt and mandatory draw/refill during
Recharge continue to reject through the turn primitive. No full-match simulator,
resource economy or family playtest is claimed by these fixtures.

## Verification and rollback
25 focused tests cover whole-effect health, simultaneous defeat/draw, delayed
victory, cancellation, source-independent pending effects, owned/controlled/token
and attachment cleanup, trigger witnesses and explicit ordering, three-controller
ordering, paid/declined/insufficient refill, Recharge intent, abandoned turns,
serial concessions, final End responses, repeated hand checks after expiration,
stale/invalid choices, unsupported content and the combat adapter.

Windows command: `$env:PYTHONPATH='src'; python -m unittest discover -s tests -q`.
114 tests pass (25 new plus 89 regressions). No combat matrix rerun is needed:
combat rules and scenarios are unchanged. Existing checkpoint/report/catalog
formats and saved data are untouched. Remove this isolated coordinator/tests and
revert the optional deferred-health draw parameter to roll back; do not delete
experiment data. A persisted match schema will need a separate versioned migration
and rollback design before it is introduced.

Recommended next slice: automatic Start/resource maintenance and legal action-cost
transactions with conservation/rejection fixtures; then attack/block declaration
flow and private projections before enabling full-match play.
