# Deck exhaustion, life refill and Recharge

Status: owner-approved timing/design direction, 2026-11-22. Exact life cost is a
balance candidate, not adopted. The restricted match harness implements the approved timing; current saved-state
compatibility is in SAVE_FORMAT.md. This design note does not establish balance. This supersedes the earlier Main-phase-only proposal.

## Approved rules and implementation
Canonical refill/exhaustion/Recharge timing is in RULES_DRAFT.md, including the
paid-refill exception and atomic defeat boundaries. The implementation is in
crucible_core/turns.py and match.py; tests/test_turns.py, test_match.py and
test_effect_discard.py exercise payment, continuation and turn penalties. Do not
implement a separate simulator-only refill interpretation.

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
Recharge terminology and the child-facing Core explanation live in Game_Lore.md.
Prompts must show the actual life cost and turn consequence before payment, without
implying revival or free reshuffling.

## Required evaluation

Compare frozen candidate costs under the same explicitly covered match rules. Include
simple aggression, defensive life-gain/refill and milling policies, multiple seat
orders, turn count, lost turns, life spent/gained, repeated refills, reused recovery
cards, and loop/incompletion rates. Test how a depleted player's first lost turn
plus a later Start refill costs another turn; this can be punishing for a child.
No combat-only result establishes these outcomes or a balanced refill price.

## Regression cases and explicit gaps

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

Still gated beyond the provisional test policy: exact cost/payment floor; whether several
off-turn refills before the same next turn accumulate multiple Recharge turns;
mandatory draw/refill during a Recharge turn; and explicit penalty-bypass wording.
Do not invent stacking or bypass behavior from the placeholder lore. Initial
content requiring those unresolved interactions must remain unsupported until
specified. Self-lethal health costs elsewhere remain a separate authored-cost rule.

## Implementation and rollback gate

Implement only in the reusable full-match engine: draw cursor/remaining count,
refill decision, atomic health payment, zone movement, pinned shuffle, turn-end
request and Recharge obligation. Keep this out of an independent simulator-only
mini-engine. The combat-only lab does not model this procedure; the separate practice coordinator does.
Current private saves and compatibility fixtures follow SAVE_FORMAT.md; future
model changes need their own migration/rollback plan. Lab checkpoint schemas are separate.
Retain old experiment builds; never relabel old failed-draw semantics as new rules.
