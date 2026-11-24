# Remaining package-3 regression investigation

Scope: the previously reported package-3/four-player/P3 package-deck loss. This
case was a fresh validation case in PACKAGE_REGRESSION.md; it is now development
evidence. Do not tune on it and continue calling package-3 an untouched holdout.
No new heuristic is promoted or retuned in this investigation.

## Reproduce
Set PYTHONPATH=src from Game:
```powershell
python -m crucible_play.package_eval --ablation --players 4 --seeds package-3 --seat P3 --policies baseline revised revised-no-discard revised-no-guard revised-no-setup --trace-output dist/package-followup-traces.json > dist/package-followup.json
python -m crucible_play.package_eval --ablation --report-input dist/package-followup.json --format markdown --method PACKAGE_FOLLOWUP.md > docs/experiments/PACKAGE_FOLLOWUP_ABLATION.md
```
Each revised ablation retains creature protection and disables only its named
component. A routing regression test checks that distinction. All five runs finish
within the same 4000-command bound; the generated table preserves their outcomes.

## Finding
Baseline wins for P3 with 34 observed own Starts and 33 Lantern resources. Revised
loses to P1 after 13 observed own Starts and delivers nine Lantern resources.
Disabling revised discard valuation or its short-deck guard still loses. Disabling
sequencing restores the baseline P3 win and reward totals. This isolates the issue
to the remaining sequencing component in this case, not the creature-priority fix.

The revised trace contains one choice differing from baseline on that same view:
command 738, global turn
20, MainBefore, P3 has thirty life, five available resources, 28 deck cards and
four creatures. It plays Scholar's Lantern (cost four) instead of Fresh Inspiration
(cost two). Both paths had just played unit-01. Baseline then enters Combat with
three resources and 27 deck cards; revised enters with one resource and 28 cards.
The Lantern setup leaves too little to play the known draw immediately. The
candidate's presence-of-draw check lacks an exact remaining-payment/follow-up check.
The trace compares policies on the revised trajectory, not two complete alternate
future states at every command.
The ablation establishes the changed trajectory; do not infer a universal damage
or resource value for that one draw from this result.

## Next focused implementation
Before overriding a baseline Action with payoff setup, check whether a useful
follow-up already in the acting hand remains payable after the exact first
payment. Remove actually spent owned tokens and ordinary resources from a copied
permitted view, then use the existing exact-payment helper. Do not count future
trigger refunds as upfront money. Retain the creature/lethal protections and test
ordinary-only and token-payment counterexamples before benchmarking.

That is a proposed next revision, not an implemented strategy in this checkpoint.
Use new untouched seeds for its validation. The current live opponent stays
baseline; the historical aware/revised variants remain reproducible headless tools.
This one-case investigation adds no family balance claim or rule/cost change.

## Family handoff
FAMILY_PLAYTEST.md in the parent directory is ready for an actual local session.
Its observation fields are deliberately Not run. Human results must be collected
before claiming family pacing, comprehension, enjoyment or device readiness.
Final verification: all five replay variants completed and 444 Windows tests pass;
documentation links/entry points/version labels and source syntax checks also pass.
