# Discard-permanent hand-pressure evaluation

Run from Game with PYTHONPATH=src: `python -m crucible_play.hand_pressure`.
Eighteen Salvage Battery cases pass: 2/3/4 seats, 1/2/3 excess cards, and pressure created
by actual DrawCards or RecoverDiscardCard instructions. Each seat has forty
distinct registered practice cards. The fixture starts with an intentionally
large hand and natural capacity ten; managed Start/Draw reaches Main with the
intended hand size. It is not a normal opening or a balance simulation.

Salvage Battery is paid for and resolves before pressure is applied. End discards
use normal commands, ordering confirmations and priority passes. Each actual
hand discard queues one reward. Available resources equal ten minus printed cost
plus actual discards, the hand returns to seven, and those resources persist after
rotation to the next player. Recovery/drawing do not themselves earn salvage.

This closes the functional discard-reward gap in the earlier nine-seed evaluation.
It does not establish how frequently natural play produces excess hands or whether
the printed cost is appropriate. Keep that earlier zero-discard observation as
evidence for the strategy/cost study in DISCARD_STRATEGY.md.

Archive Well adds 54 cases with the same seats/pressure amounts/sources and three
decision patterns: accept all, skip all, and alternating Use/Skip. Patterns coincide
for one-card excess but deliberately retain the same matrix shape. All pass.
Only accepted choices queue; the original multi-trigger group still confirms its
accepted order even when empty. The hand returns to seven. Current available
resources stay five after paying the printed cost; permanent_bonus equals accepted
discards. Ordinary engine commands pass through other players' turns to the real
next own Start: available resources become ten natural + one ongoing + accepted
permanent capacity. Mandatory Battery cases still verify retained immediate rewards.
