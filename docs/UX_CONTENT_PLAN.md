# Family UX and Artwork Contracts
Updated 2026-11-22. Accepted behavior is consolidated in REQUIREMENTS.md; mechanics in RULES_DRAFT.md. No UI implemented.

## Destinations
Home/Profile, Decks, Theme Creator, Card Catalog, Artwork Library, Learn/Practice, Match, Settings and cosmetic shop. Adult controls secondary with PIN; device pairing/revocation required. Last profile remembered; adult entry protected, active-match switching controlled.

## Core flows
Theme -> suggested customizable color -> three leader concepts/invent own -> small guided groups -> legality check + short review -> publish/queue art. Easy-to-pilot any color, Keep in deck, preview simplification swaps, Finish for me. Independent duplicated/shared deck copies, attribution without sync.
Legal draft practice with placeholders, simple bot/policy choices, on-demand one-action hints. Family hints default on host-wide optional; no reward penalty or automatic selections.
Public TV fixed zones, dynamic compact tiles, neutral waiting indicator; <=1s nonblocking action spotlight, device-local animation disable. Private authorized hand/target previews only on own device. Sound off, one supported vibration/request, visuals always. Read-level text/TTS do not change rules. No chat; fleeting preset avatar emoji.
Post-match TV fun accurate highlights; personal rewards on own devices, no popups in match. Cosmetic appearance instance-specific, stable in live/saved matches. Whole-number exact HP, no hidden fractions.

## Artwork worker contract (proposal for implementation)
Linux queue -> leased Windows worker -> generate -> validate/upload -> immediately ready for review. Fields jobId,draftId,requestRevision,promptTemplateVersion,subject/style/mood/dimensions,backendProfile,idempotencyKey.
States queued,claimed,generating,uploading,readyForReview,failed,cancelled,blockedByLimit.
Heartbeat/reclaim; submission dedupe; preserve completed work; hashes and stale-revision protection; no paid fallback. Deterministic prompt assembly; artwork only; fixed full-art-friendly composition. Generate after mechanical approval. Placeholder playable; approval individually/batch, apply between matches. Reject no automatic regenerate; secondary Try again accepts correction; all images retained incl rejected. Reuse saved images/crops. GTX1650 quality/speed feasibility still unverified. ChatGPT Plus unattended custom-worker path unverified, not equivalent to free API.

## Storage concepts (proposed schemas)
Profile/device/session/role; card definition/draft/published variant/character; deck and independent copy attribution; artwork asset/review/crop; cosmetic entitlement/equipment; achievement/event/currency ledger; match-pinned definitions/state; art job; backup manifest.
Immutable mechanical identity separate from artwork, character name and singleton validation. Catalog archive not normal deletion; shared original administration adult-only. Rewards ledger deduplicates event/achievement to prevent reconnect/replay payouts.
Save each committed action incl pending chain, resume paused. Midnight local active-day backups seven daily/four weekly; live art survives rotation.
See tester plan for independent simulation data; simulation never writes family achievements or currency.
