# Deck exhaustion, life refill and Recharge

Status: owner-approved timing/design direction, 2026-11-22. Exact life cost is a
balance candidate, not adopted. No full-match engine, saved-match schema change or
balance result is claimed. This supersedes the earlier Main-phase-only proposal.

## Approved rules

1. Refill is a standard deck-exhaustion procedure, not dependent on a specific
   card/leader. Pay a fixed, expensive amount of player life and reshuffle the
   discard/graveyard into the deck. Repeated use should require deliberate life
   generation; no escalating cost or once-per-game cap is adopted.
2. Required draws happen in order. If drawing3 with only2 cards, draw those2,
   offer payment/refill before the third draw fails, then complete the third draw
   after successful refill. Finish the effect already resolving. This is an
   explicit choice inside draw resolution, not player revival after elimination.
3. If a required draw cannot be completed and the player cannot or declines to
   pay for a valid refill, eliminate that player at the normal atomic cleanup
   boundary. Drawing available cards is not rolled back. An empty discard cannot
   supply a refill. Ordinary later deck recovery does not undo an unrecovered
   failed draw that was already recorded.
4. When a player's deck becomes empty during their own normal turn, request an
   end to that turn after the current effect/pending work. No further ordinary
   voluntary actions are allowed. If there are unfinished required draws in the
   current effect, apply the refill procedure above before ending the turn.
5. If the deck remains empty without an unrecovered required-draw failure, that
   player can pay/refill at the start of their next own turn. That turn then ends
   without a normal draw, Main or Combat. If payment is declined/unavailable,
   the normal required draw cannot be completed and elimination follows.
6. A refill during your own turn consumes only that current turn. It does NOT
   also make your following turn Recharge. This includes refill at your own Start.
7. A refill during someone else's turn leaves that active player's turn intact.
   The refilling player's next turn is Recharge (placeholder name): automatic
   Start recovery/resource refill and End cleanup occur, but skip the normal draw,
   voluntary cards/abilities and Combat. Mandatory effects still resolve. That
   player can block/react normally on other players' turns.
8. A future explicitly authored mechanic may bypass the turn-ending/Recharge
   penalty. No generic bypass exists and no bypass card is implemented yet.

At an exhausted Start, complete the automatic Start boundary/mandatory work and
offer refill before the required normal draw. An own-turn end request does not
truncate a resolving effect or erase surviving pending effects. Drain mandatory
work and other players' valid responses, then process End triggers, hand-limit
and expiration cleanup once. Required choices can still be answered; no new
voluntary play/ability window is created for the player ending their turn.
Recharge is a real turn for scheduled Start/End boundaries and duration anchors,
not permanent elimination or skipping all maintenance. No extra normal draw is
awarded merely for paying at Start. A draw explicitly required by a mandatory
trigger/effect is distinct from the skipped normal turn draw.

This is a narrow refill choice within an atomic item; no general reaction window
opens halfway through an effect. The original effect already had its normal
response opportunity. Future prevention/replacement effects must be explicitly
specified, not approximated as an interruptible Main-phase refill spell.

## Eligible cards and provisional payment contract

Move eligible ordinary cards from the player's discard into their remaining deck
and shuffle together. Preserve hand, exile, leader reserve and other players'
zones. Tokens are not persistent deck cards. No bonus draw is added; only finish
required draws already pending. Uniform shuffle must use pinned recorded RNG.

Candidate cost:20 life, payable only with health strictly greater than20, leaving
at least1. Payment is a cost, not damage; prevention does not absorb it. The price,
payment floor and any future cost modifiers still need adoption/evaluation.
Existing player maximum30 and rare/expensive healing outside dedicated styles
remain. No universal strong healing is introduced solely to support refill.

At max30, candidate20 leaves10. Another payment would need at least21 health, so
recover at least11 first; repeated sustainable cycles require20 net life per
refill plus incoming damage. Candidate15 would permit a second refill after only1
healing. These are arithmetic illustrations, not evidence of balance. Adding a
lost turn is a substantial extra cost: compare provisional15/20/25 with the turn
penalty in place before adopting20. Owner selected timing, not a final price.

## Lore and presentation

Placeholder name: **Recharge**. The Researcher's Vanguard Core spends their life
energy gathering unraveled Sparks from the discard and rebuilding its supply.
The Core must stabilize before it can shape new creatures or launch another
attack. On their own turn, this consumes the rest of that turn; on an opponent's
turn, stabilization occupies their next turn. Existing creatures can still defend
and the Researcher can react during opponents' turns.

Child-facing wording: "Your Core needs a recharge. Spend life to shuffle your
discard back into your deck. Finish your draws, then rest this turn. If you
recharge on another player's turn, rest on your next turn instead."
Start-turn prompt must clearly say "Refill, then rest this turn" and show actual
cost/remaining HP. Own-turn depletion warning says "Your deck is empty. Your turn
will end after this effect." Do not silently auto-spend life or imply revival.
No card, resource payment or upgrade is refunded by the fictional Spark recovery.

## Required evaluation

Compare frozen candidate costs under the same future full-match rules. Include
simple aggression, defensive life-gain/refill and milling policies, multiple seat
orders, turn count, lost turns, life spent/gained, repeated refills, reused recovery
cards, and loop/incompletion rates. Test how a depleted player's first lost turn
plus a later Start refill costs another turn; this can be punishing for a child.
No combat-only result establishes these outcomes or a balanced refill price.

## Future fixtures and explicit gaps

| Case | Expected timing |
|---|---|
| Own effect draw3, deck2, payment legal | Draw2, pay/refill, draw1, finish effect, end current turn only. |
| Required draw exhausted, no valid payment/refill | Record unrecovered failure; eliminate at cleanup; no later revival. |
| Own draw1 consumes last card exactly | No failed draw; finish effect/pending work, end turn, offer Start refill next own turn. |
| Own Start empty, accepts refill | Automatic Start work, pay/refill, no normal draw/Main/Combat, End maintenance. |
| Own Start empty, declines/cannot pay | Required draw fails; elimination, not an endless empty-deck stall. |
| Off-turn forced draw exhausts deck and refill succeeds | Finish required draws/effect, leave active turn intact, next own turn Recharge. |
| Recharge turn | Start/End maintenance and mandatory effects, no normal draw/voluntary plays/Combat. |
| Opponent attacks before/after Recharge turn | Ordinary blocking/reaction rules still apply. |
| Health-cost/modifier/recovery loop | Explicit cost legality and loop diagnostics; never silently award a draw. |
| Saved pending refill/Recharge | Restore exact choice, draw remainder, penalty state and pinned RNG; no second payment/draw. |

Still to specify before implementation: exact cost/payment floor; whether several
off-turn refills before the same next turn accumulate multiple Recharge turns;
mandatory draw/refill during a Recharge turn; and explicit penalty-bypass wording.
Do not invent stacking or bypass behavior from the placeholder lore. Initial
content requiring those unresolved interactions must remain unsupported until
specified. Self-lethal health costs elsewhere remain a separate authored-cost rule.

## Implementation and rollback gate

Implement only in the reusable full-match engine: draw cursor/remaining count,
refill decision, atomic health payment, zone movement, pinned shuffle, turn-end
request and Recharge obligation. Keep this out of an independent simulator-only
mini-engine. No such engine is enabled by the current combat lab.
Future saved state needs versioned fields/defaults, compatibility fixtures and a
migration/rollback plan. Existing report/checkpoint schemas are untouched now.
Retain old experiment builds; never relabel old failed-draw semantics as new rules.
