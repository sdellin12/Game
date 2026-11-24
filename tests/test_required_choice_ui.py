"""Hidden-window coverage of required choice packets, privacy and guidance."""
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
class RequiredChoiceUITests(unittest.TestCase):
    def setUp(self):
        self.root=tk.Tk();self.root.withdraw()
        self.session=HarnessSession(seed=b'widget-test-seed-1234567890')
        self.app=PlayWindow(self.root,self.session)
        for actor in ('P1','P2'):
            self.session.choose_deck(actor,'core-gold',expected_revision=self.session.view()['revision'])
            self.session.ready(actor,True,expected_revision=self.session.view()['revision'])
        self.session.start('P1',expected_revision=self.session.view()['revision'])
        for actor in ('P1','P2'):self.session.redraw(actor,(),expected_revision=self.session.view()['revision'])
        self.app.seat('P1');self.app.unlock()

    def tearDown(self):self.root.destroy()

    def widgets(self,kind,text=None):
        return [w for w in descendants(self.root) if isinstance(w,kind) and (text is None or w.cget('text')==text)]

    def button(self,text):return self.widgets(ttk.Button,text)[0]

    def choice(self,choice,paused=False):
        view=self.session.view('P1');view['you']['choice']=choice;view['paused']=paused
        self.frame=ttk.Frame(self.app.body);self.frame.pack(fill='x')
        self.app.render_choice(self.frame,view,choice)
        return view

    def test_end_discard_requires_exact_count_and_hiding_clears_marks(self):
        view=self.choice({'kind':'end_discard','count':2})
        checks=self.widgets(ttk.Checkbutton,'Discard this card')
        self.assertEqual(str(self.button('Confirm discards').cget('state')),'disabled')
        checks[0].invoke();checks[2].invoke()
        self.assertEqual(str(self.button('Confirm discards').cget('state')),'normal')
        checks[1].invoke();self.assertEqual(str(self.button('Confirm discards').cget('state')),'disabled');checks[1].invoke()
        with patch.object(self.app,'send') as send:
            self.button('Confirm discards').invoke()
            send.assert_called_once_with('end_discard',cards=[view['you']['hand'][i]['instance_id'] for i in (0,2)])
        self.app.hide();self.assertFalse(self.widgets(ttk.Checkbutton,'Discard this card'))

    def test_effect_discard_keeps_request_identity_and_has_no_default_selection(self):
        view=self.choice({'kind':'effect_discard','request_id':27})
        with patch.object(self.app,'send') as send:
            self.button('Confirm effect discard').invoke();send.assert_not_called()
            self.widgets(ttk.Checkbutton,'Discard this card')[1].invoke()
            self.button('Confirm effect discard').invoke()
            send.assert_called_once_with('effect_discard',card_id=view['you']['hand'][1]['instance_id'],request_id=27)

    def test_combat_order_names_preview_but_preserves_subject_and_item_ids(self):
        self.choice({'kind':'combat_order','orders':[{'subject':'attacker','items':['first','second']}]})
        listing=self.widgets(tk.Listbox)[0]
        self.assertIn('NEXT',listing.get(0));listing.selection_set(0)
        with patch.object(self.app,'send') as send:
            self.button('Move down').invoke();send.assert_not_called()
            self.assertIn('second',listing.get(0));self.assertIn('NEXT',listing.get(0))
            self.button('Confirm this order').invoke()
            send.assert_called_once_with('combat_order',subject='attacker',order=['second','first'])

    def test_trigger_order_next_marker_is_bottom_and_empty_order_still_confirms(self):
        self.choice({'kind':'trigger_order','triggers':[{'trigger_id':'a','source_id':'source-one'},{'trigger_id':'b','source_id':'source-two'}]})
        listing=self.widgets(tk.Listbox)[0]
        self.assertIn('source-one',listing.get(0));self.assertNotIn('NEXT',listing.get(0));self.assertIn('NEXT',listing.get(1))
        self.frame.destroy()
        self.choice({'kind':'trigger_order','triggers':[]})
        with patch.object(self.app,'send') as send:
            self.button('Confirm no triggered effects').invoke();send.assert_called_once_with('trigger_order',order=[])

    def test_paused_discard_and_order_controls_cannot_submit(self):
        for choice,label in (({'kind':'end_discard','count':1},'Confirm discards'),({'kind':'trigger_order','triggers':[]},'Confirm no triggered effects')):
            self.choice(choice,paused=True)
            self.assertEqual(str(self.button(label).cget('state')),'disabled')
            with patch.object(self.app,'send') as send:self.button(label).invoke();send.assert_not_called()
            self.frame.destroy()

    def test_refill_shows_life_and_penalty_and_disables_unaffordable_or_paused_payment(self):
        view=self.session.view('P1')
        health=next(p['health'] for p in view['players'] if p['player_id']=='P1')
        self.choice({'kind':'refill','cost':health,'minimum_health':1,'remaining':2,'request_id':9})
        self.assertEqual(str(self.button(f'Pay {health} life and refill').cget('state')),'disabled')
        with patch.object(self.app,'send') as send:
            self.button('Decline refill (eliminates you)').invoke();send.assert_called_once_with('refill',pay=False,request_id=9)
        self.frame.destroy()
        self.choice({'kind':'refill','cost':1,'minimum_health':1,'remaining':2,'request_id':10},paused=True)
        self.assertEqual(str(self.button('Pay 1 life and refill').cget('state')),'disabled')
        self.assertEqual(str(self.button('Decline refill (eliminates you)').cget('state')),'disabled')

    def test_shortcuts_are_registered_and_handoff_removes_private_destination(self):
        self.assertTrue(self.root.bind('<Alt-Key-2>'));self.assertTrue(self.root.bind('<Alt-h>'))
        self.app.navigate_match('hand');self.assertEqual(self.app._match_focus,('P1','hand'))
        self.app.seat('P2');self.assertFalse(self.app._match_navigation)
        self.app.navigate_match('hand');self.assertFalse(self.widgets(ttk.Button,'Inspect / play'))
