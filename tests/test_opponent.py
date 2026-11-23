import json
import unittest
from dataclasses import replace
from unittest.mock import patch
from crucible_play.opponent import choose_move,opening_choice,exact_payment
from crucible_play.session import HarnessSession
from crucible_play.smoke import choose_move as scripted_human

SEED=b'test-practice-opponent-seed-1234'


def prepared(bots=('P2',),size=2):
    s=HarnessSession(tuple(f'Player {i+1}' for i in range(size)),seed=SEED,bots=bots)
    for p in s.view()['players']:
        actor=p['player_id']
        s.choose_deck(actor,'core-gold',expected_revision=s.view()['revision'])
        s.ready(actor,True,expected_revision=s.view()['revision'])
    s.start('P1',expected_revision=s.view()['revision'])
    for p in s.view()['players']:s.redraw(p['player_id'],(),expected_revision=s.view()['revision'])
    return s


class OpponentTests(unittest.TestCase):
    def test_computer_setup_never_readies_or_redraws_for_human(self):
        s=HarnessSession(seed=SEED,bots=('P2',))
        for _ in range(5):
            if not s.step_opponent():break
        public=s.view()
        self.assertFalse(public['players'][0]['ready']);self.assertTrue(public['players'][1]['ready'])
        self.assertIsNone(public['players'][0]['deck_name'])
        s.choose_deck('P1','core-green',expected_revision=public['revision']);s.ready('P1',True,expected_revision=s.view()['revision'])
        s.start('P1',expected_revision=s.view()['revision'])
        hand=s.view('P1')['you']['hand']
        self.assertTrue(s.step_opponent());self.assertFalse(s.step_opponent())
        self.assertEqual(s.view()['phase'],'opening');self.assertIsNone(s.view()['redraw_counts'])
        self.assertFalse(s.view('P1')['you']['locked']);self.assertEqual(hand,s.view('P1')['you']['hand'])

    def test_scheduler_stops_at_human_priority_without_mutation(self):
        s=prepared()
        for _ in range(10):
            before=s.view()
            if not s.step_opponent():break
        self.assertEqual(s.view()['priority']['holder'],'P1')
        before=s.view()
        self.assertFalse(s.step_opponent());self.assertEqual(before,s.view())

    def test_policy_receives_own_projection_without_opponent_hand_or_server_fields(self):
        s=prepared()
        while s.view()['priority']['holder']!='P2':
            v=s.view('P1');s.send('P1',{'kind':'pass','args':{},'expected_revision':v['revision']})
        secrets=[c['instance_id'] for c in s.view('P1')['you']['hand']]
        captured=[]
        def spy(view):
            self.assertIs(type(view),dict)
            text=json.dumps(view)
            for secret in secrets:self.assertNotIn(secret,text)
            for field in ('shuffle_seed','draw_records','card_instances','card_definitions'):self.assertNotIn(field,view)
            self.assertEqual(view['you']['player_id'],'P2');captured.append(view)
            return choose_move(view)
        with patch('crucible_play.opponent.choose_move',side_effect=spy):self.assertTrue(s.step_opponent())
        self.assertTrue(captured)

    def test_other_hidden_hand_and_deck_changes_do_not_change_policy(self):
        from crucible_core.views import project_match
        s=prepared();state=s._lobby.match
        p=next(p for p in state.players if p.cards.player_id=='P1')
        changed=replace(state,players=tuple(replace(q,cards=replace(q.cards,hand=tuple(reversed(q.cards.hand)),deck=tuple(reversed(q.cards.deck)))) if q==p else q for q in state.players))
        self.assertEqual(project_match(state,'P2'),project_match(changed,'P2'))
        self.assertEqual(choose_move(project_match(state,'P2')),choose_move(project_match(changed,'P2')))

    def test_required_other_player_choice_prevents_spurious_pass(self):
        s=prepared();view=s.view('P2')
        view['choice_pending']=True;view['you']['choice']=None
        view['priority']={'holder':'P2','status':'priority','passes':[]}
        self.assertIsNone(choose_move(view))

    def test_policy_constructs_exact_owned_token_payment(self):
        s=prepared();view=s.view('P2')
        me=next(p for p in view['players'] if p['player_id']=='P2');me['resources']['available']=1
        view['battlefield']=[{'kind':'resource_token','instance_id':'own','controller':'P2','resource_value':2},
                             {'kind':'resource_token','instance_id':'foreign','controller':'P1','resource_value':10}]
        self.assertEqual(exact_payment(view,3),{'ordinary':1,'token_ids':['own']})
        self.assertIsNone(exact_payment(view,4))

    def test_blocking_uses_only_own_creatures_and_never_a_challenge_target(self):
        s=prepared();view=s.view('P2')
        view['you']['choice']={'kind':'blockers','locked':False}
        view['combat']={'attacks':[('a','P2',None),('b','P2',None),('challenge','P2','challenged')]}
        view['battlefield']=[{'instance_id':'blocker','controller':'P2','kind':'creature','creature':{'health':5}},
                             {'instance_id':'challenged','controller':'P2','kind':'creature','creature':{'health':9}},
                             {'instance_id':'enemy','controller':'P1','kind':'creature','creature':{'health':20}}]
        kind,args=choose_move(view)
        self.assertEqual(kind,'lock_blockers')
        used=[b for item in args['assignments'] for b in item['blockers']]
        self.assertEqual(used,['blocker'])
        self.assertEqual(len(args['assignments']),2)
        view['you']['choice']['locked']=True;self.assertIsNone(choose_move(view))

    def test_opening_policy_uses_only_own_costs_and_locks_once(self):
        view={'phase':'opening','you':{'locked':False,'hand':[{'instance_id':'cheap','cost':1},{'instance_id':'expensive','cost':5}]}}
        self.assertEqual(opening_choice(view),['expensive'])
        view['you']['locked']=True;self.assertIsNone(opening_choice(view))

    def test_practice_game_uses_both_clients_and_reaches_a_real_terminal_result(self):
        s=prepared();bot_actions=human_actions=0
        for _ in range(1800):
            public=s.view()
            if public['result']:break
            if s.step_opponent():bot_actions+=1;continue
            view=s.view('P1');move=scripted_human(view)
            self.assertIsNotNone(move)
            kind,args=move;s.send('P1',{'kind':kind,'args':args,'expected_revision':view['revision']});human_actions+=1
        else:self.fail('Practice policy reached the diagnostic limit')
        self.assertEqual(s.view()['result']['kind'],'win')
        self.assertGreater(bot_actions,0);self.assertGreater(human_actions,0)
        self.assertTrue(any(e['kind']=='leader_summoned' for e in s.view()['events']))

    def test_unknown_bot_seat_rejects(self):
        with self.assertRaises(ValueError):HarnessSession(bots=('P9',))

    def test_minor_wounds_do_not_trigger_repetitive_healing_but_low_life_does(self):
        view=prepared().view('P2');view['leaders']=[];view['choice_pending']=False
        view['turn'].update(active_player='P2',phase='MainBefore',end_requested=False)
        view['priority']={'holder':'P2','status':'priority','passes':[]}
        own=next(p for p in view['players'] if p['player_id']=='P2');own['resources']['available']=5;own['health']=29
        view['you']['hand']=[{'instance_id':'heal','kind':'action','cost':1,'target_kind':None,'steps':[{'kind':'heal','target':'$controller','amount':3}]}]
        self.assertEqual(choose_move(view),('pass',{}))
        own['health']=7;self.assertEqual(choose_move(view)[0],'play_card')

    def test_exhaust_ability_does_not_spend_an_attack_before_combat(self):
        view=prepared().view('P2');view['choice_pending']=False
        view['turn'].update(active_player='P2',phase='MainBefore',end_requested=False)
        view['priority']={'holder':'P2','status':'priority','passes':[]};view['you']['hand']=[]
        own=next(p for p in view['players'] if p['player_id']=='P2');own['resources']['available']=5
        ability={'key':'bolt','available':True,'timing':'main','cost':2,'exhaust_source':True,'target_kind':'player','target_relation':'enemy',
                 'steps':[{'kind':'damage','target':'$target','amount':1}]}
        view['leaders']=[{'owner':'P2','location':'battlefield','abilities':[ability]}]
        self.assertEqual(choose_move(view),('pass',{}))
        view['turn']['phase']='MainAfter';self.assertEqual(choose_move(view)[0],'leader_ability')

    def test_three_seat_stress_regression_finishes_under_command_cap(self):
        from crucible_play.smoke import run_smoke
        result=run_smoke(3,'smoke-1',limit=1500,practice=True)
        self.assertEqual(result['status'],'completed')
        self.assertLess(result['commands'],1500)


if __name__=='__main__':unittest.main()
