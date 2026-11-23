# Discard outlet and draw package — proposal v1

This is an implementation-ready card-design proposal, not a live practice-pack
change. Card identity, provisional cost, printed wording and count-model inputs
live in `design/packages/discard_draw.json`; generated card/economy tables are in
`experiments/DISCARD_PACKAGE_ECONOMY.md`. Existing gameplay remains governed by
RULES_DRAFT.md. New outlet semantics below are proposed for the next engine slice.

## Purpose and deck use
The preceding DISCARD_STRATEGY study found that waiting for End discards gives up
plays before rewards arrive. Scrapyard Insight creates one intentional hand discard
without requiring a hand above seven. Surveyor's Notes grows the hand for later
plays/outlet fodder. Deep Archive provides a larger refill when the board can afford
the higher upfront payment. All are Generic Actions, use ordinary own-Main timing,
and keep forty-card singleton deck construction. No new keyword is needed.

Use existing Battery/Well as payoff cards, not prerequisites to playing draw
support. Lantern improves resource efficiency but is not required. Establish a
defensive board before spending turns on engines. When possible, sequence Notes
before Insight to improve discard selection; do not hold an otherwise useful board
play solely to reach the hand limit. Support draws can naturally create End excess,
while Insight is card-neutral before cleanup when its discard succeeds.

For the first opt-in test deck, replace the three remaining plain capacity
permanents (Beacon Tower, Sun Engine, Crystal Reservoir) with one of each proposal.
This preserves forty distinct cards and the 24-creature defensive core. It also
removes six ongoing capacity, so compare the whole package as a deck change; do not
attribute every result to the outlet alone. Keep pack v9 and its original hashes
available as the control. No changes to the live deck are made in this step.

## Outlet resolution contract
1. Confirm/pay the ordinary resource cost and put the Action publicly pending.
   The pending Action is not in hand and cannot be its own discard choice.
2. Opponents respond normally before resolution. Negating the Action prevents
   its instructions; payment stays spent. There is no separate discard cost.
3. On resolution, if the controller has a hand card, privately choose exactly one
   from the current hand. Require the correct actor, request/revision and current
   hand membership. Do not pre-lock a card at play time or expose tentative choices.
4. Commit the chosen card publicly to its owner's discard, capture actual hand-
   discard triggers, then draw two. The discard is mandatory when possible; there
   is no optional cancellation or response between that discard and the draws.
5. If no hand card exists at this instruction, discard nothing and skip both draws.
   Playing the Action as the last hand card is legal but produces no draw/reward.
   This is a failed conditional instruction, not a failed required draw.
6. Complete required draws under the existing paid-refill/Recharge rules. A freshly
   discarded card can be in the refill pool; the still-pending Action cannot.
   Keep the completed-discard gate and draw cursor across any private choice/refill
   pause. Never discard or draw twice after load/retry. Finish later instructions
   and pending-card movement at the engine's existing atomic boundaries.
7. Captured discard/draw triggers wait for atomic completion, including refill
   decisions, before optional choices/order/priority. Existing End cleanup still
   checks the actual hand. Ordinary Action movement to discard is not a hand discard.

For example, with a five-card hand, playing Insight leaves four, discarding leaves
three, and two completed draws return the hand to five. Battery captures one
discard reward, Well one optional capacity reward, and Lantern two optional draw
rewards. No source can contribute resources to the initial cost from future rewards.

## Economy and loop review
The generated planner checks hand/resource conservation, the seven-card End cap,
upfront affordability and short-deck continuation across 13,200 count combinations.
It accepts all optional rewards for the illustrated ceiling, assumes no responses
or intervening plays, and excludes source setup costs. It does not simulate card
identity/selection, combat, life/refill choices, random draws, sequencing or win rate.
Short-deck cases stop at the engine continuation boundary instead of inventing a
successful refill or awarding pending triggers early.

Insight plus one Lantern/Battery can refund three after paying two, and Well can
add one capacity per successful use. This is intentional synergy to test, not proof
of a safe cost. Singleton limits are insufficient as a loop safeguard: Second Chance
can recover Insight. Its own pending copy cannot recover itself, and the outlet
still needs fodder and a complete required draw; audit additional recovery effects
before expanding this package. Do not add an arbitrary runtime iteration cap.
Use full engine tests for repeated recovery, all-engine resource gains, refill
recycling and terminal/concession boundaries before enabling the new outlet.

Keep provisional costs until matched-seat playtests compare both package/control
decks and baseline/package-aware policies. Rotate the experimental seat across
2/3/4-player games and record engine access, completed outlet uses, reward delivery,
card/resource spending, board losses and refill/Recharge penalties. Avoid interpreting
only total match duration as the experimental player's survival time.

## Implementation and save plan
The two pure draw Actions already fit existing DrawCards instructions. The outlet
needs a typed required hand-discard instruction with a conditional draw continuation,
a private resolution-choice projection/command, actor/revision validation, UI handoff
and permitted-view policy handling. Choices during an atomic effect must stay
separate from the post-effect optional-trigger barrier.

Before model changes, record a schema/rollback plan in SAVE_FORMAT.md and archive
native-v5 saves, including partial optional decisions and partial refill. A new
continuation field needs an explicit new schema and converter defaults; do not
silently add fields to v5 snapshots. Preserve frozen packs, original files/hashes,
event/request IDs and exact next-command outcomes. Old saves must not acquire these
cards. Keep original runtime/saves for rollback; publish any conversion separately.

Acceptance checks: pending Action cannot be discarded; last-card no-op; negation
before choice; wrong/stale/private-choice rejection; actual discard captures exactly
once; chosen card legal in refill; pending source excluded; partial draw resumes
once; End hand-limit recheck; elimination/concession cancellation; mixed trigger
privacy/order; paused save/load and conversion; spectator/computer projections.

## Template and external-LLM handoff
Read CARD_DESIGN.md and the information contract alongside the canonical JSON and
this proposal. Use its exact type, color, cost and rules wording in both layouts.
Keep setup assumptions and implementation notes off the card face. No extra mode,
target picker, free discard action or once-per-turn limit is implied. Names/keys are
proposal identities; set/collector/rarity/illustration details are not release-ready.
The JSON is not renderer-fixture or household-catalog data. No card-art/template
sources or generated design outputs are changed by this package design.
