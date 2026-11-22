import unittest
from crucible_sim.comparisons import comparison_summary
from crucible_sim.cli import run_scenario
from crucible_sim.groups import group_scenarios

class ComparisonTests(unittest.TestCase):
    def test_blocked_and_unblocked_ranges_are_exact(self):
        records = [run_scenario(s) for s in list(group_scenarios(1))[:2]]
        rows = comparison_summary(records)['matchups']
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row['encounters'], 2)
        self.assertEqual(row['player_damage_range'], [0, 2])
        self.assertEqual(row['attacker_losses_range'], [0, 1])
        self.assertEqual(row['defender_losses_range'], [0, 1])

    def test_wounded_boards_are_not_combined_and_empty_is_supported(self):
        import copy
        scenario = next(group_scenarios(1))
        other = copy.deepcopy(scenario)
        other['state']['creatures'][1]['exhausted'] = True
        self.assertEqual(len(comparison_summary([run_scenario(scenario), run_scenario(other)])['matchups']), 2)
        self.assertEqual(comparison_summary([])['matchups'], [])
