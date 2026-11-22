"""Launch the local pass-and-play rules harness from this source checkout."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from crucible_play.desktop import main
if __name__=='__main__':main()
