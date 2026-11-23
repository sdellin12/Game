# Discard strategy and cost study

## Method
Run with PYTHONPATH=src from Game:
```powershell
python -m crucible_play.discard_eval --players 2 3 4
python -m crucible_play.discard_eval --source-discount 1
```
Seeds discard-1/2/3, forty-card singleton pack v9, Gold leaders, keep-all openings,
4000-command limit. Pair the same seed/seats/content with baseline versus an
experimental P1 policy; all other seats use the existing opponent. Only permitted
views feed decisions. No authoritative match state is edited during games.

The holding policy prioritizes affordable Battery/Well and draw/recovery cards.
Once it controls two creatures (including its leader), it passes instead of other
card plays to retain a hand. Normal attacks, reactions, leader abilities and private
choices otherwise use the existing policy. This is a combined engine-priority and
holding treatment, not an isolated test of either choice. It can hold before seeing
a discard engine, and it does not estimate incoming danger or future draws.

Track P1 paid source resources, resolved entries, End discards, maximum hand,
withheld plays, queued triggers and delivered rewards separately. Delivered Battery
resources/Well permanent_bonus are positive projected deltas when that source's
discard trigger actually resolves on a pass. Capacity units are not current money
or measured spending. Completion/results cover the whole game even after P1 dies.

## Printed-cost results
All 18 games finish. Numbers below are totals over three seeds; wins refer to P1.

| Seats | Baseline wins | Holding wins | End discards baseline / hold | Holding delivered Battery / Well |
| --- | --- | --- | --- | --- |
| 2 | 2/3 | 0/3 | 1 / 3 | 3 resources / 3 capacity |
| 3 | 0/3 | 0/3 | 1 / 0 | 0 / 0 |
| 4 | 0/3 | 0/3 | 0 / 0 | 0 / 0 |

All baseline delivered rewards are zero. P1 pays 23 source resources in baseline
games and 43 in holding games. Holding gets two Battery and seven Well entries.
Only discard-2's duel delivers rewards: three End discards queue and resolve three
of each reward; P1 still loses, after 1404 commands/70 global turns. That policy
withholds 33 plays. Discard-1's duel instead loses at 327 commands/17 global turns
versus baseline's 1385/70; neither earns rewards. Global turns do not measure P1's
survival after elimination in multiplayer.

Reproducible command counts, seed order 1/2/3:

| Seats | Baseline | Holding |
| --- | --- | --- |
| 2 | 1385 / 1220 / 884 | 327 / 1404 / 1418 |
| 3 | 1639 / 1585 / 1751 | 1611 / 1675 / 1644 |
| 4 | 1918 / 3318 / 1926 | 1710 / 2704 / 1950 |

## Cost sensitivity and recommendation
Six additional duels apply an in-memory one-resource discount to both sources for
every seat: Battery 3, Well 4. Report the distinct content hash and discount;
canonical pack/card definitions remain unchanged. All six games finish. Baseline
still wins 2/3 and holding 0/3. Holding delivers the same three resources/three
capacity in discard-2 only. Source spending totals fall from 23 to 18 for each
duel policy. Command counts become 1385/1220/881 baseline, 290/1404/1418 holding.

Keep printed costs at Battery 4 / Well 5. The discount did not improve these
outcomes or create more reward opportunities. Three Battery rewards alone do not
recover its four-resource upfront payment; its ongoing capacity is additional value
and prevents treating this as a full break-even calculation. Well's capacity can
contribute on repeated refills, so comparing three capacity directly with five paid
resources would also be misleading.

Next, design/evaluate a deliberate discard outlet or a stronger draw/hand-building
package, with defensive board requirements and seat-rotated comparisons. Holding
cards alone incurs opportunity costs before any End reward can arrive. Do not
discount existing sources to compensate for that policy weakness.

## Limits and verification
This small deterministic study diagnoses access/strategy behavior, not general
balance or statistical win rates. No seat rotation; P1 often fails to establish
an engine in multiplayer. Gold/keep-all choices omit other leaders and mulligans.
No net capacity spending or opponent adaptation is measured. Directed cases in
HAND_PRESSURE.md independently verify reward timing and Use/Skip correctness.
Full Windows suite: 403 tests pass, including six study/Archive regression tests.
