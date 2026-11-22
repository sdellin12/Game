import math
import unittest
from dataclasses import replace

from crucible_core import (
    Attack, CombatError, CombatState, Creature, Player, Shield, resolve_combat,
)


def creature(i, controller, atk, hp, **kwargs):
    return Creature(i, controller, atk, hp, hp, **kwargs)


def state(*creatures):
    return CombatState((Player("A"), Player("B"), Player("C")), creatures)


def hp(result, i):
    return next((c.health for c in result.state.creatures if c.instance_id == i), 0)


class CombatTests(unittest.TestCase):
    def test_simultaneous_trade(self):
        s = state(creature("a", "A", 3, 2), creature("b", "B", 2, 3))
        r = resolve_combat(s, (Attack("a", "B", ("b",)),))
        self.assertEqual(r.defeated_creatures, ("a", "b"))
        self.assertEqual(s.creatures[0].health, 2)

    def test_pooled_retaliation_and_persistent_wounds(self):
        s = state(creature("a", "A", 4, 8), creature("b", "B", 2, 3),
                  creature("c", "B", 3, 5))
        r = resolve_combat(s, (Attack("a", "B", ("b", "c")),))
        self.assertEqual((hp(r, "a"), hp(r, "b"), hp(r, "c")), (3, 0, 4))
        self.assertEqual(r.events[-1].source_ids, ("b", "c"))
        survivor = next(c for c in r.state.creatures if c.instance_id == "c")
        self.assertFalse(survivor.exhausted)
        self.assertTrue(next(c for c in r.state.creatures if c.instance_id == "a").exhausted)
        # An independent later opponent's attack uses the already-wounded state.
        later = replace(r.state, creatures=r.state.creatures + (creature("d", "C", 1, 3),))
        r2 = resolve_combat(later, (Attack("d", "B", ("c",)),))
        self.assertEqual(hp(r2, "c"), 3)

    def test_breakthrough_example(self):
        s = state(creature("a", "A", 8, 8, keywords=("breakthrough",)),
                  creature("b", "B", 2, 3), creature("c", "B", 2, 2))
        r = resolve_combat(s, (Attack("a", "B", ("b", "c")),))
        self.assertEqual(r.state.players[1].health, 27)
        self.assertEqual(hp(r, "a"), 4)
        self.assertEqual(r.defeated_creatures, ("b", "c"))

    def test_without_breakthrough_excess_never_hits_player(self):
        s = state(creature("a", "A", 8, 8), creature("b", "B", 0, 1))
        r = resolve_combat(s, (Attack("a", "B", ("b",)),))
        self.assertEqual(r.state.players[1].health, 30)

    def test_removed_blockers_keep_blocked_status(self):
        s = state(creature("a", "A", 8, 8))
        blocked = (Attack("a", "B", was_blocked=True),)
        self.assertEqual(resolve_combat(s, blocked).state.players[1].health, 30)
        s2 = replace(s, creatures=(replace(s.creatures[0], keywords=("breakthrough",)),))
        self.assertEqual(resolve_combat(s2, blocked).state.players[1].health, 22)

    def test_zero_attack_defender_blocks_and_takes_wounds(self):
        s = state(creature("a", "A", 1, 2), creature("b", "B", 0, 3))
        r = resolve_combat(s, (Attack("a", "B", ("b",)),))
        self.assertEqual((hp(r, "a"), hp(r, "b")), (2, 2))

    def test_exhaustion_before_prevention_not_after(self):
        s = state(creature("a", "A", 4, 8),
                  creature("b", "B", 0, 10, exhausted=True, shields=(Shield("s", 2),)))
        r = resolve_combat(s, (Attack("a", "B", ("b",)),))
        self.assertEqual(hp(r, "b"), 6)  # ceil(4*1.5)-2 = 4 damage
        self.assertEqual((r.events[0].modified, r.events[0].prevented), (6, 2))

    def test_exhausted_breakthrough_boundary(self):
        s = state(creature("a", "A", 8, 8, keywords=("breakthrough",)),
                  creature("b", "B", 0, 5, exhausted=True))
        r = resolve_combat(s, (Attack("a", "B", ("b",)),))
        self.assertEqual((r.events[0].raw, r.events[0].health_damage), (3, 5))
        self.assertEqual(r.state.players[1].health, 25)

    def test_prevention_counts_for_breakthrough(self):
        s = state(creature("a", "A", 8, 8, keywords=("breakthrough",)),
                  creature("b", "B", 0, 3, shields=(Shield("s", 2),)))
        r = resolve_combat(s, (Attack("a", "B", ("b",)),))
        self.assertEqual(r.state.players[1].health, 27)

    def test_shields_expiry_first(self):
        s = state(creature("a", "A", 2, 3), creature("b", "B", 0, 4,
                  shields=(Shield("later", 3, 2), Shield("early", 2, 1))))
        r = resolve_combat(s, (Attack("a", "B", ("b",)),))
        self.assertEqual(r.state.creatures[1].shields, (Shield("later", 3, 2),))
        self.assertEqual(r.events[0].health_damage, 0)

    def test_blocker_penalty_not_applied_to_exhausted_attacker(self):
        s = state(creature("a", "A", 1, 8), creature("b", "B", 4, 8))
        r = resolve_combat(s, (Attack("a", "B", ("b",)),))
        self.assertEqual(hp(r, "a"), 4)

    def test_group_challenge_target_retaliates_once(self):
        s = state(creature("a", "A", 3, 3, keywords=("challenge",)),
                  creature("b", "A", 3, 3, keywords=("challenge",)),
                  creature("c", "B", 4, 5, exhausted=True))
        r = resolve_combat(s, (Attack("a", "B", challenge_target="c"),
                               Attack("b", "B", challenge_target="c")),
                           (("c", ("b", "a")),))
        self.assertEqual((hp(r, "a"), hp(r, "b"), hp(r, "c")), (2, 0, 0))
        self.assertEqual(r.state.players[1].health, 30)

    def test_challenge_miss_is_spent_attack(self):
        s = state(creature("a", "A", 8, 8, keywords=("challenge", "breakthrough")))
        r = resolve_combat(s, (Attack("a", "B", challenge_target="gone"),))
        self.assertEqual(r.misses, ("a",))
        self.assertEqual(r.state.players[1].health, 30)
        self.assertTrue(r.state.creatures[0].exhausted)
        self.assertTrue(r.state.creatures[0].attack_used)

    def test_challenged_creature_cannot_block(self):
        s = state(creature("a", "A", 3, 3, keywords=("challenge",)),
                  creature("b", "A", 3, 3), creature("c", "B", 3, 3))
        with self.assertRaises(CombatError):
            resolve_combat(s, (Attack("a", "B", challenge_target="c"),
                               Attack("b", "B", ("c",))))

    def test_same_blocker_cannot_block_twice(self):
        s = state(creature("a", "A", 1, 3), creature("b", "A", 1, 3),
                  creature("c", "B", 1, 3))
        before = repr(s)
        with self.assertRaises(CombatError):
            resolve_combat(s, (Attack("a", "B", ("c",)), Attack("b", "B", ("c",))))
        self.assertEqual(repr(s), before)

    def test_illegal_readiness_and_unknown_ability_reject(self):
        for kwargs in ({"exhausted": True}, {"attack_eligible": False},
                       {"attack_used": True}, {"keywords": ("revive",)}):
            with self.subTest(kwargs=kwargs), self.assertRaises(CombatError):
                resolve_combat(state(creature("a", "A", 1, 3, **kwargs)),
                               (Attack("a", "B"),))

    def test_duplicate_ids_and_negative_values_reject(self):
        for cs in ((creature("a", "A", 1, 3), creature("a", "B", 1, 3)),
                   (creature("a", "A", -1, 3),)):
            with self.assertRaises(CombatError):
                resolve_combat(state(*cs), ())

    def test_split_attacks_different_players(self):
        s = state(creature("a", "A", 2, 3), creature("b", "A", 3, 4))
        r = resolve_combat(s, (Attack("a", "B"), Attack("b", "C")))
        self.assertEqual([p.health for p in r.state.players], [30, 28, 27])

    def test_lethal_player_report_not_winner(self):
        s = state(creature("a", "A", 40, 3))
        r = resolve_combat(s, (Attack("a", "B"),))
        self.assertEqual(r.lethal_players, ("B",))
        self.assertEqual(len(r.state.players), 3)  # no full-match cleanup promised

    def test_declaration_order_does_not_change_independent_results(self):
        s = state(creature("a", "A", 2, 3), creature("b", "A", 3, 4),
                  creature("c", "B", 1, 3))
        attacks = (Attack("a", "B", ("c",)), Attack("b", "C"))
        self.assertEqual(resolve_combat(s, attacks).state,
                         resolve_combat(s, tuple(reversed(attacks))).state)

    def test_exhaustion_lethal_threshold_against_independent_bruteforce(self):
        # Enumerate a bounded finite domain against the rule's arithmetic,
        # independently finding the first lethal assignment by brute force.
        for health in range(1, 13):
            for shield in range(5):
                needed = next(d for d in range(30) if math.ceil(d * 1.5) - shield >= health)
                s = state(creature("a", "A", 25, 50, keywords=("breakthrough",)),
                          creature("b", "B", 0, health, exhausted=True,
                                   shields=(Shield("s", shield),)))
                r = resolve_combat(s, (Attack("a", "B", ("b",)),))
                self.assertEqual(r.events[0].raw, needed, (health, shield))
                self.assertEqual(r.state.players[1].health, 30 - (25 - needed))


if __name__ == "__main__":
    unittest.main()
