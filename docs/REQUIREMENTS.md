# The Crucible — Confirmed Requirements
Consolidated 2026-11-22 from the current design conversation. This document and RULES_DRAFT.md supersede historical ANSWERS.md, DISCOVERY.md and obsolete proposals. Numeric values are playtest candidates, not verified balance. A combat lab and restricted local full-match practice harness are implemented. The networked household product remains future work. PROJECT_STATE.md owns current implementation and validation; product requirements below are not a feature-completion claim.

## Experience and scope
Original local household multiplayer card battler for adults and children, typically four players; 40–60 minute familiar-play target. Android phones/tablets, older iPads, Google TV and Roku public displays remain required for the first completed game. Installed/packaged clients preferred; secure iPad home-screen web app acceptable under existing Screen Time browser restrictions, weekly native reinstalls accepted fallback. Actual iPad models/OS and installation feasibility remain untested. Home network only initially; automatic discovery with manual address fallback. Linux authoritative server; Windows PC artwork worker. No timers or response countdowns initially; allow future extension.

Creative themes independent of mechanics/color. Cartoon-style content, no realistic gore or swearing; future maturity levels deferred. Researchers discover across realities in The Crucible; Relic-Ring stable arena, Ring-Keepers, Vanguard Cores and 40 Sparks. Lore must not imply defeated cards/resources automatically recycle. Player revival has been scrapped; leader recovery remains.

## Colors and accessibility
All colors have a viable independent toolkit, all three basic creature profiles and an easy-to-pilot option of comparable intended strength. Well-rounded does not mean equally efficient at everything.
| Color | Identity | Specialty |
|---|---|---|
| Red | Drive | Reliable aggression, early pressure |
| Orange | Daring | Bounded risk/reward aggression and contingency |
| White | Discipline | Coordinated defense and counterattack |
| Green | Resilience | Growth, creature healing/endurance, permanent resource growth |
| Gold | Cooperation | Self/team protection; limited rewards for real accepted assistance |
| Blue | Insight | Information, timing, control and reactions |
| Purple | Cunning | Disruption and milling |
| Black | Ambition | Sacrifice and meaningful resource/health trades |
| Silver | Ingenuity | Upgrades, assembly, stored resource tokens |
| Teal | Adaptability | Flexible modes and changing roles |
Transform/combine available across colors when fitting. No universal color advantage chart; optional explicit intuitive card vulnerabilities, with exact tags/bonuses unresolved. Gold works alone/in duels, not dependent on an ally; assistance can be accepted/declined and rewards need actual benefit/cost/caps. Tactical trait effects do not infer moral truth from real speech. Detailed bargain enforcement remains outside settled core.
Reading level affects explanations, never rules or strength. Setting accessible in normal device Settings; players and parents can adjust. Speaker buttons, optional automatic narration off. Inspecting/read-aloud does not pause. Icons and public-information damage previews; reactions can change predicted outcomes.

## Decks and lobby
40 singleton cards plus separate designated leader; one color plus generic initially, two colors later, possible 60-card future testing. Small gameplay changes create distinct variants; name/art-only changes do not bypass singleton. Same character variants can coexist, including ordinary creature versions of a leader. Deck legality errors block approval; strategy/complexity warnings do not.
Lobby requires legal confirmed deck, selected leader and ready status for everyone before host starts. Deck/leader selections visible openly in lobby, card lists private unless deliberately shared. Changes clear readiness; match start freezes choices/rules/definitions/cosmetics.
Five opening cards; one free selective redraw: set rejected cards aside, draw replacements, shuffle rejected back. Choices private; replacement counts revealed only once all lock. Starting player and fixed order revealed after redraw (leaders already visible).
One draw at each own turn start; first player skips first draw in duel only. Seven-card end-turn limit, legal plays before ending then discard excess. Discard does not normally reshuffle.
30 player health initial; an unrecovered failed required draw or health <=0 permanently eliminates. Empty deck alone does not eliminate; the approved Recharge extension below can end an own turn. Milling supported. No player revival or final revival windows. Last active wins after pending valid effects/cleanup; simultaneous all-out is draw.

## Gameplay detail
RULES_DRAFT.md is the consolidated mechanics reference: attack/health only with persistent wounds, exhausted blocking, Challenge, Breakthrough, phases, costs/response chain, leaders, transformation/combine, tokens, upgrades and elimination. Old flat defense/full bypass and all player-revival rules are superseded.
Starter leaders one reserve and one battlefield ability. No commander-damage counter.
Initial starter baseline 24 creatures, 10 actions/reactions, 6 upgrades/other persistent cards, adjustable by color. Ordinary creatures mostly zero/one ability; one main strategy plus supporting plan. Simple attacking must remain enjoyable and viable, including Silver/Gold easy-pilot decks. No hidden child power bonuses.
Initial ability-free profiles, ATK/HP: cost1 2/1,1/2,0/3; cost2 3/2,2/3,1/4; cost3 4/3,3/4,2/5. Most creatures cost1–6, major threats7–10+. All provisional. Establish baseline then price abilities; small-body vs large-body tests each tier. User authorizes sensible numeric candidates/tests autonomously; ask consequential tradeoffs, not each numerical fixture.

## Guided creation and catalog
Theme -> suggested/customizable color -> leader -> small guided card groups -> review -> artwork queue. Three themed balanced leader concepts with plain play-style summaries plus invent-own-character. Supported tested effect templates assign stats/costs; free description never becomes executable rules. Concept/scale suggest roles, not hard species cost. Themes include any creature concept within content boundaries.
Guide highlights early plays, defense, answers, draw, curve and interactions with reading-level wording/TTS. Surprise me/Finish my deck throughout. All colors offer easy-to-pilot choices, adjustable on unfinished deck without changing theme/color/leader; preview/approve swaps. Keep in deck in card menu with enabled marker; does not override legality.
At most two validated gameplay traits initially; labels only, abilities explicit. Names/art cannot silently add tags or power. Thematic conflict with vulnerabilities prompts compatible alternative.
Final review short play guide; expandable analysis. Autosave private drafts. Legal drafts playable with placeholders against computer before publication.
Published finalized cards permanent searchable household catalog; unfinished drafts private/deletable. Archive own cards instead of deleting; archived usable in existing decks and findable with include-archived for new decks. Removing from deck doesn't remove catalog card.
Everyone can use published cards and make named gameplay variants; original unchanged. Published gameplay edits create distinct named variant, same character grouping; shared original/household rule administration parent-only. No exhaustive revision history required; retain reusable current values/art and match-pinned definitions.
Deck theme-based suggested editable name, leader-art default cover with optional saved artwork. Duplicate decks independently. Completed lists private by default; optional household sharing allows independent editable copies, source/creator credit retained, no synchronization/update feature. Unshare prevents new copies via listing, existing copies remain. Cosmetic entitlements don't transfer.

## Artwork and cosmetics
Illustration only; app draws frame/text/stats. Deterministic prompt template combines concept/style/mood and fixed composition/safe margins/readability for standard/full-art crops; no AI prompt-building call. Generate after concept/mechanics approval. Batch queue can process sequentially, save each output to server as finished for immediate review. Placeholder deck playable; approved artwork only applied between matches.
Creator approves individual/batch; reject keeps placeholder/current art, no automatic retry. Secondary Try again with correction while preserving mechanics/fixed art instructions. Reuse library images with crop preview. Retain ALL generated/imported artwork incl rejected/unused alternatives; deleting/archiving cards does not delete images.
No ongoing image/API charges; local PC generator preferred conditional benchmark; Ryzen5/GTX1650 known, RAM/VRAM unverified. Swappable backend. Supported ChatGPT Plus unattended worker access NOT established; ordinary API separate, no paid fallback or browser automation dependency. Use lightest suitable backend option when available, no routing/usage guarantee.
Leaders distinct attractive full-art layouts with reserve/battle abilities and exact summon costs readable separately. Cosmetics layered instantly from saved artwork: frames/holo/borders/foil etc; no generation needed. Standard cards default normal until owner explicitly assigns unlocked treatment via Change Appearance; no default-per-deck override system. Choices public on owner's used instance; others' same card unchanged. Stolen same instance retains look; copies inherit for match only. Changes outside matches; active/saved match appearance frozen.
Persistent profile avatars; 16 premade. Theme/leader avatar created with deck art, reuse where possible; anyone chooses any existing avatar. Deck changes do not change avatar automatically.

## Progression and practice
No real-money connection EVER: no paid currency/cosmetics/gameplay, ads for rewards, cash-out or random paid packs. One earned cosmetic currency recommended direction. Per-profile permanent unlocks, selectable original/unlocked looks. One-time automatically awarded achievements, repeatable capped meaningful match participation bonuses; varied card/color/creature defeat/transform/combine/help milestones, not wins only. Prevent meaningless repeated actions/concession/reconnect farming; no stronger gameplay unlocks.
Cosmetic shop preview exact appearance/price then confirmation, no adult approval. Own balances private, achievements/unlocked cosmetics/lifetime stats visible to household; no overall sibling leaderboard by default.
No reward popups in match. Shared TV fun personal statistical highlights after match; achievements/currency/loot/progress on individual devices. Define stats precisely; no automatic hand/deck reveal.
Simple code-driven balanced practice opponent default, optional play styles; no paid AI opponent. Reduced practice currency/selected achievements with safeguards. On-demand Hint button, one suggestion+why, reading-level/TTS, no automatic card/target/payment selection. Hidden-information-safe, no best-move promise. Also available in family matches; default on, host toggles for everyone, use optional/private, no reward penalty.

## Match presentation and privacy
70-inch TV: fixed player zones throughout, public full overview plus contained action spotlight, always-visible health/resources/counts/leader/turn. Dynamic compact tiles/multiple rows and readable minimum; no creature cap adopted. Identical token/copy instances group only with matching health/status, tap-expand; distinct cards visible.
Entrance/transform/combine effects about <=1s, modest flair, never hog screen, block controls or delay gameplay; shorten/merge overlap. Animations on by default, off per device only, static equivalents. TV highlight action without removing overview.
Public board/leader/discards/exile/counts/resources/chain inspectable anytime on personal devices. Private hands/deck order/lists remain hidden; shared catalog doesn't reveal deck composition. Public history remembers reveals but doesn't track hand position/continued possession. Public action log tappable only permitted card details. Tentative selection/targets/previews private until confirmed.
Browse others while waiting; persistent neutral waiting-for-player prompt on TV, no legal-response leakage. Personal one gentle vibration per new request if supported; visual always, sound default off, no repeated buzzing.
No chat/DM/text messaging. Oral negotiation; preset disappearing reaction emoji with avatar, short anti-spam cooldown; active/eliminated/spectators allowed, nonblocking.

## Profiles, permissions and operation
Persistent profiles, device remembers last with easy switch. Active-match switching requires leaving or adult approval; never exposes another hand. Adult profiles require PIN on entry and restricted approvals, not repeated ordinary gameplay. One-time adult-approved device pairing, automatic reconnect, revocation in Settings requires re-pair.
Any player requests pause; host/adult approves/resumes; inspect/TTS while paused, game actions stop. No timers. Disconnect auto-pause, state/hand restored, host resumes; designated adult takeover. Concede confirmation, no parent approval. Cancel freely before confirmation; committed actions no general undo.
Automatic durable save after committed actions/pending responses, adult Pause and exit; exact recovery paused. Midnight local America/New_York backup on days with gameplay or saved changes; retain seven daily plus four weekly, deduplicate unchanged art. Keep live artwork library independently of backup rotation. Separate-drive destination advisable but unselected.
Server authorizes private projections; never send hidden cards to TV then conceal visually. Device trust/PIN/transport/storage design still needs implementation review.
Future scope: timers, two colors, remote/visitor/TV editing, maturity levels, Pierce, effect-copy cards after starter phase, deeper card packs. Planning alone does not authorize deployment or purchases; later development authorization is recorded in the current project checkpoint.

## Balance lab request
User wants rigorous local computation instead of spending AI tokens per test. Build-plan direction: reusable game rules engine -> headless automated runner -> simple desktop dashboard; mobile report companion later candidate. Desktop preferred PC compute; no runtime LLM dependency. Export CSV/JSON/readable HTML, replay seeds/logs, batch scenarios/full matches as coverage grows. Compare multiple policies (straight attack for youngest, defensive, resource-aware, stronger later); identify policy weakness vs deck weakness. Use summaries/outlier replays for AI analysis, not bulk raw logs. The lab, local match harness and seeded policy studies now run locally. The original planning-only request is historical; current work is in PROJECT_STATE.md.


## Deck-refill extension requested 2026-11-22
Add a costly fixed-life trade to reshuffle discard/graveyard into the deck. Repeat
use should need deliberate life-gain support. Draw-time refill/turn-loss/Recharge timing is approved below; exact life cost
remains provisional (DECK_REFILL_DESIGN.md). This is an explicit exception
to the ordinary non-reshuffling discard rule, not a free automatic recycle.
Simultaneous private blocker locking/reveal is approved for multiplayer defense.


Deck-refill timing now approved: finish remaining required draws after valid
paid discard refill; eliminate if no accepted valid refill can complete a required
draw. Own-turn exhaustion/refill ends the current turn; an empty next Start offers
refill and then ends that turn. Off-turn refill causes a full next-turn Recharge
with Start/End maintenance but no normal draw, voluntary play/abilities or Combat.
Ordinary off-turn blocking/reactions remain. No additional next-turn penalty for
an own-turn refill. Recharge lore is Vanguard Core stabilization. Exact fixed
life cost is not adopted; evaluate with the lost-turn cost included.


## Card-face information contract approved 2026-11-22
CARD_INFORMATION_CONTRACT.md is the shared baseline for standard and full-art
cards: name, color/Generic identity, type/role, play/access information, artwork
and applicable rules content. Creature stats, traits, leader/location abilities,
forms and unusual costs appear when relevant. Live instance overlays are separate
from base definitions. Cosmetics preserve all gameplay information. Filled
CARD_CONTENT_EXAMPLES.md entries are template candidates, not approved/balanced
starter content. No catalog schema or renderer implementation is implied.
