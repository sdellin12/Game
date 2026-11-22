# Filled card content examples — shared template pack

Purpose: concrete content for independent standard/full-art template work.
The shared CARD_INFORMATION_CONTRACT.md was approved by Steve on 2026-11-22.
Every example below supplies ONE content set to render unchanged in both styles.
Illustration briefs describe placeholders; no artwork or visual layout is created.

These are non-canonical EXAMPLES, not a published starter pack, legal deck, effect
registry or balance result. Names, trait vocabulary, new abilities, stats and costs
are illustrative candidates. Only the ability-free numeric profiles noted below
reuse existing approved test candidates (which themselves are not proven balanced).
Do not import these into the engine/catalog without a later content/schema task.
Example labels EX-01 etc. are document references, not proposed production IDs.

## EX-01 — Ability-free creature

| Content | Value |
|---|---|
| Name | Clockwork Pup |
| Color identity | Generic, with explicit Generic text/symbol |
| Type | Creature |
| Play cost | 2 resources |
| Illustration | A friendly wind-up puppy with a bright brass key; clear silhouette. |
| Traits | None |
| Rules | None; leave ability content unused. |
| Attack | 2 |
| Base maximum health | 3 |
| Optional flavor | Small paws. Big courage. |

Content check: uses the existing cost 2 2/3 ability-free candidate. Both styles show
name/Generic/type/cost/art/2 ATK/3 HP. Flavor is optional. Do not add ability text
or a defense stat to fill empty space.

Zero-stat companion: **Pebble Buddy**, Generic Creature, cost 1, ATK 0/HP 3,
no traits/abilities, illustration of a smiling round stone companion. This uses
the existing cost 1 0/3 candidate. Its attack displays a real **0**, not a blank.

## EX-02 — Creature with traits and a costed ability

| Content | Value |
|---|---|
| Name | Moss-Stitch Medic |
| Color identity | Green — Resilience |
| Type | Creature |
| Play cost | 3 resources |
| Illustration | A soft crocheted woodland helper repairing another creature with glowing thread. |
| Traits | Construct; Healer (illustrative vocabulary, not a registered trait roster) |
| Attack | 2 |
| Base maximum health | 5 |
| Ability name | Field Repair |
| Activation cost | 1 resource and exhaust this creature |
| Timing/limit | Your Main phase, no pending effects; once per turn |
| Effect | Heal another creature you control for 2 HP. |

Suggested face wording: **Field Repair — Pay 1 and exhaust: heal another creature
you control for 2 HP. Your Main phase, no pending effects. Once per turn.**
Show the ability cost separately from play cost 3. The ability is not priced or
implemented merely because the underlying 2/5 body resembles a test profile.
Construct/Healer labels grant no automatic bonuses. Normal attack/exhaust waiting
rules and the shared maximum-health healing rule still apply.

## EX-03 — Action

| Content | Value |
|---|---|
| Name | Repair Pulse |
| Color identity | Green — Resilience |
| Type | Action |
| Play cost | 2 resources |
| Illustration | A green pulse reconnecting cracks in a creature's damaged shell. |
| Rules | Heal a creature you control for 3 HP. |
| Optional flavor | A little care can hold a whole world together. |

No ATK/HP or creature-readiness area is displayed. Target and amount are rules
content, not implied by art. Ordinary Action timing belongs in the shared rules;
healing does not exceed the target's maximum HP.

## EX-04 — Reaction with a timing restriction

| Content | Value |
|---|---|
| Name | Brace for Impact |
| Color identity | Gold — Cooperation |
| Type | Reaction |
| Play cost | 2 resources |
| Illustration | A protective golden barrier around a small determined defender. |
| Timing restriction | Play only after attacks are declared and before combat damage. |
| Effect | Give a creature you control 3 prevention until this turn ends. |

Suggested face wording: **After attacks are declared and before combat damage:
give a creature you control 3 prevention until this turn ends.**
The template must show Reaction, target restriction, amount and expiry. Prevention
is consumed by damage; unused prevention expires at that End boundary. It is not
a permanent armor stat. No ATK/HP appears on this Reaction itself.

## EX-05 — Persistent attachment / Upgrade

| Content | Value |
|---|---|
| Name | Reinforced Plating |
| Color identity | Generic |
| Type | Upgrade |
| Play cost | 2 resources |
| Illustration | Soft-edged modular armor plates being fitted onto a creature. |
| Attachment restriction | Attach to a creature you control. |
| Effect | The attached creature gains 2 maximum HP and 2 current HP when this attaches. |

Suggested face wording: **Attach to a creature you control. It gains 2 maximum HP
and 2 current HP when this attaches.**
The current-HP gain applies once when attaching, not repeatedly on redraw/render.
The existing shared rule caps current HP to the new maximum when the boost leaves;
that is not an additional printed ability on every upgrade. This card has no own
ATK/HP. Its effect has no invented end-of-turn expiry. Generic identity makes this
an example usable alongside any single-color deck's cards, subject to later balance.

## EX-06 — Non-attached persistent effect

| Content | Value |
|---|---|
| Name | Recovery Beacon |
| Color identity | Green — Resilience |
| Type | Persistent (working display label; final subtype name remains open) |
| Play cost | 3 resources |
| Illustration | A living lantern bathing a woodland clearing in gentle green light. |
| Rules | At the start of your turn, heal a creature you control for 1 HP. |

This example exercises a continuing battlefield card with a triggered effect and
no creature stats. The target is selected when required by the future trigger
system; with no legal target, there is no healing. Do not invent a permanent-card
subtype or its removal rules solely from this temporary display label.

## EX-07 — Leader (same data in either treatment)

| Content | Value |
|---|---|
| Name | Aster, Corekeeper |
| Color identity | Gold — Cooperation |
| Type/role | Creature; Leader |
| Summon cost | 4 resources (label Summon, not an ability activation price) |
| Illustration | A warm, confident guardian with a luminous Vanguard Core and a clear face. |
| Traits | Guardian (illustrative vocabulary) |
| Attack | 3 |
| Base maximum health | 5 |
| Reserve ability | **Guiding Light** |
| Reserve activation cost | 1 resource |
| Reserve timing/limit | Your Main phase, no pending effects; once per turn; reserve only and not recovering |
| Reserve effect | Give a creature you control 1 prevention until this turn ends. |
| Battlefield ability | **Shield Line** |
| Battlefield activation cost | 2 resources and exhaust Aster |
| Battlefield timing/limit | Your Main phase, no pending effects; once per turn; battlefield only |
| Battlefield effect | Give a creature you control 3 prevention until this turn ends. |

Suggested panels:

**RESERVE — Guiding Light. Pay 1: give a creature you control 1 prevention until
this turn ends. Your Main phase, no pending effects. Once per turn.**

**BATTLEFIELD — Shield Line. Pay 2 and exhaust Aster: give a creature you control 3
prevention until this turn ends. Your Main phase, no pending effects. Once per turn.**

Location labels are essential. Live availability disables a reserve ability while
summoned/recovering and a battlefield ability while in reserve. Normal readiness
and spent-use rules still apply. Recovery/increase rules are common leader rules,
not assumed extra abilities granted by full-art styling.

Live reserve example after two battlefield removals, without other modifiers:
base summon 4 + accumulated increase 4 = **Summon 8**. Display **Recovering until your
next Start** when applicable. The 8 is the actual payable cost once recovery ends;
it does not authorize summoning during recovery. The accumulated increase is
undiscountable under the existing rule. These are live overlays, not alternate
printed versions of Aster. Leader cost/body/abilities remain untested examples.

## EX-08 — Transforming creature and its linked face

### Scout face

| Content | Value |
|---|---|
| Name | Gearfox — Scout |
| Color identity | Silver — Ingenuity |
| Type | Creature |
| Play cost | 3 resources |
| Illustration | A cheerful robotic fox with folded cargo wheels. |
| Traits | Robot (illustrative vocabulary) |
| Attack / base max HP | 3 / 4 |
| Rules | Transform — Pay 1 during your Main phase with no pending effects: change into Gearfox — Hauler. Once per turn. |

### Hauler face

| Content | Value |
|---|---|
| Name | Gearfox — Hauler |
| Color identity | Silver — Ingenuity |
| Type/role | Creature; Linked Form |
| Access | Transform from Gearfox — Scout; linked face of the same card, not another deck card. |
| Illustration | The same fox transformed into a sturdy little cargo rover. |
| Traits | Robot; Vehicle (illustrative vocabulary) |
| Attack / base max HP | 1 / 7 |
| Rules | Transform — Pay 1 during your Main phase with no pending effects: change into Gearfox — Scout. Once per turn. |

Both faces refer to the same instance's spent transformation use/readiness.
Normal transform rules preserve proportional health and round up. Example:
Scout at 3/4 HP -> Hauler at ceil(7*3/4)=6/7 HP. The template displays the current
form and live HP, not a hidden fractional value. Transform costs are distinct
from initial play cost. Do not give Hauler a fake 0-resource ordinary play cost.
This is layout content, not a tested answer to round-up healing loops.

## EX-09 — Combined form with assembly requirements

| Content | Value |
|---|---|
| Name | Atlas Assembly |
| Color identity | Silver — Ingenuity |
| Type/role | Creature; Combined Form |
| Access/assembly cost | Combine — Pay 2 during your Main phase with no pending effects. |
| Requirements | Bolt Scout and Tread Guard you control. |
| Deck status | Outside the 40-card deck; accessed through assembly. |
| Illustration | Two friendly robots joined into one broad-shouldered protector. |
| Traits | Robot; Guardian (illustrative vocabulary) |
| Attack / base max HP | 6 / 9 |
| Ability | Breakthrough — Any attack left after enough is assigned to defeat all blockers hits the defending player. |

Component reference content for public inspection:
- **Bolt Scout:** Silver Creature; play 2; ATK 2/HP 3; Robot; no abilities;
  illustration of a nimble little scout bot.
- **Tread Guard:** Silver Creature; play 2; ATK 1/HP 4; Robot; no abilities;
  illustration of a sturdy tracked guard bot.

Assembly requirements must remain readable in full art, not only in a menu.
The combined form has defined 6/9 stats; these are not a sum automatically inferred
from the component cards. Example with components at 1/3 and 3/4 HP:
combined currentHP=ceil(9*(1+3)/(3+4))=6, so show **HP 6/9**. Component links,
readiness/used-attack restrictions and all actual assembly rules remain inspectable.
No special separation ability or partial-survival exception is implied.

## EX-10 — Creature token

| Content | Value |
|---|---|
| Name | Spark Drone |
| Color identity | Silver — Ingenuity |
| Type/role | Creature; Token |
| Access | Created by Deploy Drones; not played from a deck/hand. |
| Illustration | A tiny bright-eyed hovering helper robot. |
| Traits | Robot (illustrative vocabulary) |
| Attack / base max HP | 1 / 1 |
| Rules | None |

Source reference example: **Deploy Drones**, Silver Action, play cost 3,
illustration of two drones emerging from a workshop hatch, rules **Create two
Spark Drone creature tokens, each with 1 ATK and 1 HP.** No stats on the Action.
The token's creation is not a 0-cost play option and does not put a token card
into the catalog/deck as an ordinary persistent card. Common token departure
rules still apply; summoned/new-token attack waiting is a live status.

## EX-11 — Non-creature resource token

| Content | Value |
|---|---|
| Name | Stored Spark |
| Color identity | Generic |
| Type/role | Resource Token |
| Access | Created by an effect; not an ordinary deck card. |
| Illustration | A single contained glowing Spark in a simple readable capsule. |
| Value | 1 stored resource |
| Rules | Spend this token toward a legal resource payment. Consume it when spent. |

No creature ATK/HP. A public stack/count indicator may show several identical
units in the app, but it is live quantity, not a new printed resource capacity.
This token spends directly; it does not permanently increase natural capacity.

## EX-12 — Live overlay stress example, not a new card definition

Use **Clockwork Pup** from EX-01 with **Reinforced Plating** from EX-05.
This fixture changes only the live instance:

| Information | Display/example |
|---|---|
| Base definition | Generic Creature; play 2; ATK 2; maxHP 3; no abilities |
| Attached upgrade | Reinforced Plating: maximum HP is now 5 |
| Persistent wounds | After 3 damage from full 5 HP, show HP 2/5 |
| Temporary attack boost | +1 ATK from an illustrative effect: show current ATK 3; inspect base 2/+1, expiry this turn End |
| Exhaustion | Exhausted; not silently indicated by color alone |
| Prevention | 2 remaining until this turn ends (e.g.3 granted,1 consumed) |
| Current controller/owner | Shown in public instance context/inspection when relevant |

The temporary boost is a display fixture, not an imported executable card. Neither
this fixture nor these example cards establish a legal played sequence or balance.
The base card remains 2/3 with no printed ability. Show the same live 3 ATK,2/5 HP,
exhaustion, prevention and upgrade association in both standard/full-art treatments.
No permanent text/art edit, new variant or cosmetic strength increase is created.

## Standard/full-art handoff checklist

For EACH example, design the two treatments from the identical fields above:

- Name, identity, type/role and access information remain readable.
- Applicable stats/abilities/traits are retained; inapplicable fields disappear.
- Play/summon cost cannot be mistaken for ability/transform/assembly cost.
- Leader Reserve and Battlefield labels survive every cosmetic treatment.
- Optional flavor/footer yields space before gameplay wording is shrunk.
- Busy art cannot obscure costs, rules, current HP or live statuses.
- Icons have labeled/inspectable meaning; reading level changes explanation only.
- Linked forms/components can be inspected without losing current-form identity.
- No artwork text is used as the source of mechanical truth.

Recharge is a global game procedure, not a mandatory stat or text box on every
card. An explicit future card that bypasses its penalty would need that exception
written in its own rules. No such bypass card is approved by this example pack.

This document completes content examples, not rendered template approval. Starter
pack publication, ability pricing, trait vocabulary, effect registration and
actual template design remain separate work.
