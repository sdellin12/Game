import unittest
from dataclasses import replace
from crucible_core.match import MatchObject,MatchPlayer,TriggerSpec,EffectSpec,DrawCards,GrantResources,new_match,queue_effect
from crucible_core.turns import DrawPlayer,RefillPolicy
from crucible_core.resources import ResourcePool
from test_commands_cards_views import command,pass_round


class MultiplayerTriggerStressTests(unittest.TestCase):
    def test_ordering_matrix_resolves_every_candidate_once_for_two_through_four_players(self):
        for event in ('card_drawn','card_discarded'):
            for seats in (2,3,4):
                for sources in (1,2,3):
                    for count in (1,2,3):
                        with self.subTest(event=event,seats=seats,sources=sources,count=count):
                            names=tuple('ABCD'[:seats])
                            players=tuple(MatchPlayer(DrawPlayer(p,30,tuple(p+str(i) for i in range(6)),(),tuple('h'+str(i) for i in range(7+count)) if p=='A' and event=='card_discarded' else ()),resources=ResourcePool(available=0)) for p in names)
                            effects=tuple(EffectSpec('reward-'+p,p,(GrantResources(p,1),)) for p in names)+(EffectSpec('draw','A',(DrawCards('A',count),)),)
                            objects=tuple(MatchObject(p+str(i)+'-source',p,p,'permanent',triggers=(TriggerSpec(event,'reward-'+p,'any'),)) for p in names for i in range(sources))
                            s=new_match(players,objects,effects,RefillPolicy(20,1),active_player='A')
                            if event=='card_drawn':s=pass_round(queue_effect(s,'A','draw',expected_revision=s.revision))
                            else:
                                s=pass_round(command(s,'A','end_turn'))
                                s=command(s,'A','end_discard',cards=['h'+str(i) for i in range(count)])
                            if count*sources>1:
                                self.assertEqual(len(s.triggers),seats*sources*count)
                                for actor in reversed(names):
                                    s=command(s,actor,'trigger_order',order=[t.trigger_id for t in reversed(s.triggers) if t.controller==actor])
                            self.assertEqual([e.controller for e in s.priority.chain],[p for p in names for _ in range(sources*count)])
                            for actor in reversed(names):
                                for _ in range(sources*count):s=pass_round(s)
                                self.assertEqual(next(p.resources.available for p in s.players if p.cards.player_id==actor),sources*count)
                            self.assertFalse(s.priority.chain);self.assertFalse(s.triggers)

    def test_concession_during_ordering_removes_only_eliminated_controllers_candidates(self):
        from test_draw_discard_triggers import watched,orders
        s=watched(watch='any',steps=(DrawCards('A',2),));b=MatchObject('b','B','B','permanent',triggers=(TriggerSpec('card_drawn','b-reward','any'),))
        s=replace(s,battlefield=s.battlefield+(b,),effects=s.effects+(EffectSpec('b-reward','B',(GrantResources('B',1),)),))
        p=s.players[0];s=replace(s,players=(replace(p,cards=replace(p.cards,deck=('one','two','spare'))),)+s.players[1:])
        s=pass_round(queue_effect(s,'A','draw',expected_revision=s.revision));self.assertEqual(len(s.triggers),4)
        s=command(s,'B','concede',confirmed=True);self.assertEqual({t.controller for t in s.triggers},{'A'})
        s=orders(s);s=pass_round(s);s=pass_round(s);self.assertEqual(s.players[0].resources.available,12)

    def test_bounded_draw_trigger_cascade_ends_at_refill_and_does_not_revive_player(self):
        from test_draw_discard_triggers import watched
        s=watched();s=replace(s,effects=(replace(s.effects[0],steps=(DrawCards('A',1),)),s.effects[1]))
        p=s.players[0];s=replace(s,players=(replace(p,cards=replace(p.cards,deck=('one','two','three'),discard=('refill',))),)+s.players[1:])
        s=pass_round(queue_effect(s,'A','draw',expected_revision=s.revision))
        for _ in range(5):
            if s.pending and s.pending.draw:break
            s=pass_round(s)
        else:self.fail('Cascade did not reach its bounded empty-deck choice')
        self.assertEqual(sum(e.kind=='card_drawn' for e in s.events),3)
        s=command(s,'A','refill',pay=False,request_id=s.pending.draw.request_id)
        self.assertTrue(s.players[0].eliminated);self.assertFalse(s.triggers)
