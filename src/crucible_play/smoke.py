"""Bounded, view-only scripted driver for exercising the local harness."""
import argparse
import hashlib
import json
from .session import HarnessSession


def choose_move(view):
    """Input is one permitted player projection, never authoritative MatchState."""
    own=view.get('you')
    if own is None:return None
    actor=own['player_id'];choice=own['choice']
    if choice:
        kind=choice['kind']
        if kind=='refill':return 'refill',{'pay':True,'request_id':choice['request_id']}
        if kind=='end_discard':return 'end_discard',{'cards':[c['instance_id'] for c in own['hand'][:choice['count']]]}
        if kind=='blockers':
            if choice['locked']:return None
            return 'lock_blockers',{'assignments':[{'attacker_id':a[0],'blockers':[]} for a in view['combat']['attacks'] if a[1]==actor and a[2] is None]}
        if kind=='combat_order':
            order=choice['orders'][0]
            return 'combat_order',{'subject':order['subject'],'order':order['items']}
        if kind=='trigger_order':return 'trigger_order',{'order':[t['trigger_id'] for t in choice['triggers']]}
    priority=view['priority'];turn=view['turn']
    if priority and priority['status']=='closed' and turn['phase']=='Combat' and turn['active_player']==actor and view['combat'] is None:
        enemies=[p for p in view['players'] if not p['eliminated'] and p['player_id']!=actor]
        target=min(enemies,key=lambda p:(p['health'],p['player_id']))['player_id']
        attacks=[{'attacker_id':o['instance_id'],'target_player':target} for o in view['battlefield'] if o['controller']==actor and o.get('creature') and not o['creature']['exhausted'] and o['creature']['attack_eligible'] and not o['creature']['attack_used']]
        return 'declare_attacks',{'attacks':attacks}
    if priority is None or priority['holder']!=actor:return None
    if actor==turn['active_player'] and turn['phase'] in ('MainBefore','MainAfter') and not view['chain'] and not turn['end_requested']:
        available=next(p['resources']['available'] for p in view['players'] if p['player_id']==actor)
        for c in own['hand']:
            if c['cost']>available:continue
            if c['kind']=='creature':
                return 'play_card',{'card_id':c['instance_id'],'payment':{'ordinary':c['cost'],'token_ids':[]}}
            if c['kind']=='action' and c['target_kind']=='player' and c['target_relation']=='enemy':
                target=next(p['player_id'] for p in view['players'] if p['player_id']!=actor and not p['eliminated'])
                return 'play_card',{'card_id':c['instance_id'],'target':target,'payment':{'ordinary':c['cost'],'token_ids':[]}}
    return 'pass',{}


def run_smoke(players=2, seed='smoke-1', limit=4000):
    session=HarnessSession(tuple(f'Player {i+1}' for i in range(players)),seed=hashlib.sha256(seed.encode()).digest())
    actors=[p['player_id'] for p in session.view()['players']]
    for actor in actors:
        session.choose_deck(actor,'core-gold',expected_revision=session.view()['revision'])
        session.ready(actor,True,expected_revision=session.view()['revision'])
    session.start(actors[0],expected_revision=session.view()['revision'])
    for actor in actors:session.redraw(actor,(),expected_revision=session.view()['revision'])
    for index in range(limit):
        public=session.view()
        if public['result']:
            return {'status':'completed','commands':index,'turns':public['turn']['turn_id'],'result':public['result']}
        selected=None
        # The driver schedules separate projected clients; a policy never sees another hand.
        for actor in actors:
            view=session.view(actor)
            if view.get('you',{}).get('choice'):
                move=choose_move(view)
                if move:selected=(actor,view,move);break
        if selected is None:
            actor=public['priority']['holder'] or public['turn']['active_player']
            view=session.view(actor);move=choose_move(view)
            if move:selected=(actor,view,move)
        if selected is None:return {'status':'incomplete','reason':'no projected command','commands':index}
        actor,view,(kind,args)=selected
        session.send(actor,{'kind':kind,'expected_revision':view['revision'],'args':args})
    return {'status':'incomplete','reason':'command limit','commands':limit}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--players',type=int,choices=(2,3,4),default=2)
    parser.add_argument('--seed',default='smoke-1')
    parser.add_argument('--limit',type=int,default=4000)
    args=parser.parse_args()
    report=run_smoke(args.players,args.seed,args.limit)
    print(json.dumps(report,indent=2))
    return 0 if report['status']=='completed' else 2


if __name__=='__main__':raise SystemExit(main())
