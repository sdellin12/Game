# The Crucible
Original household card battler: imaginative themed decks, private phone/tablet hands and a shared TV battlefield. The combat-only balance lab includes a desktop window, resumable batches and comparison reports. The full game is not built yet.

## Open the desktop lab

Portable Windows build: double-click `dist/CrucibleLab/CrucibleLab.exe` after
[building the bundle](docs/COMBAT_LAB_QUICKSTART.md#portable-windows-app).
The desktop also includes verified, searchable combat replay inspection.
[First-run walkthrough](docs/DESKTOP_WALKTHROUGH.md) shows a complete small experiment.

```powershell
py -3 run_desktop.py
```

Choose a checkpoint and Run / Resume. Pause/cancel preserve completed jobs.
Reports show exact outcome ranges; they do not establish match win rates.

## Run the combat lab

Python 3.11+, no third-party runtime dependencies or API keys. From this directory:

```powershell
py -3 run_lab.py matrix --output lab-runs/first-matrix
```

Use `python3` instead of `py -3` on Linux/macOS. Open the exported `report.html`.
See [quickstart and coverage limits](docs/COMBAT_LAB_QUICKSTART.md). The current
matrix contains 1,156 exact encounters, not full matches or proven card balance.

## Current design
- [Project checkpoint](docs/PROJECT_STATE.md)
- [Confirmed requirements](docs/REQUIREMENTS.md)
- [Rules baseline and implementation gaps](docs/RULES_DRAFT.md)
- [Proposed full-match timing specification](docs/FULL_MATCH_TIMING_SPEC.md)
- [Life-for-deck refill proposal](docs/DECK_REFILL_DESIGN.md)
- [Delivery plan](docs/BUILD_PLAN.md)
- [UX and artwork contracts](docs/UX_CONTENT_PLAN.md)
- [Approved card information contract](docs/CARD_INFORMATION_CONTRACT.md)
- [Filled card content examples for template work](docs/CARD_CONTENT_EXAMPLES.md)
- [Lore bible](docs/Game_Lore.md)
- [Platform architecture proposals](docs/ARCHITECTURE_PROPOSAL.md)

[Balance Tester Design and Implementation Plan](docs/BALANCE_TESTER_PLAN.md) — completed four-specialist planning synthesis for a local reproducible Windows desktop lab using the eventual game's shared rules engine. No per-simulation AI/API calls. Current implementation evidence: [first combat slice](docs/experiments/FIRST_COMBAT_SLICE.md).

Current rules use attack/health only, persistent wounds,30 player health and permanent elimination; old defense/full-bypass/player-revival plans are superseded. All ten colors support approachable decks. No real-money progression.

[Historical interview](docs/ANSWERS.md) and [original discovery queue](docs/DISCOVERY.md) are archival, not current instructions. Canonical docs above preserve accepted decisions, provisional numeric test candidates and unresolved engineering details.
