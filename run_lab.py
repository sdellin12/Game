"""Run directly from a checkout without installing third-party dependencies."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from crucible_sim.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
