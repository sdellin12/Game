import unittest,tempfile,gzip,json
from dataclasses import replace
from pathlib import Path
from crucible_core.cards import CardDefinition,TriggeredAbility
from crucible_core.match import GrantResources,DrawCards,EffectSpec,ReturnCreatureToHand,NegateEffect,validate_match,MatchError
from crucible_core.views import project_match
from crucible_play.persistence import save_session,load_session
from crucible_play.migrate import migrate_save
from test_commands_cards_views import fixture,instances,play,pass_round,command
from test_zone_moves import resolve
from test_persistence import prepared,state,cmd,passes,register
from test_save_migration import legacy_lobby,sealed

ABILITY=TriggeredAbility('insight','card_drawn',(GrantResources('$controller',1),))
CARD=CardDefinition('lantern','permanent',4,capacity_bonus=1,triggered_abilities=(ABILITY,))


def source_fixture(card=CARD):
    return fixture((card,),instances(('source',card.key,'A')),ah=('source',),ad=('one','two','three'),
        effects=(EffectSpec('draw','A',(DrawCards('A',1),)),))


class AuthoredTriggerTests(unittest.TestCase):
    def test_authored_rewards_bind_each_active_controller_without_cross_player_grants(self):
        from crucible_core.match import new_match,MatchPlayer
        from crucible_core.turns import DrawPlayer,RefillPolicy
        from crucible_core.resources import ResourcePool
        for actor in 'ABC':
            players=tuple(MatchPlayer(DrawPlayer(p,30,(p+'-one',p+'-two'),(),('source',) if p==actor else ()),resources=ResourcePool(available=10)) for p in 'ABC')
            s=new_match(players,(),(EffectSpec('draw',actor,(DrawCards(actor,1),)),),RefillPolicy(20,1),active_player=actor,
                card_definitions=(CARD,),card_instances=instances(('source','lantern',actor)))
            s=pass_round(play(s,actor,'source',4));s=resolve(s,'draw',actor);s=pass_round(s)
            self.assertEqual({p.cards.player_id:p.resources.available for p in s.players},{p:7 if p==actor else 10 for p in 'ABC'})

    def test_paid_pending_source_registers_only_on_resolution_then_triggers_from_own_draw(self):
        s=source_fixture();s=play(s,'A','source',4)
        self.assertFalse(s.battlefield);self.assertFalse(any(e.source_id=='source' for e in s.effects))
        s=pass_round(s);validate_match(s);self.assertEqual(len(s.battlefield[0].triggers),1)
        self.assertEqual(len([e for e in s.effects if e.source_id=='source']),1)
        s=resolve(s,'draw');self.assertEqual(project_match(s)['chain'][0]['label'],'Draw trigger')
        s=pass_round(s);self.assertEqual(s.players[0].resources.available,7)
        self.assertEqual(project_match(s)['battlefield'][0]['triggered_abilities'][0]['event'],'card_drawn')

    def test_negated_permanent_does_not_install_abilities(self):
        s=source_fixture();s=play(s,'A','source',4);identity=s.priority.chain[-1].effect_id
        s=replace(s,effects=s.effects+(EffectSpec('counter','B',(NegateEffect(identity),)),))
        s=resolve(s,'counter','B');self.assertFalse(s.battlefield)
        self.assertFalse(any(e.source_id=='source' for e in s.effects));self.assertIn('source',s.players[0].cards.discard)

    def test_discard_permanent_rewards_only_actual_own_hand_discard(self):
        card=replace(CARD,triggered_abilities=(replace(ABILITY,event='card_discarded'),))
        s=pass_round(play(source_fixture(card),'A','source',4));p=s.players[0]
        s=replace(s,players=(replace(p,cards=replace(p.cards,hand=tuple('h'+str(i) for i in range(8)))),)+s.players[1:])
        s=pass_round(command(s,'A','end_turn'));s=command(s,'A','end_discard',cards=['h0']);s=pass_round(s)
        self.assertEqual(s.players[0].resources.available,7)

    def test_departed_source_captured_trigger_still_resolves_and_registry_is_retained(self):
        s=pass_round(play(source_fixture(),'A','source',4));s=resolve(s,'draw')
        from crucible_core.match import _depart
        s=_depart(s,{'source'},'test-removal')
        s=pass_round(s);self.assertFalse(s.battlefield);self.assertEqual(s.players[0].resources.available,7)
        self.assertEqual(len([e for e in s.effects if e.source_id=='source']),1)

    def test_reentry_reuses_registration_without_duplicate_effects(self):
        s=pass_round(play(source_fixture(),'A','source',4))
        from crucible_core.match import _depart
        s=_depart(s,{'source'},'test-bounce',hand_ids=('source',))
        s=pass_round(play(s,'A','source',4));validate_match(s)
        self.assertEqual(len([e for e in s.effects if e.source_id=='source']),1)
        s=resolve(s,'draw');s=pass_round(s);self.assertEqual(s.players[0].resources.available,3)

    def test_invalid_kind_event_watch_reward_or_duplicate_key_rejects(self):
        invalid=(replace(CARD,kind='creature',health=1),replace(CARD,triggered_abilities=[ABILITY]),
            replace(CARD,triggered_abilities=(replace(ABILITY,watch='any'),)),
            replace(CARD,triggered_abilities=(replace(ABILITY,event='departure'),)),
            replace(CARD,triggered_abilities=(replace(ABILITY,steps=(DrawCards('$controller',1),)),)),
            replace(CARD,triggered_abilities=(replace(ABILITY,steps=(GrantResources('$target',1),)),)),
            replace(CARD,triggered_abilities=(ABILITY,ABILITY)))
        for card in invalid:
            with self.subTest(card=card):
                with self.assertRaises(MatchError):source_fixture(card)

    def test_inconsistent_or_missing_registration_rejects_before_payment_or_load(self):
        from crucible_core.match import _trigger_key
        s=source_fixture();s=replace(s,effects=s.effects+(EffectSpec(_trigger_key('source','insight'),'A',(GrantResources('A',9),),'source'),))
        before=s
        with self.assertRaises(ValueError):play(s,'A','source',4)
        self.assertEqual(s,before)
        pending=play(source_fixture(),'A','source',4)
        pending=replace(pending,effects=pending.effects+(EffectSpec(_trigger_key('source','insight'),'A',(GrantResources('A',9),),'source'),))
        with self.assertRaises(MatchError):validate_match(pending)
        s=pass_round(play(source_fixture(),'A','source',4));obj=s.battlefield[0]
        with self.assertRaises(MatchError):validate_match(replace(s,battlefield=(replace(obj,triggers=()),)))

    def test_schema_v3_observer_fixture_converts_with_same_hash_and_next_result(self):
        path=Path(__file__).parent/'fixtures'/'save_v3_before_authored_triggers.json.gz'
        for case in json.loads(gzip.decompress(path.read_bytes())):
            with tempfile.TemporaryDirectory() as directory:
                source=Path(directory)/'old.crucible.json';target=Path(directory)/'new.crucible.json';source.write_bytes(sealed(case['save']));before=source.read_bytes()
                with self.assertRaises(ValueError):load_session(source)
                migrate_save(source,target);s=load_session(target);self.assertEqual(s._lobby,legacy_lobby(case['save']['payload']['lobby']))
                self.assertEqual(json.loads(target.read_text())['content_hash'],case['save']['content_hash'])
                self.assertTrue(all(not c.definition.triggered_abilities for c in s._lobby.pack.cards))
                s.resume();s.send(case['actor'],case['packet']);self.assertEqual(s._lobby,legacy_lobby(case['expected']))
                self.assertEqual(source.read_bytes(),before)

    def test_pending_practice_permanent_and_trigger_order_roundtrip(self):
        s=prepared();actor=s.view()['turn']['active_player'];m=s._lobby.match
        source=next(c for c in m.card_instances if c.owner==actor and c.definition_key=='beacon-01')
        state(s,turn=replace(m.turn,phase='MainBefore'),players=tuple(replace(p,cards=replace(p.cards,hand=(source.instance_id,),deck=tuple(i for i in p.cards.deck+p.cards.hand if i!=source.instance_id)),resources=replace(p.resources,available=4)) if p.cards.player_id==actor else p for p in m.players))
        cmd(s,actor,'play_card',card_id=source.instance_id,payment={'ordinary':4,'token_ids':[]})
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'pending.crucible.json';save_session(s,path);loaded=load_session(path);loaded.resume()
            passes(s);passes(loaded);self.assertEqual(s._lobby,loaded._lobby)
            for game in (s,loaded):register(game,'draw-two',actor,(DrawCards(actor,2),))
            self.assertEqual(len(s._lobby.match.triggers),2)
            save_session(s,path);resumed=load_session(path);self.assertEqual(s._lobby,resumed._lobby)
            self.assertEqual(s._lobby,loaded._lobby)

    def test_v3_premature_new_field_or_record_and_hash_corruption_never_publish(self):
        path=Path(__file__).parent/'fixtures'/'save_v3_before_authored_triggers.json.gz'
        edits=(lambda d:d['payload']['lobby']['fields']['pack']['fields']['cards']['tuple'][0]['fields']['definition']['fields'].update(triggered_abilities={'tuple':[]}),
               lambda d:d['payload']['lobby'].update(record='TriggeredAbility'),lambda d:d.update(content_hash='0'*64))
        for edit in edits:
            doc=json.loads(gzip.decompress(path.read_bytes()))[0]['save'];edit(doc)
            with tempfile.TemporaryDirectory() as directory:
                source=Path(directory)/'old.crucible.json';output=Path(directory)/'new.crucible.json';source.write_bytes(sealed(doc));before=source.read_bytes()
                with self.assertRaises(ValueError):migrate_save(source,output)
                self.assertFalse(output.exists());self.assertEqual(source.read_bytes(),before)
