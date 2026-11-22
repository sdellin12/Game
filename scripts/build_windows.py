"""Build a self-contained Windows folder without bundling reference corpora."""
import subprocess
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--onedir',
    '--windowed', '--name', 'CrucibleLab', '--paths', str(root / 'src'),
    '--add-data', str(root / 'src' / 'crucible_content' / 'profiles.json') + ':crucible_content', '--collect-submodules', 'crucible_sim',
    '--collect-submodules', 'crucible_lab', '--specpath', str(root / 'build'),
    '--distpath', str(root / 'dist'), '--workpath', str(root / 'build' / 'pyinstaller'),
    str(root / 'run_desktop.py')], cwd=root, check=True)

import shutil
bundle = root / 'dist' / 'CrucibleLab'
(bundle / 'START-HERE.txt').write_text(
    'The Crucible Combat Lab\n\nDouble-click CrucibleLab.exe. Keep the _internal folder beside it.\n'
    'Choose a new checkpoint, select an experiment, and click Run / Resume.\n'
    'Keep checkpoints/reports in your Documents folder, outside this app folder.\n'
    'Inspect exported replays opens verified public combat snapshots.\n'
    'Use a new checkpoint for this build; source/build hashes may differ.\n'
    'Combat-only: no full-match win rates or proven balance.\n', encoding='utf-8')
shutil.make_archive(str(root / 'dist' / 'CrucibleLab-Windows'), 'zip', root / 'dist', 'CrucibleLab')
print('Portable ZIP:', root / 'dist' / 'CrucibleLab-Windows.zip')
