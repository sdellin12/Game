import unittest
from crucible_core import CombatError
from crucible_sim.groups import creature_groups, blocker_assignments, group_scenarios
from crucible_sim.cli import run_scenario

class GroupTests(unittest.TestCase):
    def test_exact_budget_and_multisets(self):
        groups = list(creature_groups(3))
        self.assertEqual(len(groups), 22)  # 3 large, 9 mixed, 10 triples
        self.assertTrue(all(sum(p['cost'] for p in g) == 3 for g in groups))
        self.assertEqual({len(g) for g in groups}, {1, 2, 3})
        with self.assertRaises(CombatError):
            list(creature_groups(4))

    def test_block_assignments_include_order_and_unblocked(self):
        assignments = list(blocker_assignments(1, 2))
        self.assertEqual(set(assignments), {((),), ((0,),), ((1,),), ((0,1),), ((1,0),)})
        self.assertEqual(len(list(blocker_assignments(2, 1))), 3)

    def test_budget_one_all_directional_profiles_and_unblocked(self):
        records = [run_scenario(s) for s in group_scenarios(1)]
        self.assertEqual(len(records), 18)
        self.assertEqual(len({r['job_id'] for r in records}), 18)
