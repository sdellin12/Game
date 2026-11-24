"""Bounded multi-seed, all-computer practice evaluation using permitted views only."""
import argparse,hashlib,json
from .session import HarnessSession


def evaluate_game(players,seed,limit=4000):
    if players not in (2,3,4) or type(limit) is not int or limit<1:raise ValueError('Choose 2-4 players and a positive command limit')
    names=tuple(f'Player {i+1}' for i in range(players));actors=tuple(f'P{i+1}' for i in range(players))
    s=HarnessSession(names,seed=hashlib.sha256(seed.encode()).digest(),bots=actors)
    for actor in actors:
        s.choose_deck(actor,'core-gold',expected_revision=s.view()['revision']);s.ready(actor,True,expected_revision=s.view()['revision'])
    s.start('P1',expected_revision=s.view()['revision'])
    for actor in actors:s.redraw(actor,(),expected_revision=s.view()['revision'])
    known={};events=set();effects=set();entries={'beacon-01':0,'beacon-02':0,'beacon-03':0};queued={'draw':0,'discard':0}
    for count in range(limit+1):
        view=s.view()
        for card in view['pending_cards']+view['battlefield']:
            if card.get('definition_key'):known[card['instance_id']]=card['definition_key']
        for event in view['events']:
            if event['event_id'] in events:continue
            events.add(event['event_id'])
            if event['kind']=='card_resolved' and known.get(event['subject']) in entries:entries[known[event['subject']]]+=1
        for effect in view['chain']:
            if effect['effect_id'] in effects:continue
            effects.add(effect['effect_id'])
            if effect['label'] in ('Draw trigger','Discard trigger'):queued['draw' if effect['label']=='Draw trigger' else 'discard']+=1
        if view['result'] or count==limit:
            return {'players':players,'seed':seed,'status':'completed' if view['result'] else 'incomplete',
                'commands':count,'turns':view['turn']['turn_id'],'pack_version':view['setup']['pack']['version'],'result':view['result'],'entries':entries,'queued_triggers':queued}
        if not s.step_opponent():
            return {'players':players,'seed':seed,'status':'incomplete','reason':'no projected computer command',
                'commands':count,'turns':view['turn']['turn_id'],'entries':entries,'queued_triggers':queued}


def run_batch(seeds=('permanent-1','permanent-2','permanent-3'),players=(2,3,4),limit=4000):
    return [evaluate_game(count,seed,limit) for count in players for seed in seeds]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--seeds',nargs='+',default=['permanent-1','permanent-2','permanent-3'])
    parser.add_argument('--players',type=int,nargs='+',choices=(2,3,4),default=[2,3,4]);parser.add_argument('--limit',type=int,default=4000)
    args=parser.parse_args();rows=run_batch(args.seeds,args.players,args.limit);print(json.dumps(rows,indent=2))
    return 0 if all(r['status']=='completed' for r in rows) else 2


if __name__=='__main__':raise SystemExit(main())
