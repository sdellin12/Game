# Discovery Answers

## Q01 — Ideal match moment
Confirmed 2026-11-17.

Steve: "Maybe kids ganging up on adults or one of us parents asking a kid for help to defeat the other parent. That would make my boys laugh so hard."

Design target: support funny social moments through kids teaming up against adults and a parent recruiting a child to help defeat the other parent. These are desired experiences, not yet specific mechanics.

Unresolved: how assistance works; whether alliances are temporary or formal; incentives; betrayal limits; victory and elimination rules. Address these in the relevant later questions.

## Q02 — Age, reading and adaptability
Confirmed: youngest intended player is six and learning to read quickly. The game should remain relevant as children age.

Steve proposed optional simpler text and/or easier mechanics during card/deck creation, and possibly adapting match mechanics during setup based on the youngest player. These are candidate approaches, not approved implementation choices. Generation method (including whether AI is involved) is undecided.

Open clarification Q02a: should mixed-age matches use shared simplified rules, allow simpler child decks alongside deeper adult decks under common rules, or offer both as selectable options? Exact adaptation, fairness and card compatibility remain unresolved.

Q02a answer: Steve prefers not to simplify the full match. Complex mechanics should remain available with easy-to-understand wording. He cited milling as a concept that may be difficult to understand. His wife is also new to card games. Initial game setup/learning should avoid overwhelming newcomers, and sustained enjoyment and replay appeal across the family are priorities.

This supersedes any interpretation that youngest-player-based match simplification is preferred. Specific onboarding, explanations, deck guidance and complexity controls remain undecided. Do not assume tutorials, AI, simplified decks or separate rules modes have been approved.

## Q02b — Learning and deck-building tutorials
Confirmed: Steve wants a simple tutorial game mode, a deck-creation tutorial with different ways to build decks, and in-game tutorial guidance.

Proposed tutorial approaches:
- A questionnaire about preferred play style, with examples such as attacking quickly or saving resources to play large creatures.
- Small playable situations against an "AI" demonstrating different mechanics.

Interpretation limits: examples do not approve MTG's resource system, specific archetypes, or any particular deck-construction rules. "AI" opponent implementation is undecided; do not assume generative AI, a paid service, or a full general-purpose computer opponent. Questionnaire behavior, alternative creation paths, scenario structure and guidance controls require design later.

## Q03 — Player count
Steve: "Ideally anyone that wants to play. But regularly there should be four players"

Confirmed: four players is the regular match size. Aspiration: accommodate people who want to join, including larger groups. No numerical maximum or unlimited-player guarantee has been agreed. Minimum count, supported range and scaling rules remain open; revisit after turn structure and pacing are clearer.

## Q04 — Match duration
Confirmed: target a regular four-player game lasting approximately 40–60 minutes once players know how to play (the context of the question answered). This is a design/playtest target, not an enforced timer. Tutorial duration, larger-group duration and pacing mechanisms remain undecided.

## Q05 — Commander qualities
Confirmed: Steve loves singleton format and wants a leader of the deck. No separate commander-damage count. Leader implementation need not follow MTG Commander and need not require casting.

Unresolved: singleton scope/exceptions, deck size, whether differently themed versions of the same mechanical card count as duplicates; leader abilities, availability, battlefield role, defeat/reuse and deck-building restrictions. Do not assume a command zone, commander tax, always-active powers or any particular leader implementation.

## Q05a / Q14 — Leader role
Steve prefers a leader that both influences the deck/play style and participates in battlefield combat. This is the initial design direction. He is open to cool proposals and possibly different leader mechanics players could choose or add eventually.

Do not treat openness as approval of any specific ability, customization system, progression, or multiple leader modes in the first release. Leader access/cost, passive versus activated effects, defeat/reuse and restrictions remain open. Develop concrete proposals after core gameplay is clearer.

## Q06 — Initial match scope and extensibility
Confirmed: start with player-versus-player battles only; shared enemies/events and other modes are outside initial scope. The full app must be designed for adding features later through APIs/plugin-style extension interfaces, aiming for straightforward integration.

Unresolved extension details: which capabilities can be extended, content packs versus executable plugins, internal/developer-authored versus third-party plugins, installation/update/version compatibility, cross-device consistency and platform constraints. "Plug and play" is the desired integration experience, not a verified guarantee for arbitrary plugins or platforms. Defer technical design to the build-planning team, but preserve this as an architecture requirement from the outset. It does not authorize adding future modes to the first release.

## Q07 — Victory conditions
Steve likes last-player-standing via player health, leader defeat, and victory-point approaches. He proposed different game modes, a simple way to incorporate different victory conditions, and possibly a unique win condition for each leader.

These are alternatives under exploration, not approval of all approaches in the initial version. No primary victory condition, scoring system, mandatory leader-specific goal, or rule that defeating a leader eliminates its player has been selected.

## Q07a — Initial victory structure
Confirmed: shared goal only for the initial version. Leader-specific alternate wins and other victory modes are deferred.

Tentative preference: "Maybe by defeating the leader." Leader defeat is a candidate, not a finalized elimination rule.

## Q07b / Q14 / Q18 — Revised combat and leader direction
Steve changed direction: attack the player, with creatures/cards attacking and defending, using MTG as a reference. This supersedes leader defeat as the tentative victory condition. It does not adopt all MTG combat rules.

Proposed leader behavior: stays outside battle initially, may have a passive ability there, and enters when a specific condition is met to deliver a major attack or other significant effect. Entry condition, off-battle passive, duration, repeat access, combat rules and impact are not finalized. Earlier desire for both strategic influence and combat participation remains compatible with this direction.

Still confirmed: one shared initial victory goal, singleton decks, no separate commander-damage count. Exact player loss/win condition is unresolved; do not assume zero player health was explicitly selected yet.

## Q07c — Working victory rule
Steve confirmed "Yes I think so. At least for now" to player health, defeat at zero health, and last remaining player winning. Adopt this as the working initial rule, open to revision through further design/playtesting.

Unresolved: starting health, simultaneous defeats/draws, damage/healing details and post-defeat participation. No respawn or spectator influence approved.

## Q08 — Defeated-player participation and return
Confirmed: defeated players should retain a way to participate and be able to re-enter when a condition is met. No particular participation action, return trigger, health/reset state, limit or cost has been selected.

This adds a qualification to the working zero-health/last-player-standing rule: zero health removes a player from active battle but need not permanently eliminate them. Need to define when victory is final relative to eligible returns, and prevent repeated returns from undermining the 40–60 minute target. These are design issues, not approved solutions.

## Q08a — Re-entry mechanism exploration
Steve is unsure whether return should be earned independently, enabled by another player, or both, and wants to work through it. Candidate idea: a revive card of some sort. This does not select a card type, make revive cards the only return path, or resolve who can play them.

## Q08b — Leader-linked revival candidate
Steve proposed leaders having revive abilities dependent on game conditions/costs. Examples: distribute cards remaining in hand to another player, or send all currently held hand cards to the graveyard. He wants to explore options and possibly let the player choose a revive condition when generating/creating a leader.

These are proposals, not finalized mechanics. Do not assume whose leader revives whom, whose hand pays, whether the examples are costs versus prerequisites, exact distribution rules, automatic versus optional activation, leader-generation technology, or unrestricted custom conditions. This does not conclusively reject revive cards.

Next: Q08c — clarify whether a defeated player's own leader brings its owner back at a cost paid from that player's hand, versus an active player's leader reviving someone else. After ownership is clear, develop options and clarify participation, eligibility with an empty hand, retained state, limits and final victory timing.


## Q08c — Revival cost payer and hand safeguard
Steve prefers revival costs mainly from the dying/defeated player's own hand. He is also interested in play styles that reward different things; no reward mechanic or other-player revival system selected.

Proposed safeguard: a full hand must be given out; if the player lacks enough cards, they draw a full hand to revive. Ambiguities: draw up to a threshold versus draw an additional full hand; drawn cards paid away/discarded versus retained after return; definition of full hand, timing and destination. No hand size selected.

This updates the ownership uncertainty above: cost primarily from the defeated player's hand; exact leader ownership/activation remains implicit rather than finalized. Prior 'next question' notes are historical; the latest checkpoint governs.

Next: Q08d — clarify whether short-handed players draw up to a required total and then give/discard that entire hand as the revival payment, or instead receive a fresh hand to keep after revival. Later examine how the cost feels with an empty hand, revival access/limits, retained state and final victory timing.

## Q08d — Payment clarification and intentional deferral
Confirmed direction: the player gives away or discards a hand as the revival payment; it is not a fresh hand kept as a revival reward. Earlier draw-when-short idea remains a candidate; exact top-up/additional-draw sequence and hand size are not settled.

Optional complexity proposal, especially for adults: revival health could equal cards given away, with less health for discarded cards. This is illustrative, not an approved formula or mandatory age-based rules split.

Steve explicitly wants to work through these specifics later during card planning. Do not continue drilling into revival formulas now. Preserve deferred questions: access and activation, required hand size/draw behavior, destinations, return health/state, repeat limits, participation while defeated, final victory timing and abuse cases. Review against the 40–60 minute target.

Next: Q09 — concrete forms of helping during active battle. Then themes and card/deck creation; return to detailed revival rules during card planning.

## Q09 — Helping in active battle
Steve wants broad opportunities to help, inspired by what he loved about Munchkin. Explicitly includes helping during combat and blocking attacks for another player. In response to examples of contributing attackers, blockers, helpful cards or resources, he said "Pretty much anything."

Design direction: support broad cooperative intervention within competitive battles. This is not approval of unrestricted actions at any time, every transfer type, or any exact combat/timing system. Attack contribution, defensive intervention, helpful card play and resource support should be explored with clear ownership, costs, timing and acceptance rules.

Next: Q09a — are negotiated promises enforced by the app, nonbinding and breakable, or a choice between formal trades and informal promises? Then clarify theme-to-mechanics mapping. Exact combat assistance rules remain for rules design.

## Q09a — Betrayal and card-enforced truth
Confirmed: ordinary negotiated promises may be betrayed; the app should not automatically enforce every table deal.

Steve also wants specific cards (e.g. instant-like cards or creature descriptions) that "require truth." Intent is recorded, but exact meaning is unresolved: binding game commitments, factual disclosures, restrictions, verification, duration and penalties all need examples/clarification. Do not assume speech monitoring, AI lie detection, or automatic knowledge of real-world statements. Instant-like cards were mentioned as examples; no MTG-style stack/timing rules adopted.

Steve introduced ideas for "mana colors" tied to play styles beyond matching costs or elemental identities. No colors, resources, factions, restrictions or mechanics selected yet.

Next: invite Steve to explain his mana-color/play-style ideas (adaptive ordering toward Q17 and theme mechanics). Afterward return to a concrete "require truth" example and unresolved Q10–Q13 creation questions.

## Q09b / Q17 — Gold and structured agreements
Steve proposes colors representing character traits. Candidate: Gold = honesty/integrity. Cards could enforce other players keeping bargains through on-screen selection of terms. Examples: help attack, help defend, or do not attack a specified player for the next turn. Explore support across different card types.

This clarifies "require truth" toward explicit game-state agreements rather than detecting truth in conversation. Ordinary promises remain breakable; qualifying card effects are the proposed exception. Gold name/identity is a candidate, not a completed color/resource system. Colors as traits does not establish costs, resource generation, alignment restrictions or exclusive mechanics.

Unresolved: voluntary acceptance versus imposed obligation, exact valid terms/targets/duration, rewards/costs, how enforcement works, what happens if assistance is impossible, conflicting promises and cancellation. No arbitrary natural-language contract engine approved.

Next: Q09c — must all affected players explicitly accept a binding agreement before it activates, or may some cards impose obligations without consent? Then refine color identities and theme-to-mechanics mapping. Keep detailed agreement timing/edge cases for card/rules design.

## Q09c — Forced obligations
Confirmed direction: some cards may impose obligations without the affected player's agreement. Steve proposed this could be a leader's major skill. Forced obligations should not last for the whole game.

Steve mentioned "after a certain amount of turns or with a cost of some kind." Meaning unresolved: expiration or paid escape for the affected player versus activation delay/cost for the imposing player (or both). Do not choose an interpretation silently. No exact duration, cost, leader skill, escape rule or permanent restriction approved.

Next: Q09d — clarify whether turns/cost refers to ending/escaping the obligation, activating it, or both. Later detail legal effects, impossible assistance, conflicts, counters and duration counting during rules/card planning.

## Q09d — Unlock clarification
Steve primarily meant ability activation unlocks after a certain number of played turns, or through whatever energy/mana/resource system is selected. He is open to both activation requirements and expiration/escape constraints, but did not select a specific implementation.

Confirmed interpretation: turn/resource gating is a candidate for accessing powerful abilities, including the forced-obligation concept. The prior no-full-game-lock preference remains. No turn count, resource system, cooldown, escape cost or duration selected. Do not assume every leader uses identical access conditions.

Next: Q10 — can any interest theme use any trait/color/play style, or should themes constrain mechanical identities? Keep detailed unlock/contract design for later rules/card planning.

## Q10 — Persona and color
Confirmed: deck "persona" (interest/theme) should be independent of color. Steve is open to proposals about assigning color values. Do not restrict themes such as crochet, robots, cryptids or fantasy to predetermined colors.

Proposal presented, not yet approved: assign card color from its mechanical approach/traits rather than artwork or subject matter. Derive a deck's displayed color profile from its included cards. For example Gold could identify binding-agreement mechanics in any persona. Other colors, multi-color rules, weighting, deck restrictions, resource costs and whether a player chooses a color identity before construction remain undecided.

Next: Q10a — choose whether players select colors/play styles before deck creation, have the deck's color profile emerge from selected abilities/cards, or can use either guided path. Clarify ambiguous "color value" if needed; do not assume numerical pricing or a mana cost system.

## Q10a / Q12 — Guided creation and color access
Confirmed: a build wizard should help create decks and cards, ask questions to discover play styles, and provide deck suggestions based on answers. This extends the earlier questionnaire/tutorial requirement. Recommendation/generation implementation is not selected; do not assume generative AI.

Confirmed direction: some "card types" should be locked to particular colors, while generic no-color cards should be usable by everyone. MTG Earthquake/Fireball and Sol Ring were references for color-specific versus universal access, not requests to copy those cards, names, power levels or mechanics. Persona remains independent of color.

Ambiguity: "card types" may mean specific effects/abilities or broad categories such as creatures/instant-like cards. Need clarification. No complete color roster, deck color identity, mixed-color rule, leader restriction, card cost or generic-card balance system selected.

Next: Q10b — clarify whether color locks apply to particular effects (e.g. Gold binding bargains) while broad card categories remain available to all colors, versus locking whole categories. Then clarify who defines a deck's allowed colors and the creation workflow.

## Q10b — Exclusive effects, not broad categories
Clarified: colors own specific mechanical specialties. Gold is the only color that can enforce honesty/agreements. Steve offered tentative black/red (or another color to be decided) exclusivity for attack cards like MTG's Barbed Lightning.

Do not treat black/red as finalized colors, adopt the referenced card, assume its exact rules, or interpret all combat/attacking as exclusive to one color. The intended boundaries of direct-damage versus other offensive effects remain to design. No exclusivity of broad categories (creatures/equipment/instant-like cards) was requested in this clarification.

Next: Q10c — should a leader determine a deck's allowed colors, should players choose colors independently, or another system? Later develop complete color specialties and mixed-color limits.

## Q10c — Leader, color and deck creation flow
Steve accepted the proposed guided default:
1. Choose persona/theme.
2. Answer play-style questions.
3. Receive suggested compatible color identity, leader and starting deck together.
4. Customize with explanations when changes affect card eligibility.
An advanced path allows starting directly with a leader or colors and skipping the questionnaire.

Working rule: leader and deck share a compatible color identity; leader does not bypass other colors' exclusive mechanics. Number of colors, mixing restrictions, exact compatibility rules and what happens when changing identity remain unresolved. Generation/recommendation technology is not selected.

Next: Q12/Q13 — clarify whether creating personal cards means adapting approved mechanical templates, inventing new abilities, or both; then approval and balance. Q11 personal identity can be revisited if missing beyond persona/art/story and play style.

## Q12 — Deck-building freedom
Confirmed: users can choose existing deck archetypes and customize them, or build a full deck themselves. Both paths should be available to children as well as adults. Steve expects his wife may prefer the archetype path and himself the full-building path; these are expected preferences, not profile restrictions.

Steve began "I'd like ... both" in response to ability-creation choices, but elaborated in terms of deck-building depth. Do not silently equate assembling a full deck with inventing arbitrary new mechanics. Existing building-block versus genuinely new effect creation needs explicit clarification before designing a custom rules authoring/execution system.

Next: Q12a — can a user invent an ability not in the supported ability library, or does full deck building mean selecting/combining supported abilities and cards? Then Q13 balance/approval.

## Q12a — Supported effects and thematic fit
Confirmed initial scope: a defined set of card rules/effects assigned to cards, rather than arbitrary user-invented executable mechanics.

Cards' actual behavior and text should fit their identity. Steve's examples: a big dragon should not receive the same effect as a mouse or a sneaky attack; a cat should not fly like a winged creature. Record these as intended thematic coherence, not a finalized absolute species blacklist or prohibition on fantasy exceptions.

Candidate implementation approaches: AI creates appropriate card text, or categories/subcategories define permitted behavior/abilities. No AI dependency, service, generation method or taxonomy selected. Need to distinguish readable descriptive/flavor text from authoritative rules text; proposals must preserve exact correspondence between displayed rules and supported executable effects.

Persona remains independent of color; thematic ability compatibility introduces a separate constraint to resolve with free theme creation. Need clarification on user-approved extraordinary traits (e.g. winged cat) versus automatic defaults.

Next: Q12b — should supported abilities be gated by explicit traits (e.g. wings permit flight), with fantasy exceptions possible by choosing a fitting trait, rather than permanently restricted by species? Then Q13 balance/approval.

## Q12b / Q11 — Fantasy traits and creative enjoyment
Confirmed: fantasy exceptions through appropriate traits (e.g. a winged cat able to fly) are acceptable and encouraged. Steve wants children to have almost as much fun creating cards and decks as playing matches. Creative construction is a core experience, not merely setup.

Working direction: traits support thematic ability eligibility without rigid real-world species restrictions. Exact trait taxonomy, combination limits, trait/effect/color interactions and UI remain to design. No automatic entitlement to stronger cards from adding more traits approved; balance mechanism still unresolved.

Next: Q13 — how to balance custom cards: enforce common power/cost limits, require household review, or offer balanced versus experimental creation modes. Present a concrete recommendation without assuming any selected approach.
