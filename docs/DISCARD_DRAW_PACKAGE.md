# Discard outlet and draw package — proposal v1

The provisional design is now executable in an opt-in practice pack; the default
pack v9 stays unchanged. Launch with `python run_play.py --discard-package`. Card identity, provisional cost, printed wording and count-model inputs
live in `design/packages/discard_draw.json`; generated card/economy tables are in
`experiments/DISCARD_PACKAGE_ECONOMY.md`. Existing gameplay remains governed by
RULES_DRAFT.md. Outlet semantics are canonical in RULES_DRAFT.md.

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
available as the control. The opt-in deck uses this replacement; original v9 saves keep their frozen cards.

## Outlet resolution contract
Canonical behavior is in RULES_DRAFT.md, “Discard-then-draw Actions”.
Implementation evidence and loop findings: experiments/DISCARD_CONTINUATION.md.

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

## Implementation and save support
DiscardThenDraw is a typed atomic instruction with a private required hand-card
choice. Resolution.discard_request identifies the waiting request; discard_done
persists the successful gate across required-draw refill. Registered steps stay
unchanged and the draw cursor advances only once. Commands validate actor, revision,
request and hand membership. UI requires an explicit single selection and disables
confirmation when paused; ordinary handoff gates protect access. The opponent picks
from its own projection and avoids knowingly playing the outlet without fodder.

Save schema v6 / compatibility 1 supports both pauses. Explicit v1-v5 conversion,
original fixture preservation, allowlists and rollback policy: SAVE_FORMAT.md.
The opt-in pack has a distinct ID/hash; default v9 and converted saves never acquire
its cards. Canonical provisional card data remains in the proposal JSON.

## Template and external-LLM handoff
Read CARD_DESIGN.md and the information contract alongside the canonical JSON and
this proposal. Use its exact type, color, cost and rules wording in both layouts.
Keep setup assumptions and implementation notes off the card face. No extra mode,
target picker, free discard action or once-per-turn limit is implied. Names/keys are
proposal identities; set/collector/rarity/illustration details are not release-ready.
The JSON is not renderer-fixture or household-catalog data. No card-art/template
sources or generated design outputs are changed by this package design.
