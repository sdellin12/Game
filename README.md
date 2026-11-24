# The Crucible
Original household card battler. A local playable rules harness and a combat-only
balance lab are implemented; the networked household/device product remains future
work. Start with the current checkpoint rather than the original planning records.

## Continue development / AI handoff

- [Current checkpoint and next task](docs/PROJECT_STATE.md)
- [AI continuation guide and source map](docs/AI_HANDOFF.md)
- [Complete documentation index and status](docs/DOCUMENTATION_INDEX.md)

The active implementation is on `feature/combat-coverage-and-timing` (draft PR #2).
Check the branch and working tree before editing. Local uncommitted card-art/editor
work is not all in Git; the handoff guide explains that boundary.

```powershell
python scripts/audit_docs.py --write-index --bundle
```

This checks authored-document links/entry points and creates an ignored documentation
ZIP with a hash manifest. It does not publish private saves or local artwork.

## Run the local engineering harness

This is for developer checks. Family-testing timing is deferred in the requirements;
the local match UI is progressing toward that milestone.

```powershell
py -3 run_play.py
```

Use `python run_play.py --discard-package` for the provisional opt-in draw/discard
deck. The live opponent remains the baseline; research policies are separate.

Play against a computer by default, or choose two to four hotseat seats in a new
lobby. Choose a practice deck/leader, ready and lock opening redraws. Save/load
controls preserve local sessions, including pending choices. See the
[short harness walkthrough and current scope](docs/PLAY_HARNESS.md).

The default UI includes guided setup, private opening choices, a card table,
attack/block selection, exact-payment review and required-choice/order guidance.
Alt+1–5 navigate sections; Alt+H hides the hand. See [match flow and keyboard
guide](docs/MATCH_UI_FLOW.md). `--debug-ui` retains the earlier developer controls.

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
- [Timing specification and historical review](docs/FULL_MATCH_TIMING_SPEC.md)
- [Approved refill timing and provisional price rationale](docs/DECK_REFILL_DESIGN.md)
- [Delivery plan](docs/BUILD_PLAN.md)
- [UX and artwork contracts](docs/UX_CONTENT_PLAN.md)
- [Card design and LLM handoff](docs/CARD_DESIGN.md)
- [Family playtest checklist](docs/FAMILY_PLAYTEST.md)
- [Approved card information contract](docs/CARD_INFORMATION_CONTRACT.md)
- [Filled card content examples for template work](docs/CARD_CONTENT_EXAMPLES.md)
- [Lore bible](docs/Game_Lore.md)
- [Platform architecture proposals](docs/ARCHITECTURE_PROPOSAL.md)

[Balance Tester Design and Implementation Plan](docs/BALANCE_TESTER_PLAN.md) — completed four-specialist planning synthesis for a local reproducible Windows desktop lab using the eventual game's shared rules engine. No per-simulation AI/API calls. Current implementation evidence: [first combat slice](docs/experiments/FIRST_COMBAT_SLICE.md).

Rules, future ten-color product requirements and implementation coverage have
separate owners in the continuation guide; illustrative content is not automatically
an enabled mechanic or a published starter pack.

[Historical interview](docs/ANSWERS.md) and [original discovery queue](docs/DISCOVERY.md) are archival, not current instructions. Canonical docs above preserve accepted decisions, provisional numeric test candidates and unresolved engineering details.
