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

Next: Q07c — confirm whether reducing player health to zero eliminates that player, with the last remaining player winning. Then clarify post-elimination participation and leader entry design.

