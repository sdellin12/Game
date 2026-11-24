import unittest
from dataclasses import replace
from crucible_core.turns import (
    DrawPlayer, TurnFlow, RefillPolicy, TurnError, UnsupportedTurnRule, open_turn,
    request_end_turn, advance_at_boundary, may_take_main_action, begin_required_draw,
    begin_start_refill, accept_refill, decline_refill,
)
POLICY = RefillPolicy(life_cost=20, minimum_health_after_payment=1)


def advance(turn):
    return advance_at_boundary(turn, expected_turn_id=turn.turn_id, expected_revision=turn.revision)


def accept(state, order):
    return accept_refill(state, order, expected_request_id=state.request_id, expected_revision=state.revision)


class TurnDrawTests(unittest.TestCase):
    def player(self, **changes):
        return replace(DrawPlayer('A',30,('a','b'),('c','d')),**changes)

    def test_draw3_deck2_pay_refill_and_finish_remaining_draw(self):
        original=self.player()
        turn=TurnFlow('A',1,phase='MainBefore')
        state=begin_required_draw(original,turn,3,POLICY,request_id=7)
        self.assertEqual((state.status,state.remaining,state.player.hand),('needs_refill',1,('a','b')))
        self.assertTrue(state.player.end_turn_requested)
        result=accept(state,('d','c'))
        self.assertEqual((result.status,result.player.health,result.player.hand,result.player.deck),
                         ('complete',10,('a','b','d'),('c',)))
        self.assertEqual(result.shuffles,(('d','c'),))
        self.assertFalse(result.player.recharge_due)
        self.assertEqual(original.deck,('a','b'))
        self.assertEqual(state.player.health,30)

    def test_exact_last_card_ends_own_turn_without_failed_draw(self):
        state=begin_required_draw(self.player(),TurnFlow('A',1),2,POLICY,request_id=1)
        self.assertEqual(state.status,'complete')
        self.assertTrue(state.player.end_turn_requested)
        other=begin_required_draw(self.player(),TurnFlow('B',2),2,POLICY,request_id=2)
        self.assertFalse(other.player.end_turn_requested)
        self.assertFalse(other.player.recharge_due)

    def test_start_refill_draws_nothing_and_ends_only_current_turn(self):
        player=self.player(deck=())
        player,turn=open_turn(player,turn_id=5)
        state=begin_start_refill(player,turn,POLICY,request_id=1)
        result=accept(state,('d','c'))
        self.assertEqual((result.player.hand,result.player.deck),((),('d','c')))
        self.assertTrue(result.player.end_turn_requested)
        self.assertFalse(result.player.recharge_due)
        next_player,next_turn=open_turn(result.player,turn_id=6)
        self.assertFalse(next_turn.recharge)
        self.assertFalse(next_player.end_turn_requested)

    def test_decline_cannot_pay_or_no_discard_records_failure_not_draw(self):
        turn=TurnFlow('A',1)
        state=begin_required_draw(self.player(),turn,3,POLICY,request_id=1)
        result=decline_refill(state,expected_request_id=1,expected_revision=state.revision)
        self.assertEqual(result.failure,'refill_declined')
        self.assertEqual(result.player.hand,('a','b'))
        for player,reason in [(self.player(health=20),'cannot_pay_refill'),(self.player(discard=()),'no_refill_cards')]:
            failed=begin_required_draw(player,turn,3,POLICY,request_id=2)
            self.assertEqual((failed.status,failed.failure),('failed',reason))
            self.assertEqual(failed.player.health,player.health)

    def test_refill_that_still_cannot_finish_draw_keeps_payment(self):
        state=begin_required_draw(self.player(deck=(),discard=('c',)),TurnFlow('A',1),2,POLICY,request_id=1)
        result=accept(state,('c',))
        self.assertEqual((result.status,result.remaining,result.player.health,result.player.hand),('failed',1,10,('c',)))
        self.assertEqual(result.failure,'no_refill_cards')

    def test_off_turn_refill_creates_one_recharge_not_active_turn_end(self):
        state=begin_required_draw(self.player(),TurnFlow('B',3),3,POLICY,request_id=9)
        result=accept(state,('c','d'))
        self.assertTrue(result.player.recharge_due)
        self.assertFalse(result.player.end_turn_requested)
        player,turn=open_turn(result.player,turn_id=4)
        self.assertTrue(turn.recharge)
        self.assertFalse(player.recharge_due)
        self.assertFalse(may_take_main_action(turn,'A'))
        turn=advance(turn)
        self.assertEqual(turn.phase,'End')
        self.assertEqual(advance(turn).phase,'Finished')

    def test_normal_phase_sequence_and_deferred_end_request(self):
        player,turn=open_turn(self.player(),turn_id=1)
        phases=[turn.phase]
        while turn.phase!='Finished':
            turn=advance(turn);phases.append(turn.phase)
        self.assertEqual(phases,['Start','Draw','MainBefore','Combat','MainAfter','End','Finished'])
        main=TurnFlow('A',2,phase='MainBefore')
        self.assertTrue(may_take_main_action(main,'A'))
        self.assertFalse(may_take_main_action(main,'B'))
        ended=request_end_turn(main,expected_turn_id=2,expected_revision=0)
        self.assertEqual(ended.phase,'MainBefore')
        self.assertFalse(may_take_main_action(ended,'A'))
        self.assertEqual(advance(ended).phase,'End')

    def test_stale_turn_and_refill_commands_reject_without_payment(self):
        turn=TurnFlow('A',10)
        for tid,rev in [(9,0),(10,1),(True,0),(10,True)]:
            with self.assertRaises(TurnError):advance_at_boundary(turn,expected_turn_id=tid,expected_revision=rev)
        state=begin_required_draw(self.player(),turn,3,POLICY,request_id=8)
        for req,rev in [(7,1),(8,0),(True,1),(8,True)]:
            with self.assertRaises(TurnError):accept_refill(state,('c','d'),expected_request_id=req,expected_revision=rev)
        result=accept(state,('c','d'))
        with self.assertRaises(TurnError):accept(result,('c','d'))
        self.assertEqual(state.player.health,30)

    def test_bad_shuffle_rejects_atomically(self):
        state=begin_required_draw(self.player(),TurnFlow('A',1),3,POLICY,request_id=1)
        for order in [('c','c'),('c','x'),('c',),['c','d']]:
            with self.assertRaises(TurnError):accept(state,order)
            self.assertEqual(state.player.health,30)
            self.assertEqual(state.player.discard,('c','d'))

    def test_candidate_costs_are_explicit_not_adopted_defaults(self):
        for cost in (15,20,25):
            policy=RefillPolicy(cost,1)
            state=begin_required_draw(self.player(),TurnFlow('A',1),3,policy,request_id=1)
            self.assertEqual(accept(state,('c','d')).player.health,30-cost)
        with self.assertRaises(TypeError):RefillPolicy()
        for policy in [RefillPolicy(0,1),RefillPolicy(20,0),RefillPolicy(True,1)]:
            with self.assertRaises(TurnError):begin_required_draw(self.player(),TurnFlow('A',1),1,policy,request_id=1)

    def test_unresolved_recharge_cases_reject_instead_of_guessing(self):
        with self.assertRaises(UnsupportedTurnRule):
            begin_required_draw(self.player(recharge_due=True),TurnFlow('B',1),3,POLICY,request_id=1)
        with self.assertRaises(UnsupportedTurnRule):
            begin_required_draw(self.player(),TurnFlow('A',1,recharge=True),1,POLICY,request_id=1)
        with self.assertRaises(UnsupportedTurnRule):
            begin_start_refill(self.player(deck=()),TurnFlow('A',1,recharge=True),POLICY,request_id=1)

    def test_invalid_zones_counts_and_start_context_reject(self):
        for player in [self.player(deck=('a','a')),self.player(hand=('a',)),self.player(deck=['a']),self.player(health=0)]:
            with self.assertRaises(TurnError):begin_required_draw(player,TurnFlow('A',1),1,POLICY,request_id=1)
        for count in (-1,True):
            with self.assertRaises(TurnError):begin_required_draw(self.player(),TurnFlow('A',1),count,POLICY,request_id=1)
        with self.assertRaises(TurnError):begin_start_refill(self.player(),TurnFlow('A',1),POLICY,request_id=1)
        with self.assertRaises(TurnError):begin_start_refill(self.player(deck=()),TurnFlow('B',1),POLICY,request_id=1)
        zero=begin_required_draw(self.player(deck=()),TurnFlow('A',1),0,POLICY,request_id=2)
        self.assertEqual(zero.status,'complete')
        self.assertFalse(zero.player.end_turn_requested)

    def test_start_unavailable_and_declined_refills_keep_zones_and_health(self):
        player=self.player(deck=())
        state=begin_start_refill(player,TurnFlow('A',1),POLICY,request_id=2)
        failed=decline_refill(state,expected_request_id=2,expected_revision=state.revision)
        self.assertEqual((failed.status,failed.failure,failed.player),('failed','refill_declined',player))
        for bad in (replace(player,health=20),replace(player,discard=())):
            result=begin_start_refill(bad,TurnFlow('A',1),POLICY,request_id=3)
            self.assertEqual(result.status,'failed')
            self.assertEqual(result.player,bad)

    def test_card_conservation_and_recorded_shuffle_replay(self):
        original=self.player(hand=('held',))
        before=set(original.deck+original.discard+original.hand)
        for count in range(7):
            state=begin_required_draw(original,TurnFlow('A',1),count,POLICY,request_id=count+1)
            if state.status=='needs_refill':
                first=accept(state,('d','c'))
                self.assertEqual(first,accept(state,('d','c')))
                state=first
            after=state.player.deck+state.player.discard+state.player.hand
            self.assertEqual(set(after),before)
            self.assertEqual(len(after),len(before))
