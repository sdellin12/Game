"""Dependency-free deterministic combat experiments and portable reports."""

import argparse
import csv
import hashlib
import html
import json
import platform
import sys
import sqlite3
from dataclasses import asdict
from importlib.resources import files
from pathlib import Path

from crucible_core import (
    Attack, CombatError, CombatState, Creature, Player, Shield, resolve_combat,
)

SCHEMA = 1
COVERAGE = {
    "scope": "combat-only",
    "implemented": ["attack-health", "persistent-wounds", "simultaneous-combat",
                    "ordered-multiblock", "exhausted-blocker-multiplier",
                    "breakthrough", "challenge-groups", "numeric-prevention"],
    "excluded": ["full-matches", "turns", "priority-and-reactions", "resources",
                 "leaders", "elimination-cleanup", "triggers", "upgrades",
                 "transform-combine", "bots", "deck-win-rates", "player-shields"],
    "assumptions": [
        "Input is the final public combat snapshot after responses close.",
        "Challenge retaliation defaults to declaration order unless supplied.",
        "Shield expiry_rank is provided; this kernel does not advance time.",
        "Tied shields use shield ID order; per-source prevention is unsupported.",
        "Each creature belongs to one combat group; no cross-group abilities.",
        "Lethal players are reported without full-match cleanup or a winner.",
    ],
}


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def engine_hash() -> str:
    import crucible_core.combat as combat
    source = Path(combat.__file__)
    if source.suffix == '.py' and source.is_file():
        data = source.read_bytes()
    else:
        import marshal
        data = marshal.dumps(combat.__loader__.get_code(combat.__name__))
    return hashlib.sha256(data).hexdigest()


def profiles() -> dict:
    return json.loads(files("crucible_content").joinpath("profiles.json").read_text())


def require_fields(obj: dict, required: set[str], optional: set[str] = frozenset()) -> None:
    if type(obj) is not dict or set(obj) - required - optional or required - set(obj):
        raise CombatError(f"expected fields {sorted(required)}; optional {sorted(optional)}")


def decode(scenario: dict) -> tuple[CombatState, tuple[Attack, ...], tuple]:
    require_fields(scenario, {"schema_version", "state", "attacks"},
                   {"name", "challenge_orders", "required_mechanics"})
    if type(scenario["schema_version"]) is not int or scenario["schema_version"] != SCHEMA:
        raise CombatError("unsupported scenario schema")
    required = scenario.get("required_mechanics", [])
    if type(required) is not list or any(type(m) is not str for m in required):
        raise CombatError("required_mechanics must be a list of names")
    if set(required) - set(COVERAGE["implemented"]):
        raise CombatError("scenario requires unsupported mechanics")
    if "name" in scenario and type(scenario["name"]) is not str:
        raise CombatError("scenario name must be text")
    s = scenario["state"]
    require_fields(s, {"players", "creatures"})
    for collection in (s["players"], s["creatures"], scenario["attacks"]):
        if type(collection) is not list or len(collection) > 64:
            raise CombatError("collections must be lists with at most 64 entries")
    players = []
    for p in s["players"]:
        require_fields(p, {"player_id", "health"})
        players.append(Player(**p))
    creatures = []
    for c in s["creatures"]:
        require_fields(c, {"instance_id", "controller", "attack", "health", "max_health"},
                       {"exhausted", "attack_eligible", "attack_used", "keywords", "shields"})
        c = dict(c)
        for key in ("keywords", "shields"):
            if type(c.get(key, [])) is not list:
                raise CombatError(f"{key} must be a list")
        if any(type(k) is not str for k in c.get("keywords", [])):
            raise CombatError("keywords must be names")
        c["keywords"] = tuple(c.get("keywords", []))
        shields = []
        for sh in c.get("shields", []):
            require_fields(sh, {"shield_id", "amount"}, {"expiry_rank"})
            shields.append(Shield(**sh))
        c["shields"] = tuple(shields)
        creatures.append(Creature(**c))
    attacks = []
    for a in scenario["attacks"]:
        require_fields(a, {"attacker_id", "target_player"},
                       {"blockers", "was_blocked", "challenge_target"})
        a = dict(a)
        if type(a.get("blockers", [])) is not list:
            raise CombatError("blockers must be a list")
        if any(type(i) is not str for i in
               [a["attacker_id"], a["target_player"], *a.get("blockers", [])]):
            raise CombatError("combat IDs must be strings")
        a["blockers"] = tuple(a.get("blockers", []))
        attacks.append(Attack(**a))
    orders = scenario.get("challenge_orders", {})
    if type(orders) is not dict or any(
        type(k) is not str or type(v) is not list or any(type(i) is not str for i in v)
        for k, v in orders.items()
    ):
        raise CombatError("challenge_orders must map target IDs to ordered ID lists")
    return CombatState(tuple(players), tuple(creatures)), tuple(attacks), tuple(
        (k, tuple(v)) for k, v in sorted(orders.items())
    )


def run_scenario(scenario: dict) -> dict:
    state, attacks, orders = decode(scenario)
    outcome = json.loads(canonical(asdict(resolve_combat(state, attacks, orders))))
    identity = digest({"engine": engine_hash(), "input": scenario})
    return {"schema_version": SCHEMA, "job_id": identity,
            "status": "completed_combat", "input": scenario,
            "result": outcome, "result_hash": digest(outcome)}


def encode(state: CombatState, attacks: tuple[Attack, ...], name: str) -> dict:
    # JSON normalization intentionally turns immutable tuples into wire lists.
    return json.loads(canonical({"schema_version": SCHEMA, "name": name,
                                 "state": asdict(state),
                                 "attacks": [asdict(a) for a in attacks]}))


def matrix_scenarios():
    """Finite deterministic single-block encounters, not statistical samples."""
    for a in profiles()["profiles"]:
        for b in profiles()["profiles"]:
            for ah in sorted({1, a["health"]}):
                for bh in sorted({1, b["health"]}):
                    for exhausted in (False, True):
                        for prevention in (0, 2):
                            c = Creature("attacker", "A", a["attack"], ah, a["health"])
                            d = Creature("blocker", "B", b["attack"], bh, b["health"],
                                         exhausted=exhausted,
                                         shields=(Shield("shield", prevention),) if prevention else ())
                            name = (f"{a['id']} vs {b['id']}; HP {ah}/{bh}; "
                                    f"exhausted={exhausted}; shield={prevention}")
                            yield encode(CombatState((Player("A"), Player("B")), (c, d)),
                                         (Attack("attacker", "B", ("blocker",)),), name)


def export(records: list[dict], output: Path, experiment: str, progress: dict | None = None) -> None:
    if output.exists():
        raise CombatError("output already exists; choose a new directory")
    manifest = {"schema_version": SCHEMA, "experiment": experiment,
                "coverage": COVERAGE, "engine_sha256": engine_hash(),
                "profile_pack": profiles(), "profile_sha256": digest(profiles()),
                "runtime": platform.python_version(), "randomness": "none; finite deterministic enumeration",
                "record_count": len(records)}
    summary = {"scope": "combat-only", "completed_combats": len(records),
               "defeated_creatures": sum(len(r["result"]["defeated_creatures"]) for r in records),
               "player_health_damage": sum(e["health_damage"] for r in records
                                           for e in r["result"]["events"]
                                           if e["target_kind"] == "player"),
               "interpretation": "Exact encounter results, not match wins or proof of balance."}
    from .comparisons import comparison_summary
    comparisons = comparison_summary(records)
    summary["comparisons"] = comparisons
    if progress is not None:
        manifest["progress"] = progress
        summary["progress"] = progress
    output.mkdir(parents=True)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with (output / "results.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(canonical(r) + "\n")
    with (output / "results.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["job_id", "name", "status", "defeated_creatures", "player_health_damage", "result_hash"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in records:
            writer.writerow({"job_id": r["job_id"], "name": r["input"].get("name", ""),
                             "status": r["status"],
                             "defeated_creatures": ";".join(r["result"]["defeated_creatures"]),
                             "player_health_damage": sum(e["health_damage"] for e in r["result"]["events"]
                                                         if e["target_kind"] == "player"),
                             "result_hash": r["result_hash"]})
    rows = "".join("<tr><td>" + html.escape(r["input"].get("name", "")) + "</td><td>" +
                   html.escape(", ".join(r["result"]["defeated_creatures"]) or "None") +
                   "</td><td>" + html.escape(r["result_hash"][:12]) + "</td></tr>" for r in records)
    comparison_rows = "".join("<tr>" + "".join("<td>" + html.escape(str(row[key])) + "</td>" for key in
        ("attacking_board", "defending_board", "encounters", "player_damage_range", "attacker_losses_range", "defender_losses_range")) + "</tr>" for row in comparisons["matchups"])
    outcome_rows = "".join("<tr><td>" + html.escape(row["attacking_board"] + " vs " + row["defending_board"]) +
        "</td><td>" + str(o["player_damage"]) + "</td><td>" + str(o["attacker_losses"]) +
        "</td><td>" + str(o["defender_losses"]) + "</td><td>" + str(o["encounters"]) +
        "</td><td>" + html.escape(o["example_job_id"]) + "</td></tr>"
        for row in comparisons["matchups"] for o in row["outcomes"])
    comparison_html = ("<h2>Board comparisons</h2><p>" + html.escape(comparisons["interpretation"]) +
        "</p><table><tr><th>Attacking ATK/HP</th><th>Defending ATK/HP</th><th>Encounters</th><th>Player damage range</th><th>Attacker losses</th><th>Defender losses</th></tr>" + comparison_rows + "</table>"
        "<details><summary>Joint outcomes and example replay IDs</summary>"
        "<p>Counts describe enumerated choices, not probabilities. Search an ID in the replay inspector.</p>"
        "<table><tr><th>Boards</th><th>Player damage</th><th>Attacker losses</th><th>Defender losses</th>"
        "<th>Encounters</th><th>Example replay ID</th></tr>" + outcome_rows + "</table></details>")
    document = ("<!doctype html><html lang='en'><meta charset='utf-8'>"
                "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                "<title>Crucible combat experiment</title><style>"
                "body{font:16px system-ui;max-width:1100px;margin:2rem auto;padding:1rem}"
                "td,th{padding:.5rem;border-bottom:1px solid #ccc;text-align:left}"
                "table{border-collapse:collapse;width:100%}</style><h1>Crucible combat lab</h1>"
                "<p><strong>Combat-only: no full-match win rates or balance claims.</strong></p>"
                f"<p>{len(records)} exact encounters. Engine: {engine_hash()[:12]}.</p>"
                "<h2>Run progress</h2><pre>" + html.escape(json.dumps(progress, indent=2)) +
                "</pre><h2>Coverage and assumptions</h2><pre>" + html.escape(json.dumps(COVERAGE, indent=2)) +
                "</pre>" + comparison_html + "<h2>Encounters</h2><table><thead><tr><th>Scenario</th>"
                "<th>Defeated creatures</th><th>Result hash</th></tr></thead><tbody>" + rows +
                "</tbody></table><p>Inspect results.jsonl for complete input, damage calculations and output.</p></html>")
    (output / "report.html").write_text(document, encoding="utf-8")


def verify(directory: Path) -> int:
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest["engine_sha256"] != engine_hash():
        raise CombatError("engine version differs; replay with the recorded revision")
    count = 0
    ids = set()
    with (directory / "results.jsonl").open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            actual = run_scenario(r["input"])
            if r != actual or r["job_id"] in ids:
                raise CombatError(f"replay divergence/duplicate at record {count + 1}")
            ids.add(r["job_id"])
            count += 1
    if count != manifest["record_count"]:
        raise CombatError("record count mismatch")
    return count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    matrix = sub.add_parser("matrix", help="enumerate approved numeric profiles")
    matrix.add_argument("--output", type=Path, required=True)
    batch = sub.add_parser("batch", help="resume a bounded matrix batch")
    batch.add_argument("--experiment", choices=("matrix", "groups"), default="matrix")
    batch.add_argument("--condition", choices=("baseline", "wounded", "exhausted", "shielded"), default="baseline")
    batch.add_argument("--budget", type=int, default=3)
    batch.add_argument("--checkpoint", type=Path, required=True)
    batch.add_argument("--control-file", type=Path, help="optional UTF-8 file containing pause or cancel")
    batch.add_argument("--limit", type=int, default=100)
    batch.add_argument("--output", type=Path, required=True)
    groups = sub.add_parser("groups", help="equal-budget group combat enumeration")
    groups.add_argument("--condition", choices=("baseline", "wounded", "exhausted", "shielded"), default="baseline")
    groups.add_argument("--budget", type=int, default=3)
    groups.add_argument("--output", type=Path, required=True)
    run = sub.add_parser("run", help="resolve a structured combat scenario")
    run.add_argument("scenario", type=Path)
    run.add_argument("--output", type=Path, required=True)
    replay = sub.add_parser("verify", help="replay every exported encounter and check hashes")
    replay.add_argument("directory", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "verify":
            print(f"Verified {verify(args.directory)} deterministic combat records.")
        else:
            if args.output.exists():
                raise CombatError("output already exists; choose a new directory")
            if args.command == "batch":
                from .batch import run_batch, checkpoint_status
                if args.experiment == "groups":
                    from .groups import group_scenarios
                    inputs = list(group_scenarios(args.budget, args.condition))
                else:
                    if args.condition != 'baseline':
                        raise CombatError('group conditions require --experiment groups')
                    inputs = list(matrix_scenarios())
                stop_status = None
                def show_progress(event):
                    nonlocal stop_status
                    if event["status"] in ("paused", "cancelled"):
                        stop_status = event["status"]
                        print(f"Batch {stop_status}; completed jobs are saved.")
                    elif event["status"] == "error":
                        print(f"Job {event['ordinal']} failed: {event['error']}", file=sys.stderr)
                    elif event["attempted_this_batch"] % 100 == 0:
                        print(f"Attempted {event['attempted_this_batch']} jobs this batch.")
                def control():
                    if args.control_file is None or not args.control_file.exists():
                        return None
                    value = args.control_file.read_text(encoding="utf-8-sig").strip().lower()
                    if value not in ("", "pause", "cancel"):
                        raise CombatError("control file must be empty or contain pause or cancel")
                    return value or None
                records = run_batch(args.checkpoint, args.limit, scenarios=inputs,
                                    progress=show_progress, control=control)
                progress = checkpoint_status(args.checkpoint)
                progress.update(requested_combats=len(inputs), pending_combats=len(inputs) - len(records),
                                run_status=stop_status or ("completed" if len(records) == len(inputs) else "batch_limit"))
                export(records, args.output, f"resumable {args.experiment}; condition={args.condition}", progress=progress)
                print(f"Checkpoint contains {len(records)}/{len(inputs)} combats; report: {args.output}")
                return 2 if progress["failed_jobs_pending_retry"] else (130 if stop_status == "cancelled" else 0)
            if args.command == "groups":
                from .groups import group_scenarios
                inputs = group_scenarios(args.budget, args.condition)
                records = [run_scenario(s) for s in inputs]
                export(records, args.output, f"equal-budget groups: {args.budget}; condition={args.condition}")
                print(f"Exported {len(records)} exact group combats to {args.output}")
                return 0
            inputs = matrix_scenarios() if args.command == "matrix" else [
                json.loads(args.scenario.read_text(encoding="utf-8"))]
            records = [run_scenario(s) for s in inputs]
            export(records, args.output, args.command)
            print(f"Exported {len(records)} combat-only records to {args.output}")
        return 0
    except (CombatError, OSError, sqlite3.Error, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"Experiment rejected: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
