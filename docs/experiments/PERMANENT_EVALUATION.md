# Permanent seed evaluation
2026-11-23. Reproduce with PYTHONPATH=src:
`python -m crucible_play.permanent_eval --players 2 3 4 --seeds permanent-1 permanent-2 permanent-3 --limit 4000`

## Method and findings
All seats use the permitted-view practice policy, Gold leaders and kept opening
hands. Each run starts a fresh deterministic session. Report terminal/incomplete
status, commands/turns, pack version, actual beacon-01/02 entries and public queued
trigger items. An exhausted command budget stays incomplete; no result is fabricated.
Queued items are not a claim that a reward resolved or improved win rate.

The original pack-v7 policy completed all nine baseline games but played neither
permanent. Inspection found its blanket rule skipped all permanents after own turn
five. Narrowing that rule preserves the old plain-capacity cutoff while allowing
trigger-bearing permanents. The same three duel seeds on pack v7 then recorded
nine permanent entries and 29 queued draw items. Those controlled before/after
runs verify the cutoff fix without changing card behavior.

Final pack-v8 optional-choice runs completed all nine games within 4,000 commands:
- Two players: 1385/842/545 commands; 70/41/26 turns.
- Three players: 1769/1691/1831 commands; 66/68/77 turns.
- Four players: 2757/2360/2327 commands; 95/88/85 turns.
They recorded 18 Scholar's Lantern entries, 17 Salvage Battery entries and 256 queued
draw-trigger items. Both permanents entered in every run. No discard-trigger items
were observed, so these seeds do not evaluate Salvage Battery's reward value.

## Limits and tests
This is functional coverage of nine deterministic games, not a balance or general
strength study. All-computer Gold/keep-all setup differs from the default mixed
human-script smoke run. Targeted hand-pressure scenarios are the next evaluation.
Four focused tests cover the cutoff distinction, bounded incomplete reporting,
actual entries/rewards in one selected seed, and invalid limits. The normal mixed
practice smoke games still complete at 327/829/1867 commands (2/3/4 seats).
