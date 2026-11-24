import json,tempfile,unittest
from pathlib import Path
from dataclasses import replace
from crucible_core.match import (MatchObject,EffectSpec,TriggerSpec,DrawCards,GrantResources,DamagePlayer,
    ReturnCreatureToHand,validate_match,MatchError)
from crucible_core.views import project_match
from crucible_play.persistence import save_session,load_session
from test_commands_cards_views import fixture,command,pass_round
from test_zone_moves import resolve
from test_persistence import prepared,board,state,register,cmd


def watched(*,event='card_drawn',watch='self',controller='A',steps=None):
    effect=EffectSpec('reward',controller,(GrantResources(controller,1),))
    source=MatchObject('observer',controller,controller,'permanent',triggers=(TriggerSpec(event,'reward',watch),))
    return fixture(objects=(source,),effects=(effect,EffectSpec('draw','A',steps or (DrawCards('A',1),))))


def orders(s):
    while s.triggers:
        actor=s.triggers[0].controller
        s=command(s,actor,'trigger_order',order=[t.trigger_id for t in s.triggers if t.controller==actor])
    return s


class DrawDiscardTriggerTests(unittest.TestCase):
    def test_actual_draws_capture_per_card_after_whole_effect(self):
        s=watched(steps=(DrawCards('A',2),GrantResources('A',3)))
        p=s.players[0];s=replace(s,players=(replace(p,cards=replace(p.cards,deck=('hidden-one','hidden-two'))),)+s.players[1:])
        s=resolve(s,'draw');self.assertEqual(s.players[0].resources.available,13)
        self.assertEqual(len(s.triggers),2);self.assertEqual(sum(e.kind=='card_drawn' for e in s.events),2)
        s=orders(s);s=pass_round(s);s=pass_round(s);self.assertEqual(s.players[0].resources.available,15)

    def test_partial_draw_refill_counts_only_new_cards_without_repeated_triggers(self):
        s=watched(steps=(DrawCards('A',3),));p=s.players[0]
        s=replace(s,players=(replace(p,cards=replace(p.cards,deck=('one','two'),discard=('three','four'))),)+s.players[1:])
        s=resolve(s,'draw');self.assertIsNotNone(s.pending.draw);self.assertEqual(len(s.triggers),2)
        self.assertEqual(project_match(s,'A')['you']['choice']['kind'],'refill')
        s=command(s,'A','refill',pay=True,request_id=s.pending.draw.request_id)
        self.assertEqual(len(s.triggers),3);self.assertEqual(sum(e.kind=='card_drawn' for e in s.events),3)
        s=orders(s)
        for _ in range(3):s=pass_round(s)
        self.assertEqual(s.players[0].resources.available,13)

    def test_declined_partial_draw_preserves_other_players_observed_draws(self):
        s=watched(watch='any',controller='B',steps=(DrawCards('A',3),));p=s.players[0]
        s=replace(s,players=(replace(p,cards=replace(p.cards,deck=('one','two'),discard=('three',))),)+s.players[1:])
        s=resolve(s,'draw');s=command(s,'A','refill',pay=False,request_id=s.pending.draw.request_id)
        self.assertTrue(s.players[0].eliminated);self.assertEqual(len(s.triggers),2)
        s=orders(s);s=pass_round(s);s=pass_round(s)
        self.assertEqual(s.players[1].resources.available,12)

    def test_zero_draw_or_nonmatching_owner_has_no_observer_events(self):
        for controller,steps in (('B',(DrawCards('A',1),)),('A',(DrawCards('A',0),))):
            s=watched(controller=controller,steps=steps);p=s.players[0]
            s=replace(s,players=(replace(p,cards=replace(p.cards,deck=('one',))),)+s.players[1:])
            s=resolve(s,'draw');self.assertFalse(s.triggers);self.assertFalse(s.priority.chain)
            self.assertFalse(any(e.kind=='card_drawn' for e in s.events))

    def test_end_hand_discard_counts_actual_cards_and_waits_for_trigger_orders(self):
        s=watched(event='card_discarded');p=s.players[0]
        s=replace(s,players=(replace(p,cards=replace(p.cards,hand=tuple('h'+str(i) for i in range(9)))),)+s.players[1:])
        s=pass_round(command(s,'A','end_turn'));self.assertEqual(s.discard_needed,2)
        s=command(s,'A','end_discard',cards=['h0','h1']);self.assertEqual(len(s.triggers),2)
        self.assertEqual(sum(e.kind=='card_discarded' for e in s.events),2)
        s=orders(s);s=pass_round(s);s=pass_round(s);self.assertEqual(s.players[0].resources.available,12)

    def test_discard_trigger_draws_are_rechecked_against_hand_limit(self):
        s=watched(event='card_discarded');s=replace(s,effects=(replace(s.effects[0],steps=(DrawCards('A',1),)),s.effects[1]))
        p=s.players[0];s=replace(s,players=(replace(p,cards=replace(p.cards,deck=('new-card',),hand=tuple('h'+str(i) for i in range(8)))),)+s.players[1:])
        s=pass_round(command(s,'A','end_turn'));s=command(s,'A','end_discard',cards=['h0']);s=pass_round(s);s=pass_round(s)
        # Trigger creates a new excess card; it does not open an ordinary Main window.
        self.assertEqual(s.discard_needed,1);self.assertEqual(s.turn.phase,'End')

    def test_pending_card_to_discard_and_recovery_are_not_hand_discard_events(self):
        from test_recovery import recovery_fixture
        s=recovery_fixture();source=MatchObject('observer','A','A','permanent',triggers=(TriggerSpec('card_discarded','reward'),))
        s=replace(s,battlefield=(source,),effects=(EffectSpec('reward','A',(GrantResources('A',1),)),))
        s=command(s,'A','play_card',card_id='recovery',target='unit',payment={'ordinary':3,'token_ids':[]});s=pass_round(s)
        self.assertFalse(any(e.kind=='card_discarded' for e in s.events));self.assertFalse(s.priority.chain)
        self.assertEqual(s.players[0].resources.available,7)

    def test_multiple_controllers_queue_in_original_turn_order(self):
        s=watched();b=MatchObject('other','B','B','permanent',triggers=(TriggerSpec('card_drawn','other-reward','any'),))
        s=replace(s,battlefield=s.battlefield+(b,),effects=s.effects+(EffectSpec('other-reward','B',(GrantResources('B',1),)),))
        p=s.players[0];s=replace(s,players=(replace(p,cards=replace(p.cards,deck=('one',))),)+s.players[1:])
        s=resolve(s,'draw');self.assertEqual([e.controller for e in s.priority.chain],['A','B'])
        s=pass_round(s);self.assertEqual(s.players[1].resources.available,11)
        s=pass_round(s);self.assertEqual(s.players[0].resources.available,11)

    def test_public_observer_events_do_not_contain_drawn_card_identity(self):
        s=watched();p=s.players[0];s=replace(s,players=(replace(p,cards=replace(p.cards,deck=('SECRET-DRAW',))),)+s.players[1:])
        s=resolve(s,'draw');public=json.dumps(project_match(s));self.assertNotIn('SECRET-DRAW',public)
        event=next(e for e in project_match(s)['events'] if e['kind']=='card_drawn')
        self.assertEqual(set(event),{'event_id','kind','subject'});self.assertEqual(event['subject'],'A')

    def test_registered_listener_partial_refill_snapshot_restores_without_duplicate_events(self):
        s=prepared();actor=s.view()['turn']['active_player'];obj=board(s,{actor:1})[0];m=s._lobby.match
        state(s,effects=m.effects+(EffectSpec('reward',actor,(GrantResources(actor,1),)),),battlefield=(replace(obj,triggers=(TriggerSpec('card_drawn','reward'),)),))
        p=next(p for p in m.players if p.cards.player_id==actor)
        state(s,players=tuple(replace(q,cards=replace(q.cards,deck=q.cards.deck[:2],discard=q.cards.deck[2:])) if q==p else q for q in s._lobby.match.players))
        register(s,'draw-three',actor,(DrawCards(actor,3),));self.assertEqual(len(s._lobby.match.triggers),2)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'observed.crucible.json';save_session(s,path);loaded=load_session(path)
        loaded.resume()
        for game in (s,loaded):cmd(game,actor,'refill',pay=True,request_id=game._lobby.match.pending.draw.request_id)
        self.assertEqual(s._lobby,loaded._lobby);self.assertEqual(len(s._lobby.match.triggers),3)
        self.assertEqual(sum(e.kind=='card_drawn' for e in s._lobby.match.events),3)

    def test_unsupported_trigger_event_is_rejected(self):
        with self.assertRaises(MatchError):watched(event='arbitrary_code')

    def test_departed_source_only_keeps_triggers_captured_before_its_departure(self):
        from crucible_core.combat import Creature
        for draw_first in (False,True):
            source=MatchObject('observer','A','A','creature_token',Creature('observer','A',1,1,1),triggers=(TriggerSpec('card_drawn','reward'),))
            draw=DrawCards('A',1);leave=ReturnCreatureToHand('observer')
            s=watched(steps=(draw,leave) if draw_first else (leave,draw));p=s.players[0]
            s=replace(s,battlefield=(source,),players=(replace(p,cards=replace(p.cards,deck=('one',))),)+s.players[1:])
            s=resolve(s,'draw');self.assertFalse(s.battlefield)
            self.assertEqual(len(s.priority.chain),int(draw_first))
            if draw_first:s=pass_round(s)
            self.assertEqual(s.players[0].resources.available,10+int(draw_first))

    def test_normal_draw_phase_and_first_duel_draw_skip_use_actual_card_count(self):
        from test_persistence import passes
        for count in (2,3):
            s=prepared(count);actor=s.view()['turn']['active_player'];obj=board(s,{actor:1})[0];m=s._lobby.match
            state(s,effects=m.effects+(EffectSpec('reward',actor,(GrantResources(actor,1),)),),battlefield=(replace(obj,triggers=(TriggerSpec('card_drawn','reward'),)),))
            passes(s);passes(s)
            self.assertEqual(sum(e.kind=='card_drawn' for e in s._lobby.match.events),int(count>2))

    def test_failed_draw_eliminates_owner_and_cancels_their_captured_triggers(self):
        s=watched(steps=(DrawCards('A',2),));p=s.players[0]
        s=replace(s,players=(replace(p,cards=replace(p.cards,deck=('one',),discard=('two',))),)+s.players[1:])
        s=resolve(s,'draw');self.assertEqual(len(s.triggers),1)
        s=command(s,'A','refill',pay=False,request_id=s.pending.draw.request_id)
        self.assertTrue(s.players[0].eliminated);self.assertFalse(s.triggers);self.assertFalse(s.priority.chain)

    def test_draw_trigger_effect_can_be_negated_without_undoing_draw(self):
        from crucible_core.match import NegateEffect
        s=watched();p=s.players[0];s=replace(s,players=(replace(p,cards=replace(p.cards,deck=('one','spare'))),)+s.players[1:])
        s=resolve(s,'draw');identity=s.priority.chain[-1].effect_id
        s=replace(s,effects=s.effects+(EffectSpec('counter','A',(NegateEffect(identity),)),))
        s=resolve(s,'counter');self.assertFalse(s.priority.chain)
        self.assertIn('one',s.players[0].cards.hand);self.assertEqual(s.players[0].resources.available,10)

    def test_discard_order_choice_snapshot_restores_and_resolves_exactly(self):
        from test_persistence import passes
        s=prepared();actor=s.view()['turn']['active_player'];obj=board(s,{actor:1})[0];m=s._lobby.match
        p=next(p for p in m.players if p.cards.player_id==actor);take=9-len(p.cards.hand)
        state(s,effects=m.effects+(EffectSpec('reward',actor,(GrantResources(actor,1),)),),
            battlefield=(replace(obj,triggers=(TriggerSpec('card_discarded','reward'),)),),turn=replace(m.turn,phase='MainBefore'),
            players=tuple(replace(q,cards=replace(q.cards,hand=q.cards.hand+q.cards.deck[:take],deck=q.cards.deck[take:])) if q==p else q for q in m.players))
        cmd(s,actor,'end_turn');passes(s);cards=s.view(actor)['you']['hand'][:2]
        cmd(s,actor,'end_discard',cards=[c['instance_id'] for c in cards]);self.assertEqual(len(s._lobby.match.triggers),2)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'discard.crucible.json';save_session(s,path);loaded=load_session(path)
        loaded.resume();order=[t.trigger_id for t in reversed(s._lobby.match.triggers)]
        for game in (s,loaded):cmd(game,actor,'trigger_order',order=order);passes(game);passes(game)
        self.assertEqual(s._lobby,loaded._lobby);self.assertEqual(sum(e.kind=='card_discarded' for e in s._lobby.match.events),2)
