import unittest
from dataclasses import replace
from crucible_content.practice import practice_pack,pack_hash
from crucible_core.cards import CardDefinition
from crucible_core.match import RecoverDiscardCard,DrawCards,DiscardThenDraw
from crucible_core.views import project_match
from test_commands_cards_views import fixture,instances,command,play,pass_round
from test_effect_discard import OUTLET,discard


def engine_fixture(deck=tuple('draw'+str(i) for i in range(8))):
    sources=tuple(c.definition for c in practice_pack().cards if c.definition.key in ('beacon-01','beacon-02','beacon-03'))
    recovery=CardDefinition('recover','action',3,(RecoverDiscardCard('$target'),),target_kind='discard',target_relation='friendly')
    cards=instances(*[(d.key,d.key,'A') for d in sources],('outlet','outlet','A'),('recover','recover','A'))
    s=fixture(sources+(OUTLET,recovery),cards,ah=tuple(d.key for d in sources)+('outlet','recover')+tuple('fodder'+str(i) for i in range(6)),ad=deck,ag=('grave1','grave2'))
    p=s.players[0];s=replace(s,players=(replace(p,resources=replace(p.resources,available=100)),)+s.players[1:])
    for d in sources:s=pass_round(play(s,'A',d.key,d.cost))
    return s


def settle(s):
    while (project_match(s,'A')['you']['choice'] or {}).get('kind')=='optional_trigger':
        c=project_match(s,'A')['you']['choice'];s=command(s,'A','trigger_choice',trigger_id=c['trigger_id'],use=True)
    if s.triggers:s=command(s,'A','trigger_order',order=[t['trigger_id'] for t in project_match(s,'A')['you']['choice']['triggers']])
    while s.priority.chain:s=pass_round(s)
    return s


class DiscardLoopTests(unittest.TestCase):
    def test_all_engines_reward_actual_discard_and_draw_after_atomic_completion(self):
        s=engine_fixture();before=s.players[0].resources.available
        s=pass_round(play(s,'A','outlet',2));self.assertFalse(s.triggers)
        s=discard(s,'fodder0');self.assertEqual(len(s.triggers),4)
        self.assertEqual(s.players[0].resources.available,before-2)
        s=settle(s)
        self.assertEqual((s.players[0].resources.available,s.players[0].resources.permanent_bonus),(before+1,1))
        self.assertEqual(sum(e.kind=='card_effect_discarded' for e in s.events),1)

    def test_recover_and_reuse_pays_again_and_does_not_form_free_self_recovery(self):
        s=engine_fixture();before=s.players[0].resources.available
        for index in (0,1):
            if index:s=pass_round(play(s,'A','recover',3,target='outlet'))
            s=settle(discard(pass_round(play(s,'A','outlet',2)),'fodder'+str(index)))
        self.assertEqual((s.players[0].resources.available,s.players[0].resources.permanent_bonus),(before-1,2))
        self.assertEqual(len(s.players[0].cards.deck),4)
        self.assertIn('recover',s.players[0].cards.discard)
        with self.assertRaises(ValueError):play(s,'A','recover',3,target='recover')

    def test_partial_refill_defers_all_choices_and_ends_own_turn_after_completion(self):
        s=engine_fixture(('only',));before=s.players[0].resources.available
        s=discard(pass_round(play(s,'A','outlet',2)),'fodder0')
        self.assertEqual(project_match(s,'A')['you']['choice']['kind'],'refill')
        self.assertEqual(len(s.triggers),3);self.assertEqual(s.players[0].resources.available,before-2)
        s=command(s,'A','refill',pay=True,request_id=s.pending.draw.request_id)
        self.assertEqual(len(s.triggers),4);s=settle(s)
        self.assertTrue(s.players[0].cards.end_turn_requested)
        with self.assertRaises(ValueError):play(s,'A','recover',3,target='outlet')
        self.assertEqual(s.players[0].cards.health,10)
        self.assertEqual(sum(e.kind=='card_effect_discarded' for e in s.events),1)

    def test_new_instruction_hash_is_not_plain_draw_and_unsupported_targets_reject(self):
        from crucible_content.practice import discard_draw_pack
        pack=discard_draw_pack();card=next(c for c in pack.cards if c.definition.key=='proposal-scrapyard-insight')
        plain=replace(card,definition=replace(card.definition,steps=(DrawCards('$controller',2),)))
        self.assertNotEqual(pack_hash(pack),pack_hash(replace(pack,cards=tuple(plain if c==card else c for c in pack.cards))))
        leader=pack.leaders[0]
        def with_steps(step):return replace(pack,leaders=(replace(leader,definition=replace(leader.definition,reserve_ability=replace(leader.definition.reserve_ability,steps=(step,)))),)+pack.leaders[1:])
        self.assertNotEqual(pack_hash(with_steps(DrawCards('$controller',2))),pack_hash(with_steps(DiscardThenDraw('$controller',2))))
        with self.assertRaises(ValueError):fixture((replace(OUTLET,steps=(DiscardThenDraw('$target',2),),target_kind='player'),))

    def test_one_discard_alone_cannot_complete_a_two_card_refill(self):
        from test_effect_discard import waiting
        s=discard(waiting(deck=()),'fodder')
        self.assertEqual(s.pending.draw.player.discard,('fodder',))
        s=command(s,'A','refill',pay=True,request_id=s.pending.draw.request_id)
        self.assertTrue(s.players[0].eliminated);self.assertIsNone(s.pending)
        self.assertEqual(sum(e.kind=='card_effect_discarded' for e in s.events),1)

    def test_concession_at_empty_deck_discards_once_then_declines_refill(self):
        from test_effect_discard import waiting
        s=command(waiting(deck=()),'A','concede',confirmed=True)
        self.assertTrue(s.players[0].eliminated);self.assertIsNone(s.pending)
        self.assertEqual(sum(e.kind=='card_effect_discarded' for e in s.events),1)
