"""Bounded sequential jobs with atomic, version-pinned checkpoints."""
from contextlib import closing
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from crucible_core import CombatError
from .cli import canonical, digest, engine_hash, matrix_scenarios, profiles, run_scenario


def run_batch(path: Path, limit: int = 100, *, scenarios=None, progress=None, control=None) -> list[dict]:
    if type(limit) is not int or limit < 1:
        raise CombatError("limit must be a positive integer")
    path.parent.mkdir(parents=True, exist_ok=True)
    inputs = list(matrix_scenarios() if scenarios is None else scenarios)
    pin = canonical({"schema": 1, "engine": engine_hash(),
                     "profiles": digest(profiles()), "inputs": digest(inputs)})
    with closing(sqlite3.connect(path)) as db:
        db.execute("CREATE TABLE IF NOT EXISTS metadata (id INTEGER PRIMARY KEY, pin TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS results (ordinal INTEGER PRIMARY KEY, record TEXT NOT NULL)")
        row = db.execute("SELECT pin FROM metadata WHERE id=1").fetchone()
        if row and row[0] != pin:
            raise CombatError("checkpoint inputs or engine differ; use a new checkpoint")
        if not row:
            db.execute("INSERT INTO metadata VALUES (1, ?)", (pin,))
            db.commit()
        saved = dict(db.execute("SELECT ordinal, record FROM results"))
        if set(saved) - set(range(len(inputs))):
            raise CombatError("invalid checkpoint job ordinal")
        for ordinal, record in saved.items():
            if json.loads(record) != run_scenario(inputs[ordinal]):
                raise CombatError("checkpoint replay divergence")
        db.execute("CREATE TABLE IF NOT EXISTS attempts (id INTEGER PRIMARY KEY, ordinal INTEGER NOT NULL, status TEXT NOT NULL, error TEXT, recorded_at TEXT NOT NULL)")
        db.commit()
        completed = 0
        for ordinal, scenario in enumerate(inputs):
            if ordinal in saved:
                continue
            request = control() if control else None
            if request not in (None, "pause", "cancel"):
                raise CombatError("control must return None, pause or cancel")
            if request:
                if progress:
                    progress({"status": "paused" if request == "pause" else "cancelled",
                              "attempted_this_batch": completed})
                break
            error = None
            try:
                record = canonical(run_scenario(scenario))
                status = "completed"
            except Exception as exc:
                status = "error"
                error = f"{type(exc).__name__}: {exc}"
            if status == "completed":
                db.execute("INSERT INTO results VALUES (?, ?)", (ordinal, record))
            db.execute("INSERT INTO attempts (ordinal, status, error, recorded_at) VALUES (?, ?, ?, ?)",
                       (ordinal, status, error, datetime.now(timezone.utc).isoformat()))
            db.commit()  # Result and attempt commit together.
            completed += 1
            if progress:
                progress({"ordinal": ordinal, "status": status, "error": error,
                          "attempted_this_batch": completed})
            if completed >= limit:
                break
        return [json.loads(row[0]) for row in db.execute(
            "SELECT record FROM results ORDER BY ordinal")]


def checkpoint_status(path: Path) -> dict:
    """Read progress without creating a missing checkpoint or migrating old ones."""
    if not path.is_file():
        raise CombatError("checkpoint does not exist")
    with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)) as db:
        completed = db.execute('SELECT count(*) FROM results').fetchone()[0]
        exists = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='attempts'").fetchone()
        attempts = [dict(zip(('ordinal', 'status', 'error', 'recorded_at'), row))
                    for row in db.execute('SELECT ordinal, status, error, recorded_at FROM attempts ORDER BY id')] if exists else []
        failed = {a['ordinal'] for a in attempts if a['status'] == 'error'}
        finished = {r[0] for r in db.execute('SELECT ordinal FROM results')}
        return {"completed_combats": completed, "recorded_attempts": len(attempts),
                "error_attempts": sum(a['status'] == 'error' for a in attempts),
                "failed_jobs_pending_retry": len(failed - finished), "attempts": attempts}
