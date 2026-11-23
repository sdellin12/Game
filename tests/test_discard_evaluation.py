import unittest
from crucible_play.hand_pressure import evaluate_archive,pressure_case
from crucible_play.discard_eval import pressure_move,evaluate_game
from crucible_core.views import project_match


class DiscardEvaluationTests(unittest.TestCase):
    def test_archive_choices_delay_capacity_until_real_next_start(self):
        report=evaluate_archive()
        self.assertEqual((report['cases'],report['passed']),(54,54))
        for row in report['results']:
            accepted=sum(row['decisions'])
            self.assertEqual(row['available_before_refill'],5)
            self.assertEqual(row['next_start_available'],11+accepted)

    def test_bad_decision_lists_and_source_reject(self):
        for args in ({'source_key':'unknown'},{'decisions':(1,)},{'decisions':[True]},{'decisions':()}):
            with self.assertRaises(ValueError):pressure_case(**args)

    def test_experiment_limit_and_settings_are_explicit(self):
        result=evaluate_game(2,'bounded-discard',limit=1)
        self.assertEqual(result['status'],'incomplete');self.assertEqual(result['commands'],1)
        self.assertIsNone(result['result']);self.assertEqual(result['reward_units'],{'beacon-02':0,'beacon-03':0})
        for args in ({'players':True},{'strategy':'guess'},{'limit':0},{'limit':True}):
            with self.assertRaises(ValueError):evaluate_game(**args)

    def test_discount_is_isolated_and_identifies_its_content(self):
        from crucible_content.practice import practice_pack,pack_hash
        before=pack_hash(practice_pack())
        report=evaluate_game(limit=1,source_discount=1)
        self.assertEqual(report['source_discount'],1);self.assertNotEqual(report['content_hash'],before)
        self.assertEqual(pack_hash(practice_pack()),before)
        for value in (True,-1,2):
            with self.assertRaises(ValueError):evaluate_game(limit=1,source_discount=value)

    def test_pressure_policy_prioritizes_affordable_engine_using_own_view(self):
        from crucible_content.practice import practice_pack
        from crucible_core.cards import CardInstance
        from test_commands_cards_views import fixture
        card=next(c.definition for c in practice_pack().cards if c.definition.key=='beacon-03')
        s=fixture((card,),(CardInstance('well',card.key,'A'),),ah=('well',))
        view=project_match(s,'A');move=pressure_move(view)
        self.assertEqual(move,('play_card',{'card_id':'well','payment':{'ordinary':5,'token_ids':[]}}))
        from test_commands_cards_views import command
        self.assertTrue(command(s,'A',move[0],**move[1]).pending_cards)
        self.assertIsNone(pressure_move(project_match(s)))

    def test_policy_keeps_private_trigger_choices_and_opponent_priority(self):
        from test_optional_triggers import optional_fixture
        from test_zone_moves import resolve
        s=resolve(optional_fixture(),'draw')
        self.assertEqual(pressure_move(project_match(s,'A'))[0],'trigger_choice')
        self.assertIsNone(pressure_move(project_match(s,'B')))
