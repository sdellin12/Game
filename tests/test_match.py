import unittest
from dataclasses import replace
from crucible_core.match import *
from crucible_core.turns import DrawPlayer, RefillPolicy
from crucible_core.combat import Creature, Attack

POLICY=RefillPolicy(20,1)


def player(name, health=30, **kw):
    return MatchPlayer(DrawPlayer(name,health,kw.pop('deck',(name+'1',name+'2')),kw.pop('discard',()),**kw))


def fixture(effects=(), objects=(), players=None, **kw):
    return new_match(players or (player('A'),player('B'),player('C')), objects, effects, POLICY,active_player='A',**kw)


def queue(s, actor, key):
    return queue_effect(s,actor,key,expected_revision=s.revision)


def close(s):
    while s.priority and s.priority.status=='priority' and not s.triggers and not s.discard_needed:
        s=pass_match(s,s.priority.holder,expected_revision=s.revision)
    return s


def resolve(s):
    s=close(s)
    return resolve_current(s,expected_revision=s.revision)


def obj(name, owner='A', controller=None, triggers=(), kind='creature', attached_to=None):
    controller=controller or owner
    return MatchObject(name,owner,controller,kind,Creature(name,controller,2,2,2) if kind.startswith('creature') else None,attached_to,triggers)


class AtomicMatchTests(unittest.TestCase):
    def test_damage_draw_heal_is_one_atomic_effect(self):
        s=fixture((EffectSpec('save','A',(DamagePlayer('A',32),DrawCards('A',1),HealPlayer('A',5))),))
        result=resolve(queue(s,'A','save'))
        self.assertEqual(result.players[0].cards.health,3)
        self.assertFalse(result.players[0].eliminated)
        self.assertEqual(result.players[0].cards.hand,('A1',))
        self.assertEqual(s.players[0].cards.health,30)
        validate_match(result)

    def test_simultaneous_all_player_losses_are_draw(self):
        s=fixture((EffectSpec('wipe','A',tuple(DamagePlayer(p,30) for p in 'ABC')),))
        result=resolve(queue(s,'A','wipe'))
        self.assertEqual(result.result,MatchResult('draw'))
        self.assertTrue(all(p.eliminated for p in result.players))

    def test_pending_survivor_self_damage_prevents_early_victory(self):
        s=fixture((EffectSpec('self','A',(DamagePlayer('A',30),)),EffectSpec('kill','B',(DamagePlayer('B',30),DamagePlayer('C',30)))))
        s=queue(queue(s,'A','self'),'B','kill')
        s=resolve(s)
        self.assertIsNone(s.result)
        self.assertEqual(s.priority.seats,('A',))
        s=resolve(s)
        self.assertEqual(s.result,MatchResult('draw'))

    def test_eliminated_controller_pending_heal_is_cancelled(self):
        s=fixture((EffectSpec('heal','A',(HealPlayer('A',30),)),EffectSpec('kill','B',(DamagePlayer('A',30),))))
        s=resolve(queue(queue(s,'A','heal'),'B','kill'))
        self.assertTrue(s.players[0].eliminated)
        self.assertFalse(s.priority.chain)
        self.assertEqual(close(s).turn.active_player,'B')
        self.assertFalse(any(e.kind=='heal' for e in s.events))

    def test_surviving_controller_effect_outlives_borrowed_source(self):
        objects=(obj('borrowed','A','B'),)
        s=fixture((EffectSpec('later','B',(DamagePlayer('C',4),),'borrowed'),EffectSpec('kill','C',(DamagePlayer('A',30),))),objects)
        s=pass_match(s,'A',expected_revision=s.revision)
        s=queue(queue(s,'B','later'),'C','kill')
        s=resolve(s)
        self.assertFalse(s.battlefield)
        self.assertEqual(s.priority.chain[0].effect_key,'later')
        s=resolve(s)
        self.assertEqual(s.players[2].cards.health,26)

    def test_owned_controlled_tokens_and_orphan_attachment_cleanup(self):
        objects=(obj('owned','A','B'),obj('borrowed','B','A'),obj('token','B','A',kind='creature_token'),
                 obj('upgrade','C',kind='permanent',attached_to='owned'),obj('safe','C'))
        s=fixture((EffectSpec('kill','A',(DamagePlayer('A',30),)),),objects)
        s=resolve(queue(s,'A','kill'))
        self.assertEqual(tuple(o.object_id for o in s.battlefield),('safe',))
        self.assertIn('owned',s.players[0].cards.discard)
        self.assertIn('borrowed',s.players[1].cards.discard)
        self.assertNotIn('token',s.players[1].cards.discard)
        self.assertIn('upgrade',s.players[2].cards.discard)
        self.assertFalse(any(e.kind=='defeat' for e in s.events))

    def test_simultaneous_defeats_capture_witnesses_before_departure(self):
        effects=(EffectSpec('destroy','A',(DestroyCreature('x'),DestroyCreature('y'))),EffectSpec('ping','B',(DamagePlayer('C',1),)))
        s=fixture(effects,(obj('x','B',triggers=(TriggerSpec('defeat','ping','any'),)),obj('y','B')))
        s=resolve(queue(s,'A','destroy'))
        self.assertEqual(len(s.triggers),2)
        with self.assertRaises(ValueError):
            pass_match(s,'A',expected_revision=s.revision)
        order=tuple(t.trigger_id for t in reversed(s.triggers))
        s=choose_trigger_order(s,'B',order,expected_revision=s.revision)
        self.assertFalse(s.triggers)
        self.assertEqual(len(s.priority.chain),2)
        s=resolve(resolve(s))
        self.assertEqual(s.players[2].cards.health,28)

    def test_eliminated_controller_triggers_removed(self):
        effects=(EffectSpec('wipe','A',(DestroyCreature('x'),DamagePlayer('B',30))),EffectSpec('ping','B',(DamagePlayer('C',30),)))
        s=fixture(effects,(obj('x','B',triggers=(TriggerSpec('defeat','ping'),)),))
        s=resolve(queue(s,'A','wipe'))
        self.assertFalse(s.priority.chain)
        self.assertFalse(s.triggers)
        self.assertEqual(s.players[2].cards.health,30)

    def test_refill_pauses_whole_effect_then_finishes_and_ends_turn(self):
        s=fixture((EffectSpec('draw','A',(DrawCards('A',3),DamagePlayer('B',2))),),players=(player('A',discard=('a3','a4')),player('B'),player('C')))
        s=resolve(queue(s,'A','draw'))
        self.assertEqual(s.pending.draw.player.hand,('A1','A2'))
        self.assertEqual(s.players[1].cards.health,30)
        self.assertEqual(s.turn.active_player,'A')
        s=choose_refill(s,'A',pay=True,shuffled_discard=('a4','a3'),expected_request_id=s.pending.draw.request_id,expected_revision=s.revision)
        self.assertEqual(s.players[0].cards.hand,('A1','A2','a4'))
        self.assertEqual(s.players[0].cards.health,10)
        self.assertEqual(s.players[1].cards.health,28)
        self.assertEqual(close(s).turn.active_player,'B')
        self.assertFalse(s.players[0].cards.recharge_due)

    def test_declined_refill_finishes_effect_before_elimination(self):
        s=fixture((EffectSpec('draw','A',(DrawCards('A',3),HealPlayer('A',5),DamagePlayer('B',2))),),players=(player('A',discard=('a3',)),player('B'),player('C')))
        s=resolve(queue(s,'A','draw'))
        s=choose_refill(s,'A',pay=False,expected_request_id=s.pending.draw.request_id,expected_revision=s.revision)
        self.assertTrue(s.players[0].eliminated)
        self.assertEqual(s.players[0].causes,('failed_draw',))
        self.assertEqual(s.players[1].cards.health,28)

    def test_offturn_refill_creates_recharge_not_active_end(self):
        s=fixture((EffectSpec('draw','A',(DrawCards('B',3),)),),players=(player('A'),player('B',discard=('b3','b4')),player('C')))
        s=resolve(queue(s,'A','draw'))
        s=choose_refill(s,'B',pay=True,shuffled_discard=('b3','b4'),expected_request_id=s.pending.draw.request_id,expected_revision=s.revision)
        self.assertEqual(s.turn.active_player,'A')
        self.assertTrue(s.players[1].cards.recharge_due)
        s=close(request_match_end(s,'A',expected_revision=s.revision))
        self.assertEqual(close(s).turn.active_player,'B')
        self.assertTrue(s.turn.recharge)
        self.assertFalse(s.players[1].cards.recharge_due)

    def test_active_elimination_skips_end_triggers_runs_expiration_before_win(self):
        effects=(EffectSpec('kill','A',(DamagePlayer('A',30),DamagePlayer('C',30))),EffectSpec('bad_end','B',(HealPlayer('B',30),)))
        s=fixture(effects,(obj('watch','B',triggers=(TriggerSpec('turn_end','bad_end','any'),)),),end_cleanup=(DamagePlayer('B',30),))
        s=resolve(queue(s,'A','kill'))
        self.assertEqual(s.result,MatchResult('draw'))
        self.assertFalse(any(e.kind=='turn_end' for e in s.events))

    def test_end_triggers_then_seven_card_discard_then_expiration(self):
        effects=(EffectSpec('end','A',(DamagePlayer('B',1),)),)
        s=fixture(effects,(obj('watch',triggers=(TriggerSpec('turn_end','end'),)),),players=(player('A',hand=tuple('h'+str(i) for i in range(8))),player('B'),player('C')),phase='End',end_cleanup=(DamagePlayer('B',2),))
        s=close(s)
        self.assertEqual(s.priority.resolving.effect_key,'end')
        s=resolve(s)
        s=close(s)
        self.assertEqual(s.discard_needed,1)
        self.assertEqual(s.players[1].cards.health,29)
        s=choose_end_discards(s,'A',('h0',),expected_revision=s.revision)
        s=close(s)
        self.assertEqual(s.players[1].cards.health,27)
        self.assertEqual(close(s).turn.active_player,'B')
        self.assertEqual(sum(e.kind=='turn_end' for e in s.events),1)

    def test_concession_during_refill_does_not_deadlock(self):
        s=fixture((EffectSpec('draw','A',(DrawCards('A',3),DamagePlayer('B',2))),),players=(player('A',discard=('a3',)),player('B'),player('C')))
        s=resolve(queue(s,'A','draw'))
        s=concede(s,'A',expected_revision=s.revision)
        self.assertTrue(s.players[0].eliminated)
        self.assertIn('concede',s.players[0].causes)
        self.assertEqual(s.players[1].cards.health,28)

    def test_combat_snapshot_uses_existing_simultaneous_kernel(self):
        s=fixture(objects=(obj('attacker'),obj('blocker','B')),phase='Combat')
        s=close(s)
        s=resolve_combat_snapshot(s,(Attack('attacker','B',('blocker',),True),),expected_revision=s.revision)
        self.assertFalse(s.battlefield)
        self.assertEqual(sum(e.kind=='defeat' for e in s.events),2)

    def test_stale_wrong_actor_and_bad_shuffle_are_rejected_without_mutation(self):
        s=fixture((EffectSpec('draw','A',(DrawCards('A',3),)),),players=(player('A',discard=('a3',)),player('B'),player('C')))
        with self.assertRaises(ValueError):
            queue_effect(s,'A','draw',expected_revision=999)
        s=resolve(queue(s,'A','draw'))
        original=s
        for actor,order in (('B',('a3',)),('A',('invented',))):
            with self.assertRaises(ValueError):
                choose_refill(s,actor,pay=True,shuffled_discard=order,expected_request_id=s.pending.draw.request_id,expected_revision=s.revision)
        self.assertEqual(s,original)

    def test_queued_concessions_are_serial_and_terminal_stops_later_request(self):
        s=fixture((EffectSpec('noop','A',()),),players=(player('A'),player('B')))
        s=close(queue(s,'A','noop'))
        s=concede(s,'A',expected_revision=s.revision)
        s=concede(s,'B',expected_revision=s.revision)
        s=resolve_current(s,expected_revision=s.revision)
        self.assertEqual(s.result,MatchResult('win','B'))
        self.assertFalse(s.players[1].eliminated)
        self.assertEqual(tuple(e.subject for e in s.events if e.kind=='elimination'),('A',))

    def test_multiple_concessions_with_more_survivors_follow_recorded_order(self):
        s=fixture((EffectSpec('noop','A',()),))
        s=close(queue(s,'A','noop'))
        s=concede(s,'B',expected_revision=s.revision)
        s=concede(s,'A',expected_revision=s.revision)
        s=resolve_current(s,expected_revision=s.revision)
        s=close(s)
        self.assertEqual(s.result,MatchResult('win','C'))
        self.assertEqual(tuple(e.subject for e in s.events if e.kind=='elimination'),('B','A'))

    def test_concession_releases_eliminated_active_hand_choice(self):
        s=fixture(players=(player('A',hand=tuple('h'+str(i) for i in range(8))),player('B'),player('C')),phase='End')
        s=close(s)
        self.assertEqual(s.discard_needed,1)
        s=concede(s,'A',expected_revision=s.revision)
        self.assertEqual(s.discard_needed,0)
        self.assertEqual(close(s).turn.active_player,'B')

    def test_combat_adapter_rejects_wrong_phase(self):
        s=close(fixture())
        with self.assertRaises(MatchError):
            resolve_combat_snapshot(s,(),expected_revision=s.revision)

    def test_end_intent_preserves_final_response_window(self):
        s=fixture((EffectSpec('response','B',(DamagePlayer('A',1),)),))
        s=request_match_end(s,'A',expected_revision=s.revision)
        self.assertEqual(s.turn.active_player,'A')
        self.assertEqual(s.end_stage,'none')
        s=pass_match(s,'A',expected_revision=s.revision)
        s=queue(s,'B','response')
        s=resolve(s)
        self.assertEqual(s.players[0].cards.health,29)
        self.assertEqual(s.turn.active_player,'A')
        self.assertEqual(close(s).turn.active_player,'B')

    def test_three_controller_trigger_groups_last_group_resolves_first(self):
        effects=(EffectSpec('wipe','A',tuple(DestroyCreature(x) for x in ('x','y','z'))),
                 EffectSpec('a','A',(DamagePlayer('C',1),)),
                 EffectSpec('b','B',(DamagePlayer('C',2),)),
                 EffectSpec('c','C',(HealPlayer('C',3),)))
        objects=tuple(obj(name,owner,triggers=(TriggerSpec('defeat',key),)) for name,owner,key in (('x','A','a'),('y','B','b'),('z','C','c')))
        s=resolve(queue(fixture(effects,objects),'A','wipe'))
        self.assertEqual(tuple(e.effect_key for e in s.priority.chain),('a','b','c'))
        s=resolve(resolve(resolve(s)))
        self.assertEqual(s.players[2].cards.health,27)
        self.assertEqual(tuple(e.kind for e in s.events if e.kind in ('damage','heal')),('heal','damage','damage'))

    def test_expiration_trigger_draw_rechecks_hand_without_refiring_end(self):
        effects=(EffectSpec('draw','A',(DrawCards('A',2),)),)
        objects=(obj('expires',triggers=(TriggerSpec('departure','draw'),)),)
        players=(player('A',deck=('a1','a2','a3'),hand=tuple('h'+str(i) for i in range(7))),player('B'),player('C'))
        s=fixture(effects,objects,players=players,phase='End',end_cleanup=(DestroyCreature('expires'),))
        s=close(s)
        self.assertEqual(s.priority.resolving.effect_key,'draw')
        s=close(resolve(s))
        self.assertEqual(s.discard_needed,2)
        self.assertEqual(s.end_stage,'done')
        s=choose_end_discards(s,'A',('a1','a2'),expected_revision=s.revision)
        self.assertEqual(s.turn.active_player,'B')
        self.assertEqual(sum(e.kind=='turn_end' for e in s.events),1)
        self.assertEqual(sum(e.kind=='defeat' for e in s.events),1)

    def test_failed_refill_retains_payment_and_available_draws(self):
        s=fixture((EffectSpec('draw','A',(DrawCards('A',5),)),),players=(player('A',discard=('a3',)),player('B'),player('C')))
        s=resolve(queue(s,'A','draw'))
        s=choose_refill(s,'A',pay=True,shuffled_discard=('a3',),expected_request_id=s.pending.draw.request_id,expected_revision=s.revision)
        self.assertTrue(s.players[0].eliminated)
        self.assertEqual(s.players[0].cards.health,10)
        self.assertEqual(s.players[0].cards.hand,('A1','A2','a3'))
        self.assertEqual(s.draw_records[-1].shuffles,(('a3',),))

    def test_unknown_instructions_and_leaders_fail_closed(self):
        with self.assertRaises(UnsupportedMatchRule):
            fixture((EffectSpec('bad','A',('prose',)),))
        with self.assertRaises(UnsupportedMatchRule):
            fixture(objects=(obj('leader',kind='leader'),))


if __name__=='__main__':
    unittest.main()
