# Exact follow-up budget check

2026-11-24. The `budgeted` headless policy retains creature protection and requires
a useful known follow-up to remain payable after a payoff's actual first payment.
Historical `aware` and `revised` behavior remains reproducible.

The check copies only the acting player's permitted view, subtracts ordinary
resources, removes actually spent tokens and the setup card, then calls the
existing exact-payment helper for known draw/outlet cards. It counts actual hand
cards as discard fodder even when they are poor draw plays. It does not credit
future refunds, ongoing capacity or unknown draws, and does not mutate the input.

Focused tests cover the five-resource Lantern/draw counterexample, six-resource
successful setup, spent versus remaining tokens, post-setup fodder and retained
creature priority. Both known four-player P3 losses are restored: package-1 and
package-3 win for P3 with the baseline reward totals and observed own Starts.

The frozen policy was compared against baseline on package-5/package-6, all seats
at 2/3/4 players and both experimental decks: 72 completed matched games. Method,
censoring and correlation limitations are unchanged from PACKAGE_REGRESSION.md.
Generated per-group results: PACKAGE_BUDGET_COMPARISON.md.

| Fresh package cases | Baseline | Budgeted |
| --- | --- | --- |
| package-5 wins | 1/9 | 4/9 |
| package-6 wins | 3/9 | 2/9 |
| Combined wins | 4/18 | 6/18 |
| Outlet discards | 13 | 14 |
| Paid refills | 1 | 3 |

Three package-5 losses become wins (duel P1, three-player P1, four-player P2), but
package-6/four-player/P4 changes from a win to a loss. The known budget defect is
fixed; this small correlated sample does not establish uniform policy strength.
The candidate remains headless and live bots stay baseline. No rule, card cost,
save schema or default deck changes.

Reproduce with PYTHONPATH=src:
```powershell
python -m crucible_play.package_eval --seeds package-5 package-6 --policies baseline budgeted > dist/package-budget-fresh.json
python -m crucible_play.package_eval --report-input dist/package-budget-fresh.json --format markdown --method PACKAGE_BUDGET.md > docs/experiments/PACKAGE_BUDGET_COMPARISON.md
```

## Product direction
Human testing is deferred by owner direction in REQUIREMENTS.md until a usable app
takes shape. New --hotseat/--players launch options support developer setup, but an
attempted desktop walkthrough did not establish family usability and was stopped.
FAMILY_PLAYTEST.md is a future checklist. Prioritize the usable match UI milestone
instead of requiring another debug-harness family session.

Verification: 450 Windows tests pass; both known regression replays and all 72
fresh comparisons complete. Documentation/source checks pass without changing
private-save or lab-checkpoint formats.
