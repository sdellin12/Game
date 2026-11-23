import json
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from crucible_play.persistence import save_session,load_session,SaveError,_canonical
from crucible_play.session import HarnessSession
from crucible_core.match import (MatchObject,EffectSpec,DrawCards,DestroyCreature,DamagePlayer,GrantResources,
    GrantShield,TriggerSpec,queue_effect)
from crucible_core.combat import Creature
from crucible_core.durations import TimedEffect
from crucible_core.resources import ResourcePool
import hashlib

SEED=b'private-snapshot-test-seed-12345678'


def ready(s):
    for p in s.view()['players']:
        a=p['player_id'];s.choose_deck(a,'core-gold',expected_revision=s.view()['revision']);s.ready(a,True,expected_revision=s.view()['revision'])
    return s


def prepared(size=3):
    s=ready(HarnessSession(tuple(f'Player {i+1}' for i in range(size)),seed=SEED,bots=('P2',)))
    s.start('P1',expected_revision=s.view()['revision'])
    for p in s.view()['players']:s.redraw(p['player_id'],(),expected_revision=s.view()['revision'])
    return s


def cmd(s,actor,kind,**args):s.send(actor,{'kind':kind,'args':args,'expected_revision':s.view()['revision']})


def passes(s):
    for _ in range(len(s._lobby.match.priority.seats)):cmd(s,s.view()['priority']['holder'],'pass')


def state(s,**changes):s._lobby=replace(s._lobby,match=replace(s._lobby.match,**changes))


def board(s,counts):
    m=s._lobby.match;definitions={d.key:d for d in m.card_definitions};players=[];objects=[]
    for p in m.players:
        choices=[c for c in m.card_instances if c.owner==p.cards.player_id and definitions[c.definition_key].kind=='creature'][:counts.get(p.cards.player_id,0)]
        moved={c.instance_id for c in choices}
        players.append(replace(p,cards=replace(p.cards,deck=tuple(i for i in p.cards.deck if i not in moved),hand=tuple(i for i in p.cards.hand if i not in moved)),resources=replace(p.resources,available=20)))
        for c in choices:
            d=definitions[c.definition_key];objects.append(MatchObject(c.instance_id,c.owner,c.owner,'creature',Creature(c.instance_id,c.owner,d.attack,d.health,d.health,keywords=d.keywords)))
    state(s,players=tuple(players),battlefield=tuple(objects))
    return objects


def register(s,key,actor,steps):
    state(s,effects=s._lobby.match.effects+(EffectSpec(key,actor,steps),))
    state(s,**{'priority':s._lobby.match.priority})
    s._lobby=replace(s._lobby,match=queue_effect(s._lobby.match,actor,key,expected_revision=s.view()['revision']))
    passes(s)


class SaveTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'game.crucible.json'

    def roundtrip(self,s):
        save_session(s,self.path);loaded=load_session(self.path)
        self.assertEqual(s._lobby,loaded._lobby);self.assertEqual(s.bots,loaded.bots);self.assertTrue(loaded.paused)
        self.assertFalse(loaded.step_opponent())
        return loaded

    def twin(self,s,loaded,actor,kind,**args):
        with self.assertRaises(ValueError):cmd(loaded,actor,kind,**args)
        loaded.resume();cmd(s,actor,kind,**args);cmd(loaded,actor,kind,**args)
        self.assertEqual(s._lobby,loaded._lobby)

    def rewrite(self,change):
        doc=json.loads(self.path.read_text());change(doc)
        doc['checksum']=hashlib.sha256(_canonical({k:v for k,v in doc.items() if k!='checksum'})).hexdigest()
        self.path.write_text(json.dumps(doc))

    def test_fresh_lobby_and_selected_readiness_roundtrip(self):
        s=HarnessSession(seed=SEED,bots=('P2',));self.roundtrip(s)
        s.choose_deck('P1','core-green',expected_revision=s.view()['revision']);s.ready('P1',True,expected_revision=s.view()['revision'])
        self.roundtrip(s)

    def test_partial_opening_lock_restores_without_redealing(self):
        s=ready(HarnessSession(('One','Two','Three'),seed=SEED));s.start('P1',expected_revision=s.view()['revision'])
        hand=s.view('P1')['you']['hand'];s.redraw('P1',[hand[0]['instance_id']],expected_revision=s.view()['revision'])
        loaded=self.roundtrip(s);loaded.resume()
        for actor in ('P2','P3'):
            s.redraw(actor,(),expected_revision=s.view()['revision']);loaded.redraw(actor,(),expected_revision=loaded.view()['revision'])
        self.assertEqual(s._lobby,loaded._lobby)
        self.assertIsNone(loaded.view().get('you'))

    def test_priority_passes_exact_revision_and_next_command(self):
        s=prepared();actor=s.view()['priority']['holder'];cmd(s,actor,'pass')
        loaded=self.roundtrip(s);next_actor=s.view()['priority']['holder']
        self.twin(s,loaded,next_actor,'pass')

    def test_pending_card_and_dynamic_effect_roundtrip(self):
        s=prepared();passes(s);passes(s)
        actor=s.view()['turn']['active_player'];p=next(p for p in s._lobby.match.players if p.cards.player_id==actor)
        state(s,players=tuple(replace(q,resources=replace(q.resources,available=20)) if q==p else q for q in s._lobby.match.players))
        card=next(c for c in s.view(actor)['you']['hand'] if c['kind']=='creature')
        cmd(s,actor,'play_card',card_id=card['instance_id'],payment={'ordinary':card['cost'],'token_ids':[]})
        loaded=self.roundtrip(s);self.twin(s,loaded,s.view()['priority']['holder'],'pass')

    def test_required_refill_cursor_seed_and_next_shuffle_roundtrip(self):
        s=prepared();actor=s.view()['turn']['active_player'];p=next(p for p in s._lobby.match.players if p.cards.player_id==actor)
        state(s,players=tuple(replace(q,cards=replace(q.cards,deck=(),discard=q.cards.discard+q.cards.deck)) if q==p else q for q in s._lobby.match.players))
        register(s,'fixture-draw',actor,(DrawCards(actor,3),))
        self.assertIsNotNone(s._lobby.match.pending.draw)
        loaded=self.roundtrip(s);req=s._lobby.match.pending.draw.request_id
        self.twin(s,loaded,actor,'refill',pay=True,request_id=req)
        self.assertEqual(s._lobby.match.shuffle_counter,1)

    def test_private_blocker_lock_restores_without_public_disclosure(self):
        s=prepared();actor=s.view()['turn']['active_player'];others=[p['player_id'] for p in s.view()['players'] if p['player_id']!=actor]
        objects=board(s,{actor:2,others[0]:1,others[1]:1});state(s,turn=replace(s._lobby.match.turn,phase='Combat'))
        own=[o.object_id for o in objects if o.owner==actor];opponents={o.owner:o.object_id for o in objects if o.owner!=actor}
        passes(s);cmd(s,actor,'declare_attacks',attacks=[{'attacker_id':a,'target_player':p} for a,p in zip(own,others)]);passes(s)
        cmd(s,others[0],'lock_blockers',assignments=[{'attacker_id':own[0],'blockers':[opponents[others[0]]]}])
        loaded=self.roundtrip(s)
        self.assertNotIn('blockers',loaded.view()['combat'])
        self.twin(s,loaded,others[1],'lock_blockers',assignments=[{'attacker_id':own[1],'blockers':[]}])

    def test_damage_order_choice_roundtrip(self):
        s=prepared();actor=s.view()['turn']['active_player'];enemy=next(p['player_id'] for p in s.view()['players'] if p['player_id']!=actor)
        objects=board(s,{actor:1,enemy:2});state(s,turn=replace(s._lobby.match.turn,phase='Combat'))
        attacker=next(o.object_id for o in objects if o.owner==actor);blockers=[o.object_id for o in objects if o.owner==enemy]
        passes(s);cmd(s,actor,'declare_attacks',attacks=[{'attacker_id':attacker,'target_player':enemy}]);passes(s)
        cmd(s,enemy,'lock_blockers',assignments=[{'attacker_id':attacker,'blockers':blockers}])
        self.assertEqual(s.view()['combat']['stage'],'ordering')
        loaded=self.roundtrip(s);self.twin(s,loaded,actor,'combat_order',subject=attacker,order=list(reversed(blockers)))

    def test_trigger_order_choice_roundtrip(self):
        s=prepared();actor=s.view()['turn']['active_player'];objects=board(s,{actor:2})
        key='fixture-trigger'
        state(s,effects=s._lobby.match.effects+(EffectSpec(key,actor,(GrantResources(actor,1),)),),
              battlefield=(replace(objects[0],triggers=(TriggerSpec('defeat',key,'any'),)),objects[1]))
        register(s,'fixture-destroy',actor,tuple(DestroyCreature(o.object_id) for o in objects))
        self.assertEqual(len(s._lobby.match.triggers),2)
        loaded=self.roundtrip(s);order=[t.trigger_id for t in reversed(s._lobby.match.triggers)]
        self.twin(s,loaded,actor,'trigger_order',order=order)

    def test_duration_and_pending_leader_summon_roundtrip(self):
        s=prepared();actor=s.view()['turn']['active_player'];obj=board(s,{actor:1})[0]
        register(s,'fixture-ward',actor,(GrantShield(obj.object_id,2,'next_start',actor),))
        loaded=self.roundtrip(s)
        self.assertEqual(loaded._lobby.match.durations,s._lobby.match.durations)
        # A second snapshot locks a paid leader summon and its effect ID.
        state(s,turn=replace(s._lobby.match.turn,phase='MainBefore'))
        cmd(s,actor,'summon_leader',payment={'ordinary':4,'token_ids':[]})
        loaded=self.roundtrip(s);self.twin(s,loaded,s.view()['priority']['holder'],'pass')

    def test_end_discard_choice_and_terminal_result_roundtrip(self):
        s=prepared();actor=s.view()['turn']['active_player'];p=next(p for p in s._lobby.match.players if p.cards.player_id==actor)
        state(s,players=tuple(replace(q,cards=replace(q.cards,hand=q.cards.hand+q.cards.deck[:3],deck=q.cards.deck[3:])) if q==p else q for q in s._lobby.match.players),turn=replace(s._lobby.match.turn,phase='MainBefore'))
        cmd(s,actor,'end_turn');passes(s)
        self.assertEqual(s._lobby.match.discard_needed,1)
        loaded=self.roundtrip(s);card=s.view(actor)['you']['hand'][0]['instance_id']
        self.twin(s,loaded,actor,'end_discard',cards=[card])
        for player in s.view()['players'][:-1]:cmd(s,player['player_id'],'concede',confirmed=True)
        self.assertIsNotNone(s.view()['result']);self.roundtrip(s)

    def test_skipped_boundary_refill_and_rotation_queue_roundtrip(self):
        s=prepared();m=s._lobby.match;actor,dead,_=m.seat_order;p=next(p for p in m.players if p.cards.player_id==actor)
        state(s,players=tuple(replace(q,cards=replace(q.cards,discard=q.cards.deck,deck=())) if q==p else q for q in m.players),
              durations=(TimedEffect(1,actor,dead,'Start',1,expiration_steps=(DrawCards(actor,1),)),),next_duration_id=2,
              turn=replace(m.turn,phase='MainBefore'))
        register(s,'fixture-kill',actor,(DamagePlayer(dead,30),));cmd(s,actor,'end_turn');passes(s)
        self.assertTrue(s._lobby.match.rotation_queue);self.assertIsNotNone(s._lobby.match.pending.draw)
        loaded=self.roundtrip(s)
        self.twin(s,loaded,actor,'refill',pay=True,request_id=s._lobby.match.pending.draw.request_id)

    def test_backup_retains_exact_prior_bytes_and_unchanged_save_is_idempotent(self):
        s=HarnessSession(seed=SEED);save_session(s,self.path);first=self.path.read_bytes()
        result=save_session(s,self.path);self.assertTrue(result.unchanged);self.assertIsNone(result.backup)
        s.choose_deck('P1','core-gold',expected_revision=s.view()['revision']);result=save_session(s,self.path)
        self.assertEqual(result.backup.read_bytes(),first);second=self.path.read_bytes()
        s.ready('P1',True,expected_revision=s.view()['revision']);third=save_session(s,self.path)
        self.assertNotEqual(result.backup,third.backup);self.assertEqual(result.backup.read_bytes(),first);self.assertEqual(third.backup.read_bytes(),second)

    def test_interrupted_replace_keeps_prior_file_and_cleans_only_own_temp(self):
        import os
        s=HarnessSession(seed=SEED);save_session(s,self.path);original=self.path.read_bytes()
        s.choose_deck('P1','core-gold',expected_revision=s.view()['revision']);real=os.replace
        def fail(src,dst):
            if Path(dst)==self.path:raise OSError('injected write failure')
            return real(src,dst)
        with patch('crucible_play.persistence.os.replace',side_effect=fail):
            with self.assertRaises(SaveError):save_session(s,self.path)
        self.assertEqual(self.path.read_bytes(),original)
        self.assertFalse(list(self.path.parent.glob('*.tmp')))
        self.assertTrue(list(self.path.parent.glob('*.backup-*')))

    def test_foreign_or_corrupt_destination_is_never_overwritten(self):
        s=HarnessSession(seed=SEED)
        for original in (b'family notes',b'{"schema_version":1,"report":"combat-only"}'):
            self.path.write_bytes(original)
            with self.assertRaises(SaveError):save_session(s,self.path)
            self.assertEqual(self.path.read_bytes(),original)

    def test_unknown_schema_runtime_and_bad_checksum_reject_without_rewriting(self):
        s=prepared();save_session(s,self.path);valid=self.path.read_bytes()
        for edit in (lambda d:d.update(schema_version=999),lambda d:d.update(runtime_hash='0'*64)):
            self.path.write_bytes(valid);self.rewrite(edit);bad=self.path.read_bytes()
            with self.assertRaises(SaveError):load_session(self.path)
            self.assertEqual(self.path.read_bytes(),bad)
        self.path.write_bytes(valid.replace(b'"checksum": "',b'"checksum": "bad'))
        with self.assertRaises(SaveError):load_session(self.path)

    def test_unknown_record_fields_duplicate_json_and_wrong_types_reject(self):
        s=prepared();save_session(s,self.path);valid=self.path.read_bytes()
        edits=(lambda d:d['payload']['lobby'].update(record='os.system'),
               lambda d:d['payload']['lobby']['fields'].update(surprise='execute'),
               lambda d:d['payload']['lobby']['fields'].update(revision=True),
               lambda d:d['payload'].update(bots=['P9']))
        for edit in edits:
            self.path.write_bytes(valid);self.rewrite(edit)
            with self.assertRaises(SaveError):load_session(self.path)
        self.path.write_text('{"format":"one","format":"two"}')
        with self.assertRaises(SaveError):load_session(self.path)

    def test_size_depth_limits_and_invalid_extension(self):
        s=HarnessSession(seed=SEED);save_session(s,self.path)
        with patch('crucible_play.persistence.MAX_BYTES',100):
            with self.assertRaises(SaveError):load_session(self.path)
        nested=0
        for _ in range(70):nested={'tuple':[nested]}
        self.rewrite(lambda d:d['payload'].update(lobby=nested))
        with self.assertRaises(SaveError):load_session(self.path)
        with self.assertRaises(SaveError):save_session(s,self.path.with_suffix('.txt'))

    def test_runtime_change_on_save_preserves_previous_snapshot(self):
        s=prepared();save_session(s,self.path);original=self.path.read_bytes()
        with patch('crucible_play.persistence.runtime_fingerprint',return_value='changed'):
            with self.assertRaises(SaveError):save_session(s,self.path)
        self.assertEqual(self.path.read_bytes(),original)


if __name__=='__main__':unittest.main()
