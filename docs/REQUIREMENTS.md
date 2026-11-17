# Confirmed Product and Gameplay Requirements
Updated 2026-11-17. Canonical concise requirements after discovery. Historical answers: ANSWERS.md. Later explicit user choices supersede earlier brainstorms. Numeric defaults are playtest values, not proven balance.

## Experience and scope
- Original multiplayer card battler: strategic depth and library variety, appealing characters, accessible learning, alliances/help/betrayal.
- Desired moment: children gang up on adults, or parent recruits child to defeat other parent.
- Four regular players, target 40–60 minutes once familiar. Larger groups desired; supported maximum undecided.
- Household, same local network initially. Player-versus-player battles only initially.
- Roughly ten trait/play-style color identities desired; complete roster unapproved. Gold integrity/agreement enforcement is established direction; Black cunning/private negotiation and Silver daring/chance remain candidate names.
- Single-color decks plus generic cards initially. Two-color decks later. Colors restrict effects/card eligibility; generic no-color cards usable by all.
- Persona/theme independent of color: robots, superhero teams, nature/cryptids, crafts, fantasy/scifi and other themes all possible.
- Some effects color-exclusive (Gold enforced agreements); other abilities can be more frequent in one color but shared elsewhere (trample).
- Fixed supported rules/effect library initially; new implemented effects and cards added over time through extension interfaces. No unrestricted natural-language executable card rules.

## Decks, hands and victory
- 40 singleton draw-deck cards plus separate leader initially; possible move to 60 after testing.
- Small gameplay differences can distinguish variants. Same character may appear across cards. Exact duplicate identity algorithm unresolved; do not impose substantial-change threshold. Cosmetic-only uniqueness was interpreted insufficient under user's nonidentical condition, but not separately confirmed.
- Five starting cards. One free selective opening redraw: keep wanted cards, replace same number, rejected cards reshuffled into deck. Shuffle-versus-draw sequence unselected.
- Draw one at start of each own turn; first-player adjustment unselected.
- End own turn at seven cards maximum: play normally legal cards with ordinary costs before ending, then choose excess to discard. Precise end-phase ordering to specify.
- Start player health 30 for playtests; user imagined 50 and accepts upward tuning.
- Defeat at zero player health or failed required draw from empty deck. Empty deck alone does not defeat; mill/deck-depletion strategies supported.
- Last remaining active player wins, after one bounded final revival opportunity. Exact victory checkpoint/eligibility and simultaneous defeats unresolved.
- Defeated players retain participation and can conditionally re-enter. Detailed revival rules explicitly deferred to card planning.
- Latest revival candidate: leader-linked ability primarily paid from defeated player's hand, giving/discarding a full hand; drawing if short proposed. Hand size/top-up sequence, eligibility and limits NOT selected. Differential return health for giving versus discarding proposed, not formula approved.

## Resources and turns
- Sequential player turns; public actions visible, private hands on each player's device for planning.
- Universal resource type, individual player pools. At start of owner's turn add one capacity then refill. Starting capacity, cap and exact phase ordering unselected.
- Resources spent stay spent through opponents' turns unless explicit effect restores/adds.
- Temporary resource gains and permanent capacity increases exist; permanent growth costs significantly more. Exact costs/durations/rarity implementation unselected.
- Additional leader resource-growth triggers proposed, e.g. creature-defeat rewards; formula unselected.
- Colored resource costs are future extension, not initial mode.
- Instant-like cards can act out of turn. Responses may chain; newest resolves first, one effect at a time; response window reopens between resolutions.
- Fixed response/pass order around table, not fastest tap. Exact start/reset/pass semantics unselected.
- Highlight legal plays; even if no legal response, player sees Pass as sole gameplay action and must explicitly pass. Automatic skip was rejected.
- Show pending effects, targets and resolution clearly. Preview only public conditional results; don't expose hidden response options through public UI.
- Timing policy must remain revisable; no in-match arbitrary rules switching selected.

## Combat
- Creatures attack players; attackers may split across opponents.
- Defender chooses blockers; multiple creatures can block one attacker.
- Attacker orders blockers; for ready blockers, raw damage needed to defeat = defense + remaining health. App assigns that amount to first, then remainder to next; defense reduces each allocated hit before health loss. Combat damage/retaliation simultaneous, so defeated blockers still retaliate. Combine all blockers' attack damage against their attacker, then apply that attacker's defense once; scope is that one combat group, not unrelated effects.
- Creatures have attack, flat damage-reducing defense, and persistent health. Example 6 attack vs defense2 deals 4 health damage.
- Health bar at top; attack/defense at bottom. Specialized per-creature attack menus deferred.
- Damage remains until healed. Auto end-turn recovery is possible later mode.
- Attacking exhausts until owner's next turn. Blocking does not exhaust by default; creatures retain accumulated wounds and existing readiness/exhaustion. Exhausted creatures can block but take extra damage.
- Exhaustion does NOT grant the special player-damage ability. Initial playtest exhausted-blocker health damage formula accepted: ceil(max(0, allocated raw damage - defense) × 1.5). Specific interaction with player damage to clarify.
- Special player-damage ability is card-specific, weighted toward fitting colors but not universally exclusive. Latest user design supersedes ordinary trample-style lethal-first overflow: subtract blocking creature defense, bypass its health, deal remaining damage directly to defending player's HP. Full bypass selected for playtesting: blocker takes no HP damage from this attack but retaliates normally; remaining damage goes to player after defense. Exhausted-blocker multiplier does not boost player damage. Against one bypass attacker, accepted blockers' defense sums; player damage=max(0,attack-summed defense). Blockers take no HP damage from that hit and retaliate normally. Original keyword naming later; MTG terms are temporary references.
- Newly played creatures block immediately but attack only from owner's next turn, unless ability overrides.
- Ordinary allied defensive help requires defender acceptance. Broad offensive/defensive assistance, cards and resources desired; exact permissions/timing to define.
- Public offers for everyone; private negotiation via sneaky-color cards/abilities as working direction. Accepted deals and committed actions public on TV before resolution, with response opportunity.
- Ordinary promises can be betrayed. Gold card effects can enforce structured game obligations, including forced obligations.
- Agreement examples: help attack/defend, do not attack selected player next turn. No full-game forced lock. Turn/resource unlocks proposed; durations/costs/impossible obligations unselected.
- Allow interference and reversals, avoid prolonged inability to meaningfully play. Specific restrictions not yet defined.
- Most effects predictable. Occasional dice/coin effects on risk-taking cards; Silver identity candidate, no real-money wagering.
- Weaknesses: explore explicit intuitive creature-trait vulnerabilities, not universal color chart; modest beginner strategic counterplay. Bonuses/tags unselected.

## Leaders and alternate forms
- Leader influences deck and can be summoned as persistent combat creature. No separate commander-damage count.
- Outside-battle effects supported. Summon requirements turn/resource related proposed, not fixed.
- Defeated leader returns outside battle and can be resummoned with escalating differentiated costs. Stronger leaders pay more; sacrifice/exile payment options supported as direction, exact cards unselected.
- After defeat outside effects wait until owner's next turn (owner interpretation stated back); exact phase and passive while summoned unresolved.
- Transform/flip alternate forms and combine/group creatures are valid supported mechanics across fitting colors; color shapes effects.
- Transform preserves accumulated damage and readiness. Mapping when max health changes unselected.
- Combined current health = combined max health × sum(component current health)/sum(component max health). Weighted fraction accepted. Combined max stats and rounding unselected.
- Destroying combined creature destroys/discards all components unless explicit survival effect. Separate state and non-destroy removal cases unresolved.

## Creation, content and accessibility
- Creation should be nearly as enjoyable as play. Support six-year-old learner and new adult while retaining depth; do not automatically simplify whole match.
- Wording scales by reading level but effects unchanged. Optional read-aloud accepted.
- Tutorial game mode, deck-building tutorial, small practice scenarios versus computer opponent and optional in-match guidance. No generative-AI opponent required.
- Wizard default: persona -> play-style questions -> jointly suggest compatible color/leader/deck -> customize with eligibility explanations. Advanced builders start directly from cards/leader/colors.
- Archetype customization and full deck building available to children and adults.
- Traits/categories guide thematic ability fit; fantasy exceptions such as winged cats encouraged. Creature concept/art unrestricted within tone, but stats/effects must pass balance constraints.
- Full gameplay library available to everyone; no unlock grind. Cosmetic progression not selected.
- Simple creator: card type, supported effects, style (anime/3D-look/sketch etc.), mood (funny/spooky etc.), name entry/suggestions.
- Art sources: camera-import drawings, built-in gallery, generated custom illustrations.
- Illustration-only generation; app renders uniform card frame, accurate reading-level text, name, health and attack/defense.
- Current tone: cartoon-style, no realistic gore/swears. Higher maturity tiers deferred.
- Private drafts; finalized cards shared in organized searchable catalog. Other players use and make personal variants, original unchanged.
- Retain current/recent values and artwork to avoid regeneration; exhaustive version history unnecessary. Exact deletion/archive policy unselected.
- Owners edit/delete personal creations; shared-card/household-rule changes parent-only. No mandatory parental approval for every personal card.
- First family playtests use color-based starter decks; themes generate flavor/art later. Numerical card stats and complete color roster remain design work.

## Devices and operation
- Each player uses own phone/tablet. Initial personal clients Android and older iPads; iPad models/OS intentionally deferred until available.
- BOTH Google TV Streamer (bedroom) and Roku TV (living room) required for first completed version. Initial TV clients shared match display; full TV editor deferred.
- Preferred installed native/packaged apps. Latest explicit exception: iPad home-screen web app acceptable if secure and compatible with existing no-browser restrictions. Weekly native reinstalls also acceptable fallback; annual signing fee not approved. Private simple setup, app stores unnecessary. Other platform installed-app preferences unchanged.
- Home Linux server preferred authoritative match host plus central card/art/deck/profile storage. Actual OS/hardware to verify before deployment.
- Tap name for profile, no PIN. Household trust; private-hand client/seat association still required.
- Disconnect pauses match; reconnect restores exact hand/state. Deliberate cross-day saves optional.
- No-internet local play desirable lower priority. TV-free fallback, remote play and visitor QR install/join later.
- Extensible APIs/plugin boundaries required for future content/modes/features. Internal versioned modules not equivalent to arbitrary unsigned runtime plugins on every OS.

## Artwork worker and costs
- No ongoing/per-image generation fees. This was an ART-generation budget answer, not approval/refusal of all platform signing fees; broader budget unconfirmed.
- PC worker accepted: server queues deck jobs; worker generates sequentially if needed; each image saved to server linked to card and available as finished for review. Long waits acceptable. Regenerate available but not prominent.
- PC known Ryzen5/GTX1650; exact RAM/VRAM unverified. Local-model feasibility/speed/quality must be benchmarked.
- Supported ChatGPT subscription-backed generation investigated as alternative; NOT established for unattended custom worker. Ordinary API billing separate. Do not promise browser automation or account sharing.
- Prompt assembly deterministic, no LLM needed; combine user card/style/mood with fixed art composition instructions. Choose lightest suitable available image option; can't guarantee external model routing/usage savings.
- Generator swappable behind worker contract. No paid API/credit fallback without user choice.

## Later review and workflow
- Planning only; no app implementation or server changes yet.
- User requested second expert build-planning team after discovery; now active.
- Later large comparative team requested for Pokemon, Yu-Gi-Oh!, Elestrals, MTG balance lessons, explicitly deferred. Research informs, playtests establish outcomes; no perfect-balance claim.
- GPT-6.1 Sol recommended for interviews/docs/ordinary implementation; Astra for focused challenging rules/architecture review. Agents currently inherit session model.
- Preserve decisions, proposals, feasibility blockers and next task in GitHub. Use concise canonical docs; historical transcript is not the default briefing.

## iPad delivery clarification — 2026-11-17
User accepts secure web app on iPads, whose general browser access is blocked, and also accepts weekly native reinstalls if needed. Do not relax browser restrictions silently. Need identify Screen Time versus managed restriction and test actual OS/device. Full-screen Web Clip is a candidate, not proof that ordinary Add to Home Screen works under all restrictions. Prefer same-origin local-server UI/assets, no arbitrary external navigation, server-authorized private-state projection and trusted encrypted local connection; exact controls/certificate setup require design. No security guarantee from standalone display alone. User can leave hardware details deferred.

## iPad restriction source confirmed
Browser access blocked through Screen Time, not confirmed managed-device enrollment. User accepts web route if URL-bar/arbitrary-browser access can be blocked. Do not claim managed Web Clip documentation proves ordinary Screen Time support or full-screen display equals security. Prototype must test actual iPad OS with restrictions restored: home-screen launch, external link/pop-up/navigation behavior, imports/camera and reconnect. Keep in-app links/assets first-party/local; no arbitrary URL entry. Existing browser restriction preserved; weekly signed-native reinstall fallback accepted. Native wrapper with allowlisted embedded webview is another candidate only if needed, and still requires native signing/maintenance.
Guided Access can restrict to one app, but is only optional extra containment and not proof that web navigation inside app is blocked. No parental settings changed during planning. Official reference https://support.apple.com/en-gb/111795 .
