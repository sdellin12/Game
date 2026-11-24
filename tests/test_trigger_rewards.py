import gzip
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from crucible_content.practice import practice_pack, pack_hash
from crucible_core.match import HealPlayer, GrantCapacity, GrantResources, MatchError, _depart, validate_match
from crucible_core.resources import start_resources
from crucible_play.persistence import load_session, _decode, _encode
from crucible_play.desktop import PlayWindow
from crucible_play.hand_pressure import evaluate, pressure_case
from test_authored_triggers import CARD, ABILITY, source_fixture
from test_commands_cards_views import play, pass_round
from test_zone_moves import resolve
from test_optional_triggers import decide
from test_save_migration import sealed


class TriggerRewardTests(unittest.TestCase):
    def reward(self, steps, optional=False, use=True):
        card=replace(CARD,triggered_abilities=(replace(ABILITY,steps=steps,optional=optional),))
        s=source_fixture(card);p=s.players[0]
        s=replace(s,players=(replace(p,cards=replace(p.cards,health=28)),)+s.players[1:])
        s=resolve(pass_round(play(s,'A','source',4)),'draw')
        if optional:s=decide(s,use)
        return pass_round(s) if not optional or use else s

    def test_healing_caps_and_mixed_rewards_resolve_for_controller_only(self):
        s=self.reward((HealPlayer('$controller',8),GrantResources('$controller',2),GrantCapacity('$controller',3)))
        a,b=s.players[:2]
        self.assertEqual((a.cards.health,a.resources.available,a.resources.permanent_bonus),(30,8,3))
        self.assertEqual((b.cards.health,b.resources.available,b.resources.permanent_bonus),(30,10,0))

    def test_capacity_waits_for_refill_and_survives_source_departure(self):
        s=self.reward((GrantCapacity('$controller',2),))
        self.assertEqual(s.players[0].resources.available,6)
        s=_depart(s,{'source'},'test-removal');p=s.players[0]
        self.assertFalse(s.battlefield)
        self.assertEqual(p.resources.permanent_bonus,2)
        self.assertEqual(start_resources(p.resources).available,p.resources.natural_capacity+2)

    def test_optional_skip_applies_none_of_mixed_reward(self):
        s=self.reward((HealPlayer('$controller',2),GrantCapacity('$controller',2)),True,False)
        self.assertEqual((s.players[0].cards.health,s.players[0].resources.permanent_bonus),(28,0))

    def test_new_rewards_roundtrip_after_capture_and_survive_source_departure(self):
        card=replace(CARD,triggered_abilities=(replace(ABILITY,steps=(HealPlayer('$controller',2),GrantCapacity('$controller',1)),optional=True),))
        s=resolve(pass_round(play(source_fixture(card),'A','source',4)),'draw')
        restored=_decode(_encode(s));validate_match(restored);self.assertEqual(s,restored)
        s=_depart(restored,{'source'},'test-removal');s=pass_round(decide(s,True))
        self.assertFalse(s.battlefield);self.assertEqual(s.players[0].resources.permanent_bonus,1)

    def test_fixed_target_and_positive_integer_validation_for_each_reward(self):
        for kind in (HealPlayer,GrantCapacity,GrantResources):
            for target,amount in (('$target',1),('B',1),('$controller',0),('$controller',-1),('$controller',True)):
                with self.subTest(kind=kind,target=target,amount=amount),self.assertRaises(MatchError):
                    source_fixture(replace(CARD,triggered_abilities=(replace(ABILITY,steps=(kind(target,amount),)),)))

    def test_instruction_types_have_distinct_hashes(self):
        pack=practice_pack();hashes=[]
        for kind in (HealPlayer,GrantCapacity,GrantResources):
            card=replace(pack.cards[0],definition=replace(CARD,triggered_abilities=(replace(ABILITY,steps=(kind('$controller',1),)),)))
            hashes.append(pack_hash(replace(pack,cards=(card,)+pack.cards[1:])))
        self.assertEqual(len(set(hashes)),3)

    def test_native_v5_partial_decision_load_preserves_hash_and_next_result(self):
        case=json.loads(gzip.decompress((Path(__file__).parent/'fixtures/save_v5_before_reward_types.json.gz').read_bytes()))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'old.crucible.json';path.write_bytes(sealed(case['save']))
            from crucible_play.migrate import migrate_save
            output=Path(directory)/'new.crucible.json';migrate_save(path,output)
            s=load_session(output)
            self.assertEqual(pack_hash(s._lobby.pack),case['save']['content_hash'])
            s.resume();s.send(case['actor'],case['packet'])
            # This fixture includes private optional decisions: preserve them;
            # only Resolution receives the new continuation defaults.
            from crucible_play.migrate import _upgrade_payload,V5_RECORDS
            self.assertEqual(s._lobby,_decode(_upgrade_payload(case['expected'],V5_RECORDS,version=5)))

    def test_reward_text_names_healing_and_delayed_capacity(self):
        window=PlayWindow.__new__(PlayWindow)
        ability={'event':'card_discarded','optional':True,'steps':[{'kind':'heal','target':'$controller','amount':2},{'kind':'capacity','target':'$controller','amount':1}]}
        text=window.trigger_text(ability,{})
        self.assertIn('may apply',text);self.assertIn('2 life',text);self.assertIn('next refill',text)
        self.assertNotIn('gain 3 resources',text)

    def test_hand_pressure_matrix_and_invalid_cases(self):
        report=evaluate();self.assertEqual((report['cases'],report['passed']),(18,18))
        for args in ((True,1,'draw'),(5,1,'draw'),(2,0,'draw'),(2,1,'unknown')):
            with self.assertRaises(ValueError):pressure_case(*args)
