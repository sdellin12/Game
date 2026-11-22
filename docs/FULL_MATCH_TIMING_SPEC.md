# Full-match timing and elimination specification — draft 2

Status: partially approved engineering specification, reviewed 2026-11-22. This does not
change confirmed rules or enable full-match simulation. REQUIREMENTS.md and
RULES_DRAFT.md remain canonical. The rules explicitly left several sequencing
choices open; recommendations below fill those gaps for review, not silently as
accepted rules. No dependency on another TCG's timing system is implied.

## Confirmed constraints

- Fixed turn order, Start -> Draw -> Main -> Combat -> Main -> End; no timers.
- Newest pending effect resolves first; responses reopen after each resolution.
- Targets/modes/costs lock on confirmation; costs paid before responses, no refund.
- Simultaneous combat and defeat; no responses between damage and lethal cleanup.
- Permanent elimination for health <=0, unrecovered failed required draw or confirmed concede.
- Surviving pending effects may still resolve; no winner halfway through cleanup.
- Eliminated controller's pending actions/ordinary triggers removed. Elimination
  cleanup is departure, not defeat. No player revival.
- Own simultaneous triggers may be ordered by their controller, with a suggested
  order and Confirm/Adjust. Only public/authorized information informs suggestions.
- Disconnect pauses; saved pending choices and priority must restore exactly.

## State contract

Store active seats, original circular seat order, active-turn seat, phase/substep,
turn counter and per-seat own-start counter. Store pending chain items oldest to
newest, priority holder, consecutive-pass set, pending trigger-choice requests,
deferred elimination causes, duration anchors, and combat declaration records.
Every object/item/event has a stable monotonic ID; no wall-clock tie breaking.
Persist private projections separately from public replay output. Rules/content
hash and timing-spec version freeze when the match begins.

A committed command is a transaction: validate authority/priority/targets/costs;
apply locked choices and costs; append the pending item if applicable; run the
stabilization procedure; publish permitted events and durable save. Validation
failure changes nothing, including RNG and usage counters. Pending effects keep
captured parameters and source IDs after their source leaves.

## Priority — approved 2026-11-22

1. At an ordinary phase response window, the active player has first priority.
2. A legal chain addition clears all passes; priority moves to the next active
   seat after its controller in fixed circular order. It does not auto-resolve.
3. A pass gives priority to the next active seat. New decisions cannot use stale
   pass messages: commands name the expected state revision/window ID.
4. When every active seat passes consecutively, resolve exactly the newest item.
   Stabilize completely, queue eligible triggers, then give priority to the active
   seat (or next surviving seat if it was eliminated).
5. With an empty chain, all-seat passing advances the current substep/phase.
   Only the active player may take ordinary main actions; other seats can react.
6. An ordinary main action adds its pending item and opens responses. End-phase
   progression is a declared intent, allowing a final response window before it.
7. Autopass submits ordinary pass commands under the same revision rules. Public
   waiting UI must not reveal whether a private reaction is legal. No forced timer.

Owner choices needed to resolve an item (e.g. optional triggers/order) suspend
priority advancement. A response cannot preempt a cost payment or an internal
choice of an already-resolving item. Choices record IDs, not UI positions.

## Start and End boundaries — approved 2026-11-22

Start is one automatic boundary transaction for the active surviving seat:
expire next-own-start durations anchored to this boundary; reset applicable usage
and attack eligibility; ready eligible objects; clear leader recovery; increase
natural capacity (first own turn stays 2, later +1 capped10); refill from current
capacity. Then stabilize and queue Start triggers. Open priority before Draw.
Explicit card replacement effects may modify these operations only when supported.

Draw performs one required draw, except the first starting-player draw in a duel.
Stabilize, queue draw triggers, then open priority before Main. A zero-card deck
alone is not elimination. Own-turn depletion can end that turn; at an exhausted
required draw, apply the approved paid refill procedure before recording an
unrecovered failed draw. See DECK_REFILL_DESIGN.md for Start/refill/Recharge timing.
Optional draws occur only when their optional instruction is accepted.

End: queue end triggers, resolve the chain and responses to quiescence, then
request discards to seven. Discard choices are committed together; resolve their
mandatory consequences and associated response windows. Repeat hand-limit check
if consequences increase hand size. Expire turn-end durations, stabilize, and
advance. Ordinary main plays do not reopen from this loop. Any authored effect
that could repeat indefinitely needs explicit limits or a detected-loop diagnostic.

## Trigger collection and cross-controller order — approved 2026-11-22

For each atomic event batch, capture trigger candidates using the appropriate
pre/post-event snapshots. Simultaneously defeated sources witness that batch;
source departure alone does not erase a trigger already captured. Elimination
filtering below still removes an eliminated controller's ordinary triggers.

Approved ordering: active seat first, then other active seats in turn order.
Each controller chooses its own oldest-to-newest chain order. Append those groups
in that seat order; newest resolves first, so the last seat's group resolves first.
No responses interrupt the collection/order-choice batch. Then normal priority.
Later stabilization events form later batches; stable event and trigger IDs break
otherwise identical ties for suggested ordering, never replace a player's choice.

Steve approved this cross-controller ordering in the Codex review on 2026-11-22.
Acceptance fixtures must include at least three seats with conflicting triggers.

## Atomic resolution and stabilization

An atomic unit is one resolving chain item or one simultaneous combat damage
batch. Independent instructions in an item resolve in written structured order;
no priority opens between them. Recheck targets when each instruction needs them;
invalid targets fail locally and independent legal portions proceed. No arbitrary
prose parsing or imported all-targets-invalid rule.

Recommended stabilization procedure at the end of the atomic unit:

1. Determine creatures at <=0 and players with health <=0/failed required draw/
   accepted concede from the same resulting snapshot. Record causes and genuine
   creature defeats before elimination cleanup changes the battlefield.
2. Capture applicable simultaneous defeat/departure trigger candidates and last
   known source information. Apply creature departures and leader replacement.
3. Eliminate all losing players as one batch; apply ownership/control cleanup,
   cancel their pending items and ordinary trigger candidates. Capture surviving
   controllers' valid cleanup-departure triggers, not defeat triggers for cleanup.
4. Recompute ongoing modifiers/capacity/attachments and repeat mandatory cleanup
   until stable. Collect event batches in stable recorded order. No response to
   save a creature/player between detection and cleanup.
5. Queue remaining eligible triggers and gather choices before reopening priority.
6. At a quiescent checkpoint (no chain items, pending triggers, required choices
   or mandatory cleanup/boundary expirations), evaluate terminal result: zero active -> draw; one
   active -> win. Otherwise continue priority/phase progression.

Costs also stabilize before responses. If a cost causes its controller to be
eliminated, that controller's newly pending item is removed; paid costs stay spent.
Exact legality of self-lethal health costs is an authored-cost policy still to
approve; the resolver must not guess whether payment is allowed.

## Multi-draw and zero health inside one item

Approved deck-exhaustion revision: attempt required draws in order. Before an
empty-deck draw becomes an unrecovered failure, offer the eligible fixed-life
refill. Successful payment/refill resumes the remaining required draws, then
finishes the current atomic effect. A declined/unavailable refill records the
failed draw and eliminates at cleanup; ordinary later reshuffling does not erase
that recorded failure. Drawing available cards is not rolled back.

On-own-turn refill ends only that turn after pending work; own-turn deck depletion
also requests turn end. An empty next Start offers refill and then ends that turn.
Off-turn refill preserves the active turn and makes the affected player's next
turn Recharge: automatic Start/End processing, no normal draw, voluntary plays or
Combat. Ordinary defense/reactions remain available on other players' turns.
See DECK_REFILL_DESIGN.md for the approved timing, lore and remaining cost/stacking
gaps. No general mid-effect reaction window is introduced.

Health is evaluated at the atomic boundary, consistent with the confirmed rule
that cleanup follows the current effect. Thus damage and healing within the same
item can leave a living player if final health is positive; healing by a later
chain item cannot rescue an already eliminated player. Do not clamp intermediate
signed health in a way that manufactures health. Steve explicitly approved this whole-effect player-health checkpoint on
2026-11-22. It does not permit healing by a later effect after elimination.

Simultaneous combat damage uses one snapshot and resolves all damage before
checking any creature/player. A defeated blocker retaliates. If all players lose
in that batch, no controller gets a final reaction/resurrection window.

## Pending effects, concession and terminal sequencing

When a seat is eliminated, cancel its controlled pending actions/abilities and
ordinary triggers; source ownership is distinct from controller identity.
Surviving controllers' items continue if their remaining targets/instructions are
valid. Reopen normal response windows while valid pending effects remain, even
with one survivor. No new empty-chain main action window delays terminal victory.
This honors the confirmed requirement to finish valid pending work first.

Approved concession rule: a separately authorized confirmed command is processed at the
next safe atomic boundary, not halfway through another item's instructions.
Serialize simultaneous concede requests by recorded command order; do not invent
a simultaneous all-concede draw from arrival timing. A final pending effect may
still eliminate the sole survivor and produce a draw. Steve approved safe-boundary concession and recorded request order on 2026-11-22.

If the active seat is eliminated, finish stabilization and surviving pending
chain/trigger work. Skip its remaining phases (no skipped End triggers), apply
turn-end expirations for that abandoned turn, stabilize again, then advance to the
next active seat if the match continues. Never grant the eliminated seat refill,
leader recovery, actions or private observations.

## Ownership cleanup and duration anchors

Confirmed cleanup removes objects owned by an eliminated player anywhere in play,
and objects they control even when owned by survivors. Surviving-owned borrowed
cards go to owners' discard; eliminated-owned cards go to their inaccessible
zones. Tokens vanish; leaders return to reserve but have no further play. Remove
eliminated controllers' ongoing effects, preserving already granted permanent
bonuses owned by survivors when their grant explicitly survives its source.
Cleanup itself is departure, not destruction/sacrifice. A genuinely lethal
creature in the original event keeps its genuine defeat cause.

Approved 2026-11-22: an until-next-start duration references a scheduled original seat
boundary, not an immortal search for a future active turn. When that eliminated
seat's next scheduled position is crossed, expire its anchored durations once,
without executing a turn/refill/recovery for that seat. Per-turn and next-own-start
usage counters remain distinct. Do not rewrite the anchor to another player's turn.

Cross-owner combined components, attachment compatibility and disassembly HP
ordering remain unsupported until a separate assembly specification. Reject cards
that need those rules in the initial full-match content pack. No approximation.

## Combat integration gate

The legacy resolve_combat API remains the fresh-attack adapter for the lab.
Committed match attacks now pay exhaustion/usage before responses and pass through
combat_flow to the same damage kernel. Private lock/reveal and explicit damage
orders are implemented; see experiments/START_COST_COMBAT.md for evidence.

Approved blocker disclosure 2026-11-22: each defending controller chooses privately
and locks its complete blocker assignment, including an explicit no-block choice.
Reveal all defending assignments together only after every required defender has
locked. A later defender never sees an earlier defender's choices before locking.
Then collect attacker/Challenge retaliation order choices and open the final
reaction window before simultaneous damage/stabilization. No timer is added.

Integration sequence: all attacks committed -> response round -> private blocker
lock batch -> simultaneous reveal -> damage-order choices -> final response round
-> simultaneous damage -> stabilization. Later invalid blockers are removed but
blocked status persists; missing Challenge targets miss. New blockers cannot be
silently assigned during final responses. Server stores locked choices privately;
public projections show neutral waiting information without selected blockers.
An intervening public-state change (e.g. concession cleanup) invalidates the batch
and requires fresh locks before reveal; disconnect pauses and restores choices.
This replaces the earlier proposed sequential public blocker confirmations.

## Acceptance scenarios before enabling full-match mode

| ID | Given / expected |
|---|---|
| T01 | A adds effect; B adds reaction; C/A/B pass -> B's reaction only resolves, then priority resets to A. |
| T02 | New response clears earlier passes; stale-window pass rejects without state change. |
| T03 | Same-event triggers for A/B/C append in chosen seat groups; C group resolves first under proposal. |
| T04 | Simultaneous lethal attacker/blocker both deal damage; neither can react before departure. |
| T05 | A/B lose together, C survives with pending self-damage -> no premature win; C can later lose -> draw. |
| T06 | A loses with own heal pending -> heal removed; no revival. Surviving B-controlled pending heal remains if valid, regardless of source owner. |
| T07 | Draw3 with deck2 -> draw2; eligible paid refill resumes final draw; decline/unavailable refill records failure and eliminates at cleanup. |
| T08 | One item damages then heals A -> evaluate final HP; separate later heal cannot rescue boundary elimination. |
| T09 | A owns creature controlled by B; A eliminated -> card departs; B's valid departure trigger survives. |
| T10 | Eliminated controller's borrowed creature departs to surviving owner's discard; cleanup is not defeat. |
| T11 | Active seat loses in Main; finish valid chain, skip Combat/End triggers, expire turn effects, advance. |
| T12 | Next-start duration on eliminated seat expires at its next scheduled boundary, no refill/recovery. |
| T13 | Zero active seats with no permitted pending work -> draw; last survivor only wins at quiescence. |
| T14 | Save during priority/order choice; reload paused with exact chain/pass/choice IDs and private projections. |
| T15 | Attack declared and exhausted; response removes blocker -> blocked memory survives; correct Breakthrough. |
| T16 | Concede accepted during another atomic effect -> defer to safe boundary; never partially mutate effect. |
| T17 | Numeric prevention fully absorbs damage -> no dealt-damage trigger; attack trigger remains independent. |
| T18 | Loop/step limit is diagnostic incomplete status, never a draw or HP-based victory. |

## Implementation sequence and remaining approval

Priority/reset order, cross-controller trigger order, whole-effect player-health
checks, safe-boundary concession, Start/End boundaries and eliminated-seat duration
anchors are approved. Paid draw-time refill and Recharge timing are approved in
DECK_REFILL_DESIGN.md. Exact life cost and repeat/bypass interactions remain open.
Blocker lock/reveal and subsequent ordering/reaction windows are approved. Self-lethal cost legality is deferred to
an authored-cost specification; reject unsupported cost definitions. Then implement pure match
state/command validation, priority/chain and stabilization with exact fixtures;
only then connect turns/resources, combat and simple hidden-safe policies.
Assembly and complex effects remain behind coverage gates. Every enabled rule
needs tests and a versioned manifest entry; full-match mode stays disabled now.

This draft has a focused Sol consistency review and the owner approvals above.
An Astra review remains recommended before adopting the remaining proposals. It is not a request for a new discovery interview.


## Focused review record — 2026-11-22

Review scope: canonical RULES_DRAFT.md against proposed sequencing; no executable
match engine is claimed. Owner approved the three multiple-choice decisions on
priority/trigger order, whole-effect health checks and safe-boundary concessions.
Other recommendations remain proposals, not implied approval from continuing work.

Clarifications found during review:

- Capture trigger candidates at the event/instruction that causes them, with its
  local pre/post snapshot and source eligibility. Do not make a source that enters
  later in the same item retroactively witness an earlier event. Defer queueing
  and priority until the atomic item and stabilization finish. De-duplicate by
  event/source/ability ID, not by display text.
- A required end-boundary expiration may itself create triggers. Drain them before
  advancing the turn; recheck hand size after consequences, without firing End
  triggers twice. Terminal checks wait for mandatory boundary work.
- Zero declared attacks is a legal combat choice, not a rules draw. No-op combat
  still advances via the normal phase procedure and never resets attack usage.
- Retaliation/damage events are simultaneous, not sequential animation steps.
- Health checkpoint approval concerns player defeat. No implementation should
  infer arbitrary negative-HP creature form/assembly behavior from it; those
  transformation interactions remain behind their separate specification gate.
- In T06, replace ownership shorthand with controller semantics: a surviving
  controller's pending item remains even if its source was owned by another seat.

No approved game rules were changed by the experiment extensions. Review does not
satisfy independent Astra review or replace tests for a future match engine.


Owner follow-up 2026-11-22: Start/End and eliminated-seat duration boundaries approved.
Failed-draw handling and multiplayer blocker disclosure remain undecided pending
requested examples/tradeoff explanation. No approval inferred for either.


Owner follow-up 2026-11-22: approved private simultaneous blocker lock/reveal.
Requested a costly fixed-life discard-to-deck refill mechanic, intended to make
repeat use require deliberate life-gain support. That mechanic is accepted intent;
exact availability, timing and cost remain proposals in DECK_REFILL_DESIGN.md.
No failed-draw forgiveness or automatic reshuffle is inferred from this request.


Owner follow-up: approved completing required draws after paid refill, elimination
when a required draw has no accepted valid refill, and full Recharge maintenance
turns after off-turn refill. An own-turn refill ends only the current turn; it
does not additionally penalize the following turn. DECK_REFILL_DESIGN.md supersedes
the previous Main-only refill proposal and unconditional failed-draw recommendation.


## Implemented foundation (not a full-match engine)
`crucible_core.priority` now implements immutable response-window state, revision-
checked add/pass transitions, exactly-one-item resolution handoff, active-player
priority reset and ordered post-resolution trigger batches. Window reopen retains
monotonic revision/effect IDs. Ten exact tests cover these transitions and illegal
commands. It has no effect evaluator, costs, private projections, eliminated-seat
changes, initial-phase trigger collector, turn/resource state or Recharge. The
future match coordinator must validate legality and atomically resolve/stabilize
items before using the internal finish-resolution transition. Combat-lab coverage
and report claims remain combat-only.


## Turn/draw foundation implemented (still not full-match coverage)
crucible_core.turns now models pure turn-flow and required-draw/refill choices with
explicit experimental policy parameters and recorded shuffle permutations. It
emits failure/end/Recharge intent for a future atomic match coordinator; it does
not implement elimination, Start/End effects or resources. Unresolved repeat/
bypass interactions reject. See experiments/TURN_DRAW_FOUNDATION.md for coverage,
tests, trust boundaries and migration limits. No final refill price is adopted.


## Current implementation status
See PROJECT_STATE.md for the compact checkpoint and
experiments/PRIVATE_VIEWS_HAND_PLAY.md for current command/view/card evidence.
Versioned coordinator coverage is in src/crucible_core/coverage.py; the lab keeps
its separate combat-only report coverage.
