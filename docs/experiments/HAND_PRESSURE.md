# Salvage Battery hand-pressure evaluation

Run from Game with PYTHONPATH=src: `python -m crucible_play.hand_pressure`.
Eighteen directed cases pass: 2/3/4 seats, 1/2/3 excess cards, and pressure created
by actual DrawCards or RecoverDiscardCard instructions. Each seat has forty
distinct registered practice cards. The fixture starts with an intentionally
large hand and ten resources; it is not a normal opening or a balance simulation.

Salvage Battery is paid for and resolves before pressure is applied. End discards
use normal commands, ordering confirmations and priority passes. Each actual
hand discard queues one reward. Available resources equal ten minus printed cost
plus actual discards, the hand returns to seven, and those resources persist after
rotation to the next player. Recovery/drawing do not themselves earn salvage.

This closes the functional discard-reward gap in the earlier nine-seed evaluation.
It does not establish how frequently natural play produces excess hands or whether
the printed cost is appropriate. Keep that earlier zero-discard observation as
evidence for a later strategy/cost study.
