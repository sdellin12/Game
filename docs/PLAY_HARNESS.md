# Local playable harness
Updated 2026-11-23. This is a separate source launcher from the combat balance lab.

## Launch
From the Game repository directory, on Windows with Python/Tk installed:

```powershell
py -3 run_play.py
```

No new runtime package is required. The existing portable Combat Lab executable
has not been rebuilt with this harness. Closing a started local game asks for
confirmation because this session has no save/resume yet.

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
10 Actions/Reactions and 6 capacity permanents, all engine-validated. Practice pack v2 includes three functional leaders with
separate reserve/battle
abilities. Inspect/summon your leader from the hand/choices tab; current summon
cost, location and recovery are public. Canonical leader rules are in RULES_DRAFT.md.
Deck validation enforces forty singleton entries, known cards and matching color.
Rules-source/content hashes freeze before opening hands; deck choices cannot change
once setup begins. Existing catalog, checkpoint and saved-data formats are untouched.

Windows Python 3.14.3: 236 tests pass. Current opponent/leader evidence is in
experiments/OPPONENT_LEADERS.md; original setup/widget coverage is retained.
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

Fixed-seed view-only scripts completed at 205/415/740 commands and 11/16/24 turns.
The default driver is a bounded diagnostic; a command limit reports incomplete rather than inventing a result.
Add
`--practice` to exercise the actual computer policy for P2 and later seats.
Computers use only their permitted views and stop at human choices. The desktop
driver caps an uninterrupted computer burst at 200 commands and reports a diagnostic
without creating a draw/winner. A new lobby clears that diagnostic.

Visual review covered the initial lobby. Later computer-use snapshots did not
reliably target the selected window, so further input stopped. Other screens have
widget/geometry checks, not a completed visual review. Coverage/gates live in
crucible_core/coverage.py v4; PROJECT_STATE.md owns the next step. Rollback is a
source revert; preserve old experiment data. No game-runtime dependencies added.
