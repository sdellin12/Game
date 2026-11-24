# Package-policy regression audit and fresh-seed validation

## Reproduce the known-case audit
Set PYTHONPATH=src from Game:
```powershell
python -m crucible_play.package_eval --ablation --players 4 --seeds package-1 --seat P3 --policies baseline aware aware-no-discard aware-no-guard aware-no-setup revised --trace-output dist/package-traces.json > dist/package-ablation.json
python -m crucible_play.package_eval --ablation --report-input dist/package-ablation.json --format markdown > docs/experiments/PACKAGE_ABLATION.md
```
The generated table is separate from the historical 72-game PACKAGE_COMPARISON.md.
The trace callback records only the experimental seat's chosen/counterfactual
baseline actions and visible counts. No raw hands, future deck order or server
shuffle seeds are exported. Traces are for these synthetic games, not a new public
match projection or saved-game field.

## Isolating the regression
The prior full aware candidate loses the package-1/four-player/P3 case to P4;
baseline wins for P3. The one-component ablations keep every other policy choice,
deck, seed, seat, opening decision and command bound fixed:
- Disable discard valuation: still loses to P4, 31 observed own Starts.
- Disable short-deck avoidance: still loses to P4, 31 observed own Starts.
- Disable sequencing: wins for P3, 35 observed own Starts.

The full candidate's compact trace contains two deviations from baseline:
- Global turn 51, MainBefore: chooses Insight over unit-18, with 24 life, fourteen
  available resources, fifteen deck cards and two creatures in play.
- Global turn 63, MainBefore: chooses Surveyor's Notes over unit-20, with 24 life,
  thirteen resources, four deck cards and three creatures in play.

Sequencing allowed draw/outlet Actions to replace an affordable creature whenever
the player's creature count exceeded the largest enemy board. Counts alone did
not make sacrificing that deployment safe. The revision preserves any affordable
creature play selected by baseline, including when ahead on creature count. It can
still reorder payoffs/outlets when that does not displace the creature play.

The revised policy restores this case's P3 win, 35 observed own Starts, 33 Lantern
resources, one Battery resource and zero Well capacity. This fixes the identified
development regression; it does not prove every old or future case is fixed.
Historical `aware` behavior remains available unchanged. `revised` is a separate
policy name, so prior reports remain reproducible.

## Fresh-seed design
The revision was fixed before inspecting package-3/package-4 outcomes. Cross both
fresh seeds with every seat at 2/3/4 players, control/package experimental deck,
and baseline/revised experimental policy: 72 games. Opponents remain control/baseline.
Use the same shared 43-card pool, forty-card singleton deck transactions, common-card
shuffle positions, Gold leaders, keep-all openings and 4000-command limit as before.

```powershell
python -m crucible_play.package_eval --seeds package-3 package-4 --policies baseline revised > dist/package-fresh.json
python -m crucible_play.package_eval --report-input dist/package-fresh.json --format markdown --method PACKAGE_REGRESSION.md > docs/experiments/PACKAGE_FRESH_COMPARISON.md
```

Observed own Starts remain censored descriptive counts, not survival estimates.
Control/baseline rotations repeat underlying trajectories and seed pairs are
correlated. Two fresh seeds do not establish a general win rate. Queued effects,
actual discard commitments, delivered resources and permanent capacity remain
separate measurements. Rules, card costs, decks, live bots and save schema stay
unchanged during this experiment; there is no arbitrary loop or turn cap beyond
the explicitly reported evaluation command bound.

## Fresh-seed results
All 72 fresh games complete; the generated PACKAGE_FRESH_COMPARISON.md table
contains every seed/seats/deck/policy group. Together with six known-case audit
runs, this checkpoint records 78 evaluation runs.

| Experimental deck/policy | Wins / cases | Outlet discards | Lantern resources | Battery resources | Well capacity | Paid refills |
| --- | --- | --- | --- | --- | --- | --- |
| Control / baseline | 6 / 18 | 0 | 110 | 0 | 0 | 0 |
| Package / baseline | 9 / 18 | 12 | 217 | 4 | 6 | 4 |
| Control / revised | 6 / 18 | 0 | 110 | 0 | 0 | 0 |
| Package / revised | 11 / 18 | 11 | 208 | 3 | 5 | 5 |

Package wins improve from 4/9 to 5/9 on package-3 and from 5/9 to 6/9 on package-4.
Three package cases change from experimental-player losses to wins: package-3's
three-player P1 and four-player P1, plus package-4's duel P1. One changes from a
win to a loss: package-3's four-player P3 (baseline winner P3, revised winner P1).
The remaining package wins/losses are unchanged.

The revision wins more of this sample while collecting fewer resource/capacity
rewards and using one more paid refill. Do not optimize reward counts as a substitute
for match outcomes or collapse capacity into immediate resources. Neither this
aggregate improvement nor restoring the development win proves a uniformly stronger
policy. Keep the live opponent unchanged; `revised` remains explicitly selected in
the headless runner. Next investigate the remaining four-player fresh-seed loss
before promotion, and use additional untouched seeds for any subsequent tuning.

## Verification
441 Windows tests pass, including four new tests for the revised creature priority,
ablation/trace integrity and incomplete CLI results. Existing private-view, legal
payment, optional-choice, save, combat and policy tests remain green. All fifteen
policy/study tests pass in isolation as well.
No save format, runtime dependencies, card costs or card-template assets changed.
