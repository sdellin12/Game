import importlib.util
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('card_render', ROOT/'design/cards/render.py')
renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
NS={'s':'http://www.w3.org/2000/svg'}

class CardTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards=json.loads((ROOT/'design/cards/fixtures.json').read_text(encoding='utf-8'))['cards']

    def test_both_styles_preserve_identical_visible_information(self):
        for card in self.cards:
            trees=[ET.fromstring(renderer.render(card,style)) for style in ('standard','full-art')]
            texts=[[n.text for n in tree.findall('.//s:text',NS)] for tree in trees]
            self.assertEqual(texts[0],texts[1],card['id'])
            for tree in trees:
                self.assertEqual(tree.attrib['viewBox'],'0 0 750 1050')
                for slot in ('identity','access-cost','artwork','rules-panel','stats','live-status'):
                    self.assertIsNotNone(tree.find(f".//*[@id='{slot}']"))

    def test_conditional_stats_and_access_markers(self):
        for card in self.cards:
            tree=ET.fromstring(renderer.render(card,'standard'))
            stats=tree.find(".//*[@id='stats']")
            labels=[n.text for n in stats.findall('s:text',NS)]
            if 'attack' in card:
                self.assertIn(card['attack'],labels)
                self.assertIn(card['health'],labels)
            else:
                self.assertEqual(labels,[])
            if card['id'] in ('hauler','token','resource'):
                self.assertNotEqual(card['access'],'0')
        pebble=next(c for c in self.cards if c['id']=='pebble')
        self.assertIn('>0</text>',renderer.render(pebble,'full-art'))

    def test_text_overflow_and_invalid_asset_paths_reject(self):
        card=dict(self.cards[0],abilities=[{'text':'words '*200}])
        with self.assertRaises(ValueError):renderer.render(card,'standard')
        with self.assertRaises(ValueError):renderer.render(dict(self.cards[0],art_image='../README.md'),'standard')
        with self.assertRaises(ValueError):renderer.render(dict(self.cards[0],id='../escape'),'standard')
        with self.assertRaises(ValueError):renderer.render(self.cards[0],'unknown')
        with self.assertRaises(ValueError):renderer.render(dict(self.cards[0],name='A'*100),'standard')

    def test_long_name_and_text_escaping(self):
        card=dict(self.cards[0],name='Aster, Guardian of the Seventh Relic-Ring')
        tree=ET.fromstring(renderer.render(card,'standard'))
        self.assertIn('Seventh Relic-Ring', ''.join(n.text or '' for n in tree.findall('.//s:text',NS)))
        tree=ET.fromstring(renderer.render(dict(self.cards[0],name='<script>'),'full-art'))
        self.assertFalse(tree.findall('.//s:script',NS))

    def test_checked_in_svgs_match_shared_renderer(self):
        for card in self.cards:
            for style in ('standard','full-art'):
                saved=(ROOT/'design/cards/output'/f'{card["id"]}-{style}.svg').read_text(encoding='utf-8')
                self.assertEqual(saved,renderer.render(card,style))
