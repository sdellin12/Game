"""Paired, view-only discard strategy experiment; never changes the live opponent."""
import argparse
import hashlib
import json
from dataclasses import replace
from crucible_content.practice import practice_pack,pack_hash
from .session import HarnessSession
from .opponent import choose_move, exact_payment, targets

SOURCES=('beacon-02','beacon-03')


def pressure_move(view):
    move=choose_move(view)
    own=view.get('you');turn=view.get('turn');priority=view.get('priority')
    if not own or own['choice'] or view.get('choice_pending') or not move:return move
    actor=own['player_id']
    if not priority or priority['holder']!=actor or turn['active_player']!=actor or turn['phase'] not in ('MainBefore','MainAfter') or turn['recharge'] or turn['end_requested'] or view['chain']:return move
    # Prefer discard engines, then optional hand-building plays; keep all decisions
    # within the acting seat's permitted projection and ordinary payment rules.
    for card in sorted(own['hand'],key=lambda c:(c['definition_key'] not in SOURCES,c['cost'],c['instance_id'])):
        if card['definition_key'] not in SOURCES and not any(s['kind'] in ('draw','recover') for s in card['steps']):continue
        options=targets(view,card);payment=exact_payment(view,card['cost'])
        if payment is None or not options:continue
        args={'card_id':card['instance_id'],'payment':payment}
        if card.get('target_kind'):args['target']=options[0]
        return 'play_card',args
    board=[o for o in view['battlefield'] if o['controller']==actor]
    if move[0]=='play_card' and sum(bool(o.get('creature')) for o in board)>=2:
        return 'pass',{}
    return move


def evaluate_game(players=2,seed='discard-1',strategy='baseline',limit=4000,source_discount=0):
    if type(players) is not int or players not in (2,3,4) or strategy not in ('baseline','hold') or type(limit) is not int or limit<1:raise ValueError('Invalid discard evaluation settings')
    if type(source_discount) is not int or source_discount not in (0,1):raise ValueError('Choose printed costs or a one-resource experimental discount')
    actors=tuple(f'P{i+1}' for i in range(players))
    pack=practice_pack()
    if source_discount:
        pack=replace(pack,cards=tuple(replace(c,definition=replace(c.definition,cost=c.definition.cost-source_discount)) if c.definition.key in SOURCES else c for c in pack.cards))
    session=HarnessSession(tuple(f'Player {i+1}' for i in range(players)),seed=hashlib.sha256(seed.encode()).digest(),pack=pack)
    for actor in actors:
        session.choose_deck(actor,'core-gold',expected_revision=session.view()['revision'])
        session.ready(actor,True,expected_revision=session.view()['revision'])
    session.start('P1',expected_revision=session.view()['revision'])
    for actor in actors:session.redraw(actor,(),expected_revision=session.view()['revision'])
    known={};seen_events=set();seen_effects=set();entries={k:0 for k in SOURCES};queued={k:0 for k in SOURCES}
    resolved={k:0 for k in SOURCES};rewards={k:0 for k in SOURCES};discards=0;max_hand=0;spent=0;held=0
    for count in range(limit+1):
        public=session.view();p1=next(p for p in public['players'] if p['player_id']=='P1')
        max_hand=max(max_hand,p1['hand_count'])
        for card in public['pending_cards']+public['battlefield']:
            if card.get('definition_key'):known[card['instance_id']]=(card['definition_key'],card['controller'])
        for event in public['events']:
            if event['event_id'] in seen_events:continue
            seen_events.add(event['event_id'])
            key,owner=known.get(event['subject'],(None,None))
            if event['kind']=='card_resolved' and owner=='P1' and key in entries:entries[key]+=1
        for effect in public['chain']:
            if effect['effect_id'] in seen_effects:continue
            seen_effects.add(effect['effect_id'])
            key,owner=known.get(effect['source_id'],(None,None))
            if effect['label']=='Discard trigger' and owner=='P1' and key in queued:queued[key]+=1
        if public['result'] or count==limit:
            return {'players':players,'seed':seed,'strategy':strategy,'status':'completed' if public['result'] else 'incomplete',
                'commands':count,'turns':public['turn']['turn_id'],'result':public['result'],'pack_version':public['setup']['pack']['version'],
                'source_discount':source_discount,'content_hash':pack_hash(pack),
                'entries':entries,'queued':queued,'resolved':resolved,'reward_units':rewards,'source_resources_paid':spent,
                'end_discards':discards,'max_hand':max_hand,'held_plays':held}
        selected=None
        for actor in actors:
            view=session.view(actor);policy=pressure_move if actor=='P1' and strategy=='hold' else choose_move
            move=policy(view)
            if move:selected=(actor,view,move);break
        if selected is None:raise RuntimeError('No projected command available')
        actor,view,(kind,args)=selected
        if actor=='P1':
            if kind=='end_discard':discards+=len(args['cards'])
            if kind=='play_card':
                card=next(c for c in view['you']['hand'] if c['instance_id']==args['card_id'])
                if card['definition_key'] in SOURCES:spent+=card['cost']
            if strategy=='hold' and kind=='pass' and (choose_move(view) or (None,))[0]=='play_card':held+=1
        top=public['chain'][-1] if public['chain'] else None
        session.send(actor,{'kind':kind,'args':args,'expected_revision':view['revision']})
        after=session.view();remaining={e['effect_id'] for e in after['chain']}
        # Attribute only a reward that really resolved on a pass, not merely a
        # queued/negated trigger. Positive resource/bonus deltas measure delivery.
        if kind=='pass' and top and top['effect_id'] not in remaining and top['label']=='Discard trigger':
            key,owner=known.get(top['source_id'],(None,None))
            if owner=='P1' and key in resolved:
                post=next(p for p in after['players'] if p['player_id']=='P1')
                field='available' if key=='beacon-02' else 'permanent_bonus'
                gain=max(0,post['resources'][field]-p1['resources'][field])
                resolved[key]+=int(gain>0);rewards[key]+=gain


def run_batch(seeds=('discard-1','discard-2','discard-3'),players=(2,),limit=4000,source_discount=0):
    return [evaluate_game(p,seed,strategy,limit,source_discount) for p in players for seed in seeds for strategy in ('baseline','hold')]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seeds',nargs='+',default=['discard-1','discard-2','discard-3'])
    parser.add_argument('--players',type=int,nargs='+',choices=(2,3,4),default=[2])
    parser.add_argument('--limit',type=int,default=4000)
    parser.add_argument('--source-discount',type=int,choices=(0,1),default=0,help='isolated cost sensitivity only; never changes the default pack')
    args=parser.parse_args();rows=run_batch(args.seeds,args.players,args.limit,args.source_discount);print(json.dumps(rows,indent=2))
    return 0 if all(r['status']=='completed' for r in rows) else 2


if __name__=='__main__':raise SystemExit(main())
