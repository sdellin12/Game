import json
import unittest
from dataclasses import replace
from crucible_content.practice import practice_pack,validate_pack,PackCard
from crucible_core.lobby import *
from crucible_core.match import validate_match
from crucible_play.session import HarnessSession, HotseatGate

SEED=b'fixed-local-test-seed-1234567890'


def ready_lobby(size=2):
    pack=practice_pack()
    lobby=new_lobby(tuple((f'P{i+1}',f'Player {i+1}') for i in range(size)),pack,seed=SEED)
    for p in lobby.players:
        leader=pack.leaders[0]
        deck=DeckSelection('Test Forty',leader.color,leader.key,tuple(c.definition.key for c in pack.cards))
        lobby=select_deck(lobby,p.player_id,deck,expected_revision=lobby.revision)
        lobby=set_ready(lobby,p.player_id,True,expected_revision=lobby.revision)
    return lobby


class SetupTests(unittest.TestCase):
    def test_pack_has_forty_unique_engine_valid_cards(self):
        pack=practice_pack()
        self.assertEqual(len(pack.cards),40)
        self.assertEqual(len({c.definition.key for c in pack.cards}),40)
        self.assertEqual(sum(c.definition.kind=='creature' for c in pack.cards),24)
        self.assertEqual(sum(c.definition.kind=='permanent' for c in pack.cards),6)
        with self.assertRaises(ValueError):validate_pack(replace(pack,cards=pack.cards[:-1]+(pack.cards[0],)))
        bad=replace(pack.cards[0],definition=replace(pack.cards[0].definition,kind='leader'))
        with self.assertRaises(ValueError):validate_pack(replace(pack,cards=(bad,)+pack.cards[1:]))

    def test_deck_size_singleton_card_membership_and_color(self):
        lobby=ready_lobby();deck=lobby.players[0].deck
        for bad in (replace(deck,card_keys=deck.card_keys[:-1]),replace(deck,card_keys=deck.card_keys[:-1]+(deck.card_keys[0],)),
                    replace(deck,card_keys=deck.card_keys[:-1]+('unknown',)),replace(deck,color='Green'),replace(deck,leader_key='unknown')):
            with self.assertRaises(ValueError):validate_deck(lobby.pack,bad)

    def test_selection_change_resets_only_own_ready_and_prevents_start(self):
        lobby=ready_lobby()
        lobby=select_deck(lobby,'P1',replace(lobby.players[0].deck,name='Changed name'),expected_revision=lobby.revision)
        self.assertFalse(lobby.players[0].ready);self.assertTrue(lobby.players[1].ready)
        with self.assertRaises(ValueError):begin_opening(lobby,'P1',expected_revision=lobby.revision)

    def test_only_host_starts_after_every_valid_ready_selection(self):
        lobby=ready_lobby()
        with self.assertRaises(ValueError):begin_opening(lobby,'P2',expected_revision=lobby.revision)
        with self.assertRaises(ValueError):begin_opening(lobby,'P1',expected_revision=lobby.revision-1)
        opening=begin_opening(lobby,'P1',expected_revision=lobby.revision)
        self.assertEqual(opening.phase,'opening')
        self.assertEqual([(len(p.hand),len(p.deck)) for p in opening.opening],[(5,35),(5,35)])
        self.assertIsNotNone(opening.rules_hash);self.assertIsNotNone(opening.content_hash)
        with self.assertRaises(ValueError):select_deck(opening,'P1',lobby.players[0].deck,expected_revision=opening.revision)
        self.assertTrue(all(p.ready for p in lobby.players))

    def test_public_lobby_hides_deck_lists_seed_hands_and_order(self):
        lobby=ready_lobby(3)
        opening=begin_opening(lobby,'P1',expected_revision=lobby.revision)
        public=project_lobby(opening)
        encoded=json.dumps(public)
        self.assertIsNone(public['turn_order']);self.assertIsNone(public['redraw_counts'])
        for hand in opening.opening:
            for card in hand.hand+hand.deck:self.assertNotIn(card,encoded)
        self.assertNotIn('seed',encoded);self.assertNotIn('card_keys',encoded)
        private=project_lobby(opening,'P1')['you']['hand']
        self.assertEqual({c['instance_id'] for c in private},set(opening.opening[0].hand))

    def test_redraw_locks_do_not_disclose_counts_or_choices(self):
        lobby=ready_lobby(3);lobby=begin_opening(lobby,'P1',expected_revision=lobby.revision)
        before=project_lobby(lobby,'P2');before.pop('revision')
        locked=lock_redraw(lobby,'P1',lobby.opening[0].hand[:3],expected_revision=lobby.revision)
        after=project_lobby(locked,'P2');after.pop('revision')
        self.assertEqual(before,after)
        self.assertTrue(project_lobby(locked,'P1')['you']['locked'])
        with self.assertRaises(ValueError):lock_redraw(locked,'P1',(),expected_revision=locked.revision)

    def test_replace_before_reshuffling_rejects_and_conserve_all_instances(self):
        lobby=ready_lobby();lobby=begin_opening(lobby,'P1',expected_revision=lobby.revision)
        initial=lobby.opening[0];rejected=initial.hand[:3];replacement=initial.deck[:3]
        lobby=lock_redraw(lobby,'P1',rejected,expected_revision=lobby.revision)
        lobby=lock_redraw(lobby,'P2',(),expected_revision=lobby.revision)
        final=lobby.opening[0]
        self.assertEqual(final.hand,initial.hand[3:]+replacement)
        self.assertTrue(set(rejected)<=set(final.deck))
        self.assertFalse(set(rejected)&set(final.hand))
        self.assertEqual(set(final.hand+final.deck),set(initial.hand+initial.deck))
        self.assertEqual((len(final.hand),len(final.deck)),(5,35))
        self.assertEqual(lobby.redraw_counts,(('P1',3),('P2',0)))
        self.assertEqual(lobby.phase,'match');validate_match(lobby.match)
        self.assertEqual(lobby.match.turn.active_player,lobby.order[0])
        self.assertEqual(lobby.match.seat_order,lobby.order)
        self.assertEqual(lobby.match.players[0].resources.available,2)

    def test_all_five_redraw_and_zero_keep_are_deterministic(self):
        original=ready_lobby();original=begin_opening(original,'P1',expected_revision=original.revision)
        def finish(lobby):
            lobby=lock_redraw(lobby,'P1',lobby.opening[0].hand,expected_revision=lobby.revision)
            return lock_redraw(lobby,'P2',(),expected_revision=lobby.revision)
        a=finish(original);b=finish(original)
        self.assertEqual(a,b)
        self.assertEqual(a.opening[1].hand,original.opening[1].hand)
        self.assertFalse(set(a.opening[0].hand)&set(original.opening[0].hand))

    def test_start_rotates_fixed_order_instead_of_randomizing_other_seats(self):
        lobby=ready_lobby(4);lobby=begin_opening(lobby,'P1',expected_revision=lobby.revision)
        for p in lobby.players:lobby=lock_redraw(lobby,p.player_id,(),expected_revision=lobby.revision)
        base=tuple(p.player_id for p in lobby.players);index=base.index(lobby.order[0])
        self.assertEqual(lobby.order,base[index:]+base[:index])
        public=project_lobby(lobby)
        self.assertEqual(len(public['redraw_counts']),4)
        self.assertEqual(public['turn_order'],list(lobby.order))

    def test_invalid_redraw_authority_ids_duplicates_and_stale_are_immutable(self):
        lobby=ready_lobby();lobby=begin_opening(lobby,'P1',expected_revision=lobby.revision)
        for actor,cards,rev in (('P1',(lobby.opening[0].hand[0],)*2,lobby.revision),('P1',lobby.opening[1].hand[:1],lobby.revision),
                                ('unknown',(),lobby.revision),('P1',(),lobby.revision-1),('P1',(),True)):
            with self.assertRaises(ValueError):lock_redraw(lobby,actor,cards,expected_revision=rev)
        self.assertFalse(lobby.redraw_locks)


class SessionTests(unittest.TestCase):
    def start(self,size=2):
        session=HarnessSession(tuple(f'Player {i+1}' for i in range(size)),seed=SEED)
        for player in session.view()['players']:
            actor=player['player_id']
            session.choose_deck(actor,'core-gold',expected_revision=session.view()['revision'])
            session.ready(actor,True,expected_revision=session.view()['revision'])
        session.start('P1',expected_revision=session.view()['revision'])
        for player in session.view()['players']:session.redraw(player['player_id'],(),expected_revision=session.view()['revision'])
        return session

    def test_match_session_views_keep_private_opening_cards_per_seat(self):
        session=self.start()
        public=json.dumps(session.view())
        for actor in ('P1','P2'):
            view=session.view(actor)
            self.assertEqual(len(view['you']['hand']),5)
            for card in view['you']['hand']:self.assertNotIn(card['instance_id'],public)
        self.assertEqual(session.view()['turn']['phase'],'Start')

    def test_public_handoff_requires_explicit_unlock_and_hides_prior_actor(self):
        gate=HotseatGate();gate.request('P1')
        self.assertIsNone(gate.actor);gate.unlock();self.assertEqual(gate.actor,'P1')
        gate.request('P2');self.assertIsNone(gate.actor);self.assertEqual(gate.pending,'P2')
        gate.hide();self.assertIsNone(gate.actor);self.assertIsNone(gate.pending)
        with self.assertRaises(ValueError):gate.unlock()

    def test_packet_rejection_preserves_match_and_valid_pass_advances(self):
        session=self.start();before=session.view()
        actor=before['priority']['holder']
        with self.assertRaises(ValueError):session.send(actor,{'kind':'pass','expected_revision':999,'args':{}})
        self.assertEqual(before,session.view())
        session.send(actor,{'kind':'pass','expected_revision':before['revision'],'args':{}})
        self.assertNotEqual(before['revision'],session.view()['revision'])


class HarnessBoundaryTests(unittest.TestCase):
    def test_projected_depletion_end_intent_prevents_view_policy_extra_play(self):
        from crucible_core.match import MatchPlayer, EffectSpec, DrawCards, queue_effect, pass_match, resolve_current, new_match
        from crucible_core.turns import DrawPlayer, RefillPolicy
        from crucible_core.views import project_match
        state=new_match((MatchPlayer(DrawPlayer('A',30,('last',),())),MatchPlayer(DrawPlayer('B',30,('b',),()))),
                        (), (EffectSpec('draw','A',(DrawCards('A',1),)),),RefillPolicy(20,1),active_player='A')
        state=queue_effect(state,'A','draw',expected_revision=state.revision)
        for _ in range(2):state=pass_match(state,state.priority.holder,expected_revision=state.revision)
        state=resolve_current(state,expected_revision=state.revision)
        self.assertFalse(state.turn.end_requested)
        self.assertTrue(project_match(state,'A')['turn']['end_requested'])


if __name__=='__main__':unittest.main()
