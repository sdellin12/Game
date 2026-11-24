import tempfile
import unittest
from pathlib import Path
from crucible_core import CombatError
from crucible_sim.batch import run_batch
from crucible_sim.cli import matrix_scenarios, run_scenario


class BatchTests(unittest.TestCase):
    def test_resume_matches_uninterrupted_and_completed_resume_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'run.sqlite'
            self.assertEqual(len(run_batch(path, 7)), 7)
            resumed = run_batch(path, 2000)
            self.assertEqual(resumed, [run_scenario(s) for s in matrix_scenarios()])
            self.assertEqual(run_batch(path, 1), resumed)

    def test_invalid_limit_rejected_before_creating_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'run.sqlite'
            with self.assertRaises(CombatError):
                run_batch(path, 0)
            self.assertFalse(path.exists())

    def test_group_resume_and_changed_inputs_reject_without_losing_progress(self):
        from crucible_sim.groups import group_scenarios
        import sqlite3
        from contextlib import closing
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'groups.sqlite'
            inputs = list(group_scenarios(1))
            first = run_batch(path, 3, scenarios=inputs)
            self.assertEqual(len(first), 3)
            with self.assertRaises(CombatError):
                run_batch(path, 2, scenarios=list(reversed(inputs)))
            with closing(sqlite3.connect(path)) as db:
                self.assertEqual(db.execute('SELECT count(*) FROM results').fetchone()[0], 3)
            resumed = run_batch(path, 100, scenarios=inputs)
            self.assertEqual(resumed, [run_scenario(s) for s in inputs])
            self.assertEqual(run_batch(path, 1, scenarios=inputs), resumed)

    def test_group_cli_resume_and_replay(self):
        from crucible_sim.cli import main, verify
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            root = Path(directory)
            for index in range(2):
                output = root / str(index)
                self.assertEqual(main(['batch', '--experiment', 'groups', '--budget', '1',
                    '--checkpoint', str(root / 'jobs.sqlite'), '--limit', '5',
                    '--output', str(output)]), 0)
                self.assertEqual(verify(output), (index + 1) * 5)

    def test_failures_remain_retryable_and_attempt_history_is_retained(self):
        from unittest.mock import patch
        from crucible_sim.batch import checkpoint_status
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'jobs.sqlite'
            inputs = list(matrix_scenarios())[:2]
            events = []
            with patch('crucible_sim.batch.run_scenario', side_effect=CombatError('injected failure')):
                self.assertEqual(run_batch(path, 1, scenarios=inputs, progress=events.append), [])
            status = checkpoint_status(path)
            self.assertEqual(status['error_attempts'], 1)
            self.assertEqual(status['failed_jobs_pending_retry'], 1)
            self.assertEqual(events[0]['status'], 'error')
            self.assertIn('injected failure', status['attempts'][0]['error'])
            self.assertEqual(len(run_batch(path, 2, scenarios=inputs)), 2)
            status = checkpoint_status(path)
            self.assertEqual(status['recorded_attempts'], 3)
            self.assertEqual(status['error_attempts'], 1)
            self.assertEqual(status['failed_jobs_pending_retry'], 0)

    def test_legacy_checkpoint_adds_attempt_table_without_changing_results(self):
        import sqlite3
        from contextlib import closing
        from crucible_sim.batch import checkpoint_status
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'old.sqlite'
            inputs = list(matrix_scenarios())[:2]
            first = run_batch(path, 1, scenarios=inputs)
            with closing(sqlite3.connect(path)) as db:
                db.execute('DROP TABLE attempts')
                db.commit()
            self.assertEqual(checkpoint_status(path)['recorded_attempts'], 0)
            resumed = run_batch(path, 1, scenarios=inputs)
            self.assertEqual(resumed[:1], first)
            self.assertEqual(checkpoint_status(path)['recorded_attempts'], 1)


    def test_pause_cancel_preserve_results_and_resume(self):
        from crucible_sim.batch import checkpoint_status
        inputs = list(matrix_scenarios())[:4]
        for request, status in [('pause', 'paused'), ('cancel', 'cancelled')]:
            with self.subTest(request=request), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'run.sqlite'
                events = []
                def control():
                    return request if len(events) == 2 else None
                partial = run_batch(path, 10, scenarios=inputs, progress=events.append, control=control)
                self.assertEqual(len(partial), 2)
                self.assertEqual(events[-1]['status'], status)
                self.assertEqual(checkpoint_status(path)['error_attempts'], 0)
                self.assertEqual(run_batch(path, 10, scenarios=inputs),
                                 [run_scenario(s) for s in inputs])

    def test_preexisting_cancel_exports_pending_jobs_without_attempts(self):
        from crucible_sim.cli import main
        import contextlib, io, json
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            root = Path(directory)
            control = root / 'control.txt'
            control.write_text('cancel', encoding='utf-8')
            output = root / 'report'
            self.assertEqual(main(['batch', '--experiment', 'groups', '--budget', '1',
                '--checkpoint', str(root / 'jobs.sqlite'), '--control-file', str(control),
                '--output', str(output)]), 130)
            progress = json.loads((output / 'summary.json').read_text())['progress']
            self.assertEqual(progress['pending_combats'], 18)
            self.assertEqual(progress['recorded_attempts'], 0)
            self.assertEqual(progress['run_status'], 'cancelled')


    def test_condition_checkpoint_mismatch_preserves_results(self):
        from crucible_sim.groups import group_scenarios
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'run.sqlite'
            baseline = list(group_scenarios(1))
            first = run_batch(path, 2, scenarios=baseline)
            with self.assertRaises(CombatError):
                run_batch(path, 2, scenarios=list(group_scenarios(1, 'exhausted')))
            resumed = run_batch(path, 2, scenarios=baseline)
            self.assertEqual(resumed[:2], first)
            self.assertEqual(len(resumed), 4)

    def test_matrix_rejects_group_condition_before_creating_checkpoint(self):
        from crucible_sim.cli import main
        import contextlib, io
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stderr(io.StringIO()):
            root = Path(directory)
            self.assertEqual(main(['batch', '--condition', 'shielded', '--checkpoint',
                str(root / 'jobs.sqlite'), '--output', str(root / 'out')]), 2)
            self.assertFalse((root / 'jobs.sqlite').exists())

    def test_subset_checkpoint_cannot_resume_as_all_attack(self):
        from crucible_sim.groups import group_scenarios
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'jobs.sqlite'
            inputs = list(group_scenarios(1, 'mixed', 'subsets'))
            first = run_batch(path, 3, scenarios=inputs)
            with self.assertRaises(CombatError):
                run_batch(path, 1, scenarios=list(group_scenarios(1, 'mixed', 'all')))
            resumed = run_batch(path, 1000, scenarios=inputs)
            self.assertEqual(resumed[:3], first)
            self.assertEqual(resumed, [run_scenario(s) for s in inputs])
