# Local playable harness
Updated 2026-11-23. This is a separate source launcher from the combat balance lab.
This remains an engineering harness. Family testing is deferred under
[REQUIREMENTS.md](REQUIREMENTS.md); [FAMILY_PLAYTEST.md](FAMILY_PLAYTEST.md) is retained
for the later usable-app milestone.

## Launch
From the Game repository directory, on Windows with Python/Tk installed:

```powershell
py -3 run_play.py
```

For developer setup, `python run_play.py --hotseat --players 2` selects human seats
directly; --players also accepts 3 or 4. This does not make the debug interface a
family-testing milestone. No deck or opening choice is committed by the launcher.

No new runtime package is required. The existing portable Combat Lab executable
has not been rebuilt with this harness. Closing a started local game asks for
confirmation before discarding changes since your last save.

## First game
1. Leave two seats selected, or choose 3-4 and click New lobby.
2. Computer opponents in P2-P4 are enabled for a new practice lobby by default.
   Uncheck the new-lobby computer option before New lobby for human hotseat play.
   Click View Player 1, then acknowledge the handoff. Select Practice Forty and
   a reserve identity, then Ready. Computers select/ready themselves. In hotseat mode, repeat for
   the other seats.
3. Return to Player 1 (the setup host) and click Deal opening hands.
4. Each seat privately selects opening cards to replace, or confirms Keep all.
   Hide the hand before handing over. Choices lock once; counts and the starting
   player reveal together only after everyone confirms.
5. Follow the priority/next-step message. Take that seat and Pass or respond.
   Ordinary plays happen in your Main phase. Inspect a hand card, choose its
   target/payment and Confirm; Cancel keeps the tentative choice private.
6. At Combat, the active seat confirms all attacks (including an explicit none).
   After responses, defenders lock assignments privately. Damage orders, when
   needed, are confirmed before the final response round. Pass to finish damage.
7. End turn from Main, choose required discards/refill when prompted, and continue
   until the engine reports a winner/draw. Human seats require manual decisions;
   computer hands cannot be opened through the seat buttons.

Public table/history remain separate tabs. Hide private hand clears private
widgets immediately; changing seats always requires another acknowledgement.
Long attack/block/order forms scroll. Test refill cost is visibly set to 20 life;
canonical rules and open price decisions remain in RULES_DRAFT.md.

## Scope and validation
The 40-card versioned practice pack has distinct keys/names, 24 creatures,
10 Actions/Reactions and 6 capacity permanents, all engine-validated. The current default practice pack includes three functional leaders with
separate reserve/battle
abilities. Inspect/summon your leader from the hand/choices tab; current summon
cost, location and recovery are public. Ward cards now exercise timed prevention;
current prevention, anchors and expiry events appear on the public table/history.
Unravel is an enemy-creature return reaction. Banish is an exile Action; exiled
cards appear in the public table/history. Second Chance returns a selected card
from your own discard; inspect it and choose the discard target before confirming.
Scope/evidence: experiments/ZONE_MOVES.md and experiments/DISCARD_RECOVERY.md.
The opponent now compares revealed final-combat reaction outcomes and exact
payments, alongside combat threats and pending removal; its bounded tactical
harness is documented in experiments/OPPONENT_TACTICS.md.
Scholar's Lantern and Salvage Battery are four-resource capacity permanents.
Archive Well adds an optional permanent-capacity reward for hand discards.
The Lantern's own-draw reward is optional; the Battery's hand-discard reward is mandatory. Inspect their trigger text
before playing; it is also visible on the public battlefield.
For optional triggers, follow the waiting-seat message, acknowledge that seat, then
choose Use or Skip. No response/order choice interleaves; accepted effects queue
only after all optional choices finish. Multi-trigger groups confirm their selected
order even when nothing remains selected; this keeps choices private until queueing.
See experiments/OPTIONAL_TRIGGERS.md. Evidence:
experiments/AUTHORED_TRIGGERS.md and experiments/DRAW_DISCARD_TRIGGERS.md.
Canonical mechanics remain in RULES_DRAFT.md.
Deck validation enforces forty singleton entries, known cards and matching color.
Rules-source/content hashes freeze before opening hands; deck choices cannot change
once setup begins. Catalog and combat-lab checkpoint formats are untouched; local saves use schema v6.

Current validation is recorded once in PROJECT_STATE.md. Duration evidence is in
experiments/DURATIONS.md; original setup/widget coverage is retained.
Tests cover readiness, stale/foreign redraws, replace-before-reshuffle conservation,
privacy barriers, real Ready/Deal/Keep/Play button handlers, rejected actions and
scroll geometry with 30 attack choices. A projection fix makes depletion-related
End intent visible to clients, preventing extra-play suggestions after exhaustion.

```powershell
$env:PYTHONPATH='src'
python -m crucible_play.smoke --players 2
python -m crucible_play.smoke --players 3
python -m crucible_play.smoke --players 4
```

The passive view-only smoke scripts remain available. Historical pack-v8 practice
policy runs completed at 327/829/1867 commands and 17/36/74 turns for 2/3/4 seats.
The default driver is a bounded diagnostic; a command limit reports incomplete rather than inventing a result.
Add
`--practice` to exercise the actual computer policy for P2 and later seats.
Computers use only their permitted views and stop at human choices. The desktop
driver caps an uninterrupted computer burst at 200 commands and reports a diagnostic
without creating a draw/winner. A new lobby clears that diagnostic.

Visual review covered paused/resumed gameplay, public battlefield and leaders,
private handoff/hand controls, and the corrected summon confirmation dialog.
The review caught a late-bound summon callback; a regression test checks its
actual leader name and price. Header controls use two rows and fit 950px width.
Combat choice screens retain widget/geometry coverage.
Coverage/gates live in crucible_core/coverage.py; PROJECT_STATE.md owns the next
step. No game-runtime dependencies added.

## Save and resume
Click Save game to write a private `.crucible.json` snapshot. Saving over an
existing valid save retains its exact previous bytes as a uniquely named backup.
Load game also accepts those backups. Validation happens before you confirm
replacement of the current session. The restored game opens paused, with hands
hidden and computers stopped; click Resume saved game, choose a human seat and
acknowledge its handoff to continue. File pickers pause computer stepping.

Old schema-v1/v2/v3/v4/v5 files need explicit conversion to a separate v6 file before Load.
Format, privacy, build compatibility, conversion command and rollback policy: [SAVE_FORMAT.md](SAVE_FORMAT.md).

For a bounded all-computer, multi-seed evaluation, set PYTHONPATH=src and run
`python -m crucible_play.permanent_eval`. It reports completed/incomplete status,
actual permanent entries and public queued-trigger items. Evidence and limits:
experiments/PERMANENT_EVALUATION.md.

For directed End-discard cases, run `python -m crucible_play.hand_pressure`.
It checks draws/recovery, actual salvage rewards, Archive Well Use/Skip and the
next own Start refill; fixture details are in experiments/HAND_PRESSURE.md.
For paired baseline/holding-policy games, run `python -m crucible_play.discard_eval
--players 2 3 4`. Add `--source-discount 1` for isolated cost sensitivity.
Study method/results: experiments/DISCARD_STRATEGY.md.

Design-only package economics: `python -m crucible_play.package_economy`.
Regenerate its readable report with `--format markdown` into
docs/experiments/DISCARD_PACKAGE_ECONOMY.md. It reads the proposal JSON, not the
live practice deck. Scope and next engine work: DISCARD_DRAW_PACKAGE.md.

Opt-in discard/draw deck: `python run_play.py --discard-package`. New games in that
window retain the selected pack; default launch keeps Practice Forty v9. Headless
check: `python -m crucible_play.smoke --practice --discard-package --players 3`.
Timing, save and loop evidence: experiments/DISCARD_CONTINUATION.md.

Seat-rotated deck/policy comparison: `python -m crucible_play.package_eval`.
This is a separate headless experiment; `aware` is a candidate policy, while live
computer seats retain the baseline. Reproduction/report commands and limitations:
experiments/PACKAGE_POLICY.md.

Known-case policy ablations and compact synthetic decision traces are available
through package_eval's `--ablation` and `--trace-output` options. The corrected
creature-priority variant is named `revised`; request it explicitly with
`--policies baseline revised`. Fresh-seed commands and interpretation:
experiments/PACKAGE_REGRESSION.md. These remain headless policy experiments.
