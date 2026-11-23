import unittest,json,gzip,tempfile
from pathlib import Path
from dataclasses import replace
from crucible_core.cards import TriggeredAbility
from crucible_core.match import TriggerSpec,EffectSpec,DrawCards,GrantResources,DamagePlayer,validate_match,MatchError
from crucible_core.views import project_match
from crucible_play.persistence import save_session,load_session
from crucible_play.migrate import migrate_save
from crucible_play.opponent import choose_move
from test_commands_cards_views import command,pass_round
from test_draw_discard_triggers import watched
from test_zone_moves import resolve
from test_authored_triggers import CARD,ABILITY,source_fixture
from test_persistence import prepared,state,cmd,passes,register
from test_save_migration import legacy_lobby,sealed


def optional_fixture(draws=1):
    s=watched(steps=(DrawCards('A',draws),GrantResources('A',2)));source=s.battlefield[0]
    p=s.players[0];return replace(s,battlefield=(replace(source,triggers=(replace(source.triggers[0],optional=True),)),),
        players=(replace(p,cards=replace(p.cards,deck=('one','two','three','spare'))),)+s.players[1:])


def decide(s,use,actor='A'):
    choice=project_match(s,actor)['you']['choice']
    return command(s,actor,'trigger_choice',trigger_id=choice['trigger_id'],use=use)


class OptionalTriggerTests(unittest.TestCase):
    def test_use_and_skip_happen_after_atomic_effect_without_reversing_draw(self):
        for use in (False,True):
            s=resolve(optional_fixture(),'draw');self.assertEqual(s.players[0].resources.available,12)
            self.assertIn('one',s.players[0].cards.hand);self.assertFalse(s.priority.chain)
            self.assertEqual(project_match(s)['trigger_waiting'],'A')
            s=decide(s,use);self.assertFalse(s.triggers)
            if use:s=pass_round(s)
            self.assertEqual(s.players[0].resources.available,12+int(use))
            self.assertIn('one',s.players[0].cards.hand)

    def test_choices_finish_before_ordering_and_skipped_candidates_never_queue(self):
        s=resolve(optional_fixture(3),'draw');before=s
        with self.assertRaises(ValueError):command(s,'A','trigger_order',order=[t.trigger_id for t in s.triggers])
        s=decide(s,True);s=decide(s,False)
        self.assertFalse(s.priority.chain);self.assertEqual(len(s.triggers),3)
        s=decide(s,True);self.assertEqual(len(s.triggers),3)
        self.assertEqual(project_match(s,'A')['you']['choice']['kind'],'trigger_order')
        s=command(s,'A','trigger_order',order=[t['trigger_id'] for t in reversed(project_match(s,'A')['you']['choice']['triggers'])])
        s=pass_round(s);s=pass_round(s);self.assertEqual(s.players[0].resources.available,14)

    def test_wrong_actor_stale_id_nonboolean_and_repeated_choices_do_not_mutate(self):
        s=resolve(optional_fixture(),'draw');identity=s.triggers[0].trigger_id;before=s
        for actor,trigger,use in (('B',identity,True),('A',identity+1,True),('A',True,True),('A',identity,1)):
            with self.assertRaises(ValueError):command(s,actor,'trigger_choice',trigger_id=trigger,use=use)
            self.assertEqual(s,before)
        s=decide(s,False)
        with self.assertRaises(ValueError):command(s,'A','trigger_choice',trigger_id=identity,use=True)

    def test_private_decisions_do_not_change_public_or_other_seat_views_until_queueing(self):
        s=resolve(optional_fixture(2),'draw');yes=decide(s,True);no=decide(s,False)
        self.assertNotEqual(yes.triggers,no.triggers)
        for viewer in (None,'B','C'):self.assertEqual(project_match(yes,viewer),project_match(no,viewer))
        self.assertNotIn('decision',json.dumps(project_match(yes)))
        self.assertIsNone(project_match(yes,'B')['you']['choice'])

    def test_cross_controller_choices_follow_turn_order_before_mandatory_queueing(self):
        s=optional_fixture();b=replace(s.battlefield[0],object_id='b',owner='B',controller='B',triggers=(TriggerSpec('card_drawn','b-reward','any',True),))
        mandatory=replace(s.battlefield[0],object_id='c',owner='C',controller='C',triggers=(TriggerSpec('card_drawn','c-reward','any'),))
        s=replace(s,battlefield=s.battlefield+(b,mandatory),effects=s.effects+(EffectSpec('b-reward','B',(GrantResources('B',1),)),EffectSpec('c-reward','C',(GrantResources('C',1),))))
        s=resolve(s,'draw');self.assertEqual(project_match(s)['trigger_waiting'],'A');self.assertFalse(s.priority.chain)
        s=decide(s,False);self.assertEqual(project_match(s)['trigger_waiting'],'B')
        s=decide(s,True,'B');self.assertEqual([e.controller for e in s.priority.chain],['B','C'])
        s=pass_round(s);s=pass_round(s);self.assertEqual((s.players[1].resources.available,s.players[2].resources.available),(11,11))

    def test_no_decisions_or_ordering_while_required_draw_is_paused(self):
        s=optional_fixture(5);p=s.players[0];s=replace(s,players=(replace(p,cards=replace(p.cards,discard=('refill',))),)+s.players[1:])
        s=resolve(s,'draw');self.assertIsNotNone(s.pending.draw)
        self.assertIsNone(project_match(s)['trigger_waiting'])
        self.assertEqual(project_match(s,'A')['you']['choice']['kind'],'refill')
        self.assertIsNone(project_match(s,'B')['you']['choice'])
        with self.assertRaises(ValueError):command(s,'A','trigger_choice',trigger_id=s.triggers[0].trigger_id,use=True)
        with self.assertRaises(ValueError):command(s,'A','trigger_order',order=[t.trigger_id for t in s.triggers])

    def test_concession_cancels_eliminated_players_choices_and_moves_waiting_seat(self):
        s=optional_fixture();b=replace(s.battlefield[0],object_id='b',owner='B',controller='B',triggers=(TriggerSpec('card_drawn','b-reward','any',True),))
        s=replace(s,battlefield=s.battlefield+(b,),effects=s.effects+(EffectSpec('b-reward','B',(GrantResources('B',1),)),))
        s=resolve(s,'draw');s=command(s,'A','concede',confirmed=True)
        self.assertEqual(project_match(s)['trigger_waiting'],'B');self.assertEqual({t.controller for t in s.triggers},{'B'})
        s=decide(s,False,'B');self.assertFalse(s.triggers)

    def test_departure_after_capture_keeps_optional_choice_and_accepted_effect(self):
        s=resolve(optional_fixture(),'draw')
        from crucible_core.match import _depart
        s=_depart(s,{'observer'},'test-removal')
        s=decide(s,True);s=pass_round(s);self.assertEqual(s.players[0].resources.available,13)

    def test_policy_accepts_resource_reward_but_declines_registered_self_damage(self):
        for harmful in (False,True):
            s=optional_fixture()
            if harmful:s=replace(s,effects=(replace(s.effects[0],steps=(DamagePlayer('A',1),)),s.effects[1]))
            s=resolve(s,'draw');move=choose_move(project_match(s,'A'))
            self.assertEqual(move[0],'trigger_choice');self.assertEqual(move[1]['use'],not harmful)
            command(s,'A',move[0],**move[1])

    def test_v4_mandatory_authored_sources_convert_without_erasing_content_or_candidates(self):
        cases=json.loads(gzip.decompress((Path(__file__).parent/'fixtures'/'save_v4_before_optional.json.gz').read_bytes()))
        for case in cases:
            with tempfile.TemporaryDirectory() as directory:
                source=Path(directory)/'old.crucible.json';target=Path(directory)/'new.crucible.json';source.write_bytes(sealed(case['save']));before=source.read_bytes()
                migrate_save(source,target);s=load_session(target)
                self.assertEqual(s._lobby,legacy_lobby(case['save']['payload']['lobby']))
                self.assertEqual(json.loads(target.read_text())['content_hash'],case['save']['content_hash'])
                self.assertTrue(any(c.definition.triggered_abilities for c in s._lobby.pack.cards))
                self.assertFalse(any(a.optional for c in s._lobby.pack.cards for a in c.definition.triggered_abilities))
                s.resume();s.send(case['actor'],case['packet']);self.assertEqual(s._lobby,legacy_lobby(case['expected']))
                self.assertEqual(source.read_bytes(),before)

    def test_partial_private_decisions_roundtrip_paused_without_reasking_committed_choice(self):
        s=prepared();actor=s.view()['turn']['active_player'];m=s._lobby.match
        source=next(c for c in m.card_instances if c.owner==actor and c.definition_key=='beacon-01')
        state(s,turn=replace(m.turn,phase='MainBefore'),players=tuple(replace(p,cards=replace(p.cards,hand=(source.instance_id,),deck=tuple(i for i in p.cards.deck+p.cards.hand if i!=source.instance_id)),resources=replace(p.resources,available=4)) if p.cards.player_id==actor else p for p in m.players))
        cmd(s,actor,'play_card',card_id=source.instance_id,payment={'ordinary':4,'token_ids':[]});passes(s);register(s,'draw-two',actor,(DrawCards(actor,2),))
        first=s._lobby.match.triggers[0].trigger_id;cmd(s,actor,'trigger_choice',trigger_id=first,use=False)
        next_id=s.view(actor)['you']['choice']['trigger_id'];self.assertNotEqual(first,next_id)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'private.crucible.json';save_session(s,path);loaded=load_session(path)
        self.assertTrue(loaded.paused);self.assertEqual(s._lobby,loaded._lobby);self.assertIsNone(loaded.view().get('you'))
        loaded.resume()
        for game in (s,loaded):
            cmd(game,actor,'trigger_choice',trigger_id=next_id,use=True)
            cmd(game,actor,'trigger_order',order=[t['trigger_id'] for t in game.view(actor)['you']['choice']['triggers']]);passes(game)
        self.assertEqual(s._lobby,loaded._lobby)
        register(s,'draw-again',actor,(DrawCards(actor,2),))
        for _ in range(2):
            choice=s.view(actor)['you']['choice'];cmd(s,actor,'trigger_choice',trigger_id=choice['trigger_id'],use=False)
        self.assertEqual(s.view(actor)['you']['choice']['triggers'],[])
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'skipped.crucible.json';save_session(s,path);loaded=load_session(path)
        loaded.resume()
        for game in (s,loaded):cmd(game,actor,'trigger_order',order=[])
        self.assertEqual(s._lobby,loaded._lobby);self.assertFalse(s._lobby.match.triggers)

    def test_invalid_decision_flags_or_premature_order_confirmation_reject(self):
        s=resolve(optional_fixture(),'draw');candidate=s.triggers[0]
        for t in (replace(candidate,optional=1),replace(candidate,optional=False,decision=True),replace(candidate,decision='yes'),replace(candidate,decision=False)):
            with self.assertRaises(MatchError):validate_match(replace(s,triggers=(t,)))
        with self.assertRaises(MatchError):validate_match(replace(s,trigger_orders=(('A',(candidate.trigger_id,)),)))

    def test_skipping_end_discard_trigger_does_not_open_an_extra_response_window(self):
        s=watched(event='card_discarded');source=s.battlefield[0];p=s.players[0]
        s=replace(s,battlefield=(replace(source,triggers=(replace(source.triggers[0],optional=True),)),),
            players=(replace(p,cards=replace(p.cards,hand=tuple('h'+str(i) for i in range(8)))),)+s.players[1:])
        s=pass_round(command(s,'A','end_turn'));s=command(s,'A','end_discard',cards=['h0'])
        self.assertEqual(s.turn.phase,'End');s=decide(s,False)
        self.assertNotEqual(s.turn.active_player,'A');self.assertEqual(s.players[0].resources.available,10)

    def test_optional_choices_rotate_from_each_active_seat(self):
        from crucible_core.match import new_match,MatchObject,MatchPlayer
        from crucible_core.turns import DrawPlayer,RefillPolicy
        for active in 'ABC':
            players=tuple(MatchPlayer(DrawPlayer(p,30,(p+'1',p+'2'),())) for p in 'ABC')
            effects=tuple(EffectSpec(p+'-reward',p,(GrantResources(p,1),)) for p in 'ABC')+(EffectSpec('draw',active,(DrawCards(active,1),)),)
            objects=tuple(MatchObject(p+'-source',p,p,'permanent',triggers=(TriggerSpec('card_drawn',p+'-reward','any',True),)) for p in 'ABC')
            s=new_match(players,objects,effects,RefillPolicy(20,1),active_player=active)
            s=resolve(s,'draw',active);index='ABC'.index(active);order='ABC'[index:]+'ABC'[:index]
            for actor in order:
                self.assertEqual(project_match(s)['trigger_waiting'],actor);s=decide(s,True,actor)
            self.assertEqual([e.controller for e in s.priority.chain],list(order))

    def test_v4_premature_optional_or_decision_fields_never_overwrite_or_publish(self):
        path=Path(__file__).parent/'fixtures'/'save_v4_before_optional.json.gz'
        for record,field,value in (('TriggeredAbility','optional',False),('TriggerSpec','optional',False),('TriggerCandidate','decision',None)):
            doc=json.loads(gzip.decompress(path.read_bytes()))[0]['save']
            def find(item):
                if isinstance(item,dict):
                    if item.get('record')==record:return item['fields']
                    for child in item.values():
                        result=find(child)
                        if result is not None:return result
                elif isinstance(item,list):
                    for child in item:
                        result=find(child)
                        if result is not None:return result
            fields=find(doc['payload']);self.assertIsNotNone(fields);fields[field]=value
            with tempfile.TemporaryDirectory() as directory:
                source=Path(directory)/'old.crucible.json';output=Path(directory)/'new.crucible.json';source.write_bytes(sealed(doc));before=source.read_bytes()
                with self.assertRaises(ValueError):migrate_save(source,output)
                self.assertEqual(source.read_bytes(),before);self.assertFalse(output.exists())

    def test_completed_choices_keep_ordering_barrier_private_even_when_all_skipped(self):
        s=resolve(optional_fixture(2),'draw')
        yes=decide(decide(s,True),True);no=decide(decide(s,False),False)
        for viewer in (None,'B','C'):self.assertEqual(project_match(yes,viewer),project_match(no,viewer))
        self.assertEqual(project_match(no,'A')['you']['choice']['triggers'],[])
        no=command(no,'A','trigger_order',order=[]);self.assertFalse(no.triggers);self.assertFalse(no.priority.chain)
