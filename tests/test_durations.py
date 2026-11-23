import unittest
from dataclasses import replace
from crucible_core.match import *
from crucible_core.commands import route_command
from crucible_core.durations import TimedEffect
from crucible_core.turns import DrawPlayer,RefillPolicy
from crucible_core.resources import ResourcePool
from crucible_core.views import project_match


def fixture(effects=(),durations=(),objects=None,managed=False,phase=None):
    players=tuple(MatchPlayer(DrawPlayer(p,30,tuple(p+str(i) for i in range(9)),()),resources=ResourcePool(available=10)) for p in 'ABCD')
    if objects is None:objects=(MatchObject('a','A','A','creature',Creature('a','A',3,5,5)),)
    return new_match(players,objects,effects,RefillPolicy(20,1),active_player='A',phase=phase or ('Start' if managed else 'MainBefore'),managed_turns=managed,durations=durations)


def cmd(s,actor,kind,**args):return route_command(s,actor,{'kind':kind,'args':args,'expected_revision':s.revision})


def round_pass(s):
    for _ in range(len(s.priority.seats)):s=cmd(s,s.priority.holder,'pass')
    return s


def resolve(s,key,actor='A'):
    s=queue_effect(s,actor,key,expected_revision=s.revision)
    return round_pass(s)


def end(s,actor):return round_pass(cmd(s,actor,'end_turn'))


class DurationTests(unittest.TestCase):
    def test_turn_end_shield_expires_once_after_final_response(self):
        s=fixture((EffectSpec('ward','A',(GrantShield('a',3),)),))
        s=resolve(s,'ward')
        self.assertEqual(s.battlefield[0].creature.shields[0].amount,3)
        self.assertEqual((s.durations[0].anchor_player,s.durations[0].boundary,s.durations[0].occurrence),('A','End',1))
        s=cmd(s,'A','end_turn')
        self.assertTrue(s.battlefield[0].creature.shields)
        s=round_pass(s)
        self.assertEqual(s.turn.active_player,'B')
        self.assertFalse(s.battlefield[0].creature.shields);self.assertFalse(s.durations)
        self.assertEqual(sum(e.kind=='duration_expired' for e in s.events),1)
        validate_match(s)

    def test_next_start_expiry_precedes_maintenance_and_is_not_other_players_start(self):
        s=fixture((EffectSpec('ward','A',(GrantShield('a',2,'next_start','A'),)),),managed=True)
        s=round_pass(round_pass(s));s=resolve(s,'ward')
        self.assertEqual(s.durations[0].occurrence,2)
        for actor in 'ABCD':
            if actor!='A':s=round_pass(round_pass(s))
            self.assertEqual(s.turn.active_player,actor)
            self.assertTrue(s.battlefield[0].creature.shields)
            s=end(s,actor)
        self.assertEqual(s.turn.active_player,'A')
        self.assertFalse(s.battlefield[0].creature.shields)
        self.assertEqual(s.players[0].resources.own_starts,2)
        self.assertLess(next(e.event_id for e in s.events if e.kind=='duration_expired'),max(e.event_id for e in s.events if e.kind=='turn_start' and e.subject=='A'))

    def test_eliminated_anchor_gets_scheduled_expiry_without_turn_resources_or_draw(self):
        effects=(EffectSpec('ward','A',(GrantShield('a',2,'next_start','B'),)),EffectSpec('kill','A',(DamagePlayer('B',30),)))
        s=resolve(fixture(effects),'ward');s=resolve(s,'kill')
        self.assertTrue(s.durations)
        s=end(s,'A')
        self.assertEqual(s.turn.active_player,'C')
        self.assertFalse(s.durations);self.assertFalse(s.battlefield[0].creature.shields)
        b=s.players[1]
        self.assertEqual((b.resources.own_starts,b.resources.available,b.cards.hand),(0,10,()))
        self.assertFalse(any(e.kind=='turn_start' and e.subject=='B' for e in s.events))
        counts=next(b for b in s.boundary_counts if b.player_id=='B')
        self.assertEqual((counts.starts,counts.ends),(1,1))

    def test_skipped_boundary_payload_and_trigger_finish_before_next_live_start(self):
        expiry=TimedEffect(1,'A','B','Start',1,expiration_steps=(DestroyCreature('witness'),))
        effects=(EffectSpec('kill','A',(DamagePlayer('B',30),)),EffectSpec('ping','C',(DamagePlayer('D',2),)))
        objects=(MatchObject('witness','C','C','creature',Creature('witness','C',1,2,2),triggers=(TriggerSpec('defeat','ping'),)),)
        s=resolve(fixture(effects,(expiry,),objects),'kill');s=end(s,'A')
        self.assertTrue(s.rotation_queue);self.assertEqual(s.turn.active_player,'A')
        self.assertEqual(s.priority.chain[-1].effect_key,'ping')
        s=round_pass(s)
        self.assertEqual(s.players[3].cards.health,28)
        s=round_pass(s)
        self.assertEqual(s.turn.active_player,'C')
        self.assertFalse(s.rotation_queue)

    def test_skipped_start_and_end_consequences_can_produce_draw_before_victory(self):
        durations=(TimedEffect(1,'C','B','Start',1,expiration_steps=(DamagePlayer('A',30),)),
                   TimedEffect(2,'C','B','End',1,expiration_steps=(DamagePlayer('C',30),)))
        effects=(EffectSpec('kill','A',(DamagePlayer('B',30),DamagePlayer('D',30))),)
        s=resolve(fixture(effects,durations),'kill');s=end(s,'A')
        # No extra last-player window: both crossed boundaries finish before victory.
        self.assertEqual(s.result,MatchResult('draw'))
        self.assertEqual(sum(e.kind=='duration_expired' for e in s.events),2)

    def test_duration_controllers_elimination_removes_granted_shield_from_survivor(self):
        objects=(MatchObject('b','B','B','creature',Creature('b','B',1,5,5)),)
        effects=(EffectSpec('ward','A',(GrantShield('b',3,'next_start','C'),)),EffectSpec('lose','A',(DamagePlayer('A',30),)))
        s=resolve(fixture(effects,objects=objects),'ward');s=resolve(s,'lose')
        self.assertFalse(s.durations);self.assertFalse(s.battlefield[0].creature.shields)
        self.assertTrue(s.battlefield)

    def test_departed_target_cancels_timer_without_late_extra_expiry(self):
        s=fixture((EffectSpec('ward','A',(GrantShield('a',3),)),EffectSpec('destroy','A',(DestroyCreature('a'),))))
        s=resolve(s,'ward');s=resolve(s,'destroy')
        self.assertFalse(s.durations);self.assertFalse(s.battlefield)
        s=end(s,'A')
        self.assertFalse(any(e.kind=='duration_expired' for e in s.events))

    def test_until_end_grant_after_end_expiration_is_immediately_spent_at_atomic_cleanup(self):
        # Registered End expiration destroys a witness; its trigger grants an End ward.
        effects=(EffectSpec('late','A',(GrantShield('a',3),)),)
        objects=(MatchObject('a','A','A','creature',Creature('a','A',2,5,5)),
                 MatchObject('w','A','A','creature',Creature('w','A',1,1,1),triggers=(TriggerSpec('defeat','late'),)))
        expiry=TimedEffect(1,'A','A','End',1,expiration_steps=(DestroyCreature('w'),))
        s=fixture(effects,(expiry,),objects);s=end(s,'A')
        self.assertEqual(s.priority.chain[-1].effect_key,'late')
        s=round_pass(s)
        self.assertFalse(s.durations);self.assertFalse(s.battlefield[0].creature.shields)
        s=round_pass(s)
        self.assertEqual(s.turn.active_player,'B')

    def test_earliest_scheduled_expiry_is_consumed_first_by_shared_combat(self):
        effects=(EffectSpec('wards','A',(GrantShield('a',2,'next_start','A'),GrantShield('a',2))),)
        objects=(MatchObject('a','A','A','creature',Creature('a','A',3,5,5)),MatchObject('b','B','B','creature',Creature('b','B',1,8,8)))
        s=resolve(fixture(effects,objects=objects,phase='Combat'),'wards')
        late,early=s.battlefield[0].creature.shields
        self.assertLess(early.expiry_rank,late.expiry_rank)
        s=round_pass(s)
        s=cmd(s,'A','declare_attacks',attacks=[{'attacker_id':'a','target_player':'B'}]);s=round_pass(s)
        s=cmd(s,'B','lock_blockers',assignments=[{'attacker_id':'a','blockers':['b']}]);s=round_pass(s)
        shields=s.battlefield[0].creature.shields
        self.assertEqual(next(x.amount for x in shields if x.shield_id==early.shield_id),1)
        self.assertEqual(next(x.amount for x in shields if x.shield_id==late.shield_id),2)

    def test_malformed_clocks_durations_and_nested_payload_reject(self):
        s=fixture()
        with self.assertRaises(MatchError):validate_match(replace(s,boundary_counts=()))
        with self.assertRaises(MatchError):validate_match(replace(s,boundary_counts=(replace(s.boundary_counts[0],starts=True),)+s.boundary_counts[1:]))
        with self.assertRaises(ValueError):fixture(durations=(TimedEffect(1,'A','unknown','Start',1),))
        with self.assertRaises(ValueError):fixture(durations=(TimedEffect(1,'A','A','Start',1,expiration_steps=(DamagePlayer('A',1),)),))
        with self.assertRaises(UnsupportedMatchRule):fixture(durations=(TimedEffect(1,'A','B','Start',1,expiration_steps=(GrantShield('a',1),)),))

    def test_played_reaction_locks_controller_anchor_and_preserves_card_zones(self):
        definition=CardDefinition('ward','reaction',2,(GrantShield('$target',2,'next_start','$controller'),),target_kind='creature',target_relation='friendly')
        players=tuple(MatchPlayer(DrawPlayer(p,30,(p+'1',p+'2'),(),('ward-card',) if p=='A' else ()),resources=ResourcePool(available=5)) for p in 'ABC')
        obj=MatchObject('a','A','A','creature',Creature('a','A',2,5,5))
        s=new_match(players,(obj,),(),RefillPolicy(20,1),active_player='A',card_definitions=(definition,),card_instances=(CardInstance('ward-card','ward','A'),))
        s=cmd(s,'A','play_card',card_id='ward-card',payment={'ordinary':2,'token_ids':[]},target='a');s=round_pass(s)
        self.assertEqual(s.players[0].cards.discard,('ward-card',))
        self.assertEqual(s.players[0].resources.available,3)
        duration=project_match(s)['durations'][0]
        self.assertEqual((duration['controller'],duration['anchor_player'],duration['occurrence']),('A','A',2))
        self.assertEqual(project_match(s)['battlefield'][0]['creature']['shields'][0]['amount'],2)

    def test_consumed_prevention_drops_its_timer_and_does_not_restore_on_expiry(self):
        effects=(EffectSpec('ward','A',(GrantShield('a',1),)),)
        objects=(MatchObject('a','A','A','creature',Creature('a','A',2,8,8)),MatchObject('b','B','B','creature',Creature('b','B',2,8,8)))
        s=resolve(fixture(effects,objects=objects,phase='Combat'),'ward');s=round_pass(s)
        s=cmd(s,'A','declare_attacks',attacks=[{'attacker_id':'a','target_player':'B'}]);s=round_pass(s)
        s=cmd(s,'B','lock_blockers',assignments=[{'attacker_id':'a','blockers':['b']}]);s=round_pass(s)
        self.assertFalse(s.durations);self.assertFalse(s.battlefield[0].creature.shields)
        self.assertEqual(s.battlefield[0].creature.health,7)
        s=end(s,'A')
        self.assertEqual(s.battlefield[0].creature.health,7)
        self.assertFalse(s.battlefield[0].creature.shields)

    def test_skipped_expiry_can_eliminate_next_planned_seat_and_keep_original_order(self):
        expiry=TimedEffect(1,'A','B','Start',1,expiration_steps=(DamagePlayer('C',30),))
        s=resolve(fixture((EffectSpec('kill','A',(DamagePlayer('B',30),)),),(expiry,)),'kill')
        s=end(s,'A');s=round_pass(s)
        self.assertEqual(s.turn.active_player,'D')
        self.assertTrue(s.players[2].eliminated)
        self.assertFalse(any(e.kind=='turn_start' and e.subject in ('B','C') for e in s.events))
        for seat in ('B','C'):
            count=next(b for b in s.boundary_counts if b.player_id==seat)
            self.assertEqual((count.starts,count.ends),(1,1))

    def test_shield_controller_source_departure_alone_does_not_cancel_granted_duration(self):
        objects=(MatchObject('a','A','A','creature',Creature('a','A',2,5,5)),MatchObject('source','A','A','creature',Creature('source','A',1,2,2)))
        effects=(EffectSpec('ward','A',(GrantShield('a',2,'next_start','A'),),'source'),EffectSpec('destroy','B',(DestroyCreature('source'),)))
        s=fixture(effects,objects=objects)
        s=queue_effect(s,'A','ward',expected_revision=s.revision);s=queue_effect(s,'B','destroy',expected_revision=s.revision)
        s=round_pass(s);s=round_pass(s)
        self.assertEqual(len(s.durations),1)
        self.assertEqual(s.battlefield[0].creature.shields[0].amount,2)

    def test_expiry_records_are_immutable_on_invalid_stale_commands(self):
        s=resolve(fixture((EffectSpec('ward','A',(GrantShield('a',2),)),)),'ward')
        original=s
        with self.assertRaises(ValueError):route_command(s,'A',{'kind':'end_turn','args':{},'expected_revision':s.revision-1})
        self.assertEqual(s,original)
        with self.assertRaises(ValueError):validate_match(replace(s,durations=s.durations+s.durations))

    def test_next_start_anchor_survives_elimination_after_anchors_first_real_turn(self):
        s=fixture((EffectSpec('ward','A',(GrantShield('a',2,'next_start','B'),)),),managed=True)
        s=round_pass(round_pass(s));s=end(s,'A')
        self.assertEqual(s.turn.active_player,'B')
        s=round_pass(round_pass(s))
        for _ in range(3):s=cmd(s,s.priority.holder,'pass')
        s=resolve(s,'ward')
        self.assertEqual(s.durations[0].occurrence,2)
        s=cmd(s,'B','concede',confirmed=True);s=round_pass(s)
        self.assertEqual(s.turn.active_player,'C')
        self.assertTrue(s.durations)
        for actor in ('C','D','A'):
            s=round_pass(round_pass(s));self.assertEqual(s.turn.active_player,actor)
            s=end(s,actor)
        self.assertEqual(s.turn.active_player,'C')
        self.assertFalse(s.durations)
        counter=next(b for b in s.boundary_counts if b.player_id=='B')
        self.assertEqual((counter.starts,counter.ends),(2,2))
        self.assertEqual(s.players[1].resources.own_starts,1)
        self.assertEqual(sum(e.kind=='duration_expired' for e in s.events),1)

    def test_abandoned_turn_expiration_prevents_premature_last_survivor_win(self):
        expiry=TimedEffect(1,'C','A','End',1,expiration_steps=(DamagePlayer('C',30),))
        effects=(EffectSpec('lose','A',(DamagePlayer('A',30),DamagePlayer('B',30),DamagePlayer('D',30))),)
        s=resolve(fixture(effects,(expiry,)),'lose')
        self.assertEqual(s.result,MatchResult('draw'))
        self.assertFalse(any(e.kind=='turn_end' for e in s.events))
        self.assertEqual(sum(e.kind=='duration_expired' for e in s.events),1)


if __name__=='__main__':unittest.main()
