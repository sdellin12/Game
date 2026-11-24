# Matched deck and package-policy study

## Reproduce
Set PYTHONPATH=src from Game, then run:
```powershell
python -m crucible_play.package_eval > dist/package-study.json
python -m crucible_play.package_eval --report-input dist/package-study.json --format markdown > docs/experiments/PACKAGE_COMPARISON.md
```
The JSON/report are generated results; edit the evaluator/policy and regenerate.
An incomplete game is explicitly reported and makes the runner exit with code 2.
Report validation rejects duplicate cases, changed content/decks, unmatched
starting-seat/limit pairs and incomplete seat rotations.

## Comparison design
Two fixed seeds, package-1 (development) and package-2 (holdout); 2/3/4 players.
Rotate the experimental deck and policy through every seat. Opponents always use
the original forty-card control deck and baseline policy. Cross experimental deck
(control/package) with policy (baseline/package-aware): 72 games total.
All are Gold leaders, keep-all openings, no cost overrides, limit 4000 commands.

Validated normal lobby transactions select forty distinct cards from one shared
43-card pool. Both deck arms have the same content pool hash; deck hashes identify
the three replacements. Input ordering preserves common-card positions under the
same seeded shuffle; the random starting seat also stays matched. During gameplay,
policies receive only their own permitted projection. There are no match-state or
private-deck-order edits. Setup metadata never enters policy decisions.

The package removes three plain permanents providing six ongoing capacity and
adds three draw/discard Actions. This tests that whole deck substitution, not the
isolated strength of Insight. The baseline is the unchanged published opponent;
the earlier blanket holding policy is not used here.
Baseline/control repeats the same underlying match for each measured seat within
a seed/roster. These rotations and shared-seed games are correlated, not independent
win-rate samples. The policy candidate also combines several heuristics; outcomes
cannot be attributed to one heuristic without an ablation.

## Package-aware policy
Keep ordinary priority, reactions, combat, costs, optional decisions and required
refill handling from the baseline. For private discards, preserve an early defensive
creature and useful hand building/payoffs before expensive low-value cards.

In Main with a creature established, consider Lantern before known draw support,
Battery/Well before an outlet already in hand, and an outlet when a payoff is in
play. Preserve affordable early/behind-on-board creature plays and direct lethal
card plays. At low life, keep baseline decisions. Never withhold ordinary plays
just to exceed seven cards. Affordability uses current resources/tokens, not future
refunds. Avoid voluntarily choosing a draw that already exceeds the public deck
count; required refill choices still use the ordinary engine policy.

The initial two-creature setup gate prevented useful sequencing changes; final
development instead protects actual creature plays and allows setup behind one
body when no defensive creature play is available. Policy revision is fixed before
reviewing holdout outcomes. Deterministic policy tests cover these boundaries.

## Measurements and interpretation
Record the experimental player's elimination boundary and own Starts at elimination.
Surviving players are censored at match end/command limit. Report observed own Starts
as a descriptive count, not a survival estimate. Global match length is separate.
Count successful discard commitments, resolved outlet entries, queued triggers and
delivered immediate resources/permanent capacity separately. Delivery is measured
from a projected resource delta when the corresponding trigger actually resolves;
mere queueing/negation earns nothing. Focus-card spending, End discards, paid refill
and Recharge turns are also in the JSON.

Two deterministic seeds cannot establish general win rates or deck balance. The
baseline policy remains simple; no mulligan/leader variation or opponent adaptation
is included. Fixed ID/low-health targeting can create seat asymmetry, so report all
seats rather than hiding that effect. Future recovery/healing packages and alternate
policies still require their own tests. Canonical rules/costs do not change here.

## Results and decision
All 72 declared games complete below the 4000-command limit. The generated
PACKAGE_COMPARISON.md table contains every seed/seats/policy/deck group.

| Experimental deck/policy | Experimental wins / cases | Outlet discards | Lantern resources | Battery resources | Well capacity | Paid refills |
| --- | --- | --- | --- | --- | --- | --- |
| Control / baseline | 6 / 18 | 0 | 83 | 0 | 0 | 0 |
| Package / baseline | 9 / 18 | 10 | 101 | 4 | 2 | 3 |
| Control / aware | 6 / 18 | 0 | 83 | 0 | 0 | 0 |
| Package / aware | 8 / 18 | 13 | 96 | 4 | 3 | 2 |

On development seed package-1, package wins change from 4/9 baseline to 3/9 aware.
On holdout package-2, both win 5/9. The candidate adds outlet uses and reduces paid
refills, but those intermediate metrics do not establish stronger play. Well's
additional permanent capacity is a different unit from the five fewer Lantern
resources; do not combine them into a net-resource total.

One concrete regression: package-1, four players, experimental P3. Baseline package
play wins for P3; the aware policy loses to P4. Its Lantern delivery falls from 33
to 29, and observed own Starts from 35 to 31. Counts alone do not identify which
combined heuristic caused the loss; use a replay/ablation before changing it.
One concrete sequencing gain: package-1, three players, P3. The same winner and own
Starts remain, while the candidate adds one completed outlet discard, one Battery
resource and two Lantern resources. This is a functional gain, not a win-rate gain.

Keep the live opponent, card costs and default deck unchanged. The aware policy
is available only as a headless experimental variant in package_eval; it is not
wired into HarnessSession.step_opponent. No save fields or compatibility change.
Next: isolate payoff setup, discard valuation and short-deck guards as separate
ablations, then validate any winning revision against fresh untouched seeds.

Verification: 437 Windows tests pass, including eleven new policy/study tests.
They check valid mixed decks, seeded common-card positions/starting seats, incomplete
and duplicate reporting, legal exact payments, protected early creatures, no-fodder
and short-deck handling, private discard selection and other-seat boundaries.
