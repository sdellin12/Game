import json
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from crucible_sim.cli import export, run_scenario
from crucible_sim.groups import group_scenarios
from crucible_core import CombatError
from crucible_lab.replay import load_replays, replay_text, ReplayWindow

class ReplayTests(unittest.TestCase):
    def test_verified_load_and_tampered_result_rejected(self):
        records = [run_scenario(s) for s in list(group_scenarios(1))[:2]]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'report'
            export(records, output, 'test')
            self.assertEqual(load_replays(output), records)
            record = records[0]
            text = replay_text(record)
            for marker in ['BEFORE', 'AFTER', 'DAMAGE EVENTS', record['job_id']]:
                self.assertIn(marker, text)
            records[0]['result_hash'] = 'tampered'
            (output / 'results.jsonl').write_text('\n'.join(json.dumps(r) for r in records))
            with self.assertRaises(CombatError):
                load_replays(output)

    def test_filter_selection_and_empty_results(self):
        records = [run_scenario(s) for s in list(group_scenarios(1))[:2]]
        root = tk.Tk(); root.withdraw()
        try:
            window = ReplayWindow(root, records)
            root.update()
            self.assertIn('BEFORE', window.detail.get('1.0', 'end'))
            window.query.set(records[1]['job_id'])
            self.assertEqual(window.visible, [1])
            self.assertIn(records[1]['job_id'], window.detail.get('1.0', 'end'))
            window.query.set('no such encounter')
            self.assertEqual(window.visible, [])
            self.assertEqual(window.detail.get('1.0', 'end').strip(), '')
            empty = ReplayWindow(root, [])
            self.assertEqual(empty.visible, [])
        finally:
            root.destroy()

    def test_desktop_verifies_before_opening_and_reports_tamper(self):
        import time
        from unittest.mock import patch
        from crucible_lab.desktop import LabWindow
        records = [run_scenario(next(group_scenarios(1)))]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'report'
            export(records, output, 'test')
            root = tk.Tk(); root.withdraw(); desktop = LabWindow(root)
            try:
                for tamper in (False, True):
                    if tamper:
                        records[0]['result_hash'] = 'bad'
                        (output / 'results.jsonl').write_text(json.dumps(records[0]) + '\n')
                    with patch('crucible_lab.desktop.filedialog.askdirectory', return_value=str(output)), patch('crucible_lab.desktop.messagebox.showerror') as error:
                        desktop.inspect_replays()
                        deadline = time.monotonic() + 10
                        while str(desktop.inspect_button['state']) == 'disabled' and time.monotonic() < deadline:
                            root.update(); time.sleep(.02)
                        self.assertEqual(str(desktop.inspect_button['state']), 'normal')
                        if tamper:
                            error.assert_called_once()
                            self.assertIn('failed', desktop.status.get())
                        else:
                            error.assert_not_called()
                            self.assertIn('1 verified', desktop.status.get())
            finally:
                root.destroy()
