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


    def test_condition_states_and_exact_shielded_trade(self):
        for condition in ('wounded', 'exhausted', 'shielded'):
            scenarios = list(group_scenarios(1, condition))
            self.assertEqual(len(scenarios), 18)
            self.assertEqual(len({run_scenario(s)['job_id'] for s in scenarios}), 18)
            for scenario in scenarios:
                a, b = scenario['state']['creatures']
                self.assertFalse(a['exhausted'])
                if condition == 'wounded':
                    self.assertEqual((a['health'], b['health']), (1, 1))
                elif condition == 'exhausted':
                    self.assertTrue(b['exhausted'])
                else:
                    self.assertEqual(b['shields'][0]['amount'], 2)
            if condition == 'shielded':
                trade = run_scenario(scenarios[1])
                self.assertEqual(trade['result']['defeated_creatures'], ['A0'])
                defender = trade['result']['state']['creatures'][0]
                self.assertEqual((defender['health'], defender['shields']), (1, []))
        with self.assertRaises(CombatError):
            list(group_scenarios(1, 'unknown'))

    def test_optional_attacks_include_hold_all_and_preserve_nonattacker(self):
        scenarios = list(group_scenarios(2, attack_mode='subsets'))
        self.assertTrue(any(not s['attacks'] for s in scenarios))
        selected = next(s for s in scenarios if len(s['state']['creatures']) == 4
                        and [a['attacker_id'] for a in s['attacks']] == ['A1'])
        result = run_scenario(selected)['result']
        held = next(c for c in result['state']['creatures'] if c['instance_id'] == 'A0')
        self.assertFalse(held['exhausted'])
        self.assertFalse(held['attack_used'])
        hold = next(s for s in scenarios if not s['attacks'])
        self.assertEqual(run_scenario(hold)['result']['state'], hold['state'])
        ids = [run_scenario(s)['job_id'] for s in scenarios]
        self.assertEqual(len(ids), len(set(ids)))

    def test_mixed_boards_have_independent_states_and_are_bounded(self):
        scenarios = list(group_scenarios(1, 'mixed', 'subsets'))
        for scenario in scenarios:
            run_scenario(scenario)
            self.assertFalse(scenario['state']['creatures'][0]['exhausted'])
        boards = {str(s['state']) for s in scenarios}
        self.assertGreater(len(boards), 9)
        ids = [run_scenario(s)['job_id'] for s in scenarios]
        self.assertEqual(len(ids), len(set(ids)))
        with self.assertRaises(CombatError):
            list(group_scenarios(3, 'mixed'))
        with self.assertRaises(CombatError):
            list(group_scenarios(1, attack_mode='random'))

    def test_baseline_inputs_keep_previous_checkpoint_digest(self):
        from crucible_sim.cli import digest
        self.assertEqual(digest(list(group_scenarios(2))),
            '6f5487fb96081e28901e2058176cd4ccb0af46f91598fb1c08cb371d976236d0')
