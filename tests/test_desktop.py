import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from crucible_lab.desktop import batch_command
from crucible_sim.cli import verify

class DesktopTests(unittest.TestCase):
    def test_child_command_exports_from_path_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix='crucible desktop ') as directory:
            root = Path(directory)
            command = batch_command(root / 'jobs.sqlite', root / 'report', root / 'control.txt', 'groups', 1, 2)
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(verify(root / 'report'), 2)

    def test_invalid_configuration_rejected(self):
        for experiment, budget, limit in [('matches', 1, 1), ('groups', 4, 1), ('matrix', 1, 0)]:
            with self.assertRaises(ValueError):
                batch_command('a', 'b', 'c', experiment, budget, limit)
