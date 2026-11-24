import json,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
from scripts.audit_docs import broken_links,make_bundle,render_index


class DocumentationAuditTests(unittest.TestCase):
    def test_local_links_and_headings_are_checked_without_treating_code_as_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'docs').mkdir()
            (root/'README.md').write_text('[guide](docs/Guide.md#valid-heading)\n```text\n[x](missing.md)\n```\n',encoding='utf-8')
            (root/'docs/Guide.md').write_text('# Valid heading\n[web](https://example.invalid/x)\n',encoding='utf-8')
            self.assertFalse(broken_links(root))
            (root/'docs/Guide.md').write_text('# Changed\n[bad](missing.md)\n',encoding='utf-8')
            self.assertEqual(len(broken_links(root)),2)
            self.assertIn('docs/Guide.md',render_index(root))

    def test_documentation_bundle_omits_saves_art_references_and_interview(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ('README.md','docs/AI_HANDOFF.md','docs/ANSWERS.md','references/tcg/README.md','design/cards/art/private.png','private.crucible.json','design/packages/discard_draw.json'):
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('{}',encoding='utf-8')
            with patch('scripts.audit_docs.subprocess.check_output',side_effect=['abc123\n','review\n']):path,_=make_bundle(root)
            with zipfile.ZipFile(path) as bundle:
                names=bundle.namelist();manifest=json.loads(bundle.read('handoff-manifest.json'))
                self.assertIn('docs/AI_HANDOFF.md',names);self.assertIn('design/packages/discard_draw.json',names)
                self.assertFalse(any('private' in n or 'ANSWERS' in n or n.startswith('references/') for n in names))
                self.assertEqual(manifest['kind'],'documentation-only');self.assertEqual(manifest['commit'],'abc123')
