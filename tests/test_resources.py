import unittest
from dataclasses import replace
from crucible_core.resources import ResourcePool, Payment, ResourceError, start_resources, pay_resources
from crucible_core.match import *
from crucible_core.combat import Attack, Creature
from crucible_core.turns import DrawPlayer, RefillPolicy


def player(name, *, pool=ResourcePool(), deck=None, **kw):
    return MatchPlayer(DrawPlayer(name,30,deck if deck is not None else tuple(name+str(i) for i in range(8)),(),**kw),resources=pool)


def creature(name, owner='A', **kw):
    return MatchObject(name,owner,owner,'creature',Creature(name,owner,2,4,4,**kw))


def window(s):
    # Exactly one all-seat pass round; do not silently consume later phase windows.
    for _ in range(len(s.priority.seats)):
        s=pass_match(s,s.priority.holder,expected_revision=s.revision)
    return s


def run(s):
    s=window(s)
    return resolve_current(s,expected_revision=s.revision)


def game(players=None, objects=(), effects=(), actions=(), **kw):
    return new_match(players or (player('A'),player('B'),player('C')),objects,effects,RefillPolicy(20,1),
                     active_player='A',actions=actions,**kw)


class ResourceAndStartTests(unittest.TestCase):
    def test_first_start_growth_cap_bonus_and_refill(self):
        pool=ResourcePool(permanent_bonus=4)
        pool=start_resources(pool,3)
        self.assertEqual((pool.natural_capacity,pool.available,pool.own_starts),(2,9,1))
        pool=start_resources(replace(pool,available=1),3)
        self.assertEqual((pool.natural_capacity,pool.available),(3,10))
        for _ in range(20):
            pool=start_resources(pool,3)
        self.assertEqual((pool.natural_capacity,pool.available),(10,17))

    def test_exact_payment_supports_adjustable_tokens_and_rejects_every_bad_source(self):
        pool=ResourcePool(available=3)
        tokens=(('one',1),('two',2))
        self.assertEqual(pay_resources(pool,3,Payment(3),tokens).available,0)
        self.assertEqual(pay_resources(pool,3,Payment(0,('one','two')),tokens).available,3)
        for pay in (Payment(4),Payment(True),Payment(1,('two','two')),Payment(1,('missing',)),Payment(2,('two',)),Payment(0)):
            with self.assertRaises(ResourceError):pay_resources(pool,3,pay,tokens)
        self.assertEqual(pool.available,3)

    def test_start_readies_only_active_creatures_and_grants_eligibility(self):
        objects=(creature('a',exhausted=True,attack_used=True,attack_eligible=False),creature('b','B',exhausted=True,attack_used=True,attack_eligible=False),
                 MatchObject('boost','A','A','permanent',capacity_bonus=3))
        s=game(objects=objects,managed_turns=True,phase='Start')
        self.assertEqual(s.players[0].resources.available,5)
        self.assertEqual(s.players[0].resources.own_starts,1)
        self.assertEqual((s.battlefield[0].creature.exhausted,s.battlefield[0].creature.attack_used,s.battlefield[0].creature.attack_eligible),(False,False,True))
        self.assertTrue(s.battlefield[1].creature.exhausted)
        self.assertEqual(sum(e.kind=='turn_start' for e in s.events),1)
        s=window(s)
        self.assertEqual(s.turn.phase,'Draw')
        self.assertEqual(s.players[0].cards.hand,('A0',))
        self.assertEqual(s.players[0].resources.own_starts,1)
        s=window(s)
        self.assertEqual(s.turn.phase,'MainBefore')

    def test_duel_first_start_skips_draw_but_next_seat_draws(self):
        s=game(players=(player('A'),player('B')),managed_turns=True,phase='Start')
        s=window(s)
        self.assertEqual(s.turn.phase,'Draw')
        self.assertFalse(s.players[0].cards.hand)
        s=window(s)
        s=request_match_end(s,'A',expected_revision=s.revision)
        s=window(s)
        self.assertEqual(s.turn.active_player,'B')
        self.assertEqual(s.players[1].resources.available,2)
        s=window(s)
        self.assertEqual(s.players[1].cards.hand,('B0',))

    def test_recharge_runs_start_and_end_without_draw_or_actions(self):
        s=game(players=(player('A'),player('B',recharge_due=True),player('C')),managed_turns=True,phase='Start')
        s=request_match_end(s,'A',expected_revision=s.revision)
        s=window(s)
        self.assertEqual(s.turn.active_player,'B')
        self.assertTrue(s.turn.recharge)
        self.assertEqual(s.players[1].resources.available,2)
        s=window(s)
        self.assertEqual(s.turn.active_player,'C')
        self.assertFalse(s.players[1].cards.hand)
        self.assertEqual(sum(e.kind=='turn_start' and e.subject=='B' for e in s.events),1)
        self.assertEqual(sum(e.kind=='turn_end' and e.subject=='B' for e in s.events),1)

    def test_empty_start_refill_runs_maintenance_then_pays_and_ends_without_draw(self):
        a=player('A',deck=())
        a=replace(a,cards=replace(a.cards,discard=('r1','r2')))
        s=game(players=(a,player('B'),player('C')),managed_turns=True,phase='Start')
        s=window(s)
        self.assertEqual(s.pending.draw.reason,'start_refill')
        self.assertEqual(s.players[0].resources.available,2)
        s=choose_refill(s,'A',pay=True,shuffled_discard=('r2','r1'),expected_request_id=s.pending.draw.request_id,expected_revision=s.revision)
        self.assertFalse(s.players[0].cards.hand)
        self.assertEqual(s.players[0].cards.health,10)
        s=window(s)
        self.assertEqual(s.turn.active_player,'B')

    def test_start_expiration_removes_capacity_before_refill_and_triggers_see_refill(self):
        effects=(EffectSpec('start','A',(GrantResources('A',1),)),)
        objects=(creature('expired'),MatchObject('clock','A','A','permanent',triggers=(TriggerSpec('turn_start','start'),)),)
        objects=(replace(objects[0],capacity_bonus=4),objects[1])
        s=game(objects=objects,effects=effects,managed_turns=True,phase='Start',start_cleanup=(DestroyCreature('expired'),))
        self.assertEqual(s.players[0].resources.available,2)
        self.assertEqual(s.priority.chain[-1].effect_key,'start')
        s=run(s)
        self.assertEqual(s.players[0].resources.available,3)

    def test_capacity_grant_changes_next_refill_not_available_now(self):
        s=game(effects=(EffectSpec('grow','A',(GrantCapacity('A',5),GrantResources('A',1))),))
        s=queue_effect(s,'A','grow',expected_revision=s.revision)
        s=run(s)
        self.assertEqual((s.players[0].resources.permanent_bonus,s.players[0].resources.available),(5,1))
        self.assertEqual(start_resources(s.players[0].resources).available,7)

    def test_source_ability_payment_is_locked_and_effect_waits_for_passes(self):
        effects=(EffectSpec('hit','A',(DamagePlayer('B',3),),'source'),)
        actions=(ActionSpec('ability','hit','source',3,exhaust_source=True,once_per_turn=True),)
        objects=(creature('source'),MatchObject('token','A','A','resource_token',resource_value=2))
        s=game(players=(player('A',pool=ResourcePool(available=2)),player('B'),player('C')),objects=objects,effects=effects,actions=actions)
        old=s
        s=submit_action(s,'A','ability',Payment(1,('token',)),expected_revision=s.revision)
        self.assertEqual(s.players[0].resources.available,1)
        self.assertTrue(s.battlefield[0].creature.exhausted)
        self.assertEqual(len(s.battlefield),1)
        self.assertEqual(s.players[1].cards.health,30)
        self.assertEqual(s.priority.holder,'B')
        self.assertEqual(old.players[0].resources.available,2)
        s=run(s)
        self.assertEqual(s.players[1].cards.health,27)
        with self.assertRaises(MatchError):submit_action(s,'A','ability',Payment(3),expected_revision=s.revision)

    def test_bad_payment_wrong_timing_and_summoning_wait_preserve_state(self):
        effects=(EffectSpec('noop','A',()),)
        action=ActionSpec('ability','noop','source',1,exhaust_source=True)
        s=game(objects=(creature('source',attack_eligible=False),),effects=effects,actions=(action,))
        for command in (lambda:submit_action(s,'A','ability',Payment(1),expected_revision=s.revision),
                        lambda:submit_action(s,'B','ability',Payment(0),expected_revision=s.revision),
                        lambda:submit_action(s,'A','ability',Payment(0),expected_revision=999)):
            with self.assertRaises(ValueError):command()
        self.assertFalse(s.battlefield[0].creature.exhausted)
        self.assertFalse(s.action_uses)

    def test_reaction_spends_retained_resources_offturn_and_zero_cost_is_valid(self):
        effects=(EffectSpec('react','B',(DamagePlayer('A',1),)),)
        actions=(ActionSpec('reaction','react','b',2,'reaction'),)
        s=game(players=(player('A'),player('B',pool=ResourcePool(available=2)),player('C')),objects=(creature('b','B'),),effects=effects,actions=actions)
        s=pass_match(s,'A',expected_revision=s.revision)
        s=submit_action(s,'B','reaction',Payment(2),expected_revision=s.revision)
        self.assertEqual(s.players[1].resources.available,0)
        s=run(s)
        self.assertEqual(s.players[0].cards.health,29)
        self.assertEqual(pay_resources(ResourcePool(),0,Payment(0),()).available,0)

    def test_controlled_tokens_only_and_capacity_loss_preserves_available(self):
        effects=(EffectSpec('hit','A',()),)
        actions=(ActionSpec('ability','hit','source',1),)
        s=game(objects=(creature('source'),MatchObject('foreign','B','B','resource_token')),effects=effects,actions=actions)
        with self.assertRaises(ResourceError):submit_action(s,'A','ability',Payment(0,('foreign',)),expected_revision=s.revision)
        pool=ResourcePool(available=9)
        s=game(players=(player('A',pool=pool),player('B'),player('C')),
               objects=(replace(creature('boost'),capacity_bonus=4),),effects=(EffectSpec('remove','A',(DestroyCreature('boost'),)),))
        s=queue_effect(s,'A','remove',expected_revision=s.revision)
        s=run(s)
        self.assertFalse(s.battlefield)
        self.assertEqual(s.players[0].resources.available,9)
        self.assertEqual(start_resources(s.players[0].resources).available,2)

    def test_paid_pending_ability_cancelled_by_elimination_has_no_refund(self):
        effects=(EffectSpec('ability','A',(DamagePlayer('B',3),)),EffectSpec('kill','B',(DamagePlayer('A',30),)))
        s=game(players=(player('A',pool=ResourcePool(available=2)),player('B'),player('C')),
               objects=(creature('source'),),effects=effects,actions=(ActionSpec('paid','ability','source',2),))
        s=submit_action(s,'A','paid',Payment(2),expected_revision=s.revision)
        s=queue_effect(s,'B','kill',expected_revision=s.revision)
        s=run(s)
        self.assertTrue(s.players[0].eliminated)
        self.assertEqual(s.players[0].resources.available,0)
        self.assertFalse(s.priority.chain)
        self.assertEqual(s.players[1].cards.health,30)

    def test_nonexhausting_once_per_turn_ability_rejects_repeat(self):
        s=game(objects=(creature('source'),),effects=(EffectSpec('noop','A',()),),
               actions=(ActionSpec('once','noop','source',once_per_turn=True),))
        s=submit_action(s,'A','once',Payment(0),expected_revision=s.revision)
        s=run(s)
        self.assertFalse(s.battlefield[0].creature.exhausted)
        with self.assertRaises(MatchError):submit_action(s,'A','once',Payment(0),expected_revision=s.revision)

    def test_managed_snapshot_adapter_cannot_bypass_declaration(self):
        s=game(managed_turns=True,phase='Start')
        for _ in range(4):s=window(s)
        self.assertEqual((s.turn.phase,s.priority.status),('Combat','closed'))
        with self.assertRaises(MatchError):resolve_combat_snapshot(s,(),expected_revision=s.revision)

    def test_complete_managed_turn_rotates_and_grows_only_on_own_start(self):
        s=game(players=(player('A'),player('B')),managed_turns=True,phase='Start')
        for active in ('A','B','A','B'):
            self.assertEqual(s.turn.active_player,active)
            for _ in range(4):s=window(s)  # Start -> Draw -> Main -> Combat -> closed
            s=declare_match_attacks(s,active,(),expected_revision=s.revision)
            s=window(s)  # attack responses -> final responses
            s=window(s)  # damage -> MainAfter
            s=window(s)  # End -> next Start
            validate_match(s)
        self.assertEqual(s.turn.active_player,'A')
        self.assertEqual((s.players[0].resources.own_starts,s.players[0].resources.available),(3,4))
        self.assertEqual((s.players[1].resources.own_starts,s.players[1].resources.available),(2,3))


if __name__=='__main__':unittest.main()
