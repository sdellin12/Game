import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from crucible_play.migrate import migrate_save,V1_BUILDS,main
from crucible_play.persistence import load_session,save_session,SaveError,_canonical,_decode,_publish_new
from test_persistence import prepared,cmd

FIXTURE=Path(__file__).parent/'fixtures'/'save_v1_9b0f7f5.json.gz'
V2_FIXTURE=Path(__file__).parent/'fixtures'/'save_v2_before_exile.json.gz'


def legacy_lobby(value):
    # Independent expected schema delta: only the one authoritative match gains empty exile.
    value=json.loads(json.dumps(value));match=value['fields']['match']
    if match is not None:match['fields']['exiled']={'tuple':[]}
    return _decode(value)


def sealed(doc):
    doc['checksum']=hashlib.sha256(_canonical({k:v for k,v in doc.items() if k!='checksum'})).hexdigest()
    return json.dumps(doc).encode()


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.source=Path(self.tmp.name)/'old.crucible.json'
        self.output=Path(self.tmp.name)/'new.crucible.json'
        self.cases=json.loads(gzip.decompress(FIXTURE.read_bytes()))

    def test_archived_v1_cases_preserve_original_state_and_next_command_results(self):
        for case in self.cases:
            with self.subTest(case=case['name']):
                self.source.write_bytes(sealed(case['save']));original=self.source.read_bytes()
                if self.output.exists():self.output.unlink()
                migrate_save(self.source,self.output)
                s=load_session(self.output)
                self.assertTrue(s.paused);self.assertIsNone(s.view().get('you'))
                self.assertEqual(s._lobby,legacy_lobby(case['save']['payload']['lobby']))
                self.assertEqual(s.bots,frozenset(case['save']['payload']['bots']))
                s.resume();s.send(case['actor'],case['packet'])
                self.assertEqual(s._lobby,legacy_lobby(case['expected']))
                self.assertEqual(self.source.read_bytes(),original)
                self.assertEqual(json.loads(self.output.read_text())['schema_version'],3)

    def test_v1_load_requires_explicit_conversion(self):
        self.source.write_bytes(sealed(self.cases[0]['save']))
        with self.assertRaisesRegex(SaveError,'explicit conversion'):load_session(self.source)

    def test_known_newline_builds_are_explicitly_allowlisted(self):
        for runtime,rules in V1_BUILDS.items():
            doc=self.cases[0]['save'];doc['runtime_hash']=runtime
            doc['payload']['lobby']['fields']['rules_hash']=rules
            self.source.write_bytes(sealed(doc))
            if self.output.exists():self.output.unlink()
            migrate_save(self.source,self.output);self.assertTrue(load_session(self.output).paused)

    def test_unknown_build_rules_corruption_and_future_schema_never_write_output(self):
        edits=(lambda d:d.update(runtime_hash='0'*64),
               lambda d:d['payload']['lobby']['fields'].update(rules_hash='0'*64),
               lambda d:d.update(schema_version=999),
               lambda d:d['payload']['lobby'].update(record='ReturnCreatureToHand'),
               lambda d:d['payload']['lobby']['fields'].update(revision=True),
               lambda d:d['payload'].update(bots=['unknown']))
        for edit in edits:
            doc=json.loads(gzip.decompress(FIXTURE.read_bytes()))[0]['save'];edit(doc)
            self.source.write_bytes(sealed(doc));before=self.source.read_bytes()
            with self.assertRaises(SaveError):migrate_save(self.source,self.output)
            self.assertEqual(self.source.read_bytes(),before);self.assertFalse(self.output.exists())
        self.source.write_bytes(b'bad checksum')
        with self.assertRaises(SaveError):migrate_save(self.source,self.output)

    def test_existing_destination_and_input_are_preserved(self):
        self.source.write_bytes(sealed(self.cases[0]['save']));before=self.source.read_bytes()
        self.output.write_bytes(b'existing family file')
        with self.assertRaises(SaveError):migrate_save(self.source,self.output)
        with self.assertRaises(SaveError):migrate_save(self.source,self.source)
        self.assertEqual(self.source.read_bytes(),before)
        self.assertEqual(self.output.read_bytes(),b'existing family file')

    def test_failed_publication_cleans_temp_and_preserves_original(self):
        self.source.write_bytes(sealed(self.cases[0]['save']));before=self.source.read_bytes()
        with patch('crucible_play.persistence._publish_new',side_effect=OSError('injected publication failure')):
            with self.assertRaises(SaveError):migrate_save(self.source,self.output)
        self.assertFalse(self.output.exists());self.assertEqual(self.source.read_bytes(),before)
        self.assertEqual(set(self.source.parent.iterdir()),{self.source})

    def test_destination_created_during_conversion_is_never_overwritten(self):
        self.source.write_bytes(sealed(self.cases[0]['save']))
        def concurrent(src,dst):
            Path(dst).write_bytes(b'concurrent save');return _publish_new(src,dst)
        with patch('crucible_play.persistence._publish_new',side_effect=concurrent):
            with self.assertRaises(SaveError):migrate_save(self.source,self.output)
        self.assertEqual(self.output.read_bytes(),b'concurrent save')
        self.assertFalse(list(self.source.parent.glob('*.tmp')))

    def test_current_contract_loads_after_runtime_change_without_redeal(self):
        s=prepared();save_session(s,self.output)
        with patch('crucible_play.persistence.runtime_fingerprint',return_value='1'*64):
            loaded=load_session(self.output)
            self.assertEqual(loaded._lobby,s._lobby);self.assertEqual(loaded.runtime_hash,'1'*64)
            loaded.resume();actor=s.view()['priority']['holder']
            cmd(s,actor,'pass');cmd(loaded,actor,'pass');self.assertEqual(s._lobby,loaded._lobby)

    def test_current_schema_requires_matching_python_shuffle_runtime(self):
        save_session(prepared(),self.output)
        with patch('crucible_play.persistence.python_runtime',return_value='different-python'):
            with self.assertRaisesRegex(SaveError,'matching Python'):load_session(self.output)

    def test_cli_entry_creates_separate_loadable_output(self):
        self.source.write_bytes(sealed(self.cases[0]['save']))
        with patch('builtins.print') as output:main([str(self.source),str(self.output)])
        self.assertTrue(load_session(self.output).paused);output.assert_called_once()

    def test_archived_v2_cases_convert_only_empty_exile_and_preserve_next_results(self):
        for case in json.loads(gzip.decompress(V2_FIXTURE.read_bytes())):
            with self.subTest(case=case['name']):
                self.source.write_bytes(sealed(case['save']));before=self.source.read_bytes()
                with self.assertRaisesRegex(SaveError,'explicit conversion'):load_session(self.source)
                if self.output.exists():self.output.unlink()
                migrate_save(self.source,self.output);s=load_session(self.output)
                self.assertTrue(s.paused);self.assertEqual(s._lobby,legacy_lobby(case['save']['payload']['lobby']))
                self.assertEqual(s._lobby.match.exiled,());self.assertEqual(s.bots,frozenset(case['save']['payload']['bots']))
                s.resume();s.send(case['actor'],case['packet']);self.assertEqual(s._lobby,legacy_lobby(case['expected']))
                self.assertEqual(self.source.read_bytes(),before)

    def test_v2_unknown_contract_python_and_premature_exile_never_publish(self):
        edits=(lambda d:d.update(compatibility_version=999),lambda d:d.update(python_runtime='other-python'),
               lambda d:d['payload']['lobby']['fields']['match']['fields'].update(exiled={'tuple':[]}),
               lambda d:d['payload']['lobby'].update(record='ExileCreature'),
               lambda d:d['payload']['lobby']['fields']['match']['fields'].pop('shuffle_counter'))
        for edit in edits:
            doc=json.loads(gzip.decompress(V2_FIXTURE.read_bytes()))[0]['save'];edit(doc)
            self.source.write_bytes(sealed(doc));before=self.source.read_bytes()
            with self.assertRaises(SaveError):migrate_save(self.source,self.output)
            self.assertFalse(self.output.exists());self.assertEqual(self.source.read_bytes(),before)

    def test_v2_compatible_source_hash_change_still_converts(self):
        doc=json.loads(gzip.decompress(V2_FIXTURE.read_bytes()))[0]['save'];doc['runtime_hash']='0'*64
        self.source.write_bytes(sealed(doc));migrate_save(self.source,self.output)
        self.assertEqual(load_session(self.output)._lobby,legacy_lobby(doc['payload']['lobby']))

    def test_v2_lobby_and_partial_opening_convert_without_redealing(self):
        from crucible_play.session import HarnessSession
        from test_persistence import ready
        archived=json.loads(gzip.decompress(V2_FIXTURE.read_bytes()))[0]['save']
        pack=legacy_lobby(archived['payload']['lobby']).pack
        for opening in (False,True):
            s=HarnessSession(seed=b'legacy-opening-seed-1234',pack=pack)
            if opening:
                ready(s);s.start('P1',expected_revision=s.view()['revision'])
                s.redraw('P1',(s.view('P1')['you']['hand'][0]['instance_id'],),expected_revision=s.view()['revision'])
            if self.output.exists():self.output.unlink()
            save_session(s,self.source)
            doc=json.loads(self.source.read_text());doc['schema_version']=2;self.source.write_bytes(sealed(doc))
            before=self.source.read_bytes();migrate_save(self.source,self.output);loaded=load_session(self.output)
            self.assertEqual(loaded._lobby,s._lobby);self.assertEqual(self.source.read_bytes(),before)
            if opening:
                loaded.resume()
                for game in (s,loaded):game.redraw('P2',(),expected_revision=game.view()['revision'])
                self.assertEqual(loaded._lobby,s._lobby)
