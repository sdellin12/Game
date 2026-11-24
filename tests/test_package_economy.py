import unittest
from crucible_play.package_economy import load_package,plan,evaluate,markdown


class PackageEconomyTests(unittest.TestCase):
    def setUp(self):self.package=load_package();self.outlet,self.notes,self.archive=self.package['cards']

    def test_outlet_is_card_neutral_and_has_real_discard_synergy(self):
        plain=plan(self.outlet);boosted=plan(self.outlet,lantern=True,battery=True,archive=True)
        self.assertEqual((plain['hand_after'],plain['net_resources']),(5,-2))
        self.assertEqual((boosted['hand_after'],boosted['net_resources'],boosted['permanent_capacity_gained']),(5,1,1))

    def test_future_refunds_cannot_pay_the_initial_cost(self):
        row=plan(self.outlet,available=1,lantern=True,battery=True)
        self.assertEqual((row['status'],row['hand_after'],row['available_after']),('cannot_pay',5,1))

    def test_last_card_is_pending_not_discard_fodder_and_skips_draw(self):
        row=plan(self.outlet,hand=1,available=2,deck=0,lantern=True,battery=True,archive=True)
        self.assertEqual((row['status'],row['drawn'],row['hand_after']),('resolved',0,0))
        self.assertEqual((row['discarded_during_effect'],row['permanent_capacity_gained'],row['available_after']),(0,0,0))

    def test_support_builds_hand_and_end_overflow_is_a_separate_discard(self):
        self.assertEqual(plan(self.notes)['net_hand'],1)
        row=plan(self.archive,hand=8,lantern=True,battery=True,archive=True)
        self.assertEqual((row['discarded_during_effect'],row['hand_before_end'],row['end_discards'],row['hand_after']),(0,10,3,7))
        self.assertEqual((row['net_resources'],row['permanent_capacity_gained']),(1,3))

    def test_partial_draw_stops_without_premature_rewards_or_final_hand(self):
        row=plan(self.outlet,available=2,deck=1,lantern=True,battery=True,archive=True)
        self.assertEqual(row['status'],'engine_draw_continuation_required')
        self.assertEqual((row['captured_discards'],row['captured_draws'],row['draw_remaining'],row['available_during_effect']),(1,1,1,0))
        self.assertNotIn('available_after',row);self.assertNotIn('hand_after',row)

    def test_planning_grid_and_generated_report(self):
        report=evaluate(self.package)
        self.assertEqual(report['cases'],13200)
        self.assertEqual(sum(report['statuses'].values()),report['cases'])
        text=markdown(self.package,report)
        self.assertIn(self.outlet['rules_text'],text);self.assertIn('Short-deck cases stop',text)

    def test_invalid_inputs_reject(self):
        for args in ({'hand':0},{'available':-1},{'deck':True},{'hand':1.5},{'lantern':1}):
            with self.assertRaises(ValueError):plan(self.outlet,**args)
