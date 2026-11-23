import unittest
from crucible_play.package_eval import prepare,evaluate_game,study_content,summarize,markdown,validate_report


class PackageEvaluationTests(unittest.TestCase):
    def test_mixed_decks_are_valid_forty_card_singletons_from_one_pool(self):
        pool,decks=study_content();self.assertEqual(len(pool.cards),43)
        for deck in decks.values():self.assertEqual((len(deck),len(set(deck))),(40,40))
        for seat in ('P1','P2','P3','P4'):
            s,actors,_,_=prepare(4,'paired-setup',seat,'package')
            for player in s._lobby.players:
                self.assertEqual(player.deck.card_keys,decks['package' if player.player_id==seat else 'control'])

    def test_seed_pairs_preserve_start_and_common_card_positions_for_every_seat(self):
        _,decks=study_content();common=set(decks['control'])&set(decks['package'])
        for seat in ('P1','P2','P3'):
            a,_,content,control_hash=prepare(3,'paired-positions',seat,'control')
            b,_,other,package_hash=prepare(3,'paired-positions',seat,'package')
            self.assertEqual(content,other);self.assertNotEqual(control_hash,package_hash)
            self.assertEqual(a.view()['turn'],b.view()['turn'])
            for actor in ('P1','P2','P3'):
                def positions(s):
                    opening=next(o for o in s._lobby.opening if o.player_id==actor)
                    keys={c.instance_id:c.definition_key for c in opening.instances}
                    return {keys[c]:i for i,c in enumerate(opening.hand+opening.deck) if keys[c] in common}
                self.assertEqual(positions(a),positions(b))

    def test_bound_reports_incomplete_and_survival_is_censored(self):
        r=evaluate_game(limit=1)
        self.assertEqual((r['status'],r['commands']),('incomplete',1));self.assertIsNone(r['result'])
        self.assertTrue(r['survival_censored']);self.assertIsNone(r['eliminated_at_global_turn'])
        for args in ({'players':True},{'seat':'P5'},{'deck':'guess'},{'policy':'hold'},{'limit':0}):
            with self.assertRaises(ValueError):evaluate_game(**args)

    def test_report_keeps_incomplete_games_and_rejects_duplicate_or_unmatched_pairs(self):
        a=evaluate_game(deck='control',limit=1);b=evaluate_game(deck='package',limit=1)
        groups=summarize([a,b]);self.assertTrue(all(g['completed']==0 and g['wins']==0 for g in groups))
        c=evaluate_game(seat='P2',deck='control',limit=1);d=evaluate_game(seat='P2',deck='package',limit=1)
        self.assertIn('0/2',markdown([a,b,c,d]))
        for rows in ([a],[a,b,a],[a,dict(b,starting_seat='different')],[a,dict(b,content_hash='different')]):
            with self.assertRaises(ValueError):validate_report(rows)
