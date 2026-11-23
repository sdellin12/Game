# The Crucible — Rules Baseline and Implementation Gaps
Consolidated 2026-11-22. Accepted design choices below; numbers provisional, untested. No revival, universal defense stat or unrestricted full-bypass rule. Working keywords Challenge/Breakthrough are not final names.

## Setup and turn
40 singleton + leader; single color/generic; five opening, one partial redraw (replace before shuffling rejects). Counts revealed together after lock; start/order revealed after redraw. Lobby selections openly visible, lists private unless shared; all legal decks/leaders ready before start. Start random, then fixed order.
Start -> Draw -> Main -> Combat -> Main -> End. Combat optional. Ordinary cards and voluntary transform/combine during own main with no pending effects; explicit exceptions. Start readies eligible objects, recovers leader, grows/refills resources and handles start effects; exact within-Start trigger/priority ordering still requires engine specification. Draw1; first starter skips first draw in duel, all draw in multiplayer. End effects then discard to seven; no new ordinary-play window from discard.

## Payments/resources
First turn2; natural base +1 each subsequent own turn capped10. Card-granted permanent bonus tracked separately, can exceed10. Refill current total at turn start; unspent remains through opponents. Growth increases capacity now but available resource only on next refill unless explicit immediate resource grant. Ongoing capacity bonuses require source; permanent grants survive source. Losing capacity doesn't remove already available resources.
Public stored resource tokens consumed directly toward any legal payment, usable immediately incl reactions, not capacity. Controller-only unless explicit assistance. Ordinary resources first suggested, adjustable preconfirm; exact pay, no voluntary excess without card option.
Targets/modes/X/costs selected and locked at confirmation; pay before responses. No refunds for negation, invalid targets or failed assembly. X can0 unless minimum, discounts reduce payment not chosen X. Resource costs floor0 unless minimum. Non-resource costs unchanged unless explicit. Add ordinary increases/subtract discounts but leader accumulated resummon increase cannot be discounted. Full cost required even above10.
Sacrifice as cost immediate, cannot rescue afterward; counts defeat. Negating effect doesn't undo payment. Exile/bounce/shuffle aren't defeat. Effects may explicitly prevent beforehand or recover afterward.

## Responses, abilities and triggers
Reaction card class uses normal resources at response opportunities incl own turn. Newest pending first, reopen response after each resolution. Everyone passes/responds in fixed order; chosen autopass settings allowed, optional pause with no legal card to avoid timing leaks; no timers. Approved priority: active player starts a window; after a new item priority goes to the next active seat after its controller; all-seat consecutive passes resolve one newest item; after resolution priority resets to the active seat (or next surviving seat). New items clear passes. See FULL_MATCH_TIMING_SPEC.md for the approved sequence.
Abilities manual activation, legal highlights/prompts with preview; no automated spending. Reusable when legally able to pay, unless stated limit/timing. Exhaust-cost creature ability waits like attack unless haste-like permission; non-exhaust abilities can act immediately if legal. Temporary haste grants eligibility only, not ready/extra attack. Source leaving doesn't cancel already-pending ability.
Triggered effects mandatory unless may; autoqueue mandatory, optional Use/Skip. Suggest own simultaneous trigger order with Confirm/Adjust; suggestion uses authorized information. Approved cross-controller order: active seat first then surviving seats in turn order, appending each controller's chosen oldest-to-newest group; the last group resolves first.
Negation selective/expensive, broad negate rare; no automatic numerical price. Paid costs and activation limits spent if negated. Transform/control/combine/separate don't reset spent inherited uses. Per-turn distinct from once between own starts, explicit card wording; exact identity mapping across distinct form abilities needs engine spec.
Invalid targets fail if none valid, no refund; independent effect portions resolve where possible (custom rule, not wholesale import of Magic). Spell/ability semantics structured, not generated prose.
Effect-copy rules reserved future starter scope: inherits X without payment, original targets unless explicit retarget, independent of original negation, not card play. Newly created creature-copy tokens distinct.

## Combat
Only ATK/currentHP/maxHP; wounds persist. Attack floor0; zero-ATK may block/activate. Summoned/newly controlled wait until next controller turn to attack/exhaust unless permission; block immediately. Control change doesn't ready/heal/reset uses.
One combat, all attacks declared together, each creature once unless explicit extra attack. Different attackers may target different players. Attack exhausts. Each blocker blocks at most one attacker per combat unless explicit; several blockers may block one. Block doesn't exhaust; exhausted can block, receiving ceil(1.5*assigned damage) BEFORE prevention. Only blocking creature gets this modifier, not exhausted attacker/Challenge target.
Attacker chooses blocker order; automatic smallest lethal raw allocations through blockers, use current health/modifiers/prevention. Retaliation all blockers pooled against their one attacker, simultaneous. No source laundering across unrelated attacks; per-source triggers attribution unresolved.
Breakthrough: excess raw attack after lethal allocations to all blockers hits defending player. Without it no excess hits player. Attack stays blocked after blockers removed; only Breakthrough carries through even when none remain. Multiplier bonus never becomes extra player damage.
Challenge: qualified creature chooses enemy creature instead of player, same declaration/combat and normal attack use; no intervening blockers, retaliation simultaneous, no player overflow/Breakthrough and no exhausted-blocker penalty. Reactions before damage. Missing target -> miss, spent attack/exhaustion, no retarget. Challenged creature cannot also block. Multiple challengers combine damage; target retaliates once distributing by its controller's order. Multiple fights/source order needs engine-ready sequence.
Assistance ordinarily defense for oneself; special cards enable helping another, recipient may decline. Gold benefits bounded, meaningful help; no reward from empty offers/loops.
Damage zero after prevention does not trigger dealt-damage; attack triggers independent. Player health is checked after the whole resolving effect: damage followed by healing inside that same effect may leave a surviving player; a later effect cannot revive an eliminated player. After current effect/combat atomic resolution, <=0 defeated before new responses; simultaneous defeated creatures deal their damage and witness applicable simultaneous defeat triggers.

## Card play zones - approved 2026-11-22
Confirmed hand cards become public pending cards alongside their effects. Actions
and Reactions enter their owners' discard after resolution or negation, so a card
cannot refill itself during its own effect. Creature/persistent cards enter the
battlefield only on resolution. Cancelled pending cards go to owners' discard.
Exile is a separate public zone: ordinary exiled cards retain their owners and
stay outside discard/refill unless an effect explicitly moves them elsewhere.
Exiled card identities remain public after their owner is eliminated. Exiling
a creature discards its attachments to their owners; token/leader replacements
follow the existing token and leader removal rules.
Discard-to-hand recovery chooses a card in your own discard at confirmation and
checks that it is still there when the instruction resolves. The recovered card
is publicly identified and enters your hand; playing it requires a separate legal
play and payment. Recovery does not use exile, pending cards, or eliminated players'
cards. A missing recovery target does not cancel independent effect instructions.

## Healing/protection/upgrades
Healing stops max; unused excess no benefit unless explicit. No initial overheal, future expensive effects deferred. Player max30 initially, healing very rare/expensive except dedicated style; creature healing separate.
Health boost increases current+max by stated amount; when boost/health-upgrade lost, preserve currentHP capped new max (not subtract wounds), expiration alone not defeat. Same boost doesn't stack repeatedly unless explicit.
Prevention consumes stated amount, unused stays until explicitly stated expiry. Add compatible numeric shields, earliest expiry used first. No universal armor; card effects explicit. Breakthrough must account for shields; ready3HP+2 prevention takes5 raw lethal. Exhausted multiplier then shield, e.g. raw4 ->6 ->minus2 =4HP damage. General pipeline/source ordering needs formal fixtures.
Upgrades persist attached; temporary effects explicit until-this-turn-end vs next-own-start etc. Creature leaves -> upgrades owners' discard unless exception; hand/discard reentry fullHP clears battlefield effects/assignments normal attack wait. Cosmetic identity unchanged.
Transformation stays in play; no enter/leave triggers, retains readiness/compatible upgrades, incompatible discard. HP percentage preserved, roundUP immediately, whole number actual/display, no hidden fractions. Max changes from boost loss use separate cap rule.
Voluntary transform once creature/turn unless explicit, own Main empty chain, response allowed. Trigger transform at event via chain, named destination; already there no-op. All public linked forms/costs inspectable.
Rounding can heal on repeated form changes: confirmed round-up remains; test loops and constrain authored costs/limits. Once/turn doesn't completely eliminate inter-turn gain.

## Combination
Own distinct assembly status, no ordinary entry/departure/defeat merely from combining. Components require names/traits/mix, controlled at resolution; up to2 labels/creature, no inherent tag abilities, validated not art-inferred.
Combined form outside40 accessible via requirements, not draw; defined own ATK/maxHP/traits (normally<=2), not automatic sum. HP=ceil(combinedMax * sum component currentHP / sum component maxHP).
Any exhausted component -> exhausted; all must be attack-eligible for immediate attack. Preserve used attacks/ability limits. Combined own abilities plus explicit inherited; component defeat abilities remain relevant on destruction. Public form/requirements/components inspectable. One assembly level initially; designated leaders cannot participate; ordinary character versions may.
Compatible upgrades carry/apply once; compatibility and maxHP operation ordering still needs deterministic definition.
Combine own Main empty chain, opponents respond. Missing/no-longer-controlled required component -> fail, remaining separate, paid costs spent.
Destroy combined -> all components destroyed/defeat abilities + form's applicable defeat ability, except explicit survival. Bounce -> separate to owners' hands, token components disappear, upgrades discard. Exile all components, tokens disappear, no defeat triggers.
Separate in battle only explicit effect, each component receives ceil(componentMax*combinedCurrent/combinedMax); exhaustion/attack/usage restrictions carry. All attached upgrades discarded on disassembly. Pin exact order of removing upgrades vs HP calculation in engine spec before implementation.
Copy combined form -> no component cards, cannot separate. Ordinary copies printed current-form stats/traits/abilities, not boosts/upgrades/wounds; new copies tokens default fullHP/attack wait, no transform unless explicit alternate forms. Leaders uncopyable. Cosmetic source look match-only, no unlock.

## Leaders
One designated leader outside40. Distinct full art reserve/battle labeled. Initial starters one reserve/one battle ability; individually explicit timing/costs/limits, normal resource pool incl tokens. Reserve-only stops while summoned unless both locations marked. Outside battle not normal creature/attack target; abilities normal responses.
Summoned leader challengeable, cannot copy/change controller. Transform allowed, no combine.
Removed battlefield to hand/discard/exile/deck -> reserve always, reset starting form/HP/battlefield effects, upgrades discard. Default cumulative+2 next summon per battlefield removal; full cost, no discount to accumulated increase, lasts match unless explicit reset; leader-specific formulas/sac/exile permitted. Exact custom card formulas not selected.
Every removal recovery until own next start; outside abilities disabled and resummon forbidden until then. Main empty-chain summon, negatable. Negated summon remains reserve, spent costs, no extra increase/recovery, retry same turn if can pay. Recovery/cost public.
Transform changes don't reset spent limits. Leader special reserve replacement doesn't make every removal a defeat: actual removal reason needed for triggers.

## Permanent elimination (supersedes ALL revival history)
30HP; health<=0, unrecovered failed required draw, or concede removes permanently. No player revival. After valid pending effects/cleanup last active wins, simultaneous all-out draw. Use the reviewed atomic terminal checkpoints alongside the trigger queue; do not award winner midway through simultaneous processing.
All battlefield objects controller owns/controls cleared: ordinary nontoken cards to owners' discard, resource/creature tokens disappear, leaders reserve (no ordinary play after eliminated); cards OWNED by eliminated player elsewhere also leave play. Borrowed creatures they control go owners' discard, same for concede. Exact handling combined cross-owner components remains gap.
Their pending actions/ongoing effects removed, paid costs stay spent. Surviving players' pending effects resolve if valid. Eliminated controller ordinary triggers removed, explicit elimination exceptions only. Surviving departure triggers applicable; cleanup is departure not defeat/sacrifice. Actual same-event creature lethal defeats still genuine.
Own-turn elimination: finish current effect/defeat processing, other valid pending effects, skip remaining phases, cleanup expirations then advance; skipped End phase triggers don't occur.
Previously-created permanent capacity remains recorded but unusable after permanent elimination. No continuation/refill/recovery due eliminated skipped seat. Temporary until-next-start effects from surviving sources referencing eliminated turns require bounded expiry convention; prior next scheduled seat expiry rule is historical baseline to formalize.
Spectate public only, emoji yes; no private opponent info. No parent approval needed concede, confirmation prevents mistap. Confirmed concessions wait for the current atomic effect to finish, then process at a safe boundary in recorded request order. Disconnect is pause/reconnect, not elimination.

## Remaining engineering specifications, not more micro-interview
- Implement approved priority/reset and cross-controller trigger order; precise event/source attribution still needs implementation fixtures.
- Atomic defeat/terminal checkpoints, multi-draw and simultaneous player/creature defeat.
- Challenge/group combat interactions and deterministic damage/prevention allocation, tie ordering.
- Combined upgrade HP/compatibility/order, effect links/cross-owner cleanup.
- Zero-cost/repeat triggers/rounding loops; explicit card bounds, no arbitrary unmarked runtime rule.
- Mechanics coverage manifest: unimplemented rules fail validation; partial simulator never reports full rules coverage.
- Costs beyond initial profiles, ability budgets, vulnerability roster and starter packs remain tests/proposals.
Use meaningful test fixtures and specialist recommendations; ask user only consequential experience/rule tradeoffs. A combat-only subset now has exact fixtures and finite encounter enumeration; no full-match balance simulation or family testing performed. See COMBAT_LAB_QUICKSTART.md for implemented coverage and explicit experimental assumptions.


## Timing specification: approved portions and remaining proposals
[FULL_MATCH_TIMING_SPEC.md](FULL_MATCH_TIMING_SPEC.md) proposes concrete priority,
trigger, atomicity, elimination and combat-window sequencing with acceptance
fixtures. Priority/reset, cross-controller trigger order, whole-effect player-health checks and safe-boundary concession were approved by Steve in Codex on 2026-11-22. Remaining proposed defaults are not confirmed gameplay rules. Review/approval
is required before enabling a full-match engine; current combat rules above remain
unchanged.


Approved boundary sequencing (2026-11-22): Start expires next-start effects, resets
usage/readies, recovers leaders, grows/refills resources, then handles Start
triggers. End resolves triggers/responses, enforces seven cards, then expires
effects and handles their consequences before advancing. Durations anchored to
an eliminated seat expire at its next original scheduled boundary without
executing that seat's turn, refill or recovery. See FULL_MATCH_TIMING_SPEC.md.


## Approved blocker disclosure and deck-refill design intent (2026-11-22)
Multiplayer defenders select/lock complete blocker assignments privately; reveal
them together after every required defender locks, then choose damage orders and
open the final reaction window. Explicit no-block choices are part of the lock
batch. There is no timer and no early disclosure to later defenders.

A costly fixed-life payment to shuffle discard/graveyard cards back into the deck
is requested. Repeat use should require a deliberately life-generating deck.
Timing is approved below; cost and advanced repeat/bypass interactions are not
yet adopted. See DECK_REFILL_DESIGN.md for evaluation and implementation gates. No free automatic
reshuffle or player revival is approved; the paid draw-time exception below applies. Player max30 and no
player revival remain unchanged.


## Approved deck exhaustion / Recharge revision
Before a required empty-deck draw fails, offer a valid fixed-life refill. Draw
available cards first; successful refill completes remaining required draws.
Declining/unavailable payment/refill makes that required draw fail and eliminates
the player at atomic cleanup. Finish the current effect before turn progression.
Own-turn deck depletion ends that turn after current/pending work; an empty next
Start offers paid refill and then ends that turn with no normal draw/Main/Combat.
An own-turn refill ends only the current turn. Off-turn refill leaves the active
turn intact and makes the affected player's next turn Recharge: automatic Start
and End/mandatory effects, no normal draw or voluntary plays/abilities/Combat.
Blocking/reactions work normally on other players' turns. Explicit future mechanics
may bypass the penalty. Cost20 is only a test candidate; repeat-penalty stacking
and bypass interactions still need specification. See DECK_REFILL_DESIGN.md.
