"""Launch the desktop combat lab from a source checkout."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from crucible_lab.desktop import main
if __name__ == '__main__':
    main()
