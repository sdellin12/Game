# Current architecture status — 2026-11-22
The implementation stack below remains a proposal with historical platform-source findings, not a freshly verified compatibility guarantee. REQUIREMENTS.md and RULES_DRAFT.md supersede older behavioral assumptions. No player revival, no chat/private messaging system, adult PIN and pairing required. Independent local balance lab will reuse the authoritative rules core; its design is in BALANCE_TESTER_PLAN.md after specialist review. The local Python combat lab and practice harness are implemented. The networked server/device topology below remains a proposal; see AI_HANDOFF.md for the current source map.

# Platform Feasibility and Proposed Architecture
Reviewed 2026-11-17. Expert planning recommendation, not approved stack. Requirements: REQUIREMENTS.md.

## Proposed topology
| Component | Proposed responsibility | Candidate technology |
|---|---|---|
| Linux home server | Authoritative match rules, private/public projections, profiles, card/deck DB, art files and queue | Python service, SQLite, filesystem assets |
| Android/iPad personal client | Private hands, creator, catalog, learning, offers/reactions | Flutter candidate pending actual OS/install checks |
| Google TV Streamer | Public battlefield/chain/deals | Android TV app; prove TV-specific navigation/rendering before sharing Flutter code |
| Roku TV | Public battlefield/chain/deals | Separate BrightScript/SceneGraph app |
| Windows PC art worker | Queue jobs, generate via replaceable backend, upload per-card results | Python worker candidate |

A shared wire protocol is realistic; one identical binary/runtime across Roku and Android is not assumed. TV clients must never receive private hand/negotiation payloads merely hidden by UI. Clients submit intentions; server validates and resolves. Current requirements supersede old trust-only assumptions: adult profile PINs, approved/revocable device pairing, active-seat switching controls, and server-authorized private projections are required.

Use versioned JSON commands and state projections, sequence numbers, command IDs and reconnect snapshots. HTTP asset retrieval, WebSocket personal-client updates and HTTP polling Roku adapter are candidates. Snapshot polling avoids assuming particular Roku streaming support. Command deduplication and authoritative validation are necessary even on local Wi-Fi. Do not expose local services publicly for first version.

## Platform gates and historical findings — reviewed 2026-11-17
### iPad native distribution — consequential product decision
- Free Xcode Personal Team provisioning expires seven days after issuance; rebuild/reinstall needed. Up to three devices and three installed apps/device are documented limits.
- Apple Developer Program is US$99/year. No annual fee is authorized; current owner preferences are in REQUIREMENTS.md.
- Paid membership provides distribution routes, not a guarantee of maintenance-free private installation. Select and test route; document signing/build renewal and device registration.
- TestFlight currently requires iOS/iPadOS16+, and beta builds expire after 90 days. Not permanent installation; old iPads may not support current TestFlight.
- Need actual iPad model/OS (user deferred until available), compatible macOS/Xcode build access, and chosen signing route. Linux server/Windows alone not assumed sufficient.
- Current Flutter support matrix reviewed by lead lists iOS15+ for current release, while older deployment guides can mention different minimums. Use actual selected release's matrix, not a stale iOS13 assumption.
- This was the initial native-first investigation. The later approved secure iPad-web direction below supersedes it; do not reopen that settled preference.

Sources:
- https://developer.apple.com/help/account/basics/about-your-developer-account/
- https://developer.apple.com/help/account/membership/program-enrollment/
- https://testflight.apple.com/
- https://docs.flutter.dev/reference/supported-platforms
- https://docs.flutter.dev/deployment/ios
- https://developer.apple.com/documentation/bundleresources/information-property-list/nslocalnetworkusagedescription

### Roku
Developer mode supports local package sideload/install. Only one sideloaded app at a time; another replaces it. Document initial remote steps and repeat updates clearly. SceneGraph network work belongs in Task nodes. Native Roku client remains an explicit delivery workstream, not afterthought.
- https://developer.roku.com/dev/docs/developer-setup
- https://developer.roku.com/dev/docs/rourltransfer
- https://developer.roku.com/dev/docs/brightscript-support

### Google TV and Android
Installed Android TV app is plausible but needs TV manifest/launcher/remote behavior. Prove on bedroom Streamer rather than shipping unchanged phone UI. Private Android APK distribution requires checking current verification rules and regional rollout. Official limited-distribution route documents up to20 authorized devices; don't promise universal QR frictionlessness.
- https://developer.android.com/training/tv/get-started/create
- https://developer.android.com/developer-verification/guides/limited-distribution
- https://developer.android.com/developer-verification

## Feasibility experiments before substantial app work
1. Inventory available iPad/Roku/TV versions, Linux capacity and Mac build route; no need re-ask known Ryzen5/GTX1650.
2. Select user-acceptable native iPad installation route, without purchases during planning.
3. Install minimal public-card viewer on Android, actual iPad, Google TV and Roku. Fetch same versioned card from Linux, apply update and reconnect. Write setup/update instructions for each.
4. Prove private hand omitted from TV payload; restore client seat on reconnect without silently replacing another active device.
5. Benchmark one representative local art job on actual PC, then a short queued batch; record peak RAM/VRAM, latency and acceptable visual output. Investigate supported subscription-backed tool image flow separately; not guaranteed.
6. Choose/pin framework/toolchain only after these gates. Older versions may improve device reach but add maintenance risk; explicitly assess.

## Extension boundaries
Versioned card/effect schemas; registered server effect handlers; ruleset profiles; content packs; capability negotiation; art-provider adapter. Clients present supported effects/events. New mechanics need explanatory text, tests and compatible clients. Do not promise unsigned downloadable executable plugins on iPad/Roku or arbitrary natural-language rules. Freeze definitions/rules within active match; migrate or refuse incompatible saves.

## Status
No household platform installation spike or actual-device deployment is recorded. The separate local Windows lab executable and source practice harness do exist. Updated user preference: secure iPad web app acceptable under existing no-browser restrictions; weekly native reinstalls acceptable fallback; annual fee not authorized. Main unknown hardware: actual older-iPad OS and current Mac build availability. Both TV platforms remain required for first completed version.

## Updated iPad direction after review
User explicitly relaxes native-only for iPads IF web app is secure and does not undermine no-browser restrictions. Weekly native provisioning maintenance also acceptable. Investigate full-screen Web Clip and test exact restrictions before choosing stack. Apple documents managed full-screen Web Clips when Safari hidden/restricted; this does not establish compatibility of ordinary home-screen installs on unmanaged Screen Time devices. Restriction source is confirmed Screen Time; actual model/OS testing remains deferred. Do not enable Safari generally or enroll in paid management without a concrete user choice.
Source: https://support.apple.com/guide/deployment/depbc7c7808/web
Proposed app controls: no arbitrary URL input/outbound links, local first-party assets, safe image imports, escaped generated/user text, restrictive content/navigation policy, trusted HTTPS/local session and seat-based server projections. A full-screen window is presentation, not security isolation. Test native fallback and signing/build access if web restriction incompatible. No implementation done.
