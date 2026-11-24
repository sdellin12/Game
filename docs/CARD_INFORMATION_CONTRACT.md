# Card information contract — standard and full art

Status: shared template contract approved by Steve on 2026-11-22. Based on confirmed
REQUIREMENTS.md, RULES_DRAFT.md and UX_CONTENT_PLAN.md. Steve requested this before
priority review/turn-draw implementation. This defines information, not visual
layout, new card mechanics, database schemas or an implemented renderer. Treat
these as digital card faces; print/export footer requirements are optional.

## One information contract, multiple visual templates

Standard and full-art treatments of the same card must communicate the same
mechanics, costs, identity and stats. Full art may move or restyle panels, never
omit a gameplay field or move essential rules exclusively behind an inspect tap.
Artwork is illustration only; the app renders text, symbols, frames and stats.
Cosmetic treatment never changes rules, card strength or singleton identity.

The following requirements apply to the full-card view. Hand thumbnails/TV board
tiles may abbreviate and open inspection, while retaining the information needed
for their particular action. This contract does not force full-card text into
small battlefield thumbnails.

## Every card face

| Information group | What the template must communicate |
|---|---|
| Card name | Readable display name, with a distinguishing variant/form name when necessary. |
| Color identity | One of the ten colors or an explicit Generic identity. Pair color with a symbol/text label; color alone is insufficient. |
| Card type | Plain, recognizable type such as Creature, Action, Reaction or Upgrade. Leader/Token/Form markers appear when applicable. Final names for other persistent card types remain open. |
| Play/access information | Normal playable cards show their resource play cost, including an explicit0 when free. Leaders label their summon cost. Created tokens/non-playable combined forms identify how they are created/accessed; do not give them a misleading0-cost play symbol. |
| Illustration | Approved artwork or a readable placeholder while awaiting art. Same subject must work in standard and full-art crops. |
| Rules/ability area | A reserved content region that presents every ability on that card. Ability-free creatures leave it unused; they do not need filler text or repeated basic game rules. |

A universal information region need not show an artificial value: an ability-free
creature has no ability text; a non-creature has no ATK/HP. Avoid printing N/A or0
in places where the field does not apply. The type and access presentation must
still make the card's use unambiguous.

## Conditional information — required when applicable

| Card/property | Additional face information |
|---|---|
| Any creature, including summoned leaders/forms/creature tokens | Attack and health, explicitly distinguished. Static preview shows base ATK/max HP. Live view uses the current values described below. No defense/armor stat. |
| Gameplay traits | Zero to two validated trait labels initially. Display the actual labels if present; art/name cannot silently grant traits or abilities. Traits and card type are separate concepts. |
| Keyword/ability | Name or keyword, exact effect, required targets/quantities, duration, limits and exceptions. Use explanatory wording/icons without changing mechanics. A keyword alone is insufficient for a young reader without accessible explanation. |
| Activated ability | Its own labeled activation cost and timing/usage restriction, distinct from the card's play/summon cost. Show exhaust/sacrifice/life/resource requirements when the ability uses them. |
| Reaction | Clearly says Reaction and communicates any special legal response condition. Normal reaction timing can live in common rules/help. |
| Upgrade/other persistent effect | Legal attachment/target restrictions and its continuing effect. Any activation/expiry conditions belong in its rules. Do not invent a universal duration. |
| Leader | Leader marker, summon cost, separately labeled Reserve and Battlefield ability panels with their own costs/limits. The two locations cannot be inferred merely from decorative placement. Initial leaders have one ability in each panel. |
| Transforming card | Current form identity; transformation condition/cost/effect and access to linked public form information. Preserve actual current form mechanics. |
| Combined form | Combined/Form marker, access/assembly requirements and defined stats/abilities. Identify it as outside the40-card deck, not an ordinary playable card. Component details must be inspectable. |
| Token | Token marker, defined type and any applicable stats/abilities. Explain creation/access where relevant; it is not an ordinary deck card. |
| Unusual cost, variable X or alternate payment | Explicit cost formula/options and necessary restrictions. Never flatten a conditional cost into an unexplained number. |

Basic creature rules such as ordinary attacking/blocking do not need repeating on
every creature. Card-specific exceptions do. Do not import rarity, defense,
species bonuses or automatic color advantages from reference games.

## Live match overlays — supported by both templates

The base definition and live instance are distinct. Leave room for readable,
non-destructive overlays/labels, without permanently baking state into artwork.

- Current attack and current/max health for creatures. For example: ATK3, HP2/5.
  Persistent wounds must be visible; show whole-number actual values. Base values
  and modifier breakdown are available on inspection.
- Current effective play/summon/activation cost when changed, distinguished from
  base cost. Leader accumulated summon increase and recovery state are public;
  show the actual payable summon cost rather than asking players to calculate it.
- Ready/exhausted, attack eligibility/use and spent ability limits when relevant.
  These are instance statuses, not extra printed stats.
- Shields/prevention, temporary modifiers, attached upgrades and relevant duration
  or expiry indicators. Current HP alone cannot explain an exhausted blocker or
  shielded defender; public status must remain visible/inspectable.
- Controller/owner attribution, token/copy/combined-component links and other
  public instance relationships when relevant. Concealed zones expose no identity.

Selection highlights, target previews, damage predictions and read-aloud/inspect
buttons belong to app interaction chrome. They can sit beside/over the digital
card, but are not mandatory printed card content. Private tentative selections
never become public just because a full-art renderer has more room.

## Optional decorative/catalog content

Flavor text, creator/illustrator credit, character/theme emblem, cosmetic finish
name and small catalog/variant footer can be supported, but are not necessary
for every face. Keep flavor text visibly separate from executable rules. Omit or
collapse optional decoration before shrinking gameplay text.

Rarity, set/collector number, serial code, price, achievement progress and currency
are not universal gameplay requirements. No rarity/power-tier system is established
by this contract. Credits may be preserved in catalog/inspection metadata without
occupying every face. A cosmetic badge cannot imply greater gameplay strength.

## Data retained without printing it on every face

Future content models still need stable definition/variant/mechanical-identity IDs,
match-pinned version, character links, structured effect definitions, artwork/crop
references and provenance/attribution where present. Live instances need distinct
IDs and state. A short optional footer can identify a named gameplay variant;
backend IDs/hashes need not crowd the face or be spoken to young players.

Do not modify the current nine-profile test-pack schema to pretend it is a complete
card catalog. A later content-schema task must inspect compatibility and provide
an explicit migration/rollback plan before changing saved card/deck definitions.

## Readability and accessibility rules

- Same rules at all reading levels. Use plain explanations, labeled icons and
  read-aloud support; never hide a restriction in an adult-only wording mode.
- Text must remain readable over busy art. Full-art templates provide contrast
  panels/scrims and safe text zones rather than relying on the illustration.
- Recognizable information grouping across templates: name, identity/type, access,
  rules, creature stats and live statuses. Exact placement/style can vary.
- Do not distinguish color, costs, readiness or ability location by hue alone.
- No auto-shrinking long rules into illegibility. Expand the card/inspection view,
  simplify authored wording without changing rules, or revise the template.

## Template acceptance examples

Before a template is considered usable, render these with the SAME content in
standard/full-art variants and check that no gameplay information disappears:

1. Ability-free Generic creature: name, type, cost, artwork and ATK/HP.
2. Colored creature with two traits and one costed/limited ability.
3. Reaction with a target restriction and numeric duration/effect.
4. Persistent upgrade with attachment restriction and ongoing modifier.
5. Leader with summon cost, Reserve ability and Battlefield ability; live recovery
   and increased summon-cost overlays.
6. Transforming/combined creature with public form/assembly information.
7. Creature token, plus a non-creature card, to verify inapplicable stats disappear.
8. Wounded/exhausted/shielded creature with an attached upgrade and temporary
   attack modifier; same live mechanics under standard and full-art treatments.
9. Long name/variant and maximum supported initial ability text without losing
   cost, type or stat readability. Some mechanics remain unimplemented; these are
   template-content acceptance examples, not proof of engine coverage.

Suggested content slots: name; color identity; type/role; play/access cost;
artwork; traits; rules/abilities; optional creature stats; optional leader/form
panels; optional flavor/footer; separate live-state overlays. This contract is approved; standard/full-art templates can now be worked on
independently. See [filled examples](CARD_CONTENT_EXAMPLES.md) for the shared
content handoff. Example card designs/costs are illustrative, not adopted content.


## Implemented design assets
See [CARD_DESIGN.md](CARD_DESIGN.md) for completed v1 standard/full-art SVG
templates, shared fixture data, previews, verification and portable LLM handoff.
This information contract remains the required-content baseline.
