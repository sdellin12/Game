import unittest
from dataclasses import replace
from crucible_core.combat import *
from crucible_core.combat_flow import *
from crucible_core.match import *
from crucible_core.turns import DrawPlayer, RefillPolicy


def unit(name, owner, attack=3, health=4, **kw):
    return MatchObject(name,owner,owner,'creature',Creature(name,owner,attack,health,health,**kw))


def game(objects, effects=(), players=('A','B','C')):
    return new_match(tuple(MatchPlayer(DrawPlayer(p,30,(p+'1',p+'2'),())) for p in players),objects,effects,
                     RefillPolicy(20,1),active_player='A',phase='Combat')


def round_pass(s):
    for _ in range(len(s.priority.seats)):
        s=pass_match(s,s.priority.holder,expected_revision=s.revision)
    return s


def declare(s, attacks):
    s=round_pass(s)
    return declare_match_attacks(s,'A',attacks,expected_revision=s.revision)


def lock(s, actor, choices):
    return lock_match_blockers(s,actor,choices,expected_revision=s.revision)


class CombatDeclarationTests(unittest.TestCase):
    def test_attack_commit_spends_exhaust_and_usage_before_any_response(self):
        s=game((unit('a','A'),unit('held','A'),unit('b','B')))
        s=declare(s,(Attack('a','B'),))
        self.assertTrue(s.battlefield[0].creature.exhausted)
        self.assertTrue(s.battlefield[0].creature.attack_used)
        self.assertFalse(s.battlefield[1].creature.exhausted)
        self.assertEqual(s.combat.stage,'attack_responses')
        self.assertEqual(s.priority.holder,'A')
        with self.assertRaises(MatchError):declare_match_attacks(s,'A',(),expected_revision=s.revision)
        with self.assertRaises(MatchError):request_match_end(s,'A',expected_revision=s.revision)

    def test_multiplayer_locks_hidden_until_all_defenders_confirm(self):
        s=game((unit('a','A'),unit('a2','A'),unit('b','B'),unit('c','C')))
        s=round_pass(declare(s,(Attack('a','B'),Attack('a2','C'))))
        self.assertEqual(s.combat.stage,'blocking')
        public=match_combat_view(s)
        cview=match_combat_view(s,'C')
        s=lock(s,'B',(('a',('b',)),))
        self.assertEqual(match_combat_view(s),public)
        self.assertEqual(match_combat_view(s,'C'),cview)
        self.assertEqual(match_combat_view(s,'B')['own_lock'],(('a',('b',)),))
        self.assertFalse(any(e.kind=='blockers_revealed' for e in s.events))
        with self.assertRaises(MatchError):pass_match(s,'A',expected_revision=s.revision)
        s=lock(s,'C',(('a2',()),))
        self.assertEqual(s.combat.stage,'final_responses')
        self.assertEqual(match_combat_view(s)['blockers'],(('a',('b',)),('a2',())))
        self.assertEqual(sum(e.kind=='blockers_revealed' for e in s.events),1)

    def test_bad_partial_duplicate_foreign_and_challenged_blocks_reject(self):
        s=game((unit('a','A'),unit('a2','A',keywords=('challenge',)),unit('b','B'),unit('c','C')))
        s=round_pass(declare(s,(Attack('a','B'),Attack('a2','B',challenge_target='b'))))
        for choices in ((),(('a',('b',)),),(('a',('c',)),),(('a',()),('a',()))):
            with self.assertRaises(ValueError):lock(s,'B',choices)
        with self.assertRaises(ValueError):lock(s,'C',(('a',()),))
        self.assertFalse(s.combat.locks)

    def test_multiblock_explicit_attacker_order_precedes_final_response(self):
        s=game((unit('a','A',attack=4),unit('b','B',health=2),unit('b2','B',health=2)))
        s=lock(round_pass(declare(s,(Attack('a','B'),))),'B',(('a',('b','b2')),))
        self.assertEqual(s.combat.stage,'ordering')
        with self.assertRaises(ValueError):choose_match_combat_order(s,'B','a',('b2','b'),expected_revision=s.revision)
        s=choose_match_combat_order(s,'A','a',('b2','b'),expected_revision=s.revision)
        self.assertEqual(s.combat.stage,'final_responses')
        s=round_pass(s)
        self.assertEqual(s.turn.phase,'MainAfter')
        self.assertEqual(s.combat.stage,'done')
        self.assertEqual(tuple(e.subject for e in s.events if e.kind=='defeat'),('a','b','b2'))

    def test_removed_blocker_stays_blocked_with_and_without_breakthrough(self):
        for keywords,expected in (((),30),(('breakthrough',),27)):
            s=game((unit('a','A',keywords=keywords),unit('b','B')),
                   (EffectSpec('remove','A',(DestroyCreature('b'),)),))
            s=lock(round_pass(declare(s,(Attack('a','B'),))),'B',(('a',('b',)),))
            s=queue_effect(s,'A','remove',expected_revision=s.revision)
            s=round_pass(s)
            s=resolve_current(s,expected_revision=s.revision)
            self.assertTrue(s.combat.attacks[0].was_blocked)
            s=round_pass(s)
            self.assertEqual(s.players[1].cards.health,expected)
            self.assertTrue(s.battlefield[0].creature.exhausted)
            self.assertTrue(s.battlefield[0].creature.attack_used)

    def test_missing_challenge_target_misses_without_refunding_attack(self):
        s=game((unit('a','A',keywords=('challenge',)),unit('b','B')),
               (EffectSpec('remove','A',(DestroyCreature('b'),)),))
        s=declare(s,(Attack('a','B',challenge_target='b'),))
        s=queue_effect(s,'A','remove',expected_revision=s.revision)
        s=round_pass(s)
        s=resolve_current(s,expected_revision=s.revision)
        s=round_pass(s)
        self.assertEqual(s.combat.stage,'final_responses')
        s=round_pass(s)
        self.assertTrue(any(e.kind=='combat_miss' and e.subject=='a' for e in s.events))
        self.assertTrue(s.battlefield[0].creature.attack_used)
        self.assertEqual(s.players[1].cards.health,30)

    def test_challenge_target_controller_chooses_group_retaliation_order(self):
        s=game((unit('a','A',keywords=('challenge',)),unit('a2','A',keywords=('challenge',)),unit('b','B',attack=5)))
        s=round_pass(declare(s,(Attack('a','B',challenge_target='b'),Attack('a2','B',challenge_target='b'))))
        self.assertEqual(s.combat.stage,'ordering')
        with self.assertRaises(ValueError):choose_match_combat_order(s,'A','b',('a2','a'),expected_revision=s.revision)
        s=choose_match_combat_order(s,'B','b',('a2','a'),expected_revision=s.revision)
        s=round_pass(s)
        self.assertNotIn('a2',tuple(o.object_id for o in s.battlefield))
        self.assertEqual(s.battlefield[0].creature.health,3)

    def test_concession_invalidates_unrevealed_batch_and_requires_fresh_locks(self):
        s=game((unit('a','A'),unit('a2','A'),unit('b','B'),unit('c','C')))
        s=round_pass(declare(s,(Attack('a','B'),Attack('a2','C'))))
        s=lock(s,'B',(('a',('b',)),))
        s=concede(s,'C',expected_revision=s.revision)
        self.assertEqual(s.combat.stage,'attack_responses')
        self.assertFalse(s.combat.locks)
        s=round_pass(s)
        self.assertEqual(s.combat.defenders,('B',))
        self.assertNotIn('blockers',match_combat_view(s))
        s=lock(s,'B',(('a',()),))
        s=round_pass(s)
        self.assertEqual(s.players[1].cards.health,27)

    def test_zero_attack_choice_advances_and_cannot_redeclare(self):
        s=game((unit('held','A'),))
        s=round_pass(declare(s,()))
        self.assertEqual(s.combat.stage,'final_responses')
        s=round_pass(s)
        self.assertEqual(s.turn.phase,'MainAfter')
        self.assertFalse(s.battlefield[0].creature.attack_used)
        with self.assertRaises(MatchError):declare_match_attacks(s,'A',(),expected_revision=s.revision)

    def test_committed_damage_matches_legacy_adapter_across_supported_cases(self):
        # Both APIs use exactly the same kernel; readiness is committed at different times.
        for exhausted in (False,True):
            for keywords in ((),('breakthrough',)):
                for attack in (0,1,4,9):
                    snapshot=CombatState((Player('A'),Player('B')),
                        (Creature('a','A',attack,5,5,keywords=keywords),Creature('b','B',2,3,3,exhausted=exhausted,shields=(Shield('s',1),))))
                    assignment=(Attack('a','B',('b',),True),)
                    expected=resolve_combat(snapshot,assignment)
                    committed,flow=commit_attacks(snapshot,'A',(Attack('a','B'),))
                    flow=lock_blockers(committed,begin_blocking(committed,flow),'B',(('a',('b',)),))
                    actual=resolve_committed(committed,replace(flow,stage='final_responses'))
                    self.assertEqual(actual,expected)

    def test_stale_locks_and_repeated_locks_leave_private_state_unchanged(self):
        s=game((unit('a','A'),unit('a2','A'),unit('b','B'),unit('c','C')))
        s=round_pass(declare(s,(Attack('a','B'),Attack('a2','C'))))
        rev=s.revision
        s=lock(s,'B',(('a',()),))
        for actor in ('B','C'):
            with self.assertRaises(ValueError):lock_match_blockers(s,actor,(),expected_revision=rev)
        with self.assertRaises(ValueError):lock(s,'B',(('a',()),))
        self.assertEqual(len(s.combat.locks),1)

    def test_readied_attacker_is_not_exhausted_again_at_damage(self):
        original=CombatState((Player('A'),Player('B')),(Creature('a','A',3,4,4),))
        snapshot,flow=commit_attacks(original,'A',(Attack('a','B'),))
        flow=lock_blockers(snapshot,begin_blocking(snapshot,flow),'B',(('a',()),))
        snapshot=replace(snapshot,creatures=(replace(snapshot.creatures[0],exhausted=False),))
        result=resolve_committed(snapshot,replace(flow,stage='final_responses'))
        self.assertFalse(result.state.creatures[0].exhausted)
        self.assertTrue(result.state.creatures[0].attack_used)
        self.assertEqual(result.state.players[1].health,27)

    def test_lost_challenge_permission_does_not_cancel_committed_mode(self):
        original=CombatState((Player('A'),Player('B')),
                            (Creature('a','A',3,4,4,keywords=('challenge',)),Creature('b','B',1,4,4)))
        snapshot,flow=commit_attacks(original,'A',(Attack('a','B',challenge_target='b'),))
        snapshot=replace(snapshot,creatures=(replace(snapshot.creatures[0],keywords=()),snapshot.creatures[1]))
        result=resolve_committed(snapshot,replace(begin_blocking(snapshot,flow),stage='final_responses'))
        self.assertEqual(result.state.creatures[1].health,1)

    def test_own_turn_depletion_waits_for_already_committed_combat(self):
        s=game((unit('a','A'),),effects=(EffectSpec('draw','A',(DrawCards('A',2),)),))
        s=declare(s,(Attack('a','B'),))
        s=queue_effect(s,'A','draw',expected_revision=s.revision)
        s=round_pass(s)
        s=resolve_current(s,expected_revision=s.revision)
        self.assertTrue(s.players[0].cards.end_turn_requested)
        s=round_pass(s)
        self.assertEqual(s.combat.stage,'blocking')
        s=lock(s,'B',(('a',()),))
        s=round_pass(s)
        self.assertEqual(s.players[1].cards.health,27)
        s=round_pass(s)
        self.assertEqual(s.turn.active_player,'B')

    def test_control_changed_attacker_drops_and_challenge_target_change_misses(self):
        original=CombatState((Player('A'),Player('B'),Player('C')),
                            (Creature('a','A',3,4,4,keywords=('challenge',)),Creature('b','B',1,4,4)))
        snapshot,flow=commit_attacks(original,'A',(Attack('a','B',challenge_target='b'),))
        changed=replace(snapshot,creatures=(snapshot.creatures[0],replace(snapshot.creatures[1],controller='C')))
        result=resolve_committed(changed,replace(begin_blocking(changed,flow),stage='final_responses'))
        self.assertEqual(result.misses,('a',))
        self.assertEqual(result.state.creatures[1].health,4)
        changed=replace(snapshot,creatures=(replace(snapshot.creatures[0],controller='C'),snapshot.creatures[1]))
        result=resolve_committed(changed,replace(begin_blocking(changed,flow),stage='final_responses'))
        self.assertFalse(result.events)
        self.assertTrue(result.state.creatures[0].attack_used)

    def test_concession_during_ordering_invalidates_order_and_lock_batch(self):
        s=game((unit('a','A'),unit('b','B'),unit('b2','B'),unit('c','C')))
        s=lock(round_pass(declare(s,(Attack('a','B'),))),'B',(('a',('b','b2')),))
        self.assertEqual(s.combat.stage,'ordering')
        s=concede(s,'C',expected_revision=s.revision)
        self.assertEqual(s.combat.stage,'attack_responses')
        s=round_pass(s)
        self.assertEqual(s.combat.stage,'blocking')
        self.assertFalse(s.combat.locks)
        with self.assertRaises(ValueError):choose_match_combat_order(s,'A','a',('b','b2'),expected_revision=s.revision)

    def test_malformed_committed_flow_is_rejected_before_command(self):
        s=declare(game((unit('a','A'),)),(Attack('a','B'),))
        for malformed in (replace(s.combat,stage='skip_damage'),replace(s.combat,active_player='B'),
                          replace(s.combat,attacks=s.combat.attacks+s.combat.attacks)):
            with self.assertRaises(ValueError):pass_match(replace(s,combat=malformed),'A',expected_revision=s.revision)

    def test_explicit_empty_block_lock_stays_unblocked(self):
        s=game((unit('a','A'),unit('b','B')))
        s=lock(round_pass(declare(s,(Attack('a','B'),))),'B',(('a',()),))
        self.assertFalse(s.combat.attacks[0].was_blocked)
        s=round_pass(s)
        self.assertEqual(s.players[1].cards.health,27)


if __name__=='__main__':unittest.main()
