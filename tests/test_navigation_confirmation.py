"""Hidden Tk checks for navigation and exact-payment review boundaries."""
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
class NavigationConfirmationTests(unittest.TestCase):
    def setUp(self):
        self.root=tk.Tk();self.root.withdraw()
        self.session=HarnessSession(seed=b'widget-test-seed-1234567890')
        self.app=PlayWindow(self.root,self.session)
        for actor in ('P1','P2'):
            self.session.choose_deck(actor,'core-gold',expected_revision=self.session.view()['revision'])
            self.session.ready(actor,True,expected_revision=self.session.view()['revision'])
        self.session.start('P1',expected_revision=self.session.view()['revision'])
        for actor in ('P1','P2'):self.session.redraw(actor,(),expected_revision=self.session.view()['revision'])
        for _ in range(4):
            actor=self.session.view()['priority']['holder']
            self.session.send(actor,{'kind':'pass','args':{},'expected_revision':self.session.view()['revision']})
        self.actor=self.session.view()['turn']['active_player']
        self.app.seat(self.actor);self.app.unlock()

    def tearDown(self):self.root.destroy()

    def widgets(self,kind,text=None):
        return [w for w in descendants(self.root) if isinstance(w,kind) and (text is None or w.cget('text')==text)]

    def button(self,label):return self.widgets(ttk.Button,label)[0]

    def state(self):return str(self.button('Confirm play and payment').cget('state'))

    def view_card(self,cost=1,**changes):
        view=self.session.view(self.actor)
        card=next(c.copy() for c in view['you']['hand'] if c['kind']=='creature')
        card.update(cost=cost,**changes)
        return view,card

    def set_payment(self,value):
        popup=next(w for w in self.root.winfo_children() if isinstance(w,tk.Toplevel))
        spin=next(w for w in descendants(popup) if isinstance(w,ttk.Spinbox))
        self.root.setvar(str(spin.cget('textvariable')),value)

    def test_hand_shortcut_restores_after_refresh_and_hides_on_public_view(self):
        self.button('Go to hand').invoke()
        self.assertEqual(self.app._match_focus,(self.actor,'hand'))
        canvas=self.widgets(tk.Canvas)[0];self.assertGreater(canvas.yview()[0],0)
        self.app.render();self.assertEqual(self.app._match_focus,(self.actor,'hand'))
        self.assertGreater(self.widgets(tk.Canvas)[0].yview()[0],0)
        self.button('Go to history').invoke();self.assertEqual(self.app._match_focus[1],'history')
        self.app.hide()
        self.assertEqual(str(self.button('Go to hand').cget('state')),'disabled')
        self.assertFalse(self.widgets(ttk.Button,'Inspect / play'))

    def test_inspection_and_cancel_never_mutate_game(self):
        view,card=self.view_card();before=self.session.view(self.actor)
        self.app.card_dialog(view,card)
        self.set_payment('invalid')
        self.assertEqual(self.state(),'disabled')
        self.button('Cancel').invoke()
        self.assertEqual(before,self.session.view(self.actor))

    def test_only_exact_available_ordinary_and_controlled_tokens_can_confirm(self):
        view,card=self.view_card(cost=3)
        enemy=next(p['player_id'] for p in view['players'] if p['player_id']!=self.actor)
        view['battlefield']=[{'instance_id':'own-token','kind':'resource_token','controller':self.actor,'resource_value':1},
            {'instance_id':'enemy-token','kind':'resource_token','controller':enemy,'resource_value':5}]
        self.app.card_dialog(view,card)
        self.assertEqual(self.state(),'disabled')
        tokens=[w for w in self.widgets(ttk.Checkbutton) if str(w.cget('text')).startswith('Use token')]
        self.assertEqual(len(tokens),1);tokens[0].invoke()
        self.assertEqual(self.state(),'normal')
        self.set_payment('3');self.assertEqual(self.state(),'disabled')
        self.set_payment('1');self.assertEqual(self.state(),'disabled')
        self.set_payment('2');self.assertEqual(self.state(),'normal')
        with patch.object(self.app,'send',return_value=True) as send:
            self.button('Confirm play and payment').invoke()
        send.assert_called_once_with('play_card',payment={'ordinary':2,'token_ids':['own-token']},card_id=card['instance_id'])

    def test_target_is_explicit_and_enemy_filter_preserves_command_identity(self):
        view,card=self.view_card(cost=0,kind='reaction',target_kind='creature',target_relation='enemy',steps=[])
        enemy=next(p['player_id'] for p in view['players'] if p['player_id']!=self.actor)
        view['battlefield']=[{'instance_id':'foe-123456','definition_key':'unit-01','kind':'creature','controller':enemy,'creature':{}},
            {'instance_id':'own-654321','definition_key':'unit-01','kind':'creature','controller':self.actor,'creature':{}}]
        # Projected creature records are truthy; only ownership matters to target_options.
        for obj in view['battlefield']:obj['creature']={'attack':2}
        self.app.card_dialog(view,card);self.assertEqual(self.state(),'disabled')
        radios=self.widgets(ttk.Radiobutton)
        self.assertEqual(len(radios),1);self.assertIn('123456',str(radios[0].cget('text')))
        radios[0].invoke();self.assertEqual(self.state(),'normal')
        with patch.object(self.app,'send',return_value=True) as send:self.button('Confirm play and payment').invoke()
        send.assert_called_once_with('play_card',payment={'ordinary':0,'token_ids':[]},card_id=card['instance_id'],target='foe-123456')

    def test_no_target_and_pause_cannot_confirm(self):
        view,card=self.view_card(cost=0,kind='reaction',target_kind='creature',target_relation='enemy')
        self.app.card_dialog(view,card);self.assertEqual(self.state(),'disabled')
        self.app.close_inspections()
        view,card=self.view_card(cost=0);self.session.paused=True
        self.app.card_dialog(view,card);self.assertEqual(self.state(),'disabled')

    def test_stale_confirmation_rejects_without_submitting_and_refresh_closes_it(self):
        view,card=self.view_card(cost=0)
        self.app.card_dialog(view,card);self.assertEqual(self.state(),'normal')
        self.session.send(self.actor,{'kind':'pass','args':{},'expected_revision':view['revision']})
        with patch.object(self.app,'send') as send:self.button('Confirm play and payment').invoke();send.assert_not_called()
        self.assertEqual(self.state(),'disabled')
        self.app.render()
        self.assertFalse(any(isinstance(w,tk.Toplevel) for w in self.root.winfo_children()))
