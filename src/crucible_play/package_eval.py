"""Seat-rotated package/control comparisons through validated setup and private views."""
import argparse
import hashlib
import json
from pathlib import Path
from dataclasses import replace
from crucible_content.practice import practice_pack,discard_draw_pack,validate_pack,pack_hash
from crucible_core.lobby import DeckSelection,select_deck
from .session import HarnessSession
from .opponent import choose_move

PAYOFFS=('beacon-01','beacon-02','beacon-03')
PACKAGE_KEYS=('proposal-scrapyard-insight','proposal-surveyors-notes','proposal-deep-archive')


def study_content():
    control=practice_pack();package=discard_draw_pack()
    keys={c.definition.key for c in control.cards}
    pool=validate_pack(replace(control,pack_id='crucible-package-study',version=1,
        cards=control.cards+tuple(c for c in package.cards if c.definition.key not in keys)))
    return pool,{'control':tuple(c.definition.key for c in control.cards),'package':tuple(c.definition.key for c in package.cards)}


def prepare(players,seed,seat,deck):
    pool,decks=study_content();actors=tuple(f'P{i+1}' for i in range(players))
    session=HarnessSession(tuple(f'Player {i+1}' for i in range(players)),pack=pool,seed=hashlib.sha256(seed.encode()).digest())
    # The ordinary validated setup transaction selects actual forty-card decks
    # from a shared pool. No in-progress match or private draw order is edited.
    for actor in actors:
        selection=DeckSelection('Study '+(deck if actor==seat else 'control'),'Gold','core-gold',decks[deck if actor==seat else 'control'])
        session._lobby=select_deck(session._lobby,actor,selection,expected_revision=session.view()['revision'])
        session.ready(actor,True,expected_revision=session.view()['revision'])
    session.start('P1',expected_revision=session.view()['revision'])
    for actor in actors:session.redraw(actor,(),expected_revision=session.view()['revision'])
    return session,actors,pack_hash(pool),hashlib.sha256(json.dumps(decks[deck]).encode()).hexdigest()


def evaluate_game(players=2,seed='package-1',seat='P1',deck='package',policy='baseline',limit=4000):
    if type(players) is not int or players not in (2,3,4) or seat not in tuple(f'P{i+1}' for i in range(players)) or deck not in ('control','package') or policy not in ('baseline','aware') or type(limit) is not int or limit<1:raise ValueError('Invalid package comparison settings')
    experimental=choose_move
    if policy=='aware':
        from .package_opponent import choose_package_move
        experimental=choose_package_move
    s,actors,content_hash,deck_hash=prepare(players,seed,seat,deck)
    first=s.view()['turn']['active_player'];known={};events=set();effects=set();entries={k:0 for k in PAYOFFS+PACKAGE_KEYS}
    queued={k:0 for k in PAYOFFS};delivered={k:0 for k in PAYOFFS}
    elimination=None;own_starts_at_elimination=None;end_discards=0;outlet_discards=0;paid_refills=0;recharge_turns=set();paid=0
    for count in range(limit+1):
        public=s.view();me=next(p for p in public['players'] if p['player_id']==seat)
        if me['eliminated'] and elimination is None:
            elimination=public['turn']['turn_id'];own_starts_at_elimination=me['resources']['own_starts']
        if public['turn']['active_player']==seat and public['turn']['recharge']:recharge_turns.add(public['turn']['turn_id'])
        for card in public['pending_cards']+public['battlefield']:
            if card.get('definition_key'):known[card['instance_id']]=(card['definition_key'],card['controller'])
        for event in public['events']:
            if event['event_id'] in events:continue
            events.add(event['event_id']);key,owner=known.get(event['subject'],(None,None))
            if event['kind']=='card_resolved' and owner==seat and key in entries:entries[key]+=1
        for effect in public['chain']:
            if effect['effect_id'] in effects:continue
            effects.add(effect['effect_id']);key,owner=known.get(effect['source_id'],(None,None))
            if owner==seat and key in queued and effect['label'] in ('Draw trigger','Discard trigger'):queued[key]+=1
        if public['result'] or count==limit:
            return {'players':players,'seed':seed,'seat':seat,'deck':deck,'policy':policy,'limit':limit,
                'status':'completed' if public['result'] else 'incomplete','commands':count,'global_turns':public['turn']['turn_id'],
                'starting_seat':first,'result':public['result'],'content_hash':content_hash,'deck_hash':deck_hash,
                'eliminated_at_global_turn':elimination,'survival_censored':elimination is None,
                'experimental_own_starts':me['resources']['own_starts'] if own_starts_at_elimination is None else own_starts_at_elimination,
                'entries':entries,'queued':queued,'delivered':delivered,'end_discards':end_discards,
                'outlet_discards':outlet_discards,'paid_refills':paid_refills,'recharge_turns':len(recharge_turns),'focus_resources_paid':paid}
        selected=None
        for actor in actors:
            view=s.view(actor);move=(experimental if actor==seat else choose_move)(view)
            if move:selected=(actor,view,move);break
        if selected is None:raise RuntimeError('No projected legal command')
        actor,view,(kind,args)=selected
        if actor==seat:
            if kind=='end_discard':end_discards+=len(args['cards'])
            if kind=='effect_discard':outlet_discards+=1
            if kind=='refill' and args['pay']:paid_refills+=1
            if kind=='play_card':
                card=next(c for c in view['you']['hand'] if c['instance_id']==args['card_id'])
                if card['definition_key'] in entries:paid+=card['cost']
        top=public['chain'][-1] if public['chain'] else None
        s.send(actor,{'kind':kind,'args':args,'expected_revision':view['revision']})
        after=s.view()
        if kind=='pass' and top and top['effect_id'] not in {e['effect_id'] for e in after['chain']} and top['label'] in ('Draw trigger','Discard trigger'):
            key,owner=known.get(top['source_id'],(None,None))
            if owner==seat and key in delivered:
                post=next(p for p in after['players'] if p['player_id']==seat)
                field='permanent_bonus' if key=='beacon-03' else 'available'
                delivered[key]+=max(0,post['resources'][field]-me['resources'][field])


def run_batch(seeds=('package-1','package-2'),players=(2,3,4),policies=('baseline','aware'),limit=4000):
    return [evaluate_game(p,seed,f'P{i+1}',deck,policy,limit) for seed in seeds for p in players
            for i in range(p) for policy in policies for deck in ('control','package')]


def summarize(rows):
    """Keep incomplete results visible and keep observed Starts separate from wins."""
    groups={}
    for r in rows:
        key=(r['seed'],r['players'],r['policy'],r['deck'])
        g=groups.setdefault(key,{'seed':key[0],'players':key[1],'policy':key[2],'deck':key[3],
            'games':0,'completed':0,'wins':0,'own_starts':0,'outlet_entries':0,'outlet_discards':0,
            'lantern_resources':0,'battery_resources':0,'well_capacity':0,'paid_refills':0,'censored':0})
        g['games']+=1;g['completed']+=int(r['status']=='completed')
        g['wins']+=int((r['result'] or {}).get('winner')==r['seat'])
        g['own_starts']+=r['experimental_own_starts'];g['outlet_entries']+=r['entries'][PACKAGE_KEYS[0]]
        g['outlet_discards']+=r['outlet_discards'];g['lantern_resources']+=r['delivered']['beacon-01']
        g['battery_resources']+=r['delivered']['beacon-02'];g['well_capacity']+=r['delivered']['beacon-03']
        g['paid_refills']+=r['paid_refills'];g['censored']+=int(r['survival_censored'])
    return list(groups.values())


def markdown(rows):
    validate_report(rows)
    lines=['# Seat-rotated package comparison','','Generated from synthetic study records by package_eval.markdown. Method and limits: PACKAGE_POLICY.md.','',
        '| Seed | Seats | Policy | Deck | Complete | Wins | Observed own Starts (sum) | Outlet discards | Lantern resources | Battery resources | Well capacity | Paid refills |',
        '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for g in sorted(summarize(rows),key=lambda g:(g['seed'],g['players'],g['policy']!='baseline',g['deck']!='control')):
        lines.append('| '+ ' | '.join(str(g[k]) for k in ('seed','players','policy','deck'))+
            f" | {g['completed']}/{g['games']} | {g['wins']} | "+' | '.join(str(g[k]) for k in ('own_starts','outlet_discards','lantern_resources','battery_resources','well_capacity','paid_refills'))+' |')
    lines+=['','Observed own Starts include censored survivors and are not a survival estimate. Resource delivery and permanent capacity are different units. Incomplete games do not have inferred winners.','']
    return '\n'.join(lines)


def validate_report(rows):
    if not rows:raise ValueError('No study records')
    identities=set();pairs={};rotations={};deck_hashes={};content={r['content_hash'] for r in rows}
    if len(content)!=1:raise ValueError('Study content differs across records')
    for r in rows:
        key=tuple(r[k] for k in ('seed','players','seat','policy','deck'))
        if key in identities:raise ValueError('Duplicate study record')
        identities.add(key)
        rotation=tuple(r[k] for k in ('seed','players','policy'))
        rotations.setdefault(rotation,set()).add(r['seat'])
        pair=tuple(r[k] for k in ('seed','players','seat','policy'))
        p=pairs.setdefault(pair,[]);p.append(r)
        if r['deck'] in deck_hashes and deck_hashes[r['deck']]!=r['deck_hash']:raise ValueError('Deck contents changed across records')
        deck_hashes[r['deck']]=r['deck_hash']
    for pair in pairs.values():
        if {r['deck'] for r in pair}!={'control','package'} or len({(r['starting_seat'],r['limit']) for r in pair})!=1:raise ValueError('Unmatched deck pair')
    for (_,players,_),seats in rotations.items():
        if seats!={f'P{i+1}' for i in range(players)}:raise ValueError('Incomplete seat rotation')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seeds',nargs='+',default=['package-1','package-2'])
    parser.add_argument('--players',type=int,nargs='+',choices=(2,3,4),default=[2,3,4])
    parser.add_argument('--policies',nargs='+',choices=('baseline','aware'),default=['baseline','aware'])
    parser.add_argument('--limit',type=int,default=4000)
    parser.add_argument('--report-input',type=Path,nargs='+',help='regenerate a report from synthetic study JSON files')
    parser.add_argument('--format',choices=('json','markdown'),default='json')
    args=parser.parse_args()
    rows=[r for p in args.report_input for r in json.loads(p.read_text(encoding='utf-8'))] if args.report_input else run_batch(args.seeds,args.players,args.policies,args.limit)
    validate_report(rows)
    if args.format=='markdown':print(markdown(rows),end='')
    else:print(json.dumps(rows,indent=2))
    return 0 if all(r['status']=='completed' for r in rows) else 2


if __name__=='__main__':raise SystemExit(main())
