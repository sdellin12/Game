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

## Q13 — Balance boundaries and later research phase
Confirmed: balance limits required for strength, defense, stats and effects, while creature design/concepts should remain creatively unrestricted. Steve's example: a glass-cannon Godzilla with Wolverine claws is acceptable but may require small size or a major weakness. Do not enforce lore-based power entitlement from names/art; exact size mechanics are not approved.

Tradeoffs such as costs, fragility and weaknesses are candidates, not a finalized points formula. No experimental/unbalanced match mode was explicitly approved in this answer. Need to validate ability combinations as well as individual stats; no claim of guaranteed balance.

Deferred user request: eventually convene a very large expert subagent team to study Pokemon, Yu-Gi-Oh!, Elestrals and MTG for lessons toward strong balance. Explicitly not now. Plan this as a later comparative research/rules review phase after a concrete draft exists, with targeted official-source research, synthesis, simulation/playtests and iterative tuning. Do not treat the large team as already convened or research as completed; exact team size and method still open. This is an in-project future phase, not a scheduled automation request.

Next: Q15 — normal turn structure: sequential player turns with other players able to intervene versus simultaneous planning/rounds. Initial leader role already covered by Q14; access details remain deferred. Then Q16 reaction timing and Q17 resources.

## Q15 / Q16 — Turn structure and reactions
Confirmed: sequential turn-based play, with MTG Arena as a reference. Players see public actions while private cards remain hidden on each player's device, allowing private planning during other turns. Instant-like cards should permit actions during another player's turn.

This does not adopt all MTG Arena timing/priority rules, reveal card identities through prompts, or require simultaneous execution of planned actions. Existing TV public-battlefield requirement remains.

Next: Q16a — choose reaction depth: can players respond to responses, or should each event have a single reaction opportunity? Afterward clarify multi-player reaction order and prompt/pacing behavior, then Q17 resources. No stack, priority order, timers or auto-pass rules selected yet.

## Q16a — Response chains
Confirmed: players may chain responses to other responses. It must be easy to see and understand what is happening.

Presentation requirements implied by clarity goal, to design concretely: identify pending effects, relevant players/targets and upcoming resolution. Exact UI is unselected; do not assume a full MTG stack, last-in-first-out resolution, priority order, response limits or timer.

Next: Q16b — clarify whether responses resolve newest-first (last response first, then work backward), or explore another chain-resolution model using a concrete example. Then multiplayer response order/pacing and Q17 resources.

## Q16b — Resolution order
Confirmed: Steve accepts newest-response-first resolution. He notes MTG's version has confused him too, reinforcing the need for clear explanation and practice.

Working behavior: newest pending response resolves first, then remaining pending effects work backward. Resolve one effect at a time; whether fresh response windows open between resolutions remains to clarify. No wholesale adoption of MTG priority rules.

Proposed UI/training, not a selected layout: visible pending-effect list, target indication, next-to-resolve highlight and conditional outcome preview. A preview must not expose hidden cards or promise an unchangeable outcome.

Next: Q16c — after one effect resolves, can players add new responses before the next pending effect resolves, or does the existing chain finish without additions? Then multiplayer priority/pacing and Q17 resources.

## Q16c — Responses between resolutions
Confirmed working rule: after one pending effect resolves, players get another opportunity to respond before the next effect resolves. New responses follow newest-first resolution.

Steve explicitly wants this changeable in the future. Preserve revisability in rules architecture; do not assume an in-match toggle or arbitrary switching during a saved match. Proposed implementation guidance: separate timing policy from card UI and specify ruleset compatibility/version behavior during build planning.

Next: Q16d — recommend a fixed rotating response order rather than fastest-tap priority; clarify acceptance. Then pacing controls and Q17 resources. Exact first responder, pass/reset semantics and timer remain undecided.

## Q16d — Response priority
Confirmed: fixed order around the table for response/pass opportunities, rather than fastest tap. Steve emphasizes fairness.

Unresolved details: who starts each response window, rotation direction, reset after new responses, pass persistence, simultaneous triggers, pacing/auto-pass and private-information leakage through prompts. Defer these detailed proposals to rules/UX planning; do not assume an automatic timer or skip on inability to act.

Next: Q17 — resource-system preference. Explain predictable growing/refilling allowance, resource cards drawn from deck, and earned/banked resources as options without selecting a system. Pacing controls remain open for later UX questions.

## Q16e — Playability and automatic passing
Confirmed: highlight or otherwise mark cards legally playable during the current turn/window, referencing MTG Arena. Automatically skip players with no response available.

Design interpretation to validate: use all legal response actions, costs, targets, timing and existing restrictions to determine availability, rather than card-type presence alone. If the rules later allow non-card response abilities, account for those too. No automatic skipping when a player has a legal response but merely has not acted, and no default timer approved.

Privacy consideration for later UX design: auto-pass can reveal that a player currently has no legal response; do not expose the underlying hidden cards or the reason. Desired treatment of this inference remains unresolved.

## Q17 — Growing resources and acceleration
Confirmed direction: resources gained each turn so stronger cards become playable as the game builds; cards can accelerate resource growth. Steve proposed each leader also having an additional way to grow resources, e.g. an aggressive leader gains resources per creature killed.

Leader growth is a candidate system with illustrative trigger, not a selected per-kill formula. Clarify whose creatures/credit, repeatability and snowball effects later. No turn-growth number, resource name, colors/cost relation, reset/refresh schedule or banking behavior chosen.

Next: Q17a — does each turn increase a refillable spending allowance, or add currency that accumulates until spent? Explain unspent-resource handling, then later off-turn spending/refresh and leader acceleration.

## Q17a / Q16f — Resource refill and revised pass behavior
Confirmed: add one to resource capacity and refill each turn. Starting capacity and maximum not selected. In context, likely each player's own turn, but refresh timing must be explicitly clarified because out-of-turn play matters.

Supersedes Q16e automatic skipping: when a player has no playable response, still give that player a Pass button, with no other gameplay action available in that response window. Do not silently skip. Playability highlighting remains. Presentation on other screens should not reveal which response options a player has; exact UI/pacing remains to design.

Next: Q17b — confirm capacity growth/refill happens at the start of that player's own turn only, meaning resources spent on their turn stay spent through opponents' turns until their next turn. Then acceleration, resource-color link and remaining rules questions.

## Q17b — Own-turn refresh and resource effects
Confirmed: growth/refill happens at the start of the player's own turn. Resources spent remain spent through opponents' turns until the player's next start-of-turn refresh unless a specific effect changes that.

Steve wants rare, expensive cards that add resources, possibly also a leader skill. "Rare" denotes intended limited availability here; do not infer paid rarity, packs, ownership scarcity or monetization. Exact costs/access and leader implementation undecided.

Next: Q17c — distinguish temporary spendable-resource gains from permanent capacity increases; ask whether both are desired as separate effects. Temporary duration, cap/overflow, costs and balance remain unresolved. Later revisit resource colors and initial capacity.

## Q17c — Temporary versus permanent resource effects
Confirmed: both temporary resource gains and permanent capacity increases should exist. Permanent increases should cost a lot, while more casually played temporary effects cost less. Exact costs, availability, temporary expiration, whether permanent effects also refill immediately, and caps remain unresolved for card/rules balancing. Do not impose equal costs across all effects or interpret casual availability as monetization.

Next: Q17d — should resources be a universal pool with color controlling card eligibility/mechanics, or should paying card costs require particular resource colors? Recommend universal pool for accessibility while preserving color identities; no selection yet.

## Q17d — Initial universal resources and later color specificity
Confirmed: begin with one universal resource type for card payment; preserve an easy path to specific/colored resource costs later as players learn. In context "shared resources" means a universal type, not a communal balance shared among opponents; each player's own-turn growth/refill and spending pool remain.

Initial color identity and exclusive effects continue to matter through card/deck eligibility, not colored payment. Colored payment is deferred, not an initial selectable mode. Build planning should isolate cost/payment rules and use extensible cost data; exact future implementation and migration/version compatibility require design and cannot be guaranteed without validation.

Resource numbers/caps and card costs remain for balancing. Next: Q18 — combat targeting: can a player split attackers among multiple opponents in one combat, or attack only one opponent? Then blocker assignment, damage persistence and readiness/summoning timing.

## Q18a — Split attacks
Confirmed: attackers can be split across multiple opponents during combat. Exact declaration timing, helping/blocking allocation and multiple-combat behavior remain open.

## Platform update — Children's iPads
Confirmed: kids use older iPads; app support on those devices is required alongside the previously requested Android phones and TV experiences. Exact iPad models and iOS/iPadOS versions unknown. No native-app versus installed-web-app choice approved. Verify compatibility and installation constraints against official sources during architecture research once device information is available; do not promise support for arbitrary old hardware.

Next: ask for iPad models/software versions if known (Settings > General > About), with an option to record them later. Then resume Q18 blocker assignment and combat details. Existing platform queue must include iPadOS.

## iPad follow-up — Deferred
Steve does not have the iPads available and intended the requirement as a note for later. Keep older-iPad support in scope; collect model/software versions during platform/build planning, not now. Do not block gameplay discovery on this information.

Next: Q18b — blocker assignment: defending player chooses which creatures block attackers versus attacker chooses creature targets. Helping other players defend remains confirmed; detailed allied-blocking consent/allocation follows later.

## Q18b — Blocker assignment
Confirmed: defending player chooses which creatures block incoming attackers by default. Specific card abilities can provide exceptions, such as challenging a particular creature; no individual exception card approved yet.

Allied help with blocking remains required. Still unresolved: how allied blockers are offered/accepted, multiple blockers per attacker, damage assignment, damage persistence, creature readiness and attack/block exhaustion.

Next: Q18c — may multiple creatures team up to block one attacker, or should blocking be one-to-one? Recommend team blocking for big-creature counterplay; exact damage assignment to follow.

## Q18c — Multiple blockers
Confirmed: multiple creatures may block one attacker. Steve references MTG's approach for this mechanic. This does not silently adopt all MTG combat details or historical damage-assignment versions.

Next: Q18d — clarify who divides attacker damage among multiple blockers. Proposed default: attacking player chooses allocation through a clear interface while blockers each deal their damage to the attacker simultaneously, absent special effects. No allocation restrictions, lethal-first rule, damage order, overflow or special combat abilities selected. Afterward damage persistence and readiness.

## Q18d — Blocker order instead of numeric assignment
Steve prefers the attacking player chooses an order between defenders/blockers rather than manually allocating numeric damage (e.g. 2 to A and 3 to B). He is unsure of exact resolution; do not assume sequential retaliation.

Candidate rule to confirm: attacker orders blockers; game allocates enough damage to defeat the first, then remainder to the next. All combatants still deal damage simultaneously, so a blocker assigned lethal damage deals its damage back. Remaining damage stays on blockers unless a specific overflow ability exists; no damage-to-player overflow approved.

Next: Q18e — confirm automatic defeat-first allocation with a concrete example (5 attack versus two blockers with 3 defense each: first takes 3, second 2, both retaliate simultaneously). Then creature damage persistence. Ordering timing and special interactions remain open.

## Q18e — Ordered damage confirmed
Confirmed: attacker chooses blocker order; game automatically assigns enough damage to defeat each blocker before assigning remainder to the next. No manual numeric splitting.

Accepted example: 5 attack versus two blockers with 3 defense each deals 3 to the first (defeated) and 2 to the second. Both blockers deal their damage back simultaneously, including the defeated one. Ordering is damage assignment, not sequential fights that prevent retaliation.

Unresolved: exact defense/damage model, special-effect interactions, when order locks, and overflow abilities. No default overflow damage to defending player approved.

Next: Q18f — damage persistence: clear surviving creatures' damage at end of each player's turn versus keep wounds until healed/removed. Explain strategic differences without assuming MTG cleanup rules.

## Q18f — Persistent damage
Confirmed default: surviving creatures keep damage until healed; no automatic end-of-turn damage clearing. Automatic turn-end recovery, referenced to MTG, is a possible alternate mode for later exploration, not initial scope.

Steve thinks persistent damage could support bigger damage values but may be harder to handle. Stat scale remains undecided; do not infer a requirement for larger numbers. UI must make accumulated damage/current survivability understandable; exact defense versus health model and healing caps remain open.

Next: Q18g — attack exhaustion: does attacking exhaust a creature until the start of its owner's next turn, preventing blocking/helping defend in the meantime? Explain attack-versus-defense tradeoff. Then new-creature readiness and allied blocking details.

## Q18g — Exhaustion and partial blocking
Confirmed: attacking exhausts/taps a creature until its owner's next turn. Steve adds a system allowing exhausted creatures to block at reduced effectiveness while taking increased damage, modifying the proposed complete blocking prohibition.

Candidate number: a 1.5x multiplier for damage and blocking reduction. Exact interpretation unresolved: outgoing combat damage, damage interception, effective defense, or another blocking value; whether reduction divides by 1.5; rounding, damage assignment and spillover. Do not select formulas silently or double-count increased damage and reduced defense. No final multiplier approved.

Next: Q18h — clarify whether reduced blocking means lower damage dealt back to attacker or intercepting only part of incoming damage so the rest reaches the player (or another model). Then propose concrete numeric example and resolve rounding later. Persistent wounds and ordered multi-block damage remain existing requirements; check interactions during rules review.

## Q18h / Q18i — Exhausted blocking and overflow exploration
Steve's example: 6 incoming damage, reduced block stops 3, and blocker with 3 health dies. He then proposed the attacker gains a trample-like effect.

Candidate interpretation to confirm: exhausted blockers allow remaining damage through to defending player (example: 3 to creature, 3 to player). Not yet confirmed as exact formula, universal half-block rule, or lethal-overflow rule. No assumption that fresh blockers also allow overflow.

Still open: does overflow vulnerability replace the earlier extra creature damage multiplier, or apply in addition? Exact multiplier, reduced interception rule, rounding, multiple blockers (including mixed ready/exhausted), retaliation and existing overflow abilities need later specification.

Next: Q18j — use the 6 attack/3 health example to propose overflow as the exhaustion penalty without an additional multiplier; ask whether Steve wants that or both penalties. Avoid treating reference to trample as wholesale adoption of MTG rules.

## Q18j — Multiplied damage and creature stats
Steve prefers multiplied incoming damage for exhausted blockers, rather than overflow alone. Exact multiplier and interaction with overflow remain unselected. He asks whether creatures should have health, attack and defense and whether Pokemon works that way.

Verified reference: Pokemon TCG official rulebook https://assets.pokemon.com/assets/cms2/pdf/trading-card-game/rulebook/pal_rulebook_en.pdf — Pokemon have HP, individual attacks with damage values, and weakness/resistance; no universal separate numeric defense stat.

Proposal to discuss: attack and persistent health as universal creature stats, optional armor/damage-reduction abilities for select cards rather than a mandatory third defense stat. Example 6 damage against 2 armor reduces damage to 4 if using that proposed armor model; this is unapproved. Separate defense adds calculation and can nullify small attackers, affecting multi-blocking, persistent wounds and heal balance.

Next: Q18k — ask whether to start with attack + health, with armor as optional ability, or use three universal stats. Defer exhaustion/overflow numeric rules until stat model established.

## Q18k — Three-stat creature model
Confirmed: creatures have health, attack and defense. Preferred card layout: health bar at top, attack/defense at bottom (MTG referenced visually, not as adopting its toughness mechanic). Pokemon-style specialized attacks are deferred; use the shared combat model for now.

Defense meaning/formula remains undecided. Existing ordered damage examples used defense as defeat threshold; with separate health that interpretation must be revised explicitly, not silently carried forward. Need coherent calculation for damage reduction, persistent wounds, exhausted multipliers, overflow and multi-block allocation.

Next: Q18l — propose defense as flat incoming-damage reduction, with an example (6 attack, 2 defense, 8 health -> lose 4 health, retain 4), and ask if that matches intent or if defense should work another way. Minimum damage, per-hit reduction, exhaustion and ordering interactions remain open. No formula approved yet.

## Q18l — Flat defense and overflow
Confirmed: defense reduces incoming damage by its value. Accepted example: 8 health, 2 defense, 6 incoming attack -> 4 damage, 4 health remaining. This is the standard calculation unless a card changes it. Minimum-damage rules and timing relative to modifiers remain open.

Steve also wants a trample mechanic and says "This should be the standard unless we add cards ... change the specific condition." Ambiguity: standard refers to defense model alone or also to universal overflow. Clarify before adopting global trample.

Next: Q18m — should every attack pass damage exceeding blockers' defense and remaining health to the defending player by default, or only attacks with an explicit trample ability? Use 8 attack vs one ready blocker with 2 defense/3 remaining health: proposed universal overflow would prevent 2, defeat blocker with 3, deal remaining 3 to player. This math is a proposal pending confirmation, not an approved general allocation formula. Mixed/multiple blockers and exhausted multiplier remain to reconcile.

## Q18m — Trample is card-specific
Confirmed: trample/overflow is not universal; it appears on specific cards. It may be more common in a suitable color and less common in others, using MTG green as an analogy rather than selecting green or importing MTG's color roster.

Color design now needs distinguish exclusive specialties (Gold enforcing agreements) from shared mechanics weighted toward particular colors (trample). Do not interpret every color specialty as exclusive.

Pending reconciliation: earlier idea that exhausted blockers grant attackers trample-like overflow. Latest answer rejects universal trample, but does not explicitly resolve this conditional exhausted-blocker exception. Baseline interpretation: ready blockers prevent excess player damage unless attacker has trample; verify exception rather than silently discard it. Exact trample math with defense/multiple blockers still to confirm.

Next: Q18n — should exhausted blockers allow overflow even when attacker lacks trample, or should they only take multiplied damage with overflow still requiring trample? Then settle remaining damage model details and readiness.

## Q18n — Exhaustion and overflow working rule
Confirmed: exhausted blockers take extra creature damage; overflow still requires the attacker to have trample. Exhaustion does not grant automatic trample. This supersedes the earlier conditional-overflow candidate.

Recommendation presented for testing, not finalized by the narrowly scoped confirmation question: multiply damage after flat defense by 1.5 and round up (6 incoming minus 2 defense = 4, then 1.5 = 6). Exact multiplier, rounding, allocation and trample interaction remain playtest/rules-design proposals. Do not treat this as a proven balance point.

Next: Q18o — newly played creatures' readiness: can block immediately but cannot attack until owner's next turn, unless a specific ability overrides? Then allied-blocking consent and remaining core rules. Avoid further damage-formula drilling before a coherent rules draft.

## Q18o — Newly played creature readiness
Confirmed working default: newly played creatures may block immediately but cannot attack until their owner's next turn. Specific abilities can permit immediate attacks. Exact control-change timing and naming of the exception remain unselected; no wholesale adoption of MTG summoning rules.

Next: Q18p — allied-blocking consent: should the defending player accept another player's offered blockers, or can helpers intervene without permission? This concerns ordinary helping, distinct from card effects that may force obligations. Then remaining core rules (randomness, collection/progression, scope/platforms).

## Q18p — Consent and secret negotiation
Confirmed: ordinary help defending requires asking/permission from the defending player. Requests may be private between participants on their devices, without alerting other players.

Unresolved boundary: request/acceptance/secrecy versus actual committed combat actions. Public battlefield requirement suggests actual blocking must become visible before resolution; do not assume secretly resolving blockers or hiding relevant public actions. No general private chat, pre-authorized betrayal, timing extension, or private offer revealing hidden cards approved.

Next: Q18q — confirm request/negotiation may stay private but committed blockers become public before resolution, giving others their normal response opportunity. Then move beyond detailed combat to Q19/Q20 combo limits/randomness and remaining discovery.

## Q18q — Public deals after acceptance
Confirmed: once a deal is made, it becomes public on the main screen so everyone can see what is happening. Committed blockers/actions are visible before resolution with ordinary response opportunities as proposed in the question. Visibility alone does not make ordinary promises binding; Gold/card-enforced commitments remain the exception.

Candidate: secret deals could be exclusive to one color, e.g. black representing sneakiness. No final black identity or exclusive private-negotiation rule approved. Earlier private requests were a general feature; reconcile the proposed restriction explicitly rather than applying it silently.

Next: Q18r — should all players make public offers while only the sneaky color may negotiate privately, with accepted deals always public? Alternatively keep private requests universal and define a distinct stealth mechanic later. Ask this scope choice; preserve accepted-deal visibility either way. Then Q19/Q20.

## Q18r — Private negotiation access
Working direction accepted: public offers available to everyone; private requests enabled through a sneaky color's cards or abilities. Accepted deals still become public on the main screen. This qualifies earlier general private-request availability. Black remains a candidate name/identity rather than finalized color roster.

Exact private-request access, costs, duration, terms, notifications, target consent and interaction with Gold enforcement remain unresolved. No requirement for persistent private chat or concealment after deal acceptance.

Next: Q19 — tolerance for disruptive play: should card effects temporarily interfere while preserving opportunities to act, or also allow sustained denial (e.g. repeated turn skipping/resource destruction)? Present a family-accessible recommendation and clarify preference. Then Q20 randomness, progression/content and platform scope.

## Q19 — Disruption and optional change-ups
Steve accepts the recommended direction: allow interference and big reversals while avoiding combinations that prevent meaningful play for several turns. This is a design/balance goal, not a completed prohibition list or automatic enforcement formula.

He proposes optional fun "change-ups," inspired by UNO reverse/skip effects, that kids may enjoy. Explicitly outside the main game/core initial rules; add as an optional extension as the game develops. No specific skip duration, reversed turn/response order, deck insertion, trigger, exact branded card or implementation approved. Future optional rules still need reconcile pacing, turn-based resource growth and anti-lockout goals.

Next: Q20 — randomness beyond shuffled draws: mainly deterministic card effects versus some dice/coin/random-target effects, possibly confined to optional change-ups. Then Q21 support (largely covered), Q22 collection/progression and remaining audience/platform questions.

## Q20 — Randomness and potential Silver identity
Confirmed: most card effects should be predictable. Occasional dice-roll/coin-flip effects are welcome, reserved for "gambling" or risk-taking cards.

Candidate color: Silver for that identity, explicitly tentative. Exact chance mechanics, odds, stakes/rewards, exclusivity, target randomness and frequency remain unselected. Do not infer real-money wagering, monetization, paid packs or a requirement that all Silver cards use randomness. Separate from optional future change-up extension; selected chance cards can belong to core card design.

Next: Q22 — should all players have the full supported gameplay card/effect library available, or unlock cards/effects through play? Explain cosmetic progression as separate from power access; no collection system selected. Q21 accessibility is largely covered; revisit unresolved help controls later.

## Q22 / Q21 — Universal access and reading independence
Confirmed: everyone gets access to all gameplay cards and supported abilities/effects; no progression-based gameplay unlock gate. Cosmetic rewards/achievements were suggested previously but have not been selected.

Confirmed requirement: card text scales to age/reading level so children can understand cards independently rather than always asking for help. Adults remain available for questions. Adapt presentation without silently changing mechanics between readers. Exact reading levels, manual controls, explanations/read-aloud and text generation approach remain open; no AI dependency or universal perfect-comprehension guarantee selected.

Confirmed extensibility: add more cards and abilities/effects over time. Distinguish content using existing effects from newly implemented effects; initial fixed effect library is expandable, not permanently frozen. New effects require engine support/rules text/balance validation before use; exact authoring/plugin pipeline remains to design.

Next: Q24/Q25 — intended audience/distribution (household only, invited friends, eventual public release) to inform content and platform planning. Q23 tutorial/learning approaches largely covered. Revisit reading-level UX and content limits later.

## Q25 — Audience and visitors
Confirmed initial audience: household only. Future desirable convenience: visitors scan a QR code or similar to download/install and play. Lower priority, not initial release requirement. No public release or app-store distribution selected.

QR code may link to platform-appropriate installation/join instructions; do not promise one-step installation on all devices before verifying Android/iPad/TV constraints. Download versus room join are distinct steps to design later. No guest account/cloud service choice approved.

Next: Q26 — first TV platform priority: Google TV, Roku, or both required initially? Android phones and kids' older iPads remain requested personal-device support; iPad hardware details deferred. Then Q28 offline operation and Q29 location.

## Q26 / Q27 — Required TV platforms
Confirmed: both Google TV and Roku must work from the start. Household devices: Google TV Streamer in bedroom; Roku TV in living room. Do not defer either platform by default. Android phones and older iPads remain personal-device requirements; exact iPad details intentionally deferred.

Implementation still undecided. Build-planning team must verify current official platform capabilities, installation/distribution, networking and remote/input constraints before choosing an architecture; do not assume shared native binary, runtime, browser availability or one-click installation.

Next: Q28 — must installed matches work entirely without internet while home Wi-Fi/local network remains available? Distinguish gameplay/local content from optional future content generation/downloads. Then remote play/hosting requirements.

## Q28 — Offline priority and TV-free fallback
Steve wants installed games to work without internet on the home local network, but explicitly says this is not a priority. He notes internet outages at home usually coincide with power outages. Record offline operation as a lower-priority goal, not a mandatory first-release acceptance gate or a decision to require cloud gameplay.

Future desirable fallback: play without requiring a TV, explicitly can come later. No phone/tablet shared-board layout, hosting behavior or alternate hardware selected. Both TV platforms remain first-version requirements for the normal experience.

Next: Q29 — same-household local-network participants only initially, or remote players from another location required? Then hosting, reconnect/save behavior, profiles and remaining creation/platform questions.

## Q29 — Initial multiplayer location
Confirmed: initial players are in the same house on the same network. Remote play deferred. Visitors joining locally remains a lower-priority future convenience.

Next: Q33 — explain hosting options and ask whether requiring a separate home server/computer is acceptable or the game must run using only TVs and personal devices. Do not select architecture before official platform feasibility review. Then reconnect/save behavior, profiles, creation content/art and other remaining requirements.

## Q33 — Preferred host and storage
Confirmed preference: run the game from Steve's home Linux server if possible, including storing the card library there; he reports substantial available storage. This is the preferred authoritative match host and centralized content-storage direction, subject to feasibility validation. TV and personal devices remain clients; no implementation stack selected.

Server hardware/OS/runtime capacity, deployment, backups, profile/deck persistence and content delivery details remain to verify during build planning. Do not assume ample storage implies adequate AI-generation compute or commit to generation on server. No deployment or server modification authorized/performed in this discovery step.

Next: Q34 — what should happen on a temporary player-device disconnect: pause and restore their hand/turn on reconnect, versus continue/automatic actions? Recommend pause/reconnect for household matches; then saved-session resumption and profiles.

## Q34 — Temporary disconnection
Confirmed: pause match when a player's device disconnects; on reconnect restore their exact hand and place in the game, as proposed in the question. No auto-pass, substitute AI or disconnection forfeit selected.

Unresolved: reconnect identity/device replacement, disconnect detection, handling abandoned sessions and server restart. Keep private state protected during reconnect; exact implementation later.

Next: Q34a — should household be able to deliberately save/pause a match and resume another day? Distinguish persistent saved matches from temporary disconnect recovery. Then profiles/deck storage and remaining content/UX questions.

## Q34a — Deliberate saved matches
Steve would like deliberate save/close/resume-another-day if possible, but it is not necessary. Lower-priority convenience, not an initial release blocker. Required temporary-disconnect pause/reconnect remains distinct. No persistence mechanism or server-restart recovery guarantee selected.

Next: Q35 — propose household profiles stored on the server, with decks and reading preferences following each person between devices; ask whether profiles require a simple PIN versus unrestricted profile selection. Exact identity/access policy not decided. Then Q30 device allocation, Q31 TV creation privacy and remaining content/UX requirements as needed.

## Q35 — Profile selection
Confirmed: select a household profile by tapping the name; no PIN required. Server-stored decks/reading preferences following profiles across devices was recommended in the question context; specific synchronization/storage behavior not separately confirmed.

Use a household-trust model, not claims of strong authentication. Keep opponent hands off the public TV and unrelated clients; define match-seat/device association and deliberate device switching without adding a mandatory PIN against this preference. No general user-management permissions selected.

Next: Q30 — confirm every player uses their own phone/tablet during matches, versus shared-device or TV-only play required initially. TV remains public board. Then Q31 TV deck-creation visibility, controls/content/art and remaining requirements.

## Q30 — Player devices
Confirmed: first version may require each player to use their own phone/tablet during matches; this is Steve's ideal setup. TV is the shared public battlefield, personal devices show private hands. Shared-device/hot-seat or TV-only private-hand match play not required initially.

This does not remove original requirement to create decks from the main TV app outside matches. TV-free fallback remains deferred.

Next: Q31 — is TV deck/card creation visible to everyone in the room acceptable, with personal devices used for private building? Then remaining content/art, accessibility controls, household administration, budget and first-playable milestone questions.

## Q31 — Creation-device priority
Steve prefers the majority of card/deck creation on each person's own device. Personal phones/tablets are the primary creation experience.

This changes emphasis from original phone-or-TV creation brief, but does not explicitly remove TV editor support or say whether it may be deferred. TV editor/privacy scope needs one clarification; do not silently retain a full editor as a first-release gate or remove it entirely.

Next: Q31a — may full TV card/deck editing be deferred, with initial creation on personal devices and TV focused on shared match display? Then remaining content/art/UX/budget and first-playable milestone.

## Q31a — TV editor deferred
Confirmed: full TV card/deck editor deferred. Initial TV apps focus on shared match display; creation tools focus on personal phones/tablets. Both Google TV and Roku remain required from the start. This supersedes the original requirement to build/edit decks on the TV initially.

Next: Q24a — card artwork creation workflow: user-uploaded pictures/drawings, built-in art/assets, generated artwork, or a combination. Do not assume AI art, paid services, local image-generation compute or rights/distribution decisions. Then family content preferences, reading assistance, household controls, budget and first playable milestone.

## Q24a — Artwork and card creator
Requested creation paths: camera import for a child's drawing; built-in general images to select; AI-generated customized card artwork. No provider, generation architecture, cost, local compute assumption or release prioritization selected.

Simple card creator controls requested:
- Choose card type.
- Choose what card does from supported rules/effects, respecting established color/trait/balance constraints.
- Choose visual style (examples: anime, 3D-model appearance, line sketch; not exhaustive).
- Name entry or generated name.

"3D model" here is an art-style example, not a requirement for interactive 3D assets. Camera permissions/import processing, cropping/background cleanup, visual prompt controls, text/name generation and preview/save UX remain to design. Generated art must not define executable rules; exact rules text should reflect selected supported effects.

Next: Q38a — whether AI art may use a paid online service with a budget or must have no recurring/per-image cost. Explain generation compute/services can be distinct from local match hosting; do not assume user's ChatGPT subscription covers an embedded API. Then content/accessibility/controls and milestone.

## Q38a — No paid image-generation usage
Confirmed: no ongoing/per-image service costs. Steve can consider a local image generator if feasible; asks whether linking out to ChatGPT/Gemini avoids API fees.

Research 2026-11-17: ChatGPT Plus image generation is included within app limits, ordinary API usage billed separately (https://help.openai.com/en/articles/6950777-what-is-chatgpt-plus). Participating-tool allowance sharing exists for eligible tools but custom image-generation eligibility not established; do not assume arbitrary app integration. Gemini supports image generation without Google AI plan with usage limits (https://support.google.com/gemini/answer/16275805) and image downloading (https://support.google.com/gemini/answer/14286560).

Proposal: generate a prompt in card creator, copy it, open chosen consumer service, user generates/downloads image, then imports it. No paid API call; user-mediated external workflow, not automatic generation/return. Availability/account/age restrictions and limits apply; do not require children to hold external AI accounts. Local generation would support a more integrated path if available hardware permits; storage capacity alone insufficient to establish feasibility.

Next: ask CPU/RAM/GPU and GPU VRAM of Linux server or another available generation machine, allowing details to be deferred. Then finalize preferred fallback and remaining content/accessibility/budget/milestone discovery. Do not pick a local model before hardware verification.

## Q38b / Artwork — ChatGPT Plus workflow and art consistency
Steve has ChatGPT Plus and prefers using it for image generation without API fees. Available alternative generation hardware is his existing PC; prior context lists Ryzen 5 and GTX 1650, exact RAM/VRAM not verified. Do not ask him to repeat known specs or assume local model feasibility.

Requested: reusable prompt assembled from card data, art-style selection, mood selector (examples fun/funny, spooky), and a fixed portion ensuring consistent game-card composition/template fit. No specific final dimensions, frame or style taxonomy chosen.

Working generation path: copy generated prompt, open ChatGPT on user's account, manually generate/download, import artwork. Plus image generation within its limits is separate from ordinary paid API use (official reference https://help.openai.com/en/articles/6950777-what-is-chatgpt-plus). Do not imply arbitrary app integration, automatic result return or sharing adult login with children.

Recommendation pending acceptance: generate artwork only, with fixed aspect/composition rules; app renders uniform frame, live health, attack/defense, name and reading-level-correct rules. This avoids baking mutable game text/stats into image pixels. Consistency prompt improves composition but cannot guarantee exact layouts by itself.

Illustrative prompt schema (not final art specification): subject/persona; traits/appearance; visual style; mood; scene/ability cues; fixed output aspect ratio and safe framing; clear subject at small size; no text, numbers, card border or UI. Mechanical card data used as visual cues must not override supported rules.

Next: confirm artwork-only generation with app-rendered consistent frame/text/stats versus generating entire card image. Then remaining content/accessibility/controls and initial milestone. Local image generator remains optional later, no additional hardware requested.
