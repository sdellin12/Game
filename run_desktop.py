"""Launch the desktop combat lab from a source checkout."""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from crucible_lab.desktop import main
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--worker':
        if sys.stdout is None:
            sys.stdout = open(os.environ['CRUCIBLE_WORKER_LOG'], 'a', encoding='utf-8', buffering=1)
            sys.stderr = sys.stdout
        from crucible_sim.cli import main as worker_main
        raise SystemExit(worker_main(sys.argv[2:]))
    main()
