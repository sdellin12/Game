import unittest
from dataclasses import replace
from crucible_core.priority import (
    PriorityError, PriorityState, PendingEffect, new_priority, add_effect,
    pass_priority, finish_resolution, reopen_priority, validate_priority,
)


def add(state, actor, key):
    return add_effect(state, actor, key, expected_revision=state.revision)


def passes(state, *actors):
    for actor in actors:
        state = pass_priority(state, actor, expected_revision=state.revision)
    return state


class PriorityTests(unittest.TestCase):
    def test_three_seat_chain_resolves_one_newest_item_and_resets_to_active(self):
        original = new_priority(('A', 'B', 'C'), 'A')
        state = add(original, 'A', 'summon')
        state = add(state, 'B', 'reaction')
        state = passes(state, 'C', 'A', 'B')
        self.assertEqual((state.status, state.resolving.effect_key), ('resolving', 'reaction'))
        self.assertEqual([e.effect_key for e in state.chain], ['summon'])
        state = finish_resolution(state, 2, expected_revision=state.revision)
        self.assertEqual((state.holder, state.status, state.passes), ('A', 'priority', ()))
        state = passes(state, 'A', 'B', 'C')
        self.assertEqual(state.resolving.effect_key, 'summon')
        self.assertEqual(original.chain, ())

    def test_new_effect_discards_earlier_passes(self):
        state = passes(new_priority(('A', 'B', 'C'), 'A'), 'A')
        state = add(state, 'B', 'reaction')
        self.assertEqual((state.holder, state.passes), ('C', ()))
        state = passes(state, 'C', 'A')
        self.assertEqual(state.status, 'priority')
        self.assertEqual(passes(state, 'B').status, 'resolving')

    def test_wrong_actor_stale_revision_and_bad_key_leave_state_unchanged(self):
        state = new_priority(('A', 'B'), 'A')
        for action in (
            lambda: add_effect(state, 'B', 'x', expected_revision=0),
            lambda: pass_priority(state, 'B', expected_revision=0),
            lambda: pass_priority(state, 'A', expected_revision=True),
            lambda: add_effect(state, 'A', '', expected_revision=0),
            lambda: add_effect(state, 'A', 'x', expected_revision=99),
        ):
            with self.assertRaises(PriorityError):
                action()
            self.assertEqual(state, new_priority(('A', 'B'), 'A'))

    def test_no_commands_or_wrong_ack_during_resolution(self):
        state = passes(add(new_priority(('A', 'B'), 'A'), 'A', 'x'), 'B', 'A')
        for action in (
            lambda: add(state, 'A', 'y'),
            lambda: passes(state, 'A'),
            lambda: finish_resolution(state, 9, expected_revision=state.revision),
            lambda: finish_resolution(state, 1, expected_revision=0),
            lambda: reopen_priority(state, 'B', expected_revision=state.revision),
        ):
            with self.assertRaises(PriorityError):
                action()

    def test_empty_chain_closes_only_after_all_seats_pass(self):
        state = passes(new_priority(('A', 'B', 'C'), 'B'), 'B', 'C')
        self.assertEqual((state.holder, state.status), ('A', 'priority'))
        state = passes(state, 'A')
        self.assertEqual((state.status, state.holder, state.chain), ('closed', None, ()))
        with self.assertRaises(PriorityError):
            add(state, 'A', 'x')
        reopened = reopen_priority(state, 'C', expected_revision=state.revision)
        self.assertEqual((reopened.holder, reopened.active_player), ('C', 'C'))
        with self.assertRaises(PriorityError):
            pass_priority(reopened, 'C', expected_revision=0)

    def test_trigger_groups_follow_active_seat_order_not_submission_order(self):
        state = passes(add(new_priority(('A', 'B', 'C'), 'B'), 'B', 'root'), 'C', 'A', 'B')
        state = finish_resolution(state, 1, expected_revision=state.revision,
            trigger_groups=(('A', ('a1', 'a2')), ('C', ('c1',)), ('B', ('b1',))))
        self.assertEqual([(e.controller, e.effect_key) for e in state.chain],
                         [('B', 'b1'), ('C', 'c1'), ('A', 'a1'), ('A', 'a2')])
        self.assertEqual([e.effect_id for e in state.chain], [2, 3, 4, 5])
        state = passes(state, 'B', 'C', 'A')
        self.assertEqual(state.resolving.effect_key, 'a2')

    def test_bad_trigger_groups_reject_atomically(self):
        state = passes(add(new_priority(('A',), 'A'), 'A', 'x'), 'A')
        for groups in ((('A', ('x',)), ('A', ('y',))), (('B', ('x',)),), (('A', ['x']),), (('A', ('',)),)):
            with self.assertRaises(PriorityError):
                finish_resolution(state, 1, expected_revision=state.revision, trigger_groups=groups)
            self.assertEqual(state.resolving.effect_key, 'x')
            self.assertEqual(state.next_effect_id, 2)

    def test_single_seat_still_requires_pass_and_explicit_resolution_ack(self):
        state = add(new_priority(('A',), 'A'), 'A', 'x')
        self.assertEqual(state.status, 'priority')
        state = passes(state, 'A')
        self.assertEqual(state.status, 'resolving')
        state = finish_resolution(state, 1, expected_revision=state.revision)
        self.assertEqual(passes(state, 'A').status, 'closed')

    def test_invalid_states_fail_closed(self):
        valid = new_priority(('A', 'B'), 'A')
        for state in (
            replace(valid, seats=('A', 'A')), replace(valid, seats=()),
            replace(valid, active_player='C'), replace(valid, holder='C'),
            replace(valid, passes=('A',)), replace(valid, revision=True),
            replace(valid, chain=(PendingEffect(1, 'A', 'x'),)),
            replace(valid, chain=(PendingEffect(2, 'A', 'y'), PendingEffect(1, 'B', 'x')), next_effect_id=3),
            replace(valid, status='closed', holder=None, chain=(PendingEffect(1, 'A', 'x'),), next_effect_id=2),
        ):
            with self.assertRaises(PriorityError):
                validate_priority(state)

    def test_id_counter_survives_resolution_and_new_window(self):
        state = passes(add(new_priority(('A',), 'A'), 'A', 'first'), 'A')
        state = finish_resolution(state, 1, expected_revision=state.revision)
        state = passes(state, 'A')
        state = reopen_priority(state, 'A', expected_revision=state.revision)
        state = add(state, 'A', 'second')
        self.assertEqual(state.chain[0].effect_id, 2)
