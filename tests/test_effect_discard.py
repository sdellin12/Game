import gzip,json,tempfile,unittest,os
from dataclasses import replace
from pathlib import Path
from crucible_core.cards import CardDefinition
from crucible_core.match import DiscardThenDraw,DrawCards,NegateEffect,EffectSpec,GrantResources,validate_match
from crucible_core.views import project_match
from crucible_play.persistence import save_session,load_session,_encode,_decode
from crucible_play.migrate import migrate_save,_upgrade_payload,V5_RECORDS
from crucible_content.practice import discard_draw_pack,practice_pack,pack_hash
from crucible_play.session import HarnessSession
from crucible_play.opponent import choose_move
from test_commands_cards_views import fixture,instances,command,pass_round,play
from test_persistence import ready,state,cmd,passes
from test_save_migration import sealed

OUTLET=CardDefinition('outlet','action',2,(DiscardThenDraw('$controller',2),))


def opening(deck=('one','two'),hand=('outlet','fodder'),discard=()):
    return fixture((OUTLET,),instances(('outlet','outlet','A')),ah=hand,ad=deck,ag=discard)


def waiting(**kw):return pass_round(play(opening(**kw),'A','outlet',2))


def discard(s,card='fodder',actor='A',request=None):
    return command(s,actor,'effect_discard',card_id=card,request_id=s.pending.discard_request if request is None else request)


class EffectDiscardTests(unittest.TestCase):
    def test_resolution_choice_is_private_and_action_cannot_discard_itself(self):
        s=waiting();self.assertEqual(s.players[0].resources.available,8)
        self.assertEqual(project_match(s,'A')['you']['choice']['kind'],'effect_discard')
        for actor in ('B','C'):self.assertIsNone(project_match(s,actor)['you']['choice'])
        self.assertNotIn('fodder',json.dumps(project_match(s)))
        for actor,card,request in (('B','fodder',None),('A','outlet',None),('A','fodder',True),('A','fodder',999)):
            with self.assertRaises(ValueError):discard(s,card,actor,request)
        with self.assertRaises(ValueError):command(s,'A','pass')
        result=discard(s)
        self.assertEqual(result.players[0].cards.hand,('one','two'))
        self.assertEqual(result.players[0].cards.discard,('fodder','outlet'))
        with self.assertRaises(ValueError):discard(result,request=s.pending.discard_request)

    def test_last_hand_card_skips_draw_without_empty_deck_defeat(self):
        s=waiting(deck=(),hand=('outlet',))
        self.assertIsNone(s.pending);self.assertFalse(s.players[0].eliminated)
        self.assertEqual(s.players[0].cards.discard,('outlet',))
        self.assertFalse(any(e.kind=='required_draw' for e in s.events))

    def test_negation_prevents_discard_and_draw_but_keeps_payment(self):
        s=play(opening(),'A','outlet',2);identity=s.priority.chain[-1].effect_id
        from test_zone_moves import resolve
        s=replace(s,effects=s.effects+(EffectSpec('counter','B',(NegateEffect(identity),)),))
        s=resolve(s,'counter','B')
        self.assertIsNone(s.pending);self.assertEqual(s.players[0].cards.hand,('fodder',))
        self.assertEqual(s.players[0].resources.available,8)

    def test_discard_can_refill_but_pending_outlet_cannot_and_resumes_once(self):
        s=discard(waiting(deck=('one',),discard=('grave',)))
        self.assertEqual(s.pending.draw.remaining,1);self.assertTrue(s.pending.discard_done)
        self.assertIn('fodder',s.pending.draw.player.discard);self.assertNotIn('outlet',s.pending.draw.player.discard)
        restored=_decode(_encode(s));validate_match(restored)
        for game in (s,restored):
            result=command(game,'A','refill',pay=True,request_id=game.pending.draw.request_id)
            self.assertIsNone(result.pending);self.assertEqual(len(result.players[0].cards.hand),2)
            self.assertEqual(sum(e.kind=='card_effect_discarded' for e in result.events),1)
            self.assertEqual(result.players[0].cards.health,10)
            self.assertEqual(result.players[0].cards.discard,('outlet',))

    def test_declined_refill_and_concession_never_deadlock_choice(self):
        s=discard(waiting(deck=()))
        s=command(s,'A','refill',pay=False,request_id=s.pending.draw.request_id)
        self.assertTrue(s.players[0].eliminated)
        s=command(waiting(),'A','concede',confirmed=True)
        self.assertIsNone(s.pending);self.assertTrue(s.players[0].eliminated)

    def test_policy_selects_own_card_and_malformed_continuation_rejects(self):
        s=waiting();kind,args=choose_move(project_match(s,'A'))
        self.assertEqual(kind,'effect_discard');self.assertIsNone(command(s,'A',kind,**args).pending)
        for r in (replace(s.pending,discard_done=True),replace(s.pending,discard_request=True),replace(s.pending,index=50)):
            with self.assertRaises(ValueError):validate_match(replace(s,pending=r))

    def test_v5_optional_and_refill_convert_without_reset_or_replay(self):
        for name in ('save_v5_before_reward_types.json.gz','save_v5_before_discard_refill.json.gz'):
            case=json.loads(gzip.decompress((Path(__file__).parent/'fixtures'/name).read_bytes()))
            with tempfile.TemporaryDirectory() as directory:
                source=Path(directory)/'old.crucible.json';target=Path(directory)/'new.crucible.json'
                source.write_bytes(sealed(case['save']));original=source.read_bytes()
                with self.assertRaises(ValueError):load_session(source)
                migrate_save(source,target);s=load_session(target)
                self.assertEqual(pack_hash(s._lobby.pack),case['save']['content_hash'])
                s.resume();s.send(case['actor'],case['packet'])
                self.assertEqual(s._lobby,_decode(_upgrade_payload(case['expected'],V5_RECORDS,version=5)))
                self.assertEqual(source.read_bytes(),original)

    def test_native_choice_save_roundtrip_and_opt_in_pack_identity(self):
        pack=discard_draw_pack();self.assertEqual(len(pack.cards),40);self.assertNotEqual(pack_hash(pack),pack_hash(practice_pack()))
        s=ready(HarnessSession(pack=pack,seed=b'discard-private-save-fixture-1234'))
        s.start('P1',expected_revision=s.view()['revision'])
        for p in s.view()['players']:s.redraw(p['player_id'],(),expected_revision=s.view()['revision'])
        m=s._lobby.match;a=m.turn.active_player
        card=next(c for c in m.card_instances if c.owner==a and c.definition_key=='proposal-scrapyard-insight')
        p=next(p for p in m.players if p.cards.player_id==a);all_cards=p.cards.deck+p.cards.hand
        fodder=next(i for i in all_cards if i!=card.instance_id)
        remaining=tuple(i for i in all_cards if i not in (card.instance_id,fodder))
        state(s,turn=replace(m.turn,phase='MainBefore'),players=tuple(replace(p,cards=replace(p.cards,hand=(card.instance_id,fodder),deck=remaining[:1],discard=remaining[1:]),resources=replace(p.resources,available=2)) if p.cards.player_id==a else p for p in m.players))
        cmd(s,a,'play_card',card_id=card.instance_id,payment={'ordinary':2,'token_ids':[]});passes(s)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'choice.crucible.json';save_session(s,path);loaded=load_session(path)
            self.assertTrue(loaded.paused);loaded.resume()
            for game in (s,loaded):cmd(game,a,'effect_discard',card_id=fodder,request_id=game.view(a)['you']['choice']['request_id'])
            self.assertEqual(s._lobby,loaded._lobby)
            self.assertTrue(s._lobby.match.pending.discard_done)
            save_session(s,path);resumed=load_session(path);resumed.resume()
            for game in (s,resumed):cmd(game,a,'refill',pay=True,request_id=game.view(a)['you']['choice']['request_id'])
            self.assertEqual(s._lobby,resumed._lobby)

    def test_v5_premature_continuation_fields_and_new_records_reject_without_output(self):
        original=json.loads(gzip.decompress((Path(__file__).parent/'fixtures/save_v5_before_discard_refill.json.gz').read_bytes()))['save']
        for corrupt in ('field','record'):
            doc=json.loads(json.dumps(original))
            def visit(value):
                if isinstance(value,dict):
                    if value.get('record')=='Resolution':
                        if corrupt=='field':value['fields']['discard_done']=False
                        else:value['record']='DiscardThenDraw'
                    for child in value.values():visit(child)
                elif isinstance(value,list):
                    for child in value:visit(child)
            visit(doc)
            with tempfile.TemporaryDirectory() as directory:
                source=Path(directory)/'old.crucible.json';target=Path(directory)/'new.crucible.json';source.write_bytes(sealed(doc));before=source.read_bytes()
                with self.assertRaises(ValueError):migrate_save(source,target)
                self.assertFalse(target.exists());self.assertEqual(source.read_bytes(),before)


@unittest.skipUnless(os.name=='nt' or os.environ.get('DISPLAY'),'Tk display required')
class EffectDiscardWidgetTests(unittest.TestCase):
    def test_selection_is_single_explicit_and_disabled_while_paused(self):
        import tkinter as tk
        from tkinter import ttk
        from crucible_play.desktop import PlayWindow
        root=tk.Tk();root.withdraw()
        try:
            app=PlayWindow.__new__(PlayWindow);calls=[]
            app.label=lambda c:c['instance_id'];app.send=lambda kind,**args:calls.append((kind,args))
            s=waiting();view=project_match(s,'A');choice=view['you']['choice']
            for paused in (True,False):
                frame=ttk.Frame(root);app.render_choice(frame,dict(view,paused=paused),choice)
                listing=next(c for c in frame.winfo_children() if isinstance(c,tk.Listbox))
                button=next(c for c in frame.winfo_children() if isinstance(c,ttk.Button))
                button.invoke();self.assertFalse(calls)
                listing.selection_set(0);button.invoke()
                if paused:self.assertFalse(calls)
                else:self.assertEqual(calls,[('effect_discard',{'card_id':'fodder','request_id':choice['request_id']})])
                frame.destroy()
        finally:root.destroy()
