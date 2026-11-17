# Family UX, Card Data and Artwork Worker Proposal
2026-11-17. Recommendations unless confirmed in REQUIREMENTS.md. No interface implemented.

## Personal-device destinations
| Destination | Purpose |
|---|---|
| Home/Profile | Tap name, current match, decks, art queue |
| Decks | Starters, archetype customization, full building |
| Creator | Fixed mechanics, traits/persona, name/style/mood/art |
| Library | Finalized cards, search/filter, add/copy variant |
| Learn | Tutorial game, practice scenarios, deck tutorial |
| Match | Private hand, public-board inspection, actions/reactions/deals |
Household settings/management secondary. Profiles on server proposed; tap-name trust confirmed. Don't silently require new PIN.

First use proposal: profile -> reading preference -> optional short practice -> starter -> join match. No age gating full editor. Tutorials optional/resumable; scenario opponent can be scripted, no LLM needed. Actual end-to-end reading comprehension needs kid/adult playtesting.

Creation: persona -> playstyle questions -> compatible color/leader/deck suggestions -> inspect/customize. Explain suggestions in concrete terms (protects smaller creatures), not unexplained archetype labels. Separate mechanics and appearance with live preview. Supported effect/color/trait/balance checks give actionable adjustments. Winged cat valid; art/name does not confer free stats.

## Match and visibility
TV receives only public fields: battlefield, public health/resources/leaders, phase, accepted deals, response chain. Never include opponent hands/private requests in TV JSON. Personal clients receive authorized private projection only.
Playable highlights reflect actual legal cost/target/timing, explicit pass even when nothing playable, visible turn/response/wait status. Do not broadcast disabled choices.
Newest pending effect marked resolves-next; targets visible; preview describes conditional result using available information, not hidden future actions.
Private offers only qualifying sneaky-color ability; rejected/unfinished offers stay private. Accepted terms/committed blockers public before response/resolution. UI distinguishes informal/breakable versus card-bound terms.
Disconnect pauses; reconnect snapshot restores seat/private state. Prevent accidental takeover by second active device without adding mandatory password. Exact handoff procedure to design.
Color plus icon/name so ten identities aren't differentiated by color alone. Show wounds/exhaustion simultaneously; test TV font sizes and actual iPads.

## Rules wording and read-aloud
Single structured effect definition drives plain wording, detail, optional examples and read-aloud. No inference of game behavior from generated prose. Initial deterministic templates, not LLM paraphrase of rules.
Example mill: "Put the top 3 cards of that player's deck into their discard pile."
Reading level changes wording, never targeting/cost/timing. Flavor visibly separate. New effect cannot publish without mechanics validator and matching explanations.
Read-aloud use native/device TTS candidate; verify languages/voices/offline behavior per actual device, no paid speech service assumed.

## Minimum data entities
| Entity | Responsibility |
|---|---|
| Profile | ID, reading preference, tutorial state, household role |
| CardDefinition | Stable ID, owner, color/traits, structured effects/cost/stats, artwork reference |
| CardDraft | Private working revision |
| PublishedCard | Finalized shared catalog view |
| Deck | Card references, leader, validation |
| ArtworkAsset | Hash, origin, dimensions, review status, files |
| MatchSnapshot | Pinned definitions/rules and runtime instances |
| ArtJob | Card revision, prompt version, backend, status, outputs |

Separate singleton gameplay identity from card name/art/character. Small mechanical variants allowed; exact identity/abuse policy needs tests.
Published-card update policy still a question: owners manage personal creations, parent-only shared changes. Recommendation: owner freely edits private draft/personal variant; changes to shared published original pass parent-controlled publish step. This interpretation NOT selected silently.
Delete deck doesn't delete shared referenced art or another player's variants. Keep reusable images/current data, not endless revision history. Match-pinned snapshots a technical isolation feature, not universal catalog version history.

## Artwork queue contract
Linux queue -> PC worker claims -> generates -> validates/uploads -> server review item immediately.
Job fields: jobId, draftId, requestRevision, promptTemplateVersion, subject/traits/style/mood, dimensions, backendProfile, idempotencyKey.
States: queued, claimed, generating, uploading, readyForReview, failed, cancelled, blockedByLimit.
- Lease/heartbeat so stopped PC doesn't strand job.
- Dedupe submissions and retry safely.
- Preserve completed results across restart.
- Hash/check images and reject stale result overwrites after card edit.
- Reuse art for stat/reading wording changes.
- Stop on limits, never silently use paid backend.
- Regeneration under Edit Artwork -> Advanced; keep old art until replacement accepted.
- Artwork only; app draws uniform frame/text/live stats.
- Exact export meaning (automatic server save/review vs downloaded image file) can be clarified with UX prototype.

Backend interface isolates local model from a supported subscription-backed tool if feasible. ChatGPT Plus direct unattended pipeline remains unverified; no browser automation/account-sharing dependency. Deterministic prompt templates avoid premium text-model calls.
GTX1650 benchmark before commitment; slow sequential okay but output quality and actual VRAM/RAM matter.

## Initial versus later
Family starter playtest: private hands/public TVs, core combat, profiles, readable rules, pause/reconnect.
Creation milestone: wizard, supported-effect builder, catalog, drawing/gallery import, reviewable generated art queue.
Deferred: TV editor, multicolor, remote/visitor joining, maturity tiers, optional reverse/skip changes, guaranteed cross-day saves, TV-free fallback.
Intermediate milestones don't remove four-platform commitments from first completed version.
