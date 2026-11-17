# Card Battler — Project State

Updated: 2026-11-17. Phase: discovery interview. No gameplay rules or technology stack approved.

## Resume here
Read this file, docs/ANSWERS.md, and relevant questions from docs/DISCOVERY.md. Q01–Q05 and initial Q14 leader role covered. Q06 answered. Q07c confirmed as a working rule. Q08 requires continued participation plus conditional re-entry. Re-entry mechanism under exploration. Latest proposal: leader revive abilities with selectable conditions/costs during leader creation; examples involve giving hand cards to another player or discarding the whole hand. Q08c: cost should mainly come from the dying/defeated player's hand. Proposed full-hand payment safeguard and drawing when short. Next: Q08d, clarify whether drawn cards are paid away/discarded or retained, and whether drawing tops up versus adds a fresh hand. Do not force final choices; retain candidates for later comparison. Then participation, empty-hand eligibility, retained state, limits and final victory timing. Singleton scope/exceptions, deck size and detailed leader rules need later clarification. DISCOVERY.md's original status line predates the answers; this checkpoint and ANSWERS.md are authoritative for progress.

Ask one question per turn. Clarify consequential ambiguity without inventing requirements. Save substantive answers and implications. Distinguish user decisions from proposals and unresolved questions. Complete discovery before convening a second expert team for implementation planning.

## Confirmed brief
- Original card game: MTG depth/card-library variety, Pokemon character appeal/accessibility, Elestrals ease, Munchkin helping and playful betrayal.
- Commander-like group play. Singleton format and a deck leader requested. Leader need not follow Commander rules or require casting. No separate commander-damage count. Initial leader direction: both influence deck/play style and participate in combat. Steve welcomes proposals and possibly selectable/additional leader mechanics eventually; no particular variant system approved. Singleton scope/exceptions, deck size and detailed leader mechanics remain open.
- Desired funny moments: children teaming up against adults; a parent recruiting a child to help defeat the other parent. Assistance mechanics and alliance structure remain open.
- Independent interest-themed deck creation on personal devices or TV. Themes include superhero/transforming robots, nature/cryptids, crafts, fantasy/scifi; not an exhaustive list or fixed factions.
- Locally installable Android and Google TV/Roku experiences requested; initial platform scope unresolved.
- Personal devices show playable cards privately. TV shows shared battlefield without exposing opponents' hidden cards.
- Plan actual gameplay here, then build plan with a second expert team. All durable details saved to this repository.

- Youngest intended player is six, learning to read quickly. Game should grow with children. Steve prefers retaining match depth and complex mechanics with understandable wording. His wife is also a card-game newcomer. A welcoming initial setup/learning experience and lasting family replay appeal are goals. Earlier match-simplification idea is not the preferred approach; exact onboarding tools and deck guidance remain open.

- Onboarding requested: simple tutorial game mode; deck-creation tutorial covering different ways to build; in-game tutorial guidance. Proposed approaches include a play-style questionnaire and small practice scenarios against an "AI". Opponent implementation, creation paths and tutorial controls remain undecided. Resource/archetype examples are illustrative, not selected rules.

- Regular matches should have four players. Steve would ideally accommodate anyone who wants to play; larger groups are an aspiration. Maximum, minimum and scaling rules remain unresolved, with no unlimited-player commitment.

- Target regular four-player match duration: approximately 40–60 minutes once players know the game. Design/playtest target; no enforced timer decided.

- Initial match scope: player-versus-player battles only. Future modes/features must be supported by intentionally designed API/plugin-style extension interfaces. Exact extension boundaries and plugin types remain open for build planning; do not promise arbitrary runtime plugins across platforms or add future modes to the initial scope.

- Initial victory structure: one shared goal only. Revised direction supersedes leader-defeat candidate: players are attacked; creatures/cards attack and defend (MTG reference, not wholesale rule adoption). Working rule confirmed: zero player health defeats that player; last remaining player wins. Steve explicitly leaves this open to future revision. Starting health and simultaneous-defeat rules remain open. Subsequent Q08 requires ongoing participation and conditional re-entry after defeat, so define final victory timing relative to possible returns; do not treat zero health as permanent elimination. Other victory modes and leader-specific goals are deferred.
- Revised leader proposal: outside battle initially, possibly with a passive ability; a specific condition allows entry for a major attack/effect. Condition, passive details, duration, reuse and strength remain unresolved.

- Defeated players must have a way to participate and conditionally re-enter active battle. Trigger, participation actions, ally involvement, return state/cost/limits and final victory timing remain undecided. Preserve the 40–60 minute match target when proposing rules.

- Leader-linked revival is the latest candidate: possible choice of revive condition during leader creation, with giving away/discarding hand cards as illustrative costs. Cost payer is primarily the defeated player. Full-hand payment with drawing when short is proposed; draw/payment sequence, hand size, ownership/target, selection limits and exact rules remain unconfirmed. Revive cards have not been conclusively rejected.

## Open decisions
Remaining reading-support details, supported player-count range and larger-group/tutorial duration, win/elimination rules, leader role, turn/resource/combat/reaction systems, helping/betrayal mechanics, deck construction, theme-to-mechanics mapping, custom-card balance, art/creation tools, progression, offline/remote play, hosting, TV priority, device/input needs, budget/distribution and first milestone.

## Completed work and workflow
Three expert discovery reviews completed: rules; family/content creation; platform planning. Consolidated queue in docs/DISCOVERY.md; answers in docs/ANSWERS.md. Queue is adaptive, not a commitment to ask redundant questions.

Model recommendations: GPT-6.1 Sol for interviews, documentation and ordinary implementation; GPT-6 Astra for focused difficult rules/architecture reviews. Agents inherit this session's model; no automatic switch claimed. Verify current platform constraints using official sources before selecting technology. Conserve tokens with short canonical records, scoped specialist briefs and reviews at meaningful phase boundaries.
