import unittest
from dataclasses import replace
from crucible_core.match import *
from crucible_core.match import _depart
from crucible_core.leaders import *
from crucible_core.commands import route_command,CommandError
from crucible_core.resources import ResourcePool,Payment
from crucible_core.turns import DrawPlayer,RefillPolicy
from crucible_core.views import project_match


def definition(**changes):
    d=LeaderDefinition('core','Test Core','Gold',4,3,5,
        LeaderAbility('repair',2,(HealPlayer('$controller',2),)),
        LeaderAbility('bolt',2,(DamagePlayer('$target',1),),target_kind='player',target_relation='enemy',exhaust_source=True))
    return replace(d,**changes)


def fixture(*, battle=False,removals=0,available=20,managed=False,defs=None,effects=()):
    d=defs or definition()
    leader=LeaderState('leader-A','A','core',location='battlefield' if battle else 'reserve',removals=removals)
    objects=(MatchObject('leader-A','A','A','leader',Creature('leader-A','A',d.attack,d.health,d.health)),) if battle else ()
    players=tuple(MatchPlayer(DrawPlayer(p,30,tuple(p+str(i) for i in range(8)),()),resources=ResourcePool(permanent_bonus=20,available=available)) for p in 'ABC')
    return new_match(players,objects,effects,RefillPolicy(20,1),active_player='A',phase='Start' if managed else 'MainBefore',managed_turns=managed,
                     leader_definitions=(d,),leaders=(leader,))


def cmd(s,actor,kind,**args):
    return route_command(s,actor,{'kind':kind,'expected_revision':s.revision,'args':args})


def round_pass(s):
    for _ in range(len(s.priority.seats)):s=cmd(s,s.priority.holder,'pass')
    return s


def summon(s,cost=4):return cmd(s,'A','summon_leader',payment={'ordinary':cost,'token_ids':[]})


class LeaderTests(unittest.TestCase):
    def test_outside_deck_public_cost_and_reserve_not_a_creature_target(self):
        s=fixture()
        view=project_match(s,'B')
        leader=view['leaders'][0]
        self.assertEqual((leader['summon_cost'],leader['location'],leader['health']),(4,'reserve',5))
        self.assertEqual(len(s.players[0].cards.deck),8)
        self.assertFalse(s.battlefield)
        self.assertTrue(leader['abilities'][0]['available']);self.assertFalse(leader['abilities'][1]['available'])
        with self.assertRaises(MatchError):
            from crucible_core.match import _bound_card_steps
            _bound_card_steps(s,'B',CardDefinition('destroy','action',0,(DestroyCreature('$target'),),target_kind='creature'), 'leader-A')

    def test_summon_pays_before_responses_then_enters_full_and_waiting(self):
        s=fixture();s=summon(s)
        self.assertEqual(s.players[0].resources.available,16)
        self.assertFalse(s.battlefield)
        self.assertIsNotNone(s.leaders[0].pending_effect_id)
        self.assertEqual(s.priority.holder,'B')
        s=round_pass(s)
        self.assertEqual(s.leaders[0].location,'battlefield')
        c=s.battlefield[0].creature
        self.assertEqual((c.health,c.max_health,c.exhausted,c.attack_eligible),(5,5,False,False))
        self.assertIsNone(s.leaders[0].pending_effect_id)
        self.assertNotIn('leader-A',s.players[0].cards.discard)
        validate_match(s)

    def test_negated_summon_has_no_removal_or_recovery_and_can_retry(self):
        s=fixture(effects=(EffectSpec('counter','B',(NegateEffect(1),)),))
        s=summon(s);s=queue_effect(s,'B','counter',expected_revision=s.revision);s=round_pass(s)
        self.assertEqual((s.leaders[0].location,s.leaders[0].removals,s.leaders[0].recovering),('reserve',0,False))
        self.assertEqual(s.players[0].resources.available,16)
        self.assertIsNone(s.leaders[0].pending_effect_id)
        s=round_pass(summon(s))
        self.assertEqual(s.leaders[0].location,'battlefield')
        self.assertEqual(s.players[0].resources.available,12)

    def test_defeat_returns_reserve_increases_cost_and_blocks_reuse(self):
        s=fixture(battle=True,effects=(EffectSpec('destroy','A',(DestroyCreature('leader-A'),)),))
        s=round_pass(queue_effect(s,'A','destroy',expected_revision=s.revision))
        self.assertEqual((s.leaders[0].location,s.leaders[0].removals,s.leaders[0].recovering),('reserve',1,True))
        self.assertEqual(project_match(s)['leaders'][0]['summon_cost'],6)
        self.assertEqual(sum(e.kind=='defeat' for e in s.events),1)
        self.assertNotIn('leader-A',s.players[0].cards.discard)
        with self.assertRaises(CommandError):summon(s,6)
        with self.assertRaises(CommandError):cmd(s,'A','leader_ability',key='repair',payment={'ordinary':2,'token_ids':[]})

    def test_nondefeat_departure_does_not_manufacture_defeat(self):
        s=fixture(battle=True)
        s=_depart(s,{'leader-A'},'bounce')
        self.assertFalse(any(e.kind=='defeat' for e in s.events))
        self.assertEqual((s.leaders[0].location,s.leaders[0].removals,s.leaders[0].recovering),('reserve',1,True))
        self.assertFalse(s.players[0].cards.hand)
        self.assertFalse(s.players[0].cards.discard)
        validate_match(s)

    def test_recovery_clears_only_at_own_next_start_and_resummon_resets_health(self):
        s=fixture(managed=True,effects=(EffectSpec('destroy','A',(DestroyCreature('leader-A'),)),))
        s=round_pass(round_pass(s));s=round_pass(summon(s))
        s=round_pass(queue_effect(s,'A','destroy',expected_revision=s.revision))
        for actor in 'ABC':
            if actor!='A':s=round_pass(round_pass(s))
            self.assertEqual(s.turn.active_player,actor)
            self.assertTrue(s.leaders[0].recovering)
            s=cmd(s,actor,'end_turn');s=round_pass(s)
        self.assertEqual(s.turn.active_player,'A')
        self.assertFalse(s.leaders[0].recovering)
        s=round_pass(round_pass(s));s=round_pass(summon(s,6))
        self.assertEqual((s.battlefield[0].creature.health,s.battlefield[0].creature.max_health),(5,5))
        self.assertFalse(s.battlefield[0].creature.attack_eligible)

    def test_cost_above_ten_is_not_capped_or_underpaid(self):
        s=fixture(removals=4,available=11)
        with self.assertRaises(CommandError):summon(s,10)
        with self.assertRaises(CommandError):summon(s,12)
        self.assertEqual(s.players[0].resources.available,11)
        s=fixture(removals=4,available=14);s=summon(s,12)
        self.assertEqual(s.players[0].resources.available,2)
        self.assertEqual(project_match(s)['leaders'][0]['summon_cost'],12)

    def test_reserve_ability_once_per_turn_and_wrong_location_block(self):
        s=fixture();p=s.players[0]
        s=replace(s,players=(replace(p,cards=replace(p.cards,health=20)),)+s.players[1:])
        s=cmd(s,'A','leader_ability',key='repair',payment={'ordinary':2,'token_ids':[]})
        self.assertEqual(s.players[0].cards.health,20)
        s=round_pass(s);self.assertEqual(s.players[0].cards.health,22)
        with self.assertRaises(CommandError):cmd(s,'A','leader_ability',key='repair',payment={'ordinary':2,'token_ids':[]})
        s=round_pass(summon(s))
        self.assertFalse(project_match(s)['leaders'][0]['abilities'][0]['available'])
        with self.assertRaises(CommandError):cmd(s,'A','leader_ability',key='bolt',target='B',payment={'ordinary':2,'token_ids':[]})

    def test_exhaust_battle_ability_survives_source_departure_and_keeps_use(self):
        s=fixture(battle=True,effects=(EffectSpec('destroy','B',(DestroyCreature('leader-A'),)),))
        s=cmd(s,'A','leader_ability',key='bolt',target='B',payment={'ordinary':2,'token_ids':[]})
        self.assertTrue(s.battlefield[0].creature.exhausted)
        s=queue_effect(s,'B','destroy',expected_revision=s.revision);s=round_pass(s)
        self.assertTrue(s.leaders[0].recovering)
        self.assertEqual(len(s.action_uses),1)
        self.assertEqual(len(s.priority.chain),1)
        s=round_pass(s)
        self.assertEqual(s.players[1].cards.health,29)
        self.assertEqual(s.players[0].resources.available,18)

    def test_reserve_reaction_can_resolve_while_summon_is_pending(self):
        d=definition(reserve_ability=LeaderAbility('repair',1,(HealPlayer('$controller',1),),timing='reaction'))
        s=summon(fixture(defs=d))
        s=cmd(s,'B','pass');s=cmd(s,'C','pass')
        s=cmd(s,'A','leader_ability',key='repair',payment={'ordinary':1,'token_ids':[]})
        s=round_pass(s)
        self.assertEqual(s.leaders[0].location,'reserve')
        self.assertIsNotNone(s.leaders[0].pending_effect_id)
        s=round_pass(s);self.assertEqual(s.leaders[0].location,'battlefield')

    def test_elimination_returns_battle_leader_without_fake_defeat(self):
        s=fixture(battle=True,effects=(EffectSpec('lose','A',(DamagePlayer('A',30),)),))
        s=round_pass(queue_effect(s,'A','lose',expected_revision=s.revision))
        self.assertTrue(s.players[0].eliminated)
        self.assertEqual(s.leaders[0].location,'reserve')
        self.assertFalse(any(e.kind=='defeat' for e in s.events))
        self.assertFalse(any(a['available'] for a in project_match(s)['leaders'][0]['abilities']))
        with self.assertRaises(CommandError):summon(s,6)

    def test_pending_summon_cancelled_on_elimination_without_removal_increase(self):
        s=fixture(effects=(EffectSpec('lose','B',(DamagePlayer('A',30),)),))
        s=summon(s);s=queue_effect(s,'B','lose',expected_revision=s.revision);s=round_pass(s)
        self.assertTrue(s.players[0].eliminated)
        self.assertEqual(s.leaders[0].removals,0)
        self.assertIsNone(s.leaders[0].pending_effect_id)
        self.assertFalse(s.priority.chain)
        validate_match(s)

    def test_control_change_hidden_zone_duplicate_leader_and_invalid_payment_reject(self):
        s=fixture(battle=True)
        bad=replace(s,battlefield=(replace(s.battlefield[0],controller='B',creature=replace(s.battlefield[0].creature,controller='B')),))
        with self.assertRaises(MatchError):validate_match(bad)
        with self.assertRaises(MatchError):validate_match(replace(s,leaders=s.leaders+s.leaders))
        reserve=fixture();p=reserve.players[0]
        with self.assertRaises(MatchError):validate_match(replace(reserve,players=(replace(p,cards=replace(p.cards,hand=('leader-A',))),)+reserve.players[1:]))
        with self.assertRaises(CommandError):cmd(reserve,'B','summon_leader',payment={'ordinary':4,'token_ids':[]})
        with self.assertRaises(CommandError):cmd(reserve,'A','summon_leader',payment={'ordinary':3,'token_ids':[]})

    def test_summoned_leader_is_challengeable_and_retaliates(self):
        d=definition();players=tuple(MatchPlayer(DrawPlayer(p,30,(p+'1',),())) for p in 'ABC')
        objects=(MatchObject('leader-A','A','A','leader',Creature('leader-A','A',3,5,5)),
                 MatchObject('challenger','B','B','creature',Creature('challenger','B',5,6,6,keywords=('challenge',))))
        s=new_match(players,objects,(),RefillPolicy(20,1),active_player='B',phase='Combat',
                    leader_definitions=(d,),leaders=(LeaderState('leader-A','A','core',location='battlefield'),))
        s=round_pass(s)
        s=cmd(s,'B','declare_attacks',attacks=[{'attacker_id':'challenger','target_player':'A','challenge_target':'leader-A'}])
        s=round_pass(round_pass(s))
        self.assertEqual(s.leaders[0].location,'reserve')
        self.assertEqual(s.leaders[0].removals,1)
        self.assertEqual(s.battlefield[0].creature.health,3)
        self.assertEqual(s.players[0].cards.health,30)

    def test_simultaneous_leader_defeat_and_owner_elimination_counts_one_removal(self):
        d=definition();players=tuple(MatchPlayer(DrawPlayer(p,4 if p=='A' else 30,(p+'1',),())) for p in 'ABC')
        objects=(MatchObject('leader-A','A','A','leader',Creature('leader-A','A',3,5,5)),
                 MatchObject('attacker','B','B','creature',Creature('attacker','B',9,10,10,keywords=('breakthrough',))),
                 MatchObject('upgrade','C','C','permanent',attached_to='leader-A'))
        s=new_match(players,objects,(),RefillPolicy(20,1),active_player='B',phase='Combat',
                    leader_definitions=(d,),leaders=(LeaderState('leader-A','A','core',location='battlefield'),))
        s=round_pass(s)
        s=cmd(s,'B','declare_attacks',attacks=[{'attacker_id':'attacker','target_player':'A'}]);s=round_pass(s)
        s=cmd(s,'A','lock_blockers',assignments=[{'attacker_id':'attacker','blockers':['leader-A']}]);s=round_pass(s)
        self.assertTrue(s.players[0].eliminated)
        self.assertEqual(s.leaders[0].removals,1)
        self.assertEqual(sum(e.kind=='defeat' and e.subject=='leader-A' for e in s.events),1)
        self.assertEqual(sum(e.kind=='leader_returned' for e in s.events),1)
        self.assertIn('upgrade',s.players[2].cards.discard)
        self.assertFalse(any(e.kind=='defeat' and e.subject=='upgrade' for e in s.events))

    def test_client_discount_field_cannot_reduce_accumulated_cost(self):
        s=fixture(removals=2)
        with self.assertRaises(CommandError):cmd(s,'A','summon_leader',discount=4,payment={'ordinary':4,'token_ids':[]})
        self.assertEqual(s.players[0].resources.available,20)

    def test_nonexhausting_battle_ability_is_usable_on_entry(self):
        d=definition(battle_ability=LeaderAbility('renewal',1,(HealPlayer('$controller',1),)))
        s=fixture(defs=d);p=s.players[0]
        s=replace(s,players=(replace(p,cards=replace(p.cards,health=20)),)+s.players[1:])
        s=round_pass(summon(s))
        self.assertFalse(s.battlefield[0].creature.attack_eligible)
        s=cmd(s,'A','leader_ability',key='renewal',payment={'ordinary':1,'token_ids':[]});s=round_pass(s)
        self.assertEqual(s.players[0].cards.health,21)
        self.assertFalse(s.battlefield[0].creature.exhausted)
        with self.assertRaises(MatchError):validate_match(replace(s,card_definitions=(CardDefinition('core','creature',1,attack=1,health=1),)))


if __name__=='__main__':unittest.main()
