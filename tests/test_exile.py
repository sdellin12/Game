import json
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from crucible_core.match import (ExileCreature,ReturnCreatureToHand,DrawCards,DamagePlayer,GrantShield,
    GrantResources,EffectSpec,TriggerSpec,MatchObject,MatchError,NegateEffect,validate_match)
from crucible_core.cards import CardDefinition
from crucible_core.combat import Creature
from crucible_core.views import project_match
from crucible_play.persistence import save_session,load_session
from crucible_play.opponent import choose_move
from test_commands_cards_views import fixture,instances,command,pass_round,play
from test_zone_moves import UNIT,unit,resolve
from test_leaders import fixture as leader_fixture
from test_persistence import prepared,board,state,cmd,passes,register

BANISH=CardDefinition('banish','action',6,(ExileCreature('$target'),),target_kind='creature',target_relation='enemy')


def ordinary(*,borrowed=False,effects=()):
    owner='A' if borrowed else 'B'
    return fixture((UNIT,BANISH),instances(('unit-b','unit',owner),('spell','banish','A')),ah=('spell',),
        objects=(unit(owner=owner,controller='B'),),effects=effects)


class ExileTests(unittest.TestCase):
    def test_paid_card_enters_separate_public_exile_owned_by_original_owner(self):
        for borrowed in (False,True):
            with self.subTest(borrowed=borrowed):
                s=ordinary(borrowed=borrowed);s=play(s,'A','spell',6,target='unit-b')
                self.assertEqual(s.players[0].resources.available,4);self.assertFalse(s.exiled)
                s=pass_round(s);validate_match(s)
                self.assertEqual(s.exiled,('unit-b',));self.assertFalse(s.battlefield)
                self.assertFalse(any('unit-b' in p.cards.deck+p.cards.hand+p.cards.discard for p in s.players))
                for viewer in (None,'A','B','C'):
                    row=project_match(s,viewer)['exile'][0]
                    self.assertEqual((row['instance_id'],row['definition_key'],row['owner']),('unit-b','unit','A' if borrowed else 'B'))
                self.assertEqual(s.players[0].cards.discard,('spell',));self.assertFalse(any(e.kind=='defeat' for e in s.events))

    def test_exiled_cards_are_not_playable_or_returnable_by_battlefield_effects(self):
        s=ordinary(effects=(EffectSpec('return','A',(ReturnCreatureToHand('unit-b'),DamagePlayer('B',1))),))
        s=pass_round(play(s,'A','spell',6,target='unit-b'));before=s
        with self.assertRaises(ValueError):play(s,'B','unit-b',1)
        self.assertEqual(s,before);s=resolve(s,'return')
        self.assertEqual(s.exiled,('unit-b',));self.assertEqual(s.players[1].cards.health,29)

    def test_tokens_disappear_and_leaders_recover_in_reserve_instead_of_exile(self):
        token=MatchObject('token','B','B','creature_token',Creature('token','B',2,2,2))
        s=fixture(objects=(token,),effects=(EffectSpec('exile','A',(ExileCreature('token'),)),))
        s=resolve(s,'exile');self.assertFalse(s.battlefield);self.assertFalse(s.exiled)
        self.assertFalse(any('token' in p.cards.discard+p.cards.hand for p in s.players))
        s=leader_fixture(battle=True,effects=(EffectSpec('exile','A',(ExileCreature('leader-A'),)),))
        s=resolve(s,'exile');validate_match(s)
        self.assertFalse(s.exiled);self.assertEqual((s.leaders[0].location,s.leaders[0].removals,s.leaders[0].recovering),('reserve',1,True))
        self.assertEqual(project_match(s)['leaders'][0]['summon_cost'],6)
        self.assertFalse(any(e.kind=='defeat' for e in s.events))

    def test_attachments_discard_to_owner_and_timed_prevention_is_removed(self):
        upgrade=CardDefinition('up','permanent',1,capacity_bonus=1)
        attachment=MatchObject('upgrade','C','B','permanent',attached_to='unit-b',capacity_bonus=1)
        s=fixture((UNIT,upgrade),instances(('unit-b','unit','B'),('upgrade','up','C')),objects=(unit(),attachment),
            effects=(EffectSpec('ward','A',(GrantShield('unit-b',2),)),EffectSpec('exile','A',(ExileCreature('unit-b'),))))
        s=resolve(s,'ward');self.assertTrue(s.durations)
        s=resolve(s,'exile');validate_match(s)
        self.assertEqual(s.exiled,('unit-b',));self.assertEqual(s.players[2].cards.discard,('upgrade',))
        self.assertFalse(s.durations);self.assertFalse(s.battlefield)

    def test_departure_trigger_fires_once_and_defeat_trigger_does_not(self):
        obj=replace(unit(),triggers=(TriggerSpec('departure','witness'),TriggerSpec('defeat','witness')))
        s=fixture((UNIT,),instances(('unit-b','unit','B')),objects=(obj,),
            effects=(EffectSpec('witness','B',(GrantResources('B',1),)),EffectSpec('exile','A',(ExileCreature('unit-b'),))))
        s=resolve(s,'exile');self.assertEqual(len(s.priority.chain),1)
        s=pass_round(s);self.assertEqual(s.players[1].resources.available,11)
        self.assertEqual(sum(e.kind=='departure' for e in s.events),1);self.assertEqual(sum(e.kind=='defeat' for e in s.events),0)

    def test_negating_exile_keeps_target_and_spends_both_payments(self):
        negate=CardDefinition('negate','reaction',2,(NegateEffect('$target'),),target_kind='effect')
        s=fixture((UNIT,BANISH,negate),instances(('unit-b','unit','B'),('spell','banish','A'),('negate','negate','B')),
            ah=('spell',),bh=('negate',),objects=(unit(),))
        s=play(s,'A','spell',6,target='unit-b');effect=s.priority.chain[-1].effect_id
        s=play(s,'B','negate',2,target=str(effect));s=pass_round(s)
        self.assertFalse(s.exiled);self.assertEqual([o.object_id for o in s.battlefield],['unit-b'])
        self.assertEqual((s.players[0].resources.available,s.players[1].resources.available),(4,8))
        self.assertIn('spell',s.players[0].cards.discard);self.assertIn('negate',s.players[1].cards.discard)

    def test_absent_targets_and_illegal_authored_targets(self):
        s=fixture(effects=(EffectSpec('exile','A',(ExileCreature('absent'),DamagePlayer('B',1))),))
        s=resolve(s,'exile');self.assertFalse(s.exiled);self.assertEqual(s.players[1].cards.health,29)
        bad=replace(BANISH,target_kind='player')
        with self.assertRaises(MatchError):fixture((bad,))
        s=ordinary();before=s
        for target in ('A','absent'):
            with self.assertRaises(ValueError):play(s,'A','spell',6,target=target)
            self.assertEqual(s,before)

    def test_exile_conservation_rejects_unknown_duplicate_or_wrongly_typed_entries(self):
        s=ordinary()
        for exiled in (['unit-b'],('unit-b',),('unknown',),('unit-b','unit-b'),(True,)):
            with self.subTest(exiled=exiled):
                with self.assertRaises(MatchError):validate_match(replace(s,exiled=exiled))
        with self.assertRaises(MatchError):fixture(objects=(unit(),),effects=(EffectSpec('exile','A',(ExileCreature('unit-b'),)),))

    def test_public_exile_stays_known_after_owner_is_eliminated_without_leaking_hand(self):
        s=ordinary();b=s.players[1];s=replace(s,players=(s.players[0],replace(b,cards=replace(b.cards,hand=('SECRET-HAND',))),s.players[2]))
        s=pass_round(play(s,'A','spell',6,target='unit-b'));s=command(s,'B','concede',confirmed=True)
        self.assertTrue(s.players[1].eliminated)
        self.assertEqual(project_match(s)['exile'][0]['owner'],'B')
        self.assertNotIn('SECRET-HAND',json.dumps(project_match(s,'B')))

    def test_exile_before_refill_is_saved_and_never_shuffled_from_discard(self):
        s=prepared();actor=s.view()['turn']['active_player'];objects=board(s,{actor:1});target=objects[0].object_id
        register(s,'ward',actor,(GrantShield(target,2),))
        p=next(p for p in s._lobby.match.players if p.cards.player_id==actor)
        state(s,players=tuple(replace(q,cards=replace(q.cards,deck=(),discard=q.cards.discard+q.cards.deck)) if q==p else q for q in s._lobby.match.players))
        register(s,'exile-draw',actor,(ExileCreature(target),DrawCards(actor,1)))
        self.assertIsNotNone(s._lobby.match.pending.draw);self.assertEqual(s._lobby.match.exiled,(target,));self.assertFalse(s._lobby.match.durations)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'pending.crucible.json';save_session(s,path);loaded=load_session(path)
        self.assertEqual(s._lobby,loaded._lobby);loaded.resume()
        for game in (s,loaded):cmd(game,actor,'refill',pay=True,request_id=game._lobby.match.pending.draw.request_id)
        self.assertEqual(s._lobby,loaded._lobby)
        p=next(p for p in s._lobby.match.players if p.cards.player_id==actor)
        self.assertNotIn(target,p.cards.deck+p.cards.hand+p.cards.discard)

    def test_practice_banish_can_be_saved_pending_and_resumes_identically(self):
        s=prepared();actor=s.view()['turn']['active_player'];enemy=next(p['player_id'] for p in s.view()['players'] if p['player_id']!=actor)
        objects=board(s,{enemy:1});m=s._lobby.match;card=next(c for c in m.card_instances if c.owner==actor and c.definition_key=='spell-05')
        state(s,turn=replace(m.turn,phase='MainBefore'),players=tuple(replace(p,cards=replace(p.cards,hand=(card.instance_id,),deck=tuple(i for i in p.cards.deck+p.cards.hand if i!=card.instance_id)),resources=replace(p.resources,available=6)) if p.cards.player_id==actor else p for p in m.players))
        # Exercise the actual paid card path; the policy may prefer summoning its reserve leader.
        cmd(s,actor,'play_card',card_id=card.instance_id,target=objects[0].object_id,payment={'ordinary':6,'token_ids':[]})
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'card.crucible.json';save_session(s,path);loaded=load_session(path)
        loaded.resume();passes(s);passes(loaded);self.assertEqual(s._lobby,loaded._lobby)
        self.assertEqual(s._lobby.match.exiled,(objects[0].object_id,))

    def test_exile_policy_prefers_large_permanent_removal_over_small_token(self):
        from crucible_play.tactics import fixture as tactical,creature
        s=tactical([creature('token','B',2,2,token=True),creature('giant','C',9,9)])
        s=replace(s,card_definitions=tuple(replace(d,steps=(ExileCreature('$target'),)) if d.key=='unravel' else d for d in s.card_definitions))
        view=project_match(s,'A');move=choose_move(view)
        self.assertEqual(move[0],'play_card');self.assertEqual(move[1]['target'],'giant')
        result=command(s,'A',move[0],**move[1]);result=pass_round(result)
        self.assertEqual(result.exiled,('giant',))

    def test_exiling_revealed_blocker_preserves_blocked_memory(self):
        for breakthrough in (False,True):
            with self.subTest(breakthrough=breakthrough):
                attacker=unit('attacker','A',keywords=('breakthrough',) if breakthrough else ())
                s=fixture((UNIT,),instances(('attacker','unit','A'),('blocker','unit','B')),objects=(attacker,unit('blocker','B')),
                    effects=(EffectSpec('exile','A',(ExileCreature('blocker'),)),))
                s=replace(s,turn=replace(s.turn,phase='Combat'));s=pass_round(s)
                s=command(s,'A','declare_attacks',attacks=[{'attacker_id':'attacker','target_player':'B'}]);s=pass_round(s)
                s=command(s,'B','lock_blockers',assignments=[{'attacker_id':'attacker','blockers':['blocker']}])
                s=resolve(s,'exile');s=pass_round(s)
                self.assertEqual(s.exiled,('blocker',));self.assertEqual(s.players[1].cards.health,27 if breakthrough else 30)

    def test_exile_policy_values_permanent_card_removal_over_temporary_leader_return(self):
        from test_leaders import definition
        from crucible_core.leaders import LeaderState
        leader=definition(attack=9,health=9)
        obj=MatchObject('leader-B','B','B','leader',Creature('leader-B','B',9,9,9))
        s=fixture((UNIT,BANISH),instances(('ordinary','unit','C'),('spell','banish','A')),ah=('spell',),
            objects=(obj,unit('ordinary','C')),leader_definitions=(leader,),
            leaders=(LeaderState('leader-B','B','core',location='battlefield'),))
        move=choose_move(project_match(s,'A'));self.assertEqual(move[1]['target'],'ordinary')
        s=command(s,'A',move[0],**move[1]);s=pass_round(s)
        self.assertEqual(s.exiled,('ordinary',));self.assertEqual(s.leaders[0].location,'battlefield')
