import json
import unittest
from dataclasses import replace
from crucible_play.tactics import evaluate,scenarios,command,round_pass
from crucible_play.opponent import choose_move
from crucible_core.views import project_match


class TacticsTests(unittest.TestCase):
    def test_eight_curated_unravel_decisions_are_legal_and_match_intent(self):
        report=evaluate()
        for row in report['results']:
            with self.subTest(case=row['scenario']):self.assertTrue(row['passed'],row)
        self.assertEqual(report['legal'],8)

    def test_tactical_moves_resolve_through_real_engine_without_mutating_input(self):
        for case in scenarios():
            if case.expected_target is None:continue
            before=case.state;view=project_match(before,'A');original=json.dumps(view,sort_keys=True)
            move=choose_move(view);after=command(before,'A',move[0],**move[1]);after=round_pass(after)
            self.assertFalse(any(o.object_id==case.expected_target for o in after.battlefield))
            self.assertEqual(json.dumps(view,sort_keys=True),original)
            self.assertTrue(any(o.object_id==case.expected_target for o in before.battlefield))

    def test_hidden_zone_permutations_leave_tactical_decisions_unchanged(self):
        for case in scenarios():
            changed=replace(case.state,players=tuple(replace(p,cards=replace(p.cards,deck=tuple(reversed(p.cards.deck)))) for p in case.state.players),shuffle_seed=b'new-secret-seed')
            self.assertEqual(project_match(case.state,'A'),project_match(changed,'A'))
            self.assertEqual(choose_move(project_match(case.state,'A')),choose_move(project_match(changed,'A')))

    def test_permuting_public_objects_does_not_change_tie_breaks(self):
        for case in scenarios():
            changed=replace(case.state,battlefield=tuple(reversed(case.state.battlefield)))
            self.assertEqual(choose_move(project_match(case.state,'A')),choose_move(project_match(changed,'A')))
