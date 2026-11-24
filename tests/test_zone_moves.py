import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from crucible_core.match import (ReturnCreatureToHand,DamagePlayer,DrawCards,GrantResources,GrantShield,
    EffectSpec,TriggerSpec,MatchObject,queue_effect,validate_match,MatchError)
from crucible_core.cards import CardDefinition
from crucible_core.combat import Creature
from crucible_core.views import project_match
from crucible_play.persistence import save_session,load_session
from crucible_play.opponent import choose_move
from test_commands_cards_views import fixture,instances,command,pass_round,play
from test_leaders import fixture as leader_fixture
from test_persistence import prepared,board,state,cmd,passes,register

BOUNCE=CardDefinition('bounce','reaction',3,(ReturnCreatureToHand('$target'),),target_kind='creature',target_relation='enemy')
UNIT=CardDefinition('unit','creature',1,attack=3,health=4)


def unit(identity='unit-b',owner='B',controller=None,**changes):
    controller=controller or owner
    return MatchObject(identity,owner,controller,'creature',Creature(identity,controller,3,4,4,**changes))


def resolve(s,key,actor='A'):
    return pass_round(queue_effect(s,actor,key,expected_revision=s.revision))


class ReturnToHandTests(unittest.TestCase):
    def test_paid_card_returns_to_owner_then_reentry_resets_battlefield_state(self):
        obj=unit('borrowed','A','B',exhausted=True,attack_used=True)
        obj=replace(obj,creature=replace(obj.creature,health=1))
        s=fixture((UNIT,BOUNCE),instances(('borrowed','unit','A'),('spell','bounce','A')),
                  ah=('spell',),objects=(obj,),effects=(EffectSpec('ward','A',(GrantShield('borrowed',2),)),))
        s=resolve(s,'ward');self.assertTrue(s.durations)
        s=play(s,'A','spell',3,target='borrowed')
        self.assertEqual(s.players[0].resources.available,7)
        self.assertIn('spell',[c.card_id for c in s.pending_cards]);self.assertTrue(s.battlefield)
        s=pass_round(s);validate_match(s)
        self.assertEqual(s.players[0].cards.hand,('borrowed',));self.assertFalse(s.players[1].cards.hand)
        self.assertEqual(s.players[0].cards.discard,('spell',));self.assertFalse(s.battlefield);self.assertFalse(s.durations)
        self.assertFalse(any(e.kind=='defeat' for e in s.events))
        s=pass_round(play(s,'A','borrowed',1));c=s.battlefield[0].creature
        self.assertEqual((c.controller,c.health,c.max_health),('A',4,4))
        self.assertFalse(c.exhausted);self.assertFalse(c.attack_used);self.assertFalse(c.attack_eligible);self.assertFalse(c.shields)

    def test_tokens_disappear_and_structural_attachments_go_to_their_owners_discard(self):
        upgrade=CardDefinition('upgrade','permanent',1,capacity_bonus=1)
        obj=MatchObject('token','B','B','creature_token',Creature('token','B',2,2,2))
        attached=MatchObject('up','C','B','permanent',attached_to='token',capacity_bonus=1)
        s=fixture((upgrade,),instances(('up','upgrade','C')),objects=(obj,attached),
                  effects=(EffectSpec('return','A',(ReturnCreatureToHand('token'),)),))
        s=resolve(s,'return');validate_match(s)
        self.assertFalse(s.battlefield);self.assertEqual(s.players[2].cards.discard,('up',))
        self.assertFalse(any('token' in p.cards.hand+p.cards.discard for p in s.players))
        self.assertFalse(any(e.kind=='defeat' for e in s.events))

    def test_leader_returns_to_reserve_with_recovery_and_removal_cost_without_defeat(self):
        s=leader_fixture(battle=True,effects=(EffectSpec('return','B',(ReturnCreatureToHand('leader-A'),)),))
        s=command(s,'A','pass')
        s=resolve(s,'return','B');validate_match(s)
        leader=s.leaders[0]
        self.assertEqual((leader.location,leader.removals,leader.recovering),('reserve',1,True))
        self.assertEqual(project_match(s)['leaders'][0]['summon_cost'],6)
        self.assertFalse(any('leader-A' in p.cards.hand+p.cards.discard for p in s.players))
        self.assertFalse(any(e.kind=='defeat' for e in s.events))

    def test_departure_triggers_fire_without_defeat_triggers(self):
        effect=EffectSpec('witness','B',(GrantResources('B',1),))
        obj=replace(unit(),triggers=(TriggerSpec('departure','witness'),TriggerSpec('defeat','witness')))
        s=fixture(objects=(obj,),effects=(effect,EffectSpec('return','A',(ReturnCreatureToHand('unit-b'),))))
        s=resolve(s,'return');self.assertEqual(len(s.priority.chain),1)
        s=pass_round(s);self.assertEqual(s.players[1].resources.available,11)
        self.assertEqual(sum(e.kind=='departure' for e in s.events),1)
        self.assertEqual(sum(e.kind=='defeat' for e in s.events),0)

    def test_absent_target_leaves_independent_effect_instructions_intact(self):
        s=fixture(effects=(EffectSpec('return','A',(ReturnCreatureToHand('gone'),DamagePlayer('B',2))),))
        s=resolve(s,'return');self.assertEqual(s.players[1].cards.health,28)
        self.assertFalse(any(e.kind=='departure' for e in s.events))

    def test_target_relation_and_noncreature_rejections_preserve_state(self):
        obj=unit(owner='A');s=fixture((BOUNCE,),instances(('spell','bounce','A')),ah=('spell',),objects=(obj,))
        before=s
        for target in ('unit-b','A','missing'):
            with self.assertRaises(ValueError):play(s,'A','spell',3,target=target)
            self.assertEqual(s,before)
        bad=replace(BOUNCE,steps=(ReturnCreatureToHand('$controller'),),target_kind=None,target_relation='any')
        with self.assertRaises(MatchError):fixture((bad,))

    def test_negated_return_spends_cost_but_does_not_move_target(self):
        from crucible_core.match import NegateEffect
        negate=CardDefinition('negate','reaction',2,(NegateEffect('$target'),),target_kind='effect')
        s=fixture((BOUNCE,negate,UNIT),instances(('spell','bounce','A'),('interrupt','negate','B'),('unit-b','unit','B')),
                  ah=('spell',),bh=('interrupt',),objects=(unit(),))
        s=play(s,'A','spell',3,target='unit-b');effect=s.priority.chain[-1].effect_id
        s=play(s,'B','interrupt',2,target=str(effect));s=pass_round(s)
        self.assertEqual(s.players[0].resources.available,7);self.assertEqual(s.players[1].resources.available,8)
        self.assertEqual([o.object_id for o in s.battlefield],['unit-b'])
        self.assertIn('spell',s.players[0].cards.discard);self.assertIn('interrupt',s.players[1].cards.discard)
        self.assertFalse(s.pending_cards)

    def test_return_during_final_combat_preserves_blocked_memory_and_breakthrough(self):
        for breakthrough in (False,True):
            with self.subTest(breakthrough=breakthrough):
                attacker=unit('attacker','A',keywords=('breakthrough',) if breakthrough else ())
                blocker=unit('blocker','B')
                s=fixture(objects=(attacker,blocker),effects=(EffectSpec('return','A',(ReturnCreatureToHand('blocker'),)),))
                s=replace(s,turn=replace(s.turn,phase='Combat'));s=pass_round(s)
                s=command(s,'A','declare_attacks',attacks=[{'attacker_id':'attacker','target_player':'B'}]);s=pass_round(s)
                s=command(s,'B','lock_blockers',assignments=[{'attacker_id':'attacker','blockers':['blocker']}])
                self.assertEqual(s.combat.stage,'final_responses')
                s=resolve(s,'return');s=pass_round(s)
                self.assertEqual(s.players[1].cards.health,27 if breakthrough else 30)
                self.assertIn('blocker',s.players[1].cards.hand);self.assertTrue(s.battlefield[0].creature.attack_used)

    def test_returned_card_identity_is_public_history_but_other_hand_contents_stay_private(self):
        s=fixture((UNIT,),instances(('unit-b','unit','B')),bh=('B-HIDDEN',),objects=(unit(),),
                  effects=(EffectSpec('return','A',(ReturnCreatureToHand('unit-b'),)),))
        s=resolve(s,'return');public=project_match(s)
        event=next(e for e in public['events'] if e['kind']=='card_returned')
        self.assertEqual(event['card']['definition_key'],'unit')
        self.assertNotIn('B-HIDDEN',json.dumps(public));self.assertNotIn('B-HIDDEN',json.dumps(project_match(s,'A')))
        self.assertEqual([c['instance_id'] for c in project_match(s,'B')['you']['hand']],['B-HIDDEN','unit-b'])

    def test_returning_a_pending_ability_source_does_not_cancel_its_effect(self):
        s=fixture(objects=(unit(),),effects=(EffectSpec('bolt','B',(DamagePlayer('A',2),),'unit-b'),
                    EffectSpec('return','A',(ReturnCreatureToHand('unit-b'),))))
        s=command(s,'A','pass');s=queue_effect(s,'B','bolt',expected_revision=s.revision)
        s=command(s,'C','pass');s=resolve(s,'return')
        self.assertFalse(s.battlefield);self.assertTrue(s.priority.chain)
        s=pass_round(s);self.assertEqual(s.players[0].cards.health,28)

    def test_returning_challenge_target_causes_a_miss_without_retargeting(self):
        attacker=unit('attacker','A',keywords=('challenge',))
        s=fixture(objects=(attacker,unit('target','B')),effects=(EffectSpec('return','A',(ReturnCreatureToHand('target'),)),))
        s=replace(s,turn=replace(s.turn,phase='Combat'));s=pass_round(s)
        s=command(s,'A','declare_attacks',attacks=[{'attacker_id':'attacker','target_player':'B','challenge_target':'target'}]);s=pass_round(s)
        if s.combat.stage=='blocking':s=command(s,'B','lock_blockers',assignments=[])
        s=resolve(s,'return');s=pass_round(s)
        self.assertEqual(s.players[1].cards.health,30)
        self.assertTrue(any(e.kind=='combat_miss' and e.subject=='attacker' for e in s.events))
        self.assertTrue(s.battlefield[0].creature.exhausted)

    def test_return_then_required_refill_snapshot_has_no_stale_shield_or_attachment(self):
        s=prepared();actor=s.view()['turn']['active_player'];objects=board(s,{actor:1});target=objects[0].object_id
        register(s,'ward',actor,(GrantShield(target,2),))
        p=next(p for p in s._lobby.match.players if p.cards.player_id==actor)
        state(s,players=tuple(replace(q,cards=replace(q.cards,deck=(),discard=q.cards.discard+q.cards.deck)) if q==p else q for q in s._lobby.match.players))
        register(s,'return-draw',actor,(ReturnCreatureToHand(target),DrawCards(actor,1)))
        self.assertIsNotNone(s._lobby.match.pending.draw);self.assertFalse(s._lobby.match.durations)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'pending.crucible.json';save_session(s,path);loaded=load_session(path)
        self.assertEqual(s._lobby,loaded._lobby);loaded.resume()
        for game in (s,loaded):cmd(game,actor,'refill',pay=True,request_id=game._lobby.match.pending.draw.request_id)
        self.assertEqual(s._lobby,loaded._lobby)

    def test_practice_policy_uses_new_card_from_its_projection_and_resumes_pending_play(self):
        s=prepared();actor=s.view()['turn']['active_player'];enemy=next(p['player_id'] for p in s.view()['players'] if p['player_id']!=actor)
        objects=board(s,{enemy:1});m=s._lobby.match
        card=next(c for c in m.card_instances if c.owner==actor and c.definition_key=='spell-02')
        state(s,turn=replace(m.turn,phase='MainBefore'),players=tuple(replace(p,cards=replace(p.cards,hand=(card.instance_id,),deck=tuple(i for i in p.cards.deck+p.cards.hand if i!=card.instance_id)),resources=replace(p.resources,available=3)) if p.cards.player_id==actor else p for p in m.players))
        # Prevent a leader summon from taking precedence over this three-resource card.
        move=choose_move(s.view(actor));self.assertEqual(move[0],'play_card');self.assertEqual(move[1]['target'],objects[0].object_id)
        cmd(s,actor,move[0],**move[1])
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'card.crucible.json';save_session(s,path);loaded=load_session(path)
        loaded.resume();passes(s);passes(loaded);self.assertEqual(s._lobby,loaded._lobby)
        self.assertIn(objects[0].object_id,next(p.cards.hand for p in s._lobby.match.players if p.cards.player_id==enemy))
