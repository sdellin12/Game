"""Default table regression checks, using hidden Tk windows, not human testing."""
import os
import tkinter as tk
from tkinter import ttk
import unittest
from crucible_play.desktop import PlayWindow
from crucible_play.session import HarnessSession
from crucible_play.match_screen import action_state


def descendants(widget):
    return [item for child in widget.winfo_children() for item in [child]+descendants(child)]


@unittest.skipUnless(os.name=='nt' or os.environ.get('DISPLAY'),'Tk requires a display')
class MatchScreenTests(unittest.TestCase):
    def setUp(self):
        self.root=tk.Tk();self.root.withdraw()
        self.session=HarnessSession(seed=b'widget-test-seed-1234567890')
        self.app=PlayWindow(self.root,self.session)
        for actor in ('P1','P2'):
            self.session.choose_deck(actor,'core-gold',expected_revision=self.session.view()['revision'])
            self.session.ready(actor,True,expected_revision=self.session.view()['revision'])
        self.session.start('P1',expected_revision=self.session.view()['revision'])
        for actor in ('P1','P2'):self.session.redraw(actor,(),expected_revision=self.session.view()['revision'])
        self.app.render()

    def tearDown(self):self.root.destroy()

    def buttons(self,label):
        return [w for w in descendants(self.root) if isinstance(w,ttk.Button) and w.cget('text')==label]

    def test_private_tiles_require_acknowledgement_and_hide_closes_inspection(self):
        self.assertFalse(self.buttons('Inspect / play'))
        self.app.seat('P1');self.assertFalse(self.buttons('Inspect / play'))
        self.app.unlock()
        self.assertEqual(len(self.buttons('Inspect / play')),len(self.session.view('P1')['you']['hand']))
        before=self.session.view()
        self.buttons('Inspect / play')[0].invoke()
        self.assertEqual(before,self.session.view(),'Inspection must not submit a command')
        self.assertTrue(any(isinstance(w,tk.Toplevel) for w in self.root.winfo_children()))
        self.app.hide()
        self.assertFalse(self.buttons('Inspect / play'))
        self.assertFalse(any(isinstance(w,tk.Toplevel) for w in self.root.winfo_children()))

    def test_action_buttons_match_priority_and_pause(self):
        actor=self.session.view()['priority']['holder']
        self.app.seat(actor);self.app.unlock()
        self.assertEqual(action_state(self.session.view(actor),actor),(True,False))
        self.assertEqual(str(self.buttons('Pass / continue phase')[0].cget('state')),'normal')
        self.buttons('Pass / continue phase')[0].invoke()
        self.assertNotEqual(self.session.view()['priority']['holder'],actor)
        self.session.paused=True;self.app.render()
        self.assertEqual(str(self.buttons('Pass / continue phase')[0].cget('state')),'disabled')

    def test_many_cards_scroll_with_bounded_window(self):
        self.app.seat('P1');self.app.unlock()
        view=self.session.view('P1')
        view['you']['hand']=view['you']['hand']*8
        for child in self.app.body.winfo_children():child.destroy()
        self.app.render_match(view);self.root.update_idletasks()
        canvas=next(w for w in descendants(self.root) if isinstance(w,tk.Canvas))
        self.assertGreater(canvas.bbox('all')[3],canvas.winfo_reqheight())
        self.assertLess(self.root.winfo_reqheight(),1000)
        self.assertLess(self.root.winfo_reqwidth(),1200)

    def test_existing_payment_confirmation_operates_on_default_table(self):
        for _ in range(4):
            self.app.seat(self.session.view()['priority']['holder']);self.app.unlock()
            self.buttons('Pass / continue phase')[0].invoke()
        actor=self.session.view()['turn']['active_player']
        self.app.seat(actor);self.app.unlock()
        view=self.session.view(actor)
        index=next(i for i,c in enumerate(view['you']['hand']) if c['kind']=='creature' and c['cost']<=2)
        card=view['you']['hand'][index]
        self.buttons('Inspect / play')[index].invoke()
        self.buttons('Confirm play and payment')[0].invoke()
        self.assertIn(card['instance_id'],[c['instance_id'] for c in self.session.view(actor)['pending_cards']])

    def test_public_combat_and_creature_status_render_without_private_locks(self):
        view=self.session.view()
        view['battlefield']=[{'instance_id':'fixture-attacker','definition_key':'unit-01',
            'controller':'P1','owner':'P1','kind':'creature','cost':1,
            'creature':{'attack':2,'health':1,'max_health':3,'exhausted':True,
                'attack_eligible':True,'attack_used':True,'shields':[{'amount':4}]}},
            {'instance_id':'resource-token-fixture','controller':'P1','owner':'P1',
                'kind':'resource_token','capacity_bonus':0,'resource_value':2}]
        view['combat']={'stage':'blocking','attacks':(('fixture-attacker','P2',None),),
            'own_lock':'PRIVATE-LOCK-MARKER'}
        for child in self.app.body.winfo_children():child.destroy()
        self.app.render_match(view)
        text='\n'.join(str(w.cget('text')) for w in descendants(self.root) if isinstance(w,ttk.Label))
        self.assertIn('1/3 HP',text);self.assertIn('Prevention: 4',text)
        self.assertIn('Resource value: 2',text)
        self.assertIn('→ P2',text);self.assertNotIn('PRIVATE-LOCK-MARKER',text)
        self.assertFalse(self.buttons('Inspect / play'))
