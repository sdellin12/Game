import unittest
from dataclasses import replace
from crucible_core.cards import CardDefinition
from crucible_content.practice import discard_draw_pack
from crucible_core.match import MatchObject
from crucible_core.combat import Creature
from crucible_core.views import project_match
from crucible_play.package_opponent import choose_package_move,choose_revised_move,choose_budgeted_move,_payable_followup
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

    def test_revised_preserves_affordable_creature_even_when_ahead_on_board(self):
        s=policy_fixture(('beacon-02','proposal-scrapyard-insight','unit-18'))
        view=project_match(s,'A')
        self.assertEqual(choose_package_move(view)[1]['card_id'],'beacon-02')
        move=choose_revised_move(view);self.assertEqual(move[1]['card_id'],'unit-18')
        command(s,'A',move[0],**move[1])

    def test_revised_still_sequences_payoff_when_no_creature_play_is_available(self):
        s=policy_fixture(('beacon-02','proposal-scrapyard-insight','proposal-deep-archive'))
        move=choose_revised_move(project_match(s,'A'));self.assertEqual(move[1]['card_id'],'beacon-02')
        command(s,'A',move[0],**move[1])

    def test_budgeted_setup_cannot_spend_the_known_draw_payment(self):
        for available,expected in ((5,'spell-04'),(6,'beacon-01')):
            s=policy_fixture(('beacon-01','spell-04','proposal-deep-archive'))
            p=s.players[0];s=replace(s,players=(replace(p,resources=replace(p.resources,available=available)),)+s.players[1:])
            view=project_match(s,'A');move=choose_budgeted_move(view)
            self.assertEqual(move[1]['card_id'],expected);command(s,'A',move[0],**move[1])
            self.assertEqual(view,project_match(s,'A'))

    def test_spent_token_is_removed_and_future_refunds_are_not_counted(self):
        from crucible_play.opponent import exact_payment
        s=policy_fixture(('beacon-01','spell-04'));p=s.players[0]
        s=replace(s,players=(replace(p,resources=replace(p.resources,available=2)),)+s.players[1:],
            battlefield=s.battlefield+(MatchObject('token','A','A','resource_token',resource_value=2),))
        view=project_match(s,'A');setup=view['you']['hand'][0];payment=exact_payment(view,4)
        self.assertEqual(payment,{'ordinary':2,'token_ids':['token']})
        self.assertFalse(_payable_followup(view,setup,payment))
        extra=MatchObject('extra','A','A','resource_token',resource_value=2)
        s=replace(s,battlefield=s.battlefield+(extra,));view=project_match(s,'A')
        self.assertTrue(_payable_followup(view,view['you']['hand'][0],exact_payment(view,4)))
        move=choose_budgeted_move(view);command(s,'A',move[0],**move[1])

    def test_outlet_needs_fodder_after_setup_but_unsafe_draw_can_be_fodder(self):
        s=policy_fixture(('beacon-02','proposal-scrapyard-insight'))
        view=project_match(s,'A');self.assertFalse(_payable_followup(view,view['you']['hand'][0],{'ordinary':4,'token_ids':[]}))
        s=policy_fixture(('beacon-02','proposal-scrapyard-insight','proposal-deep-archive'),deck=2)
        p=s.players[0];s=replace(s,players=(replace(p,resources=replace(p.resources,available=6)),)+s.players[1:])
        view=project_match(s,'A');self.assertTrue(_payable_followup(view,view['you']['hand'][0],{'ordinary':4,'token_ids':[]}))
        s=policy_fixture(('beacon-01','proposal-scrapyard-insight','proposal-deep-archive'),deck=2)
        p=s.players[0];s=replace(s,players=(replace(p,resources=replace(p.resources,available=6)),)+s.players[1:])
        view=project_match(s,'A');move=choose_budgeted_move(view)
        self.assertEqual(move[1]['card_id'],'beacon-01');command(s,'A',move[0],**move[1])

    def test_budgeted_preserves_creature_deployment_and_other_seat_boundaries(self):
        s=policy_fixture(('beacon-02','proposal-scrapyard-insight','unit-18'))
        move=choose_budgeted_move(project_match(s,'A'));self.assertEqual(move[1]['card_id'],'unit-18')
        command(s,'A',move[0],**move[1]);self.assertIsNone(choose_budgeted_move(project_match(s,'B')))

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
