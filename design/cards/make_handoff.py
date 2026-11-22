"""Package only public design sources and examples for a separate LLM/editor."""
import hashlib
import json
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[2]
files=[ROOT/'docs'/name for name in ('CARD_DESIGN.md','CARD_INFORMATION_CONTRACT.md','CARD_CONTENT_EXAMPLES.md','RULES_DRAFT.md','REQUIREMENTS.md','UX_CONTENT_PLAN.md')]
files += [p for p in (ROOT/'design/cards').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.zip')]
files += [ROOT/'tests/test_card_templates.py']
files=sorted(set(files))
manifest={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
out=ROOT/'dist'/'CardTemplate-Handoff-v1.zip'
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
    for path in files:
        archive.write(path,str(path.relative_to(ROOT)))
    archive.writestr('design-manifest.json',json.dumps({'version':1,'files':manifest},indent=2))
print(f'Packaged {len(files)} design files: {out}')
