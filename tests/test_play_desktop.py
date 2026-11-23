import unittest
import os
import tkinter as tk
from tkinter import ttk
from crucible_play.desktop import PlayWindow
from crucible_play.session import HarnessSession
from crucible_play.smoke import run_smoke,choose_move


def children(widget):
    return [child for direct in widget.winfo_children() for child in [direct]+children(direct)]


class HarnessSmokeTests(unittest.TestCase):
    def test_view_only_driver_finishes_two_three_and_four_player_games(self):
        for count in (2,3,4):
            result=run_smoke(count)
            self.assertEqual(result['status'],'completed')
            self.assertEqual(result['result']['kind'],'win')
            self.assertLess(result['commands'],4000)

    def test_command_limit_is_incomplete_not_a_fabricated_result(self):
        result=run_smoke(2,limit=1)
        self.assertEqual(result,{'status':'incomplete','reason':'command limit','commands':1})

    def test_policy_has_no_move_for_spectator_projection(self):
        self.assertIsNone(choose_move({'you':None}))


@unittest.skipUnless(os.name=='nt' or os.environ.get('DISPLAY'), 'Tk widget tests require a desktop display')
class HarnessWidgetTests(unittest.TestCase):
    def setUp(self):
        self.root=tk.Tk();self.root.withdraw()
        self.session=HarnessSession(seed=b'widget-test-seed-1234567890')
        self.app=PlayWindow(self.root,self.session)
        self.root.update_idletasks()

    def tearDown(self):self.root.destroy()

    def text(self):
        result=[]
        for child in children(self.root):
            if isinstance(child,(ttk.Label,ttk.Button)):
                result.append(str(child.cget('text')))
            elif isinstance(child,tk.Listbox):result.extend(child.get(0,'end'))
            elif isinstance(child,tk.Text):result.append(child.get('1.0','end'))
        return '\n'.join(result)

    def button(self,label):
        return next(c for c in children(self.root) if isinstance(c,ttk.Button) and c.cget('text')==label)

    def ready_opening(self):
        for p in self.session.view()['players']:
            actor=p['player_id']
            self.session.choose_deck(actor,'core-gold',expected_revision=self.session.view()['revision'])
            self.session.ready(actor,True,expected_revision=self.session.view()['revision'])
        self.session.start('P1',expected_revision=self.session.view()['revision'])
        self.app.render()

    def test_seat_buttons_show_handoff_before_private_widgets(self):
        self.ready_opening()
        self.button('View Player 1').invoke()
        self.assertIn('Pass to P1',self.text())
        self.assertFalse(any(isinstance(c,tk.Listbox) for c in children(self.root)))
        self.button('I am P1 - continue').invoke()
        self.assertTrue(any(isinstance(c,tk.Listbox) for c in children(self.root)))
        own_names=[c['name'] for c in self.session.view('P1')['you']['hand']]
        self.button('View Player 2').invoke()
        self.assertIn('Pass to P2',self.text())
        for name in own_names:self.assertNotIn(name,self.text())
        self.assertFalse(any(isinstance(c,tk.Listbox) for c in children(self.root)))

    def test_keep_all_button_uses_real_setup_transaction_then_renders_match(self):
        self.ready_opening()
        for actor in ('P1','P2'):
            self.app.seat(actor);self.app.unlock()
            self.button('Confirm selected replacements / Keep all if none').invoke()
        self.root.update_idletasks()
        self.assertIn('Turn 1',self.text())
        self.assertIsNotNone(self.session.view().get('turn'))
        self.assertEqual(len(self.session.view('P1')['you']['hand']),5)
        self.assertTrue(any(isinstance(c,tk.Canvas) for c in children(self.root)))
        self.button('Hide private hand / public view').invoke()
        self.assertFalse(any(isinstance(c,tk.Listbox) for c in children(self.root)))

    def test_rejected_action_keeps_engine_state_and_reports_error(self):
        self.ready_opening()
        for actor in ('P1','P2'):self.session.redraw(actor,(),expected_revision=self.session.view()['revision'])
        actor=next(p['player_id'] for p in self.session.view()['players'] if p['player_id']!=self.session.view()['priority']['holder'])
        self.app.seat(actor);self.app.unlock();before=self.session.view()
        self.assertFalse(self.app.send('pass'))
        self.assertEqual(before,self.session.view())
        self.assertEqual(self.app.notice.get(),'command unavailable')

    def test_readiness_and_deal_controls_work_through_visible_buttons(self):
        for actor in ('P1','P2'):
            self.app.seat(actor);self.app.unlock()
            self.button('Select Practice Forty + reserve identity').invoke()
            self.button('Ready').invoke()
        self.app.seat('P1');self.app.unlock()
        self.button('Deal opening hands').invoke()
        self.assertEqual(self.session.view()['phase'],'opening')

    def test_many_attack_choices_scroll_without_forcing_an_oversized_window(self):
        self.ready_opening()
        for actor in ('P1','P2'):self.session.redraw(actor,(),expected_revision=self.session.view()['revision'])
        actor=self.session.view()['turn']['active_player']
        self.app.seat(actor);self.app.unlock()
        view=self.session.view(actor)
        view['turn']['phase']='Combat';view['priority']={'holder':None,'status':'closed','passes':[]}
        view['battlefield']=[{'instance_id':f'fixture-{i}','definition_key':'unit-01','owner':actor,'controller':actor,
              'kind':'creature','cost':1,'capacity_bonus':0,'attack':2,'health':1,
              'creature':{'attack':2,'health':1,'max_health':1,'exhausted':False,'attack_eligible':True,'attack_used':False,'keywords':[],'shields':[]}} for i in range(30)]
        for child in self.app.body.winfo_children():child.destroy()
        self.app.render_match(view);self.root.update_idletasks()
        canvas=next(c for c in children(self.root) if isinstance(c,tk.Canvas))
        self.assertGreater(canvas.bbox('all')[3],canvas.winfo_reqheight())
        self.assertLess(self.root.winfo_reqheight(),1000)
        self.assertTrue(any(isinstance(c,ttk.Scrollbar) for c in children(self.root)))

    def test_card_text_explains_effects_without_internal_target_placeholders(self):
        self.ready_opening()
        for actor in ('P1','P2'):self.session.redraw(actor,(),expected_revision=self.session.view()['revision'])
        view=self.session.view('P1')
        self.assertEqual(self.app.effect_text({'kind':'damage','target':'$target','amount':3},view),'Deal 3 damage to the chosen target.')
        self.assertNotIn('$controller',self.app.effect_text({'kind':'draw','target':'$controller','amount':1},view))

    def test_card_confirmation_uses_projected_choice_and_commits_payment(self):
        from unittest.mock import patch
        self.ready_opening()
        for actor in ('P1','P2'):self.session.redraw(actor,(),expected_revision=self.session.view()['revision'])
        for _ in range(4):
            actor=self.session.view()['priority']['holder']
            self.app.seat(actor);self.app.unlock()
            self.button('Pass / continue phase').invoke()
        actor=self.session.view()['turn']['active_player']
        self.app.seat(actor);self.app.unlock()
        view=self.session.view(actor)
        self.assertEqual(view['turn']['phase'],'MainBefore')
        card=next(c for c in view['you']['hand'] if c['kind']=='creature' and c['cost']<=2)
        with patch.object(tk.Toplevel,'grab_set'):
            self.app.card_dialog(view,card)
        self.button('Confirm play and payment').invoke()
        after=self.session.view(actor)
        self.assertEqual(after['pending_cards'][0]['instance_id'],card['instance_id'])
        self.assertNotIn(card['instance_id'],[c['instance_id'] for c in after['you']['hand']])
        self.assertEqual(next(p['resources']['available'] for p in after['players'] if p['player_id']==actor),2-card['cost'])

    def test_computer_seat_is_not_a_viewable_human_hand(self):
        self.app.session=HarnessSession(seed=b'computer-widget-seed-1234',bots=('P2',))
        self.app.render()
        self.assertEqual(str(self.button('Computer P2').cget('state')),'disabled')
        self.app.seat('P2')
        self.assertIsNone(self.app.gate.actor);self.assertIsNone(self.app.gate.pending)
        self.assertIn('Computer hands stay private',self.app.notice.get())

    def test_bot_timer_readies_computer_but_stops_before_human_setup(self):
        self.app.session=HarnessSession(seed=b'computer-widget-seed-1234',bots=('P2',))
        self.app._schedule_bots()
        import time
        deadline=time.monotonic()+8
        def until_ready():
            ready=self.app.session.view()['players'][1]['ready']
            if ready or time.monotonic()>=deadline:self.root.quit()
            else:self.root.after(25,until_ready)
        self.root.after(25,until_ready);self.root.mainloop()
        roster=self.app.session.view()['players']
        self.assertFalse(roster[0]['ready']);self.assertTrue(roster[1]['ready'])
        self.assertIsNone(self.app.gate.actor)

    def test_summon_inspection_displays_current_price_and_both_ability_locations(self):
        from unittest.mock import patch
        self.ready_opening()
        for actor in ('P1','P2'):self.session.redraw(actor,(),expected_revision=self.session.view()['revision'])
        actor=self.session.view()['turn']['active_player'];self.app.seat(actor);self.app.unlock()
        with patch.object(tk.Toplevel,'grab_set'):
            self.button('Inspect / summon leader').invoke()
        popup=next(c for c in self.root.winfo_children() if isinstance(c,tk.Toplevel))
        labels=[str(c.cget('text')) for c in children(popup) if isinstance(c,ttk.Label)]
        leader=next(l for l in self.session.view(actor)['leaders'] if l['owner']==actor)
        self.assertTrue(any(label.startswith(f"{leader['name']} | leader | cost {leader['summon_cost']}") for label in labels))
        self.assertFalse(any('Guiding Bolt' in label for label in labels))
        self.assertEqual(next(c for c in children(popup) if isinstance(c,ttk.Spinbox)).get(),str(leader['summon_cost']))
        popup=next(c for c in self.root.winfo_children() if isinstance(c,tk.Toplevel));popup.destroy()

    def test_load_installs_paused_hides_hand_and_requires_explicit_resume(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from crucible_play.persistence import save_session
        candidate=HarnessSession(seed=b'loaded-widget-seed-1234',bots=('P2',))
        self.app.seat('P1');self.app.unlock()
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'game.crucible.json';save_session(candidate,path)
            with patch('crucible_play.desktop.filedialog.askopenfilename',return_value=str(path)),patch('crucible_play.desktop.messagebox.askyesno',return_value=True):
                self.app.load_game()
        self.assertIsNone(self.app.gate.actor);self.assertIsNone(self.app.gate.pending)
        self.assertTrue(self.app.session.paused);self.assertIsNone(self.app._bot_timer)
        self.assertEqual(self.app.session._lobby,candidate._lobby)
        self.button('Resume saved game').invoke()
        self.assertFalse(self.app.session.paused);self.assertIsNotNone(self.app._bot_timer)

    def test_invalid_load_and_cancelled_save_preserve_current_session(self):
        from unittest.mock import patch
        before=self.session._lobby
        with patch('crucible_play.desktop.filedialog.askopenfilename',return_value='missing.crucible.json'),patch('crucible_play.desktop.messagebox.askyesno') as confirm:
            self.app.load_game();confirm.assert_not_called()
        self.assertIs(self.app.session,self.session);self.assertEqual(self.session._lobby,before)
        self.assertFalse(self.session.paused)
        with patch('crucible_play.desktop.filedialog.asksaveasfilename',return_value=''):
            self.app.save_game()
        self.assertEqual(self.session._lobby,before);self.assertFalse(self.session.paused)

    def test_header_controls_fit_minimum_window_width(self):
        self.root.deiconify();self.root.geometry('950x700');self.root.update()
        for label in ('Save game...','Load game...','Resume saved game','Hide private hand / public view'):
            button=self.button(label)
            self.assertGreater(button.winfo_width(),20)
            self.assertLessEqual(button.winfo_rootx()+button.winfo_width(),self.root.winfo_rootx()+950)


if __name__=='__main__':unittest.main()
