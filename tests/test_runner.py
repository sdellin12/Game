import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from crucible_core import CombatError
from crucible_sim.cli import export, main, matrix_scenarios, profiles, run_scenario, verify


class RunnerTests(unittest.TestCase):
    def test_nine_approved_profiles(self):
        self.assertEqual([(p["cost"], p["attack"], p["health"]) for p in profiles()["profiles"]],
                         [(1, 2, 1), (1, 1, 2), (1, 0, 3),
                          (2, 3, 2), (2, 2, 3), (2, 1, 4),
                          (3, 4, 3), (3, 3, 4), (3, 2, 5)])

    def test_finite_matrix_is_unique_and_repeatable(self):
        inputs = list(matrix_scenarios())
        self.assertEqual(len(inputs), 1156)
        records = [run_scenario(s) for s in inputs]
        self.assertEqual(len({r["job_id"] for r in records}), 1156)
        self.assertEqual(records, [run_scenario(s) for s in inputs])

    def test_export_replay_and_tamper_detection(self):
        records = [run_scenario(next(matrix_scenarios()))]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "run"
            export(records, out, "test")
            self.assertEqual(verify(out), 1)
            for name in ("manifest.json", "summary.json", "results.csv", "results.jsonl", "report.html"):
                self.assertTrue((out / name).exists())
            records[0]["result"]["misses"] = ["tampered"]
            (out / "results.jsonl").write_text(json.dumps(records[0]) + "\n", encoding="utf-8")
            with self.assertRaises(CombatError):
                verify(out)

    def test_html_escapes_names_and_existing_output_is_not_overwritten(self):
        scenario = next(matrix_scenarios())
        scenario["name"] = "<script>alert('no')</script>"
        record = run_scenario(scenario)
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "run"
            export([record], out, "test")
            text = (out / "report.html").read_text(encoding="utf-8")
            self.assertNotIn("<script>", text)
            self.assertIn("&lt;script&gt;", text)
            with self.assertRaises(CombatError):
                export([record], out, "test")

    def test_unknown_mechanics_and_fields_fail_closed(self):
        for mutate in (
            lambda s: s.update(required_mechanics=["leaders"]),
            lambda s: s["state"]["creatures"][0].update(defense=2),
            lambda s: s.update(schema_version=True),
            lambda s: s["attacks"][0].update(blockers="blocker"),
        ):
            s = next(matrix_scenarios())
            mutate(s)
            with self.assertRaises(CombatError):
                run_scenario(s)

    def test_cli_example_and_replay(self):
        example = Path(__file__).resolve().parents[1] / "examples" / "breakthrough.json"
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()):
            out = str(Path(d) / "example")
            self.assertEqual(main(["run", str(example), "--output", out]), 0)
            self.assertEqual(main(["verify", out]), 0)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(["run", str(example), "--output", out]), 2)


if __name__ == "__main__":
    unittest.main()
