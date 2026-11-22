# Group condition experiment evidence

2026-11-22, Windows Python 3.14.3. Combat-only numeric fixtures, no full matches.

| Budget2 condition | Exact encounters | Directional starting-board matchups | Distinct joint outcomes summed across matchups |
|---|---:|---:|---:|
| baseline | 558 | 81 | 233 |
| wounded (all current HP1) | 558 | 81 | 261 |
| exhausted (all defenders) | 558 | 81 | 235 |
| shielded (2 prevention per defender) | 558 | 81 | 214 |

Every export replayed exactly. Counts are finite legal blocker assignments/orders,
not independent games. Repeated numeric profiles do not establish singleton deck
legality. Outcomes contain player damage, attacker losses and defender losses;
example replay IDs identify actual joint outcomes. Different unique-outcome counts
show changed combat possibilities, not stronger decks or proof of balance.

Reproduce with `py -3 run_lab.py groups --budget 2 --condition CONDITION --output
NEW_DIRECTORY` (one line), then `py -3 run_lab.py verify NEW_DIRECTORY`.
Conditions are baseline/wounded/exhausted/shielded. Outputs stay under ignored
lab-runs; the repository retains this compact evidence instead of bulk histories.

Validation: 53 source tests pass, including exact shielded trade, condition state
validation, replay uniqueness, joint outcome denominator/witness checks, and
condition-mismatched checkpoint rejection preserving completed jobs. Existing
baseline scenario names/encoding are unchanged. Conditions add no keyword/stat
changes to the core. Full-match timing proposals are documented separately.

The rebuilt portable Windows executable also exported and replayed 18 budget-1
encounters for each added condition. Desktop condition selection is tested through
a real worker/export; matrix mode rejects group-only conditions before creating
checkpoint files. Existing source and packaged baseline entry points remain.
