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


    def test_joint_outcomes_retain_counts_and_valid_witnesses(self):
        records = [run_scenario(s) for s in list(group_scenarios(1))[:2]]
        row = comparison_summary(records)['matchups'][0]
        outcomes = row['outcomes']
        self.assertEqual([(o['player_damage'], o['attacker_losses'], o['defender_losses'])
                          for o in outcomes], [(0, 1, 1), (2, 0, 0)])
        self.assertEqual(sum(o['encounters'] for o in outcomes), row['encounters'])
        self.assertTrue(all(o['example_job_id'] in {r['job_id'] for r in records} for o in outcomes))

    def test_no_attack_outcome_is_included_and_labeled(self):
        record = run_scenario(next(group_scenarios(1, attack_mode='subsets')))
        row = comparison_summary([record])['matchups'][0]
        self.assertTrue(row['no_attacks'])
        self.assertEqual(row['attacker_ids'], [])
        self.assertEqual(row['outcomes'][0]['player_damage'], 0)
        self.assertEqual(row['outcomes'][0]['attacker_losses'], 0)
        self.assertIn('no attacks', row['attacking_board'])

    def test_empty_combat_without_players_does_not_break_comparison_export(self):
        record = run_scenario({'schema_version': 1, 'state': {'players': [], 'creatures': []}, 'attacks': []})
        self.assertEqual(comparison_summary([record])['matchups'], [])
