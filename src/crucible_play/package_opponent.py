"""Conservative package-aware policy; only one permitted seat projection is input."""
from .opponent import choose_move,exact_payment,targets

PAYOFFS=('beacon-01','beacon-02','beacon-03')


def _draw_count(card):
    return sum(s.get('amount',0) for s in card.get('steps',[]) if s['kind'] in ('draw','discard_then_draw'))


def _keep_value(card,view):
    own=view['you'];actor=own['player_id']
    board=[o for o in view['battlefield'] if o['controller']==actor]
    creatures=sum(bool(o.get('creature')) for o in board)
    key=card.get('definition_key');cost=card.get('cost',0)
    if card.get('kind')=='creature':return (50 if creatures<2 else 15)+card.get('attack',0)+card.get('health',0)
    if key in PAYOFFS:return 25 if creatures>=2 and not any(o.get('definition_key')==key for o in board) else 8
    if _draw_count(card):return 25 if len(own['hand'])<=4 else 12
    if any(s['kind']=='recover' for s in card.get('steps',[])):
        me=next(p for p in view['players'] if p['player_id']==actor)
        return 20 if any(c.get('definition_key')=='proposal-scrapyard-insight' for c in me['discard']) else 8
    return 10 if card.get('kind')=='reaction' else max(0,8-cost)


def choose_package_move(view):
    own=view.get('you')
    if not own or view.get('result'):return None
    choice=own['choice']
    if choice and choice['kind'] in ('effect_discard','end_discard'):
        cards=sorted(own['hand'],key=lambda c:(_keep_value(c,view),-c.get('cost',0),c['instance_id']))
        if choice['kind']=='effect_discard':return 'effect_discard',{'card_id':cards[0]['instance_id'],'request_id':choice['request_id']}
        return 'end_discard',{'cards':[c['instance_id'] for c in cards[:choice['count']]]}
    baseline=choose_move(view)
    if choice or view.get('choice_pending') or not baseline:return baseline
    actor=own['player_id'];turn=view['turn'];priority=view['priority']
    if not priority or priority['holder']!=actor or turn['active_player']!=actor or turn['phase'] not in ('MainBefore','MainAfter') or turn['recharge'] or turn['end_requested'] or view['chain']:return baseline
    me=next(p for p in view['players'] if p['player_id']==actor)
    # Do not voluntarily start a required draw that already needs paid refill.
    safe=[c for c in own['hand'] if _draw_count(c)<=me['deck_count']]
    if len(safe)!=len(own['hand']):
        view=dict(view,you=dict(own,hand=safe));baseline=choose_move(view)
    board=[o for o in view['battlefield'] if o['controller']==actor]
    creatures=sum(bool(o.get('creature')) for o in board)
    enemy_board=max((sum(bool(o.get('creature')) and o['controller']==p['player_id'] for o in view['battlefield']) for p in view['players'] if not p['eliminated'] and p['player_id']!=actor),default=0)
    if creatures<1 or me['health']<=me['max_health']//3 or baseline[0]=='summon_leader':return baseline
    if baseline[0]=='play_card':
        card=next(c for c in safe if c['instance_id']==baseline[1]['card_id'])
        if card['kind']=='creature' and (creatures<2 or creatures<=enemy_board):return baseline
        # Preserve a direct lethal play instead of spending on an engine.
        target=next((p for p in view['players'] if p['player_id']==baseline[1].get('target')),None)
        if target and sum(s.get('amount',0) for s in card['steps'] if s['kind']=='damage')>=target['health']:return baseline
    installed={o.get('definition_key') for o in board}
    has_outlet=any(any(s['kind']=='discard_then_draw' for s in c.get('steps',[])) for c in safe)
    has_draw=any(_draw_count(c)>0 for c in safe)
    candidates=[]
    for card in safe:
        key=card.get('definition_key');steps=card.get('steps',[]);score=0
        if key=='beacon-01' and has_draw:score=80
        elif key in ('beacon-02','beacon-03') and has_outlet and len(own['hand'])>=3 and me['deck_count']>=6:score=75 if key=='beacon-02' else 70
        elif any(s['kind']=='discard_then_draw' for s in steps) and len(own['hand'])>=2 and installed.intersection(PAYOFFS):score=65
        elif steps and all(s['kind']=='draw' for s in steps) and len(own['hand'])<=4:score=50
        if not score:continue
        options=targets(view,card);payment=exact_payment(view,card['cost'])
        if not options or payment is None:continue
        args={'card_id':card['instance_id'],'payment':payment}
        if card.get('target_kind'):args['target']=options[0]
        candidates.append((-score,card['cost'],card['instance_id'],args))
    return ('play_card',min(candidates,key=lambda c:c[:3])[3]) if candidates else baseline
