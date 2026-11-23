import unittest
from dataclasses import replace
from crucible_core.cards import CardDefinition
from crucible_content.practice import discard_draw_pack
from crucible_core.match import MatchObject
from crucible_core.combat import Creature
from crucible_core.views import project_match
from crucible_play.package_opponent import choose_package_move
from test_commands_cards_views import fixture,instances,command


def policy_fixture(hand_keys,board=2,deck=20):
    pack=discard_draw_pack();definitions=tuple(c.definition for c in pack.cards)
    keys=[c.definition.key for c in pack.cards]
    cards=instances(*[(key,key,'A') for key in hand_keys])
    objects=tuple(MatchObject('body'+str(i),'A','A','creature',Creature('body'+str(i),'A',2,3,3)) for i in range(board))
    return fixture(definitions,cards,ah=tuple(hand_keys),ad=tuple('draw'+str(i) for i in range(deck)),objects=objects)


class PackageOpponentTests(unittest.TestCase):
    def move(self,s):
        move=choose_package_move(project_match(s,'A'))
        command(s,'A',move[0],**move[1])
        return move

    def test_engine_is_played_before_outlet_on_established_board(self):
        s=policy_fixture(('beacon-02','proposal-scrapyard-insight','unit-01'))
        self.assertEqual(self.move(s)[1]['card_id'],'beacon-02')

    def test_early_creature_is_kept_before_engine(self):
        for board in (0,1):
            s=policy_fixture(('beacon-02','proposal-scrapyard-insight','unit-01'),board=board)
            self.assertEqual(self.move(s)[1]['card_id'],'unit-01')

    def test_one_body_can_support_setup_when_no_creature_play_is_available(self):
        s=policy_fixture(('beacon-02','proposal-scrapyard-insight','proposal-deep-archive'),board=1)
        self.assertEqual(self.move(s)[1]['card_id'],'beacon-02')

    def test_draw_payoff_precedes_hand_building_and_no_refund_is_assumed(self):
        s=policy_fixture(('beacon-01','proposal-surveyors-notes','unit-01'))
        self.assertEqual(self.move(s)[1]['card_id'],'beacon-01')
        p=s.players[0];s=replace(s,players=(replace(p,resources=replace(p.resources,available=3)),)+s.players[1:])
        self.assertEqual(self.move(s)[1]['card_id'],'proposal-surveyors-notes')

    def test_no_voluntary_short_deck_draw_and_no_last_card_outlet(self):
        for key in ('proposal-deep-archive','proposal-scrapyard-insight'):
            s=policy_fixture((key,),deck=1)
            self.assertEqual(self.move(s),('pass',{}))

    def test_discard_keeps_defensive_creature_instead_of_unusable_spell(self):
        from test_effect_discard import OUTLET
        from test_commands_cards_views import play,pass_round
        pack=discard_draw_pack();unit=next(c.definition for c in pack.cards if c.definition.key=='unit-01')
        expensive=next(c.definition for c in pack.cards if c.definition.key=='proposal-deep-archive')
        s=fixture((OUTLET,unit,expensive),instances(('outlet','outlet','A'),('unit',unit.key,'A'),('draw',expensive.key,'A')),ah=('outlet','unit','draw'),ad=('one','two'))
        s=pass_round(play(s,'A','outlet',2));move=self.move(s)
        self.assertEqual(move[1]['card_id'],'draw')

    def test_other_players_priority_choices_and_spectators_are_not_overridden(self):
        s=policy_fixture(('beacon-02','proposal-scrapyard-insight'))
        self.assertIsNone(choose_package_move(project_match(s)))
        self.assertIsNone(choose_package_move(project_match(s,'B')))
        from test_optional_triggers import optional_fixture
        from test_zone_moves import resolve
        s=resolve(optional_fixture(),'draw')
        self.assertEqual(self.move(s)[0],'trigger_choice')
