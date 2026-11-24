# First run in the Windows app

## Open the app

Double-click `dist/CrucibleLab/CrucibleLab.exe`. Keep its `_internal` folder next
to the executable. This is a local combat lab; no sign-in or API key is needed.

## Run a small complete experiment

1. Experiment: **groups**.
2. Group resource budget: **1**.
3. New attempts per batch: **100**.
4. Group condition: **baseline**.
5. Attacks: **subsets** (includes attacking with nothing).
6. Choose a new checkpoint, such as `my-first-run.sqlite`, in your Documents
   folder or another writable experiment folder outside the app bundle.
7. Click **Run / Resume**. This preset completes **27 encounters**.

The status should show **27/27 completed**, zero pending and zero errors.
A checkpoint stores progress; each run creates a fresh report directory beside it.

## Read the report

Click **Open latest report**. First check coverage and completion counts. The
board comparison rows show ATK/current HP and observed damage/loss ranges.
Expand **Joint outcomes and example replay IDs** for actual combinations of
player damage, attacking creature losses and defending creature losses.
Counts describe enumerated choices, not probabilities or deck win rates.

Copy one example replay ID. In the lab, choose **Inspect exported replays...**
and select that report directory. Paste the ID into the filter, then select the
encounter. Read BEFORE -> DECLARATIONS -> DAMAGE EVENTS -> AFTER. The events are
simultaneous even though displayed as lines. No-attack examples preserve the board;
that is a legal choice, not a draw or victory.

## Try mixed states and resume

Choose **groups**, budget **2**, condition **mixed**, attacks **subsets**, batch
size **100**, and a NEW checkpoint. The entire experiment has **35,058 encounters**;
100 completes only a subset. Repeated **Run / Resume** continues the same job set.
Pause/cancel stop scheduling after the current combat and preserve saved work.
Wait for the report before closing. If the small batch finishes before a pause
click, it simply reaches its batch limit normally.

Mixed varies attackers between full/1 HP and defenders between full/1 HP,
exhausted, or shielded. Duplicate states (e.g. a full-health 1HP creature) are
removed. These are alternatives per creature, not every combination of modifiers
on one creature. Mixed is bounded to budgets1–2. All-attack mode and the older
condition presets remain available.

Do not change an existing checkpoint's experiment options. Start a new checkpoint
for a new budget/condition/attack mode; mismatched pins reject without replacing
completed results. Source/package engine hashes can differ, so use reports and
checkpoints with the build that created them. Reports are readable without the
app, but verification requires the matching engine build.

## Useful next questions

- Which attacks prevent player damage, and what creatures are lost in exchange?
- Does attacking with only one creature change the available outcomes?
- How do persistent wounds, exhaustion or prevention change the same board?

These experiments do not include deployment timing, card draws, bots or full
matches. An appealing combat exchange does not establish a balanced deck.
