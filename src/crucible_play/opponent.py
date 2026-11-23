"""Deterministic practice policy. Receives one permitted projection, never server state."""


def exact_payment(view, cost):
    actor=view['you']['player_id']
    available=next(p['resources']['available'] for p in view['players'] if p['player_id']==actor)
    tokens=[o for o in view['battlefield'] if o['controller']==actor and o['kind']=='resource_token']
    for ordinary in range(min(cost,available),-1,-1):
        needed=cost-ordinary;options={0:[]}
        for token in tokens:
            for amount,ids in tuple(options.items()):
                total=amount+token['resource_value']
                if total<=needed and total not in options:options[total]=ids+[token['instance_id']]
        if needed in options:return {'ordinary':ordinary,'token_ids':options[needed]}
    return None


def targets(view, card):
    actor=view['you']['player_id'];kind=card.get('target_kind');relation=card.get('target_relation','any')
    if kind is None:return [None]
    if kind=='player':items=[(p['player_id'],p['player_id'],p['health']) for p in view['players'] if not p['eliminated']]
    elif kind=='creature':items=[(o['instance_id'],o['controller'],-o['creature']['attack']) for o in view['battlefield'] if o.get('creature')]
    else:items=[(str(e['effect_id']),e['controller'],-e['effect_id']) for e in view['chain'] if not e['resolving']]
    return [key for key,owner,_ in sorted(items,key=lambda x:(x[2],x[0])) if relation=='any' or (relation=='enemy' and owner!=actor) or (relation=='friendly' and owner==actor)]


def opening_choice(view):
    own=view.get('you')
    if view.get('phase')!='opening' or not own or own['locked']:return None
    return [c['instance_id'] for c in own['hand'] if c.get('cost',0)>3]


def _useful(view, card):
    actor=view['you']['player_id'];me=next(p for p in view['players'] if p['player_id']==actor)
    steps=card.get('steps',[])
    if any(s['kind']=='damage' and s.get('target')=='$controller' for s in steps):return False
    # Keep limited healing for low-life emergencies rather than recasting at every scratch.
    if steps and all(s['kind']=='heal' for s in steps) and me['health']>me['max_health']//3:return False
    if card.get('kind')=='permanent' and me['resources']['own_starts']>5:return False
    return True


def choose_move(view):
    own=view.get('you')
    if not own or view.get('result'):return None
    actor=own['player_id'];choice=own['choice'];turn=view['turn'];priority=view['priority']
    if choice:
        kind=choice['kind']
        if kind=='refill':return 'refill',{'pay':True,'request_id':choice['request_id']}
        if kind=='end_discard':
            cards=sorted(own['hand'],key=lambda c:(-c['cost'],c['instance_id']))
            return 'end_discard',{'cards':[c['instance_id'] for c in cards[:choice['count']]]}
        if kind=='trigger_order':return 'trigger_order',{'order':[t['trigger_id'] for t in choice['triggers']]}
        if kind=='combat_order':
            order=choice['orders'][0]
            return 'combat_order',{'subject':order['subject'],'order':list(order['items'])}
        if kind=='blockers':
            if choice['locked']:return None
            challenged={a[2] for a in view['combat']['attacks'] if a[2]}
            blockers=sorted((o for o in view['battlefield'] if o['controller']==actor and o.get('creature') and o['instance_id'] not in challenged),key=lambda o:(-o['creature']['health'],o['instance_id']))
            assigned=[]
            for attacker,target,challenge in view['combat']['attacks']:
                if target!=actor or challenge is not None:continue
                # A simple public-stat heuristic, not a second damage resolver.
                used=[blockers.pop(0)['instance_id']] if blockers else []
                assigned.append({'attacker_id':attacker,'blockers':used})
            return 'lock_blockers',{'assignments':assigned}
    if view.get('choice_pending'):return None
    if priority and priority['status']=='closed' and turn['phase']=='Combat' and turn['active_player']==actor and view['combat'] is None:
        enemies=[p for p in view['players'] if not p['eliminated'] and p['player_id']!=actor]
        if not enemies:return None
        target=min(enemies,key=lambda p:(p['health'],p['player_id']))['player_id']
        return 'declare_attacks',{'attacks':[{'attacker_id':o['instance_id'],'target_player':target} for o in view['battlefield'] if o['controller']==actor and o.get('creature') and o['creature']['attack']>0 and not o['creature']['exhausted'] and o['creature']['attack_eligible'] and not o['creature']['attack_used']]}
    if not priority or priority['holder']!=actor:return None
    active=turn['active_player']==actor
    if active and (turn['recharge'] or turn['end_requested']):return 'pass',{}
    main=active and turn['phase'] in ('MainBefore','MainAfter') and not view['chain']
    own_leader=next((l for l in view.get('leaders',[]) if l['owner']==actor),None)
    if main and own_leader and own_leader['location']=='reserve' and not own_leader['recovering'] and own_leader['pending_effect_id'] is None:
        payment=exact_payment(view,own_leader['summon_cost'])
        if payment and sum(o['controller']==actor and bool(o.get('creature')) for o in view['battlefield'])<2:
            return 'summon_leader',{'payment':payment}
    if main or view['chain']:
        cards=sorted(own['hand'],key=lambda c:(c['kind']!='creature',c['cost'],c['instance_id']))
        for card in cards:
            if not main and card['kind']!='reaction':continue
            if not _useful(view,card):continue
            options=targets(view,card);payment=exact_payment(view,card['cost'])
            if not options or payment is None:continue
            args={'card_id':card['instance_id'],'payment':payment}
            if card.get('target_kind'):args['target']=options[0]
            return 'play_card',args
        if own_leader:
            for ability in own_leader.get('abilities',[]):
                if not ability['available'] or (not main and ability['timing']!='reaction') or not _useful(view,ability):continue
                if ability['exhaust_source'] and turn['phase']=='MainBefore':continue
                options=targets(view,ability);payment=exact_payment(view,ability['cost'])
                if payment is None or not options:continue
                args={'key':ability['key'],'payment':payment}
                if ability.get('target_kind'):args['target']=options[0]
                return 'leader_ability',args
    return 'pass',{}
