"""Hidden-window tests of setup transactions and combat assignment commands."""
import os
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import patch
from crucible_play.desktop import PlayWindow
from crucible_play.session import HarnessSession


def descendants(widget):
    return [item for child in widget.winfo_children() for item in [child]+descendants(child)]


@unittest.skipUnless(os.name=='nt' or os.environ.get('DISPLAY'),'Tk requires a display')
class SetupCombatUITests(unittest.TestCase):
    def setUp(self):
        self.root=tk.Tk();self.root.withdraw()
        self.session=HarnessSession(seed=b'widget-test-seed-1234567890')
        self.app=PlayWindow(self.root,self.session)

    def tearDown(self):self.root.destroy()

    def widgets(self,kind,text=None):
        return [w for w in descendants(self.root) if isinstance(w,kind) and (text is None or w.cget('text')==text)]

    def button(self,text):return self.widgets(ttk.Button,text)[0]

    def opening(self):
        for actor in ('P1','P2'):
            self.session.choose_deck(actor,'core-gold',expected_revision=self.session.view()['revision'])
            self.session.ready(actor,True,expected_revision=self.session.view()['revision'])
        self.session.start('P1',expected_revision=self.session.view()['revision'])
        self.app.render()

    def match(self):
        self.opening()
        for actor in ('P1','P2'):self.session.redraw(actor,(),expected_revision=self.session.view()['revision'])
        self.app.seat('P1');self.app.unlock()
        return self.session.view('P1')

    def test_guided_lobby_requires_deck_and_all_ready_before_host_deals(self):
        self.app.seat('P1');self.app.unlock()
        self.assertEqual(str(self.button('Ready').cget('state')),'disabled')
        self.assertEqual(str(self.button('Deal opening hands').cget('state')),'disabled')
        for actor in ('P1','P2'):
            self.app.seat(actor);self.app.unlock()
            self.button('Apply deck and reserve identity').invoke()
            self.button('Ready').invoke()
        self.app.seat('P1');self.app.unlock()
        self.assertEqual(str(self.button('Deal opening hands').cget('state')),'normal')
        self.button('Deal opening hands').invoke()
        self.assertEqual(self.session.view()['phase'],'opening')

    def test_opening_tiles_submit_only_marked_cards_and_hide_destroys_selections(self):
        self.opening();self.app.seat('P1')
        self.assertFalse(self.widgets(ttk.Checkbutton,'Replace this card'))
        self.app.unlock();before=self.session.view('P1')
        checks=self.widgets(ttk.Checkbutton,'Replace this card');self.assertEqual(len(checks),len(before['you']['hand']))
        checks[1].invoke();checks[3].invoke()
        self.assertEqual(self.session.view('P1'),before)
        self.app.hide();self.assertFalse(self.widgets(ttk.Checkbutton,'Replace this card'))
        self.app.seat('P1');self.app.unlock()
        checks=self.widgets(ttk.Checkbutton,'Replace this card');checks[1].invoke();checks[3].invoke()
        self.button('Lock opening choice').invoke()
        self.assertTrue(self.session.view('P1')['you']['locked'])
        self.assertEqual(dict(self.session._lobby.redraw_locks)['P1'],tuple(before['you']['hand'][i]['instance_id'] for i in (1,3)))
        self.assertFalse(self.widgets(ttk.Checkbutton,'Replace this card'))
        self.assertIsNone(self.session.view()['redraw_counts'])

    def test_paused_setup_and_opening_controls_cannot_submit(self):
        self.session.paused=True;self.app.seat('P1');self.app.unlock()
        self.assertEqual(str(self.button('Apply deck and reserve identity').cget('state')),'disabled')
        self.session.paused=False;self.opening();self.app.seat('P1');self.app.unlock()
        self.session.paused=True;self.app.render();before=self.session.view('P1')
        self.assertEqual(str(self.button('Lock opening choice').cget('state')),'disabled')
        self.button('Lock opening choice').invoke();self.assertEqual(before,self.session.view('P1'))

    @staticmethod
    def creature(key,owner='P1',**changes):
        creature={'attack':2,'health':3,'max_health':3,'exhausted':False,'attack_eligible':True,'attack_used':False,'keywords':[],'shields':[]}
        creature.update(changes)
        return {'instance_id':key,'definition_key':'unit-01','kind':'creature','cost':1,'controller':owner,'owner':owner,'creature':creature}

    def test_attack_tiles_filter_ineligible_creatures_and_submit_explicit_targets(self):
        view=self.match();view['battlefield']=[self.creature('attacker',keywords=['challenge']),self.creature('tired',exhausted=True),self.creature('foe','P2')]
        frame=ttk.Frame(self.app.body);frame.pack()
        with patch.object(self.app,'send') as send:
            self.app.attack_panel(frame,view)
            self.assertEqual(len(self.widgets(ttk.Radiobutton,'Stay back')),1)
            self.widgets(ttk.Radiobutton,'Attack P2')[0].invoke();send.assert_not_called()
            self.button('Confirm all attacks / no attacks').invoke()
            send.assert_called_once_with('declare_attacks',attacks=[{'attacker_id':'attacker','target_player':'P2'}])
            send.reset_mock()
            next(w for w in self.widgets(ttk.Radiobutton) if str(w.cget('text')).startswith('Challenge ')).invoke()
            self.button('Confirm all attacks / no attacks').invoke()
            send.assert_called_once_with('declare_attacks',attacks=[{'attacker_id':'attacker','target_player':'P2','challenge_target':'foe'}])

    def test_blockers_stay_local_until_batch_lock_and_challenged_card_is_excluded(self):
        view=self.match();view['battlefield']=[self.creature('blocker'),self.creature('challenged'),self.creature('foe','P2')]
        view['combat']={'stage':'blocking','attacks':(('foe','P1',None),('challenger','P1','challenged'))}
        frame=ttk.Frame(self.app.body);frame.pack()
        with patch.object(self.app,'send') as send:
            self.app.render_choice(frame,view,{'kind':'blockers','locked':False})
            self.assertEqual(len(self.widgets(ttk.Radiobutton,'Do not block')),1)
            next(w for w in self.widgets(ttk.Radiobutton) if str(w.cget('text')).startswith('Block ')).invoke()
            send.assert_not_called()
            self.button('Lock complete blocker choice / no blocks').invoke()
            send.assert_called_once_with('lock_blockers',assignments=[{'attacker_id':'foe','blockers':['blocker']}])

    def test_empty_attack_batch_uses_real_engine_command_and_paused_batch_is_disabled(self):
        from crucible_play.smoke import choose_move
        self.match()
        for _ in range(100):
            public=self.session.view();priority=public['priority']
            if public['turn']['phase']=='Combat' and priority['status']=='closed':break
            actor=priority['holder']
            kind,args=choose_move(self.session.view(actor))
            self.session.send(actor,{'expected_revision':public['revision'],'kind':kind,'args':args})
        else:self.fail('Did not reach attack declaration')
        actor=self.session.view()['turn']['active_player'];self.app.seat(actor);self.app.unlock()
        before=self.session.view()
        self.session.paused=True;self.app.render()
        self.assertFalse(self.widgets(ttk.Button,'Confirm all attacks / no attacks'))
        self.session.paused=False;self.app.render()
        self.button('Confirm all attacks / no attacks').invoke()
        self.assertGreater(self.session.view()['revision'],before['revision'])
        self.assertNotEqual(self.app.notice.get(),'command unavailable')

    def test_large_attack_selection_scrolls_without_forcing_window_growth(self):
        view=self.match();view['turn']['active_player']='P1';view['turn']['phase']='Combat'
        view['priority']={'holder':None,'status':'closed','passes':[]}
        view['battlefield']=[self.creature(f'creature-{i}') for i in range(30)]
        for child in self.app.body.winfo_children():child.destroy()
        self.app.render_match(view);self.root.update_idletasks()
        self.assertEqual(len(self.widgets(ttk.Radiobutton,'Stay back')),30)
        canvas=self.widgets(tk.Canvas)[0]
        self.assertGreater(canvas.bbox('all')[3],canvas.winfo_reqheight())
        self.assertLess(self.root.winfo_reqheight(),1000)
        self.assertLess(self.root.winfo_reqwidth(),1200)
