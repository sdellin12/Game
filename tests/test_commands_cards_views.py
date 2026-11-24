import json
import unittest
from dataclasses import replace
from crucible_core.match import *
from crucible_core.turns import DrawPlayer, RefillPolicy
from crucible_core.resources import ResourcePool, Payment
from crucible_core.commands import route_command, CommandError
from crucible_core.views import project_match


def fixture(definitions=(), instances=(), ah=(), bh=(), ad=(), bd=(), ag=(), effects=(), objects=(), actions=(), **kw):
    players=(MatchPlayer(DrawPlayer('A',30,ad,ag,ah),resources=ResourcePool(available=10)),
             MatchPlayer(DrawPlayer('B',30,bd,(),bh),resources=ResourcePool(available=10)),
             MatchPlayer(DrawPlayer('C',30,('c-deck',),()),resources=ResourcePool(available=10)))
    return new_match(players,objects,effects,RefillPolicy(20,1),active_player='A',
        card_definitions=definitions,card_instances=instances,shuffle_seed=b'server-only-seed-value',actions=actions,**kw)


def command(s, actor, kind, **args):
    return route_command(s,actor,{'kind':kind,'expected_revision':s.revision,'args':args})


def pass_round(s):
    for _ in range(len(s.priority.seats)):
        s=command(s,s.priority.holder,'pass')
    return s


def play(s, actor, card, ordinary=0, **kw):
    return command(s,actor,'play_card',card_id=card,payment={'ordinary':ordinary,'token_ids':[]},**kw)


def instances(*pairs):
    return tuple(CardInstance(i,d,owner) for i,d,owner in pairs)


class ViewTests(unittest.TestCase):
    def test_public_and_opponent_views_omit_private_zones_registry_seed_and_replay(self):
        s=fixture(ah=('A-SECRET-HAND',),bh=('B-SECRET-HAND',),ad=('A-SECRET-TOP',),bd=('B-SECRET-TOP',))
        public=json.dumps(project_match(s))
        for hidden in ('SECRET','shuffle_seed','draw_records','card_instances','card_definitions','effects','pending'):
            if hidden=='pending':continue  # public pending_cards is intentional
            self.assertNotIn(hidden,public)
        a=json.dumps(project_match(s,'A'))
        self.assertIn('A-SECRET-HAND',a)
        self.assertNotIn('B-SECRET-HAND',a)
        self.assertNotIn('SECRET-TOP',a)

    def test_hidden_state_permutations_have_identical_public_and_other_player_views(self):
        s=fixture(ah=('hidden-one','hidden-two'),bh=('b-hand',),ad=('top-one','top-two'),bd=('b-top',))
        a=s.players[0]
        changed=replace(s,players=(replace(a,cards=replace(a.cards,hand=tuple(reversed(a.cards.hand)),deck=tuple(reversed(a.cards.deck)))),)+s.players[1:],
                        shuffle_seed=b'different-secret-seed',shuffle_counter=900)
        self.assertEqual(project_match(s),project_match(changed))
        self.assertEqual(project_match(s,'B'),project_match(changed,'B'))
        self.assertNotEqual(project_match(s,'A'),project_match(changed,'A'))

    def test_raw_unknown_events_and_causes_are_not_serialized(self):
        s=fixture()
        s=replace(s,events=(MatchEvent(1,'private_replay','SECRET-CARD','SECRET-ORDER'),MatchEvent(2,'required_draw','A','SECRET-CAUSE')))
        value=json.dumps(project_match(s))
        self.assertNotIn('SECRET',value)
        self.assertEqual(project_match(s)['events'],[{'event_id':2,'kind':'required_draw','subject':'A'}])

    def test_projection_is_detached_and_json_serializable(self):
        s=fixture(ah=('own',),objects=(MatchObject('unit','A','A','creature',Creature('unit','A',2,3,3)),))
        view=json.loads(json.dumps(project_match(s,'A')))
        view['you']['hand'].clear();view['battlefield'][0]['creature']['health']=999
        self.assertEqual(s.players[0].cards.hand,('own',))
        self.assertEqual(s.battlefield[0].creature.health,3)

    def test_eliminated_player_session_gets_public_view_and_no_command_authority(self):
        s=fixture(ah=('secret',))
        s=command(s,'A','concede',confirmed=True)
        self.assertNotIn('you',project_match(s,'A'))
        self.assertNotIn('secret',json.dumps(project_match(s,'A')))
        with self.assertRaises(CommandError):command(s,'A','pass')
        with self.assertRaises(MatchError):project_match(s,'unknown')

    def test_only_refill_owner_sees_request_and_server_shuffle_is_not_leaked(self):
        s=fixture(ag=('g1','g2'),effects=(EffectSpec('draw','A',(DrawCards('A',1),)),))
        s=queue_effect(s,'A','draw',expected_revision=s.revision)
        s=pass_round(s)
        self.assertEqual(project_match(s,'A')['you']['choice']['kind'],'refill')
        self.assertIsNone(project_match(s,'B')['you']['choice'])
        value=json.dumps(project_match(s))
        self.assertNotIn('request_id',value)
        self.assertNotIn('server-only',value)


class CommandTests(unittest.TestCase):
    def test_identity_spoof_internal_commands_bad_shapes_and_stale_replays_reject(self):
        s=fixture()
        for packet in ({'kind':'pass','expected_revision':0,'args':{},'actor':'A'},
                       {'kind':'queue_effect','expected_revision':0,'args':{'key':'free'}},
                       {'kind':'resolve_current','expected_revision':0,'args':{}},
                       {'kind':'pass','expected_revision':True,'args':{}},
                       {'kind':'pass','expected_revision':0,'args':{'actor':'A'}},
                       {'kind':'pass','expected_revision':0,'args':[]}):
            with self.assertRaises(CommandError):route_command(s,'B',packet)
        with self.assertRaises(CommandError):command(s,None,'pass')
        after=command(s,'A','pass')
        with self.assertRaises(CommandError):route_command(after,'B',{'kind':'pass','expected_revision':0,'args':{}})
        self.assertEqual(s.revision,0)

    def test_all_passes_resolve_only_newest_item_without_client_resolve_command(self):
        s=fixture(effects=(EffectSpec('one','A',(DamagePlayer('B',1),)),EffectSpec('two','B',(DamagePlayer('A',2),))))
        s=queue_effect(s,'A','one',expected_revision=s.revision)
        s=queue_effect(s,'B','two',expected_revision=s.revision)
        s=pass_round(s)
        self.assertEqual(s.players[0].cards.health,28)
        self.assertEqual(s.players[1].cards.health,30)
        self.assertEqual(len(s.priority.chain),1)

    def test_client_cannot_choose_shuffle_and_valid_commands_are_replayable(self):
        s=fixture(ag=('g1','g2','g3'),effects=(EffectSpec('draw','A',(DrawCards('A',1),)),))
        s=pass_round(queue_effect(s,'A','draw',expected_revision=s.revision))
        req=s.pending.draw.request_id
        with self.assertRaises(CommandError):command(s,'A','refill',pay=True,request_id=req,shuffled_discard=['g1','g2','g3'])
        with self.assertRaises(CommandError):command(s,'B','refill',pay=True,request_id=req)
        first=command(s,'A','refill',pay=True,request_id=req)
        self.assertEqual(first,command(s,'A','refill',pay=True,request_id=req))
        self.assertEqual((s.shuffle_counter,first.shuffle_counter),(0,1))
        self.assertEqual(first.players[0].cards.health,10)
        self.assertNotIn('g1',json.dumps(project_match(first)))

    def test_concede_requires_confirmation(self):
        s=fixture()
        with self.assertRaises(CommandError):command(s,'A','concede',confirmed=False)
        self.assertTrue(command(s,'A','concede',confirmed=True).players[0].eliminated)


class HandCardTests(unittest.TestCase):
    def test_action_leaves_hand_pays_before_responses_and_discards_after_resolution(self):
        defs=(CardDefinition('hit','action',2,(DamagePlayer('$target',3),),target_kind='player',target_relation='enemy'),)
        s=fixture(defs,instances(('a-card','hit','A')),ah=('a-card',),ad=('a-top',))
        self.assertNotIn('hit',json.dumps(project_match(s)))
        self.assertEqual(project_match(s,'A')['you']['hand'][0]['definition_key'],'hit')
        s=play(s,'A','a-card',2,target='B')
        self.assertFalse(s.players[0].cards.hand)
        self.assertFalse(s.players[0].cards.discard)
        self.assertEqual(s.players[0].resources.available,8)
        self.assertEqual(s.players[1].cards.health,30)
        self.assertEqual(project_match(s)['pending_cards'][0]['definition_key'],'hit')
        self.assertEqual(project_match(s)['chain'][0]['steps'][0]['target'],'B')
        s=pass_round(s)
        self.assertEqual(s.players[1].cards.health,27)
        self.assertEqual(s.players[0].cards.discard,('a-card',))
        self.assertFalse(s.pending_cards)
        validate_match(s)

    def test_creature_enters_only_after_resolution_ready_full_health_but_attack_wait(self):
        d=CardDefinition('unit','creature',1,attack=2,health=4)
        s=fixture((d,),instances(('a-unit','unit','A')),ah=('a-unit',))
        s=play(s,'A','a-unit',1)
        self.assertFalse(s.battlefield)
        s=pass_round(s)
        c=s.battlefield[0].creature
        self.assertEqual((c.health,c.max_health,c.exhausted,c.attack_eligible,c.attack_used),(4,4,False,False,False))
        self.assertFalse(s.players[0].cards.discard)
        validate_match(s)

    def test_reaction_negates_pending_creature_both_cards_discard_without_refund(self):
        defs=(CardDefinition('unit','creature',3,attack=2,health=3),
              CardDefinition('deny','reaction',2,(NegateEffect('$target'),),target_kind='effect',target_relation='enemy'))
        s=fixture(defs,instances(('unit-a','unit','A'),('deny-b','deny','B')),ah=('unit-a',),bh=('deny-b',))
        s=play(s,'A','unit-a',3)
        s=play(s,'B','deny-b',2,target=str(s.priority.chain[0].effect_id))
        s=pass_round(s)
        self.assertFalse(s.pending_cards)
        self.assertFalse(s.battlefield)
        self.assertEqual(s.players[0].cards.discard,('unit-a',))
        self.assertEqual(s.players[1].cards.discard,('deny-b',))
        self.assertEqual((s.players[0].resources.available,s.players[1].resources.available),(7,8))
        validate_match(s)

    def test_invalid_hand_owner_timing_targets_and_payment_do_not_move_cards(self):
        d=CardDefinition('hit','action',2,(DamagePlayer('$target',3),),target_kind='player',target_relation='enemy')
        s=fixture((d,),instances(('a-card','hit','A')),ah=('a-card',))
        for actor,card,cost,target in (('B','a-card',2,'A'),('A','invented',2,'B'),('A','a-card',1,'B'),('A','a-card',2,'A'),('A','a-card',2,'not-a-player')):
            with self.assertRaises(CommandError):play(s,actor,card,cost,target=target)
        self.assertEqual(s.players[0].cards.hand,('a-card',))
        self.assertEqual(s.players[0].resources.available,10)
        self.assertFalse(s.pending_cards)

    def test_permanent_capacity_changes_only_when_resolved_and_next_refill(self):
        s=fixture((CardDefinition('beacon','permanent',2,capacity_bonus=4),),instances(('p','beacon','A')),ah=('p',))
        s=play(s,'A','p',2)
        self.assertFalse(s.battlefield)
        s=pass_round(s)
        self.assertEqual(s.battlefield[0].capacity_bonus,4)
        self.assertEqual(s.players[0].resources.available,8)

    def test_pending_draw_card_is_not_available_to_its_own_refill(self):
        d=CardDefinition('draw','action',0,(DrawCards('$controller',1),))
        s=fixture((d,),instances(('draw-a','draw','A')),ah=('draw-a',),ag=('g1','g2'))
        s=pass_round(play(s,'A','draw-a'))
        self.assertEqual(s.pending.draw.player.discard,('g1','g2'))
        self.assertEqual(s.pending_cards[0].card_id,'draw-a')
        s=command(s,'A','refill',pay=True,request_id=s.pending.draw.request_id)
        self.assertEqual(s.players[0].cards.discard,('draw-a',))
        self.assertEqual(set(s.players[0].cards.deck+s.players[0].cards.hand),{'g1','g2'})
        self.assertFalse(s.pending_cards)
        validate_match(s)

    def test_elimination_cancels_pending_hand_card_and_keeps_paid_cost(self):
        d=CardDefinition('unit','creature',3,attack=2,health=3)
        s=fixture((d,),instances(('unit-a','unit','A')),ah=('unit-a',),effects=(EffectSpec('kill','B',(DamagePlayer('A',30),)),))
        s=play(s,'A','unit-a',3)
        s=queue_effect(s,'B','kill',expected_revision=s.revision)
        s=pass_round(s)
        self.assertTrue(s.players[0].eliminated)
        self.assertEqual(s.players[0].cards.discard,('unit-a',))
        self.assertEqual(s.players[0].resources.available,7)
        self.assertFalse(s.pending_cards)
        self.assertFalse(s.priority.chain)
        validate_match(s)

    def test_duplicate_zone_and_unsupported_definition_reject_at_factory(self):
        with self.assertRaises(ValueError):fixture((CardDefinition('unit','creature',1,attack=1,health=1),),instances(('u','unit','A')),ah=('u',),ad=('u',))
        with self.assertRaises(ValueError):fixture((CardDefinition('upgrade','upgrade',1),))
        with self.assertRaises(ValueError):fixture((CardDefinition('bad','action',1,(DamagePlayer('B',3),)),))


class BoundaryIntegrationTests(unittest.TestCase):
    def test_router_cannot_skip_mandatory_start_draw_or_end_choices(self):
        s=fixture(ad=('a1','a2'),bd=('b1','b2'),managed_turns=True,phase='Start')
        with self.assertRaises(CommandError):command(s,'A','end_turn')
        s=pass_round(s)
        self.assertEqual(s.turn.phase,'Draw')
        with self.assertRaises(CommandError):command(s,'A','end_turn')
        s=pass_round(s)
        self.assertEqual(s.turn.phase,'MainBefore')
        s=command(s,'A','end_turn')
        self.assertTrue(s.turn.end_requested)

    def test_router_blocker_batches_keep_views_identical_until_reveal(self):
        objects=tuple(MatchObject(i,p,p,'creature',Creature(i,p,2,4,4)) for i,p in (('a','A'),('a2','A'),('b','B'),('c','C')))
        s=fixture(objects=objects,phase='Combat')
        s=pass_round(s)
        s=command(s,'A','declare_attacks',attacks=[{'attacker_id':'a','target_player':'B'},{'attacker_id':'a2','target_player':'C'}])
        s=pass_round(s)
        before=project_match(s,'C')
        s=command(s,'B','lock_blockers',assignments=[{'attacker_id':'a','blockers':['b']}])
        after=project_match(s,'C')
        before.pop('revision');after.pop('revision')
        self.assertEqual(before,after)
        s=command(s,'C','lock_blockers',assignments=[{'attacker_id':'a2','blockers':[]}])
        self.assertIn('blockers',project_match(s)['combat'])
        s=pass_round(s)
        self.assertEqual(s.turn.phase,'MainAfter')
        self.assertEqual(s.players[2].cards.health,28)

    def test_hidden_registered_definitions_do_not_change_another_players_view(self):
        one=CardDefinition('secret-one','action',1,(DamagePlayer('$controller',1),))
        two=CardDefinition('secret-two','action',7,(HealPlayer('$controller',5),))
        s=fixture((one,two),instances(('hidden','secret-one','A')),ah=('hidden',),bh=('b-own',))
        changed=replace(s,card_instances=(CardInstance('hidden','secret-two','A'),))
        validate_match(changed)
        self.assertEqual(project_match(s),project_match(changed))
        self.assertEqual(project_match(s,'B'),project_match(changed,'B'))
        self.assertNotEqual(project_match(s,'A'),project_match(changed,'A'))

    def test_public_source_ability_does_not_reveal_unseen_target_instance(self):
        s=fixture(ah=('UNSEEN',),objects=(MatchObject('source','A','A','permanent'),),
                  effects=(EffectSpec('probe','A',(DestroyCreature('UNSEEN'),)),),actions=(ActionSpec('ability','probe','source'),))
        public=project_match(s)
        self.assertNotIn('UNSEEN',json.dumps(public))
        self.assertIsNone(public['battlefield'][0]['abilities'][0]['steps'][0]['target'])

    def test_source_ability_and_end_discard_commands_use_session_authority(self):
        s=fixture(ah=tuple('h'+str(i) for i in range(8)),objects=(MatchObject('source','A','A','permanent'),),
                  effects=(EffectSpec('ping','A',(DamagePlayer('B',1),)),),actions=(ActionSpec('ability','ping','source',1),))
        s=command(s,'A','activate',key='ability',payment={'ordinary':1,'token_ids':[]})
        s=pass_round(s)
        self.assertEqual(s.players[1].cards.health,29)
        s=command(s,'A','end_turn')
        s=pass_round(s)
        self.assertEqual(project_match(s,'A')['you']['choice'],{'kind':'end_discard','count':1})
        with self.assertRaises(CommandError):command(s,'B','end_discard',cards=['h0'])
        s=command(s,'A','end_discard',cards=['h0'])
        self.assertEqual(s.players[0].cards.discard,('h0',))
        self.assertEqual(s.turn.active_player,'B')

    def test_creature_can_block_immediately_despite_attack_wait(self):
        defs=(CardDefinition('unit','creature',0,attack=2,health=4),)
        s=fixture(defs,instances(('a-unit','unit','A')),ah=('a-unit',),ad=('a1','a2'),bd=('b1','b2'),managed_turns=True,phase='Start',
                  objects=(MatchObject('b','B','B','creature',Creature('b','B',3,5,5)),))
        s=pass_round(pass_round(s))
        s=pass_round(play(s,'A','a-unit'))
        self.assertFalse(s.battlefield[-1].creature.attack_eligible)
        s=command(s,'A','end_turn');s=pass_round(s)
        for _ in range(4):s=pass_round(s)
        self.assertEqual((s.turn.active_player,s.turn.phase,s.priority.status),('B','Combat','closed'))
        s=command(s,'B','declare_attacks',attacks=[{'attacker_id':'b','target_player':'A'}])
        s=pass_round(s)
        s=command(s,'A','lock_blockers',assignments=[{'attacker_id':'b','blockers':['a-unit']}])
        s=pass_round(s)
        self.assertEqual(s.players[0].cards.health,30)
        self.assertEqual(next(o.creature.health for o in s.battlefield if o.object_id=='a-unit'),1)

    def test_invalid_refill_commands_leave_global_random_and_shuffle_counter_unchanged(self):
        import random
        s=fixture(ag=('g1','g2'),effects=(EffectSpec('draw','A',(DrawCards('A',1),)),))
        s=pass_round(queue_effect(s,'A','draw',expected_revision=s.revision))
        before=random.getstate()
        with self.assertRaises(CommandError):command(s,'A','refill',pay=True,request_id=999)
        self.assertEqual(random.getstate(),before)
        self.assertEqual(s.shuffle_counter,0)

    def test_pending_card_negation_does_not_undo_another_cards_reveal(self):
        defs=(CardDefinition('hit','action',1,(DamagePlayer('$target',3),),target_kind='player',target_relation='enemy'),
              CardDefinition('deny','reaction',1,(NegateEffect('$target'),),target_kind='effect',target_relation='enemy'))
        s=fixture(defs,instances(('a','hit','A'),('b','deny','B')),ah=('a',),bh=('b',))
        s=play(s,'A','a',1,target='B')
        s=play(s,'B','b',1,target=str(s.priority.chain[0].effect_id))
        s=pass_round(s)
        self.assertEqual(s.players[1].cards.health,30)
        self.assertEqual([e['subject'] for e in project_match(s)['events'] if e['kind']=='card_played'],['a','b'])
        self.assertEqual(project_match(s)['players'][0]['discard'][0]['definition_key'],'hit')


    def test_hidden_foreign_card_and_invented_card_fail_with_identical_errors(self):
        s=fixture((CardDefinition('hidden','action',0),),instances(('b-secret','hidden','B')),bh=('b-secret',))
        errors=[]
        for card in ('b-secret','unknown'):
            with self.assertRaises(CommandError) as caught:play(s,'A',card)
            errors.append(str(caught.exception))
        self.assertEqual(errors[0],errors[1])

    def test_card_registry_conservation_rejects_missing_or_duplicate_pending_item(self):
        s=fixture((CardDefinition('noop','action',0),),instances(('a','noop','A')),ah=('a',))
        s=play(s,'A','a')
        with self.assertRaises(MatchError):validate_match(replace(s,pending_cards=()))
        with self.assertRaises(MatchError):validate_match(replace(s,pending_cards=s.pending_cards+s.pending_cards))

    def test_reaction_cannot_be_replayed_from_discard_or_another_players_hand(self):
        s=fixture((CardDefinition('react','reaction',0,(DamagePlayer('$target',1),),target_kind='player',target_relation='enemy'),),
                  instances(('b','react','B')),bh=('b',))
        s=command(s,'A','pass')
        s=play(s,'B','b',target='A')
        s=pass_round(s)
        s=command(s,'A','pass')
        with self.assertRaises(CommandError):play(s,'B','b',target='A')
        self.assertEqual(s.players[1].cards.discard,('b',))

    def test_locked_target_disappearing_does_not_return_card_or_refund_cost(self):
        d=CardDefinition('destroy','action',2,(DestroyCreature('$target'),),target_kind='creature',target_relation='enemy')
        s=fixture((d,),instances(('spell','destroy','A')),ah=('spell',),
                  objects=(MatchObject('b','B','B','creature',Creature('b','B',2,4,4)),),
                  effects=(EffectSpec('remove','B',(DestroyCreature('b'),)),))
        s=play(s,'A','spell',2,target='b')
        s=queue_effect(s,'B','remove',expected_revision=s.revision)
        s=pass_round(s)
        self.assertTrue(s.pending_cards)
        s=pass_round(s)
        self.assertEqual(s.players[0].cards.discard,('spell',))
        self.assertEqual(s.players[0].resources.available,8)
        self.assertFalse(s.pending_cards)

    def test_public_history_remembers_played_card_after_elimination_without_revealing_remaining_hand(self):
        s=fixture((CardDefinition('revealed','action',0),CardDefinition('hidden','action',0)),
                  instances(('a-played','revealed','A'),('a-secret','hidden','A')),ah=('a-played','a-secret'))
        s=pass_round(play(s,'A','a-played'))
        s=command(s,'A','concede',confirmed=True)
        view=project_match(s,'B')
        self.assertNotIn('a-secret',json.dumps(view))
        reveal=next(e for e in view['events'] if e['kind']=='card_played')
        self.assertEqual(reveal['card']['definition_key'],'revealed')
        self.assertNotIn('discard',view['players'][0])


if __name__=='__main__':unittest.main()
