import contextlib
import tempfile
import time
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch
from crucible_lab.desktop import LabWindow

class DesktopControlTests(unittest.TestCase):
    def wait(self, root, window):
        deadline = time.monotonic() + 30
        while window.process is not None and time.monotonic() < deadline:
            root.update()
            time.sleep(.02)
        self.assertIsNone(window.process)

    def test_pause_cancel_resume_and_report_open(self):
        for request, status in [('pause', 'Paused'), ('cancel', 'Cancelled')]:
            with self.subTest(request=request), tempfile.TemporaryDirectory() as directory:
                root = tk.Tk(); root.withdraw()
                window = LabWindow(root)
                try:
                    window.checkpoint.set(str(Path(directory) / 'jobs.sqlite'))
                    window.experiment.set('groups'); window.budget.set('1'); window.limit.set('2')
                    window.start(); window.stop(request)
                    self.wait(root, window)
                    self.assertIn(status, window.status.get())
                    self.assertEqual(str(window.pause['state']), 'disabled')
                    self.assertTrue(window.report.is_file())
                    with patch('crucible_lab.desktop.webbrowser.open') as opened:
                        window.open_report()
                        opened.assert_called_once_with(window.report.as_uri())
                    window.start()
                    self.wait(root, window)
                    self.assertIn('2/18 completed', window.status.get())
                    self.assertEqual(str(window.start_button['state']), 'normal')
                finally:
                    root.destroy()

    def test_close_waits_for_saved_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = tk.Tk(); root.withdraw()
            window = LabWindow(root)
            window.checkpoint.set(str(Path(directory) / 'jobs.sqlite'))
            window.limit.set('10')
            window.start(); window.close()
            self.wait(root, window)
            self.assertTrue(window.closing)
            self.assertTrue(window.report.is_file())

    def test_bad_checkpoint_reports_error_and_restores_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = tk.Tk(); root.withdraw()
            window = LabWindow(root)
            try:
                path = Path(directory) / 'bad.sqlite'
                path.write_text('not a database')
                window.checkpoint.set(str(path))
                window.start(); self.wait(root, window)
                self.assertIn('exit 2', window.status.get())
                self.assertEqual(str(window.start_button['state']), 'normal')
                self.assertIsNone(window.report)
            finally:
                root.destroy()

    def test_desktop_passes_selected_group_condition(self):
        import json
        with tempfile.TemporaryDirectory() as directory:
            root = tk.Tk(); root.withdraw()
            window = LabWindow(root)
            try:
                window.checkpoint.set(str(Path(directory) / 'jobs.sqlite'))
                window.experiment.set('groups'); window.budget.set('1')
                window.condition.set('wounded'); window.limit.set('2')
                window.start(); self.wait(root, window)
                self.assertTrue(window.report.is_file())
                record = json.loads((window.report.parent / 'results.jsonl').read_text().splitlines()[0])
                self.assertTrue(all(c['health'] == 1 for c in record['input']['state']['creatures']))
                self.assertIn('all creatures at 1 HP', record['input']['name'])
            finally:
                root.destroy()
