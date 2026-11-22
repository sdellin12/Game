# Life-for-deck refill — design proposal

Status 2026-11-22: Steve requested the mechanic and strategic goal. Availability,
timing and exact cost are not selected yet. No implementation, balance result or
full-match coverage is claimed. Existing schemas/saves are unchanged.

## Accepted intent

Pay a fixed, expensive amount of player life to reshuffle discard/graveyard cards
into the deck. A second use in one game should require deliberate life generation.
This is a health/resource strategy, not player revival or free discard recycling.
The fixed cost should not silently escalate each use or impose a once-per-game
cap; either would change the requested repeat-use design.

## Recommended first candidate (awaiting choice)

A standard action available to every surviving player during their own Main phase
with an empty chain. Confirm the action, pay 20 life, then queue the refill so
opponents have normal reaction opportunities. Require health strictly greater
than the cost so payment leaves at least1 HP. The discard must contain at least
one eligible card. A failed required draw cannot be undone by this action.

At resolution, move eligible ordinary cards from your current discard into your
remaining deck and shuffle together. Do not touch hand, exile, leader reserve or
another player's zones. Cards discarded in response are included; cards removed
from discard in response are not. Existing deck need not be empty. No immediate
draw is included. The 20-life payment is a cost, not damage: prevention does not
pay/reduce it. Costs remain spent if the effect is negated or its discard becomes
empty. Initial content should not alter this fixed life cost.

This recommendation makes refill a planned main-phase action. An empty deck can
still be lethal when an opponent forces a draw before your next Main, preserving
an answer for milling. A low-deck warning can help young players remember without
automatically spending their life or exposing private cards.

## Why test20 with starting/max30?

- First use: 30 ->10 HP. This creates a serious immediate combat risk.
- A second use needs at least21 HP: from10, recover at least11 before paying again.
- After a second use at21, only1 HP remains. Comfortable repeat use needs more.
- Candidate15 permits a second use after only1 healing (30 ->15 ->heal1 ->16 ->1),
  which is weaker pressure than Steve's requested deliberate life-gain investment.
- The recurring sustainable threshold is not just11: over repeated cycles the
  strategy needs20 net life per refill plus enough to offset incoming damage.

These are arithmetic illustrations, not evidence that20 is balanced. Healing
remains rare/expensive outside dedicated styles and caps at30. Universal strong
healing should not be introduced solely to make repeat refill easy.

## Other selectable implementations

1. Card/leader ability: refill requires a legal authored ability with explicit
   timing/cost. More deck commitment and potential color/style identity, but a
   deck missing that enabler cannot use the mechanic; repeat access can loop.
2. Emergency empty-deck prompt: immediately before a required draw would fail,
   offer payment and refill. Easier to remember, but introduces a new choice
   inside atomic draw resolution and weakens milling. Must explicitly specify
   draw-N mid-effect behavior, no-discard handling, response timing and payment
   legality. Do not implement this as an accidental exception to elimination.

## Required evaluation before adopting a cost

Compare provisional15/20/25 under the SAME future full-match rules. Freeze each
candidate within an experiment; do not tune until a favored deck wins. Include:

- Simple attacking decks vs defensive life-gain/refill decks and milling pressure.
- Time to finish, repeat-refill count, effective life spent/gained, card reuse,
  decisions per turn and incompletion/loop rate; not just victory counts.
- Opponents forcing draws while empty, negating refill after payment, removing
  discard cards, responding with damage, and recovery cards recycled by refill.
- Multiple policy styles and seat rotation. The present combat lab cannot measure
  any of these full-match outcomes yet; never label them as completed tests.

## Future exact fixtures

| Case | Recommended standard-action expectation |
|---|---|
| Health30, cost20, discard nonempty, own Main/empty chain | Pay to10, queue refill; no automatic draw. |
| Health20 or lower | Reject unchanged; never pay down to0 to create a revival path. |
| Outside Main or pending chain | Reject ordinary action; special exceptions require explicit cards. |
| Discard empty when confirming | Reject without payment. |
| Discard emptied in response / effect negated | Payment remains; no cards recovered. |
| Deck contains cards | Mix eligible discard into remaining deck, then shuffle uniformly. |
| Cards in hand/exile/leader reserve | Unchanged. |
| Tokens in invalid zones | Reject invalid state; no token cards added. |
| Required draw already failed | Refill cannot erase that failure under the proposed failure rule. |
| Save before/after refill resolution | Pinned shuffle/random outcomes replay identically; public count, private order. |

## Implementation gate and rollback

Choose availability/timing first, then settle failed-draw policy. Standard action
needs an explicit registered command, health-cost transaction, eligible-zone
movement, reaction chain, deterministic shuffle and checkpoint/replay fixtures.
None are present in the combat-only lab. Do not add a standalone simulated refill
that forks future game rules. Preserve old content/schema defaults; any future
saved-match change needs versioning, compatibility tests and a migration plan.
Until approval, keep this document as a proposal and existing engine unchanged.
