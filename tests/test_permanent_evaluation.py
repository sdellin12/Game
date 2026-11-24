import unittest
from dataclasses import replace
from crucible_play.permanent_eval import evaluate_game
from crucible_play.opponent import choose_move
from crucible_core.views import project_match
from test_authored_triggers import CARD,source_fixture
from test_commands_cards_views import command,pass_round


class PermanentEvaluationTests(unittest.TestCase):
    def test_late_triggered_permanent_is_considered_but_plain_capacity_still_held(self):
        for triggered in (False,True):
            definition=CARD if triggered else replace(CARD,triggered_abilities=())
            s=source_fixture(definition);p=s.players[0]
            s=replace(s,players=(replace(p,resources=replace(p.resources,own_starts=6)),)+s.players[1:])
            move=choose_move(project_match(s,'A'))
            self.assertEqual(move[0],'play_card' if triggered else 'pass')
            s=command(s,'A',move[0],**move[1])
            if triggered:self.assertTrue(pass_round(s).battlefield[0].triggers)

    def test_limit_reports_incomplete_instead_of_a_fabricated_result(self):
        result=evaluate_game(2,'bounded-evaluation',1)
        self.assertEqual(result['status'],'incomplete');self.assertEqual(result['commands'],1)
        self.assertIsNone(result['result'])
        self.assertEqual(result['entries'],{'beacon-01':0,'beacon-02':0,'beacon-03':0})

    def test_selected_seed_actually_plays_permanents_and_queues_draw_rewards(self):
        result=evaluate_game(2,'permanent-2')
        self.assertEqual(result['status'],'completed');self.assertEqual(result['pack_version'],9)
        self.assertGreater(result['entries']['beacon-01'],0);self.assertGreater(result['entries']['beacon-02'],0)
        self.assertGreater(result['queued_triggers']['draw'],0)

    def test_invalid_evaluation_limits_reject_before_starting(self):
        for players,limit in ((5,1),(2,0),(2,True)):
            with self.assertRaises(ValueError):evaluate_game(players,'validation',limit)
