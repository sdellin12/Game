import gzip
import json
import tempfile
from pathlib import Path
from dataclasses import replace
import unittest
from crucible_core.cards import CardDefinition
from crucible_core.match import (RecoverDiscardCard,DrawCards,GrantResources,EffectSpec,NegateEffect,
    MatchError,validate_match)
from crucible_core.views import project_match
from crucible_play.persistence import save_session,load_session,_decode
from crucible_play.opponent import choose_move
from test_commands_cards_views import fixture,instances,command,pass_round,play
from test_zone_moves import UNIT,resolve
from test_persistence import prepared,state,cmd,passes,register

RECOVER=CardDefinition('recovery','action',3,(RecoverDiscardCard('$target'),),target_kind='discard',target_relation='friendly')


def recovery_fixture(*,definition=RECOVER,extra=(),discard=('unit',),effects=()):
    return fixture((UNIT,definition)+tuple(d for d,_ in extra),
        instances(('unit','unit','A'),('recovery','recovery','A'),*((i,d.key,'A') for d,i in extra)),
        ah=('recovery',)+tuple(i for _,i in extra),ag=discard,effects=effects)


class RecoveryTests(unittest.TestCase):
    def test_paid_recovery_locks_discard_target_then_returns_to_hand_without_playing_it(self):
        s=recovery_fixture();s=play(s,'A','recovery',3,target='unit')
        self.assertEqual(s.players[0].resources.available,7);self.assertEqual(s.players[0].cards.discard,('unit',))
        step=project_match(s)['chain'][-1]['steps'][0];self.assertEqual(step,{'kind':'recover','target':'unit'})
        s=pass_round(s);validate_match(s)
        self.assertEqual(s.players[0].cards.hand,('unit',));self.assertEqual(s.players[0].cards.discard,('recovery',))
        self.assertFalse(s.battlefield);self.assertEqual(sum(e.kind=='card_recovered' for e in s.events),1)
        s=pass_round(play(s,'A','unit',1));self.assertEqual(s.battlefield[0].creature.health,UNIT.health)
        self.assertFalse(s.battlefield[0].creature.attack_eligible)

    def test_can_recover_action_reaction_or_permanent_as_well_as_creature(self):
        for kind in ('action','reaction','permanent'):
            with self.subTest(kind=kind):
                d=CardDefinition('target',kind,1)
                s=fixture((RECOVER,d),instances(('recovery','recovery','A'),('target','target','A')),ah=('recovery',),ag=('target',))
                s=pass_round(play(s,'A','recovery',3,target='target'))
                self.assertEqual(s.players[0].cards.hand,('target',));self.assertFalse(s.battlefield)

    def test_rejects_foreign_hand_deck_exile_and_own_pending_card_targets_without_payment(self):
        s=recovery_fixture();p=s.players[0]
        for zone in ('deck','hand'):
            changed=replace(s,players=(replace(p,cards=replace(p.cards,discard=(),**{zone:getattr(p.cards,zone)+('unit',)})),)+s.players[1:])
            with self.assertRaises(ValueError):play(changed,'A','recovery',3,target='unit')
            self.assertEqual(changed.players[0].resources.available,10)
        changed=replace(s,players=(replace(p,cards=replace(p.cards,discard=())),)+s.players[1:],exiled=('unit',))
        with self.assertRaises(ValueError):play(changed,'A','recovery',3,target='unit')
        foreign=fixture((RECOVER,UNIT),instances(('recovery','recovery','A'),('unit','unit','B')),ah=('recovery',),bh=('unit',),
            objects=())
        b=foreign.players[1];foreign=replace(foreign,players=(foreign.players[0],replace(b,cards=replace(b.cards,hand=(),discard=('unit',))),foreign.players[2]))
        with self.assertRaises(ValueError):play(foreign,'A','recovery',3,target='unit')
        with self.assertRaises(ValueError):play(s,'A','recovery',3,target='recovery')

    def test_empty_discard_or_invalid_authored_target_cannot_spend_resources(self):
        s=fixture((RECOVER,),instances(('recovery','recovery','A')),ah=('recovery',))
        self.assertEqual(choose_move(project_match(s,'A')),('pass',{}))
        with self.assertRaises(ValueError):play(s,'A','recovery',3,target='missing')
        for bad in (replace(RECOVER,target_relation='enemy'),replace(RECOVER,target_kind='creature'),
                    replace(RECOVER,steps=(RecoverDiscardCard('$controller'),),target_kind=None,target_relation='any')):
            with self.assertRaises(MatchError):fixture((bad,))

    def test_negated_recovery_spends_payment_and_keeps_chosen_card_in_discard(self):
        negate=CardDefinition('interrupt','reaction',2,(NegateEffect('$target'),),target_kind='effect')
        s=fixture((RECOVER,UNIT,negate),instances(('recovery','recovery','A'),('unit','unit','A'),('interrupt','interrupt','B')),
            ah=('recovery',),ag=('unit',),bh=('interrupt',))
        s=play(s,'A','recovery',3,target='unit');target=s.priority.chain[-1].effect_id
        s=pass_round(play(s,'B','interrupt',2,target=str(target)))
        self.assertEqual(s.players[0].resources.available,7);self.assertEqual(s.players[0].cards.discard,('unit','recovery'))
        self.assertFalse(s.players[0].cards.hand);self.assertFalse(any(e.kind=='card_recovered' for e in s.events))

    def test_two_recoveries_revalidate_same_card_and_resolve_independent_instructions(self):
        reaction=replace(RECOVER,kind='reaction',steps=(RecoverDiscardCard('$target'),GrantResources('$controller',1)))
        second=replace(reaction,key='second')
        s=recovery_fixture(definition=reaction,extra=((second,'second'),))
        s=play(s,'A','recovery',3,target='unit');s=command(s,'B','pass');s=command(s,'C','pass')
        s=pass_round(play(s,'A','second',3,target='unit'));s=pass_round(s)
        self.assertEqual(s.players[0].cards.hand,('unit',));self.assertEqual(sum(e.kind=='card_recovered' for e in s.events),1)
        self.assertEqual(s.players[0].resources.available,6)

    def test_refill_moves_locked_target_out_of_discard_before_recovery_instruction(self):
        d=replace(RECOVER,steps=(DrawCards('$controller',1),RecoverDiscardCard('$target'),GrantResources('$controller',1)))
        s=recovery_fixture(definition=d);s=play(s,'A','recovery',3,target='unit');s=pass_round(s)
        self.assertIsNotNone(s.pending.draw)
        s=command(s,'A','refill',pay=True,request_id=s.pending.draw.request_id)
        self.assertEqual(s.players[0].cards.hand,('unit',));self.assertFalse(any(e.kind=='card_recovered' for e in s.events))
        self.assertEqual(s.players[0].resources.available,8)

    def test_eliminated_owner_is_not_recovered_by_later_registered_effect(self):
        s=recovery_fixture(effects=(EffectSpec('recover','B',(RecoverDiscardCard('unit'),)),))
        s=command(s,'A','concede',confirmed=True)
        self.assertTrue(s.players[0].eliminated)
        while s.priority.holder!='B':s=command(s,s.priority.holder,'pass')
        s=resolve(s,'recover','B');self.assertNotIn('unit',s.players[0].cards.hand)
        self.assertFalse(any(e.kind=='card_recovered' for e in s.events))

    def test_recovery_above_seven_cards_uses_existing_end_discard_boundary(self):
        s=recovery_fixture();p=s.players[0]
        s=replace(s,players=(replace(p,cards=replace(p.cards,hand=p.cards.hand+tuple('extra'+str(i) for i in range(7)))),)+s.players[1:])
        s=pass_round(play(s,'A','recovery',3,target='unit'));self.assertEqual(len(s.players[0].cards.hand),8)
        s=command(s,'A','end_turn');s=pass_round(s)
        self.assertEqual(s.discard_needed,1)
        s=command(s,'A','end_discard',cards=['unit']);self.assertEqual(len(s.players[0].cards.hand),7)

    def test_recovery_event_is_public_but_other_hand_contents_are_not(self):
        s=recovery_fixture();p=s.players[0];s=replace(s,players=(replace(p,cards=replace(p.cards,hand=p.cards.hand+('SECRET',))),)+s.players[1:])
        s=pass_round(play(s,'A','recovery',3,target='unit'));public=project_match(s)
        event=next(e for e in public['events'] if e['kind']=='card_recovered')
        self.assertEqual(event['card']['definition_key'],'unit');self.assertNotIn('SECRET',json.dumps(public))
        self.assertNotIn('SECRET',json.dumps(project_match(s,'B')))

    def test_archived_v3_states_load_without_conversion_and_keep_next_results(self):
        cases=json.loads(gzip.decompress((Path(__file__).parent/'fixtures'/'save_v3_before_recovery.json.gz').read_bytes()))
        for case in cases:
            with tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/'legacy.crucible.json';path.write_text(json.dumps(case['save']));before=path.read_bytes()
                s=load_session(path);self.assertTrue(s.paused);self.assertEqual(s._lobby,_decode(case['save']['payload']['lobby']))
                s.resume();s.send(case['actor'],case['packet']);self.assertEqual(s._lobby,_decode(case['expected']))
                self.assertEqual(path.read_bytes(),before)

    def test_practice_recovery_pending_save_and_replay_use_same_seeded_state(self):
        s=prepared();actor=s.view()['turn']['active_player'];m=s._lobby.match
        recovery=next(c for c in m.card_instances if c.owner==actor and c.definition_key=='spell-09')
        unit=next(c for c in m.card_instances if c.owner==actor and c.definition_key=='unit-01')
        moved={unit.instance_id,recovery.instance_id}
        state(s,turn=replace(m.turn,phase='MainBefore'),players=tuple(replace(p,cards=replace(p.cards,hand=(recovery.instance_id,),discard=(unit.instance_id,),deck=tuple(i for i in p.cards.deck+p.cards.hand if i not in moved)),resources=replace(p.resources,available=4)) if p.cards.player_id==actor else p for p in m.players),
              leaders=tuple(replace(l,recovering=True) if l.owner==actor else l for l in m.leaders))
        move=choose_move(s.view(actor));self.assertEqual(move[0],'play_card');self.assertEqual(move[1]['target'],unit.instance_id)
        cmd(s,actor,move[0],**move[1])
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'recovery.crucible.json';save_session(s,path);loaded=load_session(path)
        loaded.resume();passes(s);passes(loaded);self.assertEqual(s._lobby,loaded._lobby)
        move=choose_move(s.view(actor));self.assertEqual(move[1]['card_id'],unit.instance_id)
        for game in (s,loaded):cmd(game,actor,move[0],**move[1]);passes(game)
        self.assertEqual(s._lobby,loaded._lobby);self.assertTrue(any(o.object_id==unit.instance_id for o in s._lobby.match.battlefield))

    def test_snapshot_resumes_draw_cursor_before_and_after_recovery_instruction(self):
        for recover_first in (False,True):
            with self.subTest(recover_first=recover_first):
                s=prepared();actor=s.view()['turn']['active_player'];m=s._lobby.match
                p=next(p for p in m.players if p.cards.player_id==actor);target=p.cards.deck[0]
                state(s,players=tuple(replace(q,cards=replace(q.cards,deck=(),discard=q.cards.discard+q.cards.deck)) if q==p else q for q in m.players))
                steps=(RecoverDiscardCard(target),DrawCards(actor,1)) if recover_first else (DrawCards(actor,1),RecoverDiscardCard(target))
                register(s,'recovery-draw',actor,steps);self.assertIsNotNone(s._lobby.match.pending.draw)
                with tempfile.TemporaryDirectory() as directory:
                    path=Path(directory)/'cursor.crucible.json';save_session(s,path);loaded=load_session(path)
                loaded.resume()
                for game in (s,loaded):cmd(game,actor,'refill',pay=True,request_id=game._lobby.match.pending.draw.request_id)
                self.assertEqual(s._lobby,loaded._lobby)
                self.assertEqual(sum(e.kind=='card_recovered' for e in s._lobby.match.events),int(recover_first))
