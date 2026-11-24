"""Deterministic practice policy. Receives one permitted projection, never server state."""
from crucible_core.combat import CombatState,Player,Creature,Shield,Attack
from crucible_core.combat_flow import CombatFlow,resolve_committed


def _public_combat(view, removed=(), ward=None):
    """Reuse the damage kernel on revealed data only; never inspect private locks."""
    creatures=[]
    for obj in view['battlefield']:
        if not obj.get('creature') or obj['instance_id'] in removed:continue
        c=obj['creature'];shields=tuple(Shield(s['shield_id'],s['amount'],s['expiry_rank']) for s in c['shields'])
        if ward and obj['instance_id']==ward[0]:
            identity='policy-probe'
            while any(s.shield_id==identity for s in shields):identity+='-'
            shields+=(Shield(identity,ward[1]),)
        creatures.append(Creature(obj['instance_id'],obj['controller'],c['attack'],c['health'],c['max_health'],c['exhausted'],c['attack_eligible'],c['attack_used'],tuple(c['keywords']),shields))
    combat=view['combat'];blockers=dict(combat['blockers'])
    attacks=tuple(Attack(i,p,tuple(blockers.get(i,())),bool(blockers.get(i,())),challenge) for i,p,challenge in combat['attacks'])
    flow=CombatFlow(view['turn']['active_player'],attacks,'final_responses',orders=tuple(combat['orders']))
    snapshot=CombatState(tuple(Player(p['player_id'],p['health']) for p in view['players'] if not p['eliminated']),tuple(creatures))
    return resolve_committed(snapshot,flow)


def _final_reaction(view):
    combat=view.get('combat')
    if not combat or combat['stage']!='final_responses':return None
    live=_expected_chain(view)
    if any(s['kind'] not in ('destroy','return_to_hand','exile','negate') for e in live for s in e['steps']):return None
    removed={s.get('target') for e in live for s in e['steps'] if s['kind'] in ('destroy','return_to_hand','exile')}
    baseline=_public_combat(view,removed);actor=view['you']['player_id']
    health={p.player_id:p.health for p in baseline.state.players}
    own={o['instance_id']:max(1,o['creature']['attack']+o.get('cost',0)) for o in view['battlefield'] if o['controller']==actor and o.get('creature')}
    choices=[]
    for card in view['you']['hand']:
        steps=card.get('steps',[])
        if card['kind']!='reaction' or len(steps)!=1 or steps[0]['kind'] not in ('return_to_hand','exile','shield'):continue
        payment=exact_payment(view,card['cost'])
        if payment is None:continue
        for target in targets(view,card):
            if target in removed:continue
            result=_public_combat(view,removed,ward=(target,steps[0]['amount'])) if steps[0]['kind']=='shield' else _public_combat(view,removed|{target})
            after={p.player_id:p.health for p in result.state.players}
            saved=sum(value for identity,value in own.items() if identity in baseline.defeated_creatures and identity not in result.defeated_creatures)
            score=1000000*int(health[actor]<=0<after[actor])+100*max(0,after[actor]-health[actor])+10*sum(max(0,h-after[p]) for p,h in health.items() if p!=actor)+saved
            if score>0:choices.append((-score,card['cost'],card['instance_id'],target,payment))
    if not choices:return None
    _,_,identity,target,payment=min(choices,key=lambda c:c[:4])
    return 'play_card',{'card_id':identity,'target':target,'payment':payment}


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
    elif kind=='discard':
        own=next(p for p in view['players'] if p['player_id']==actor)
        committed={s.get('target') for e in _expected_chain(view) for s in e['steps'] if s['kind']=='recover'}
        budget=max(0,own['resources']['available']-card['cost'])
        cards=[c for c in own.get('discard',[]) if c.get('definition_key') and c['instance_id'] not in committed]
        return [c['instance_id'] for c in sorted(cards,key=lambda c:(c['kind']!='creature',c['cost']>budget,-c.get('attack',0),c['cost'],c['instance_id']))]
    else:items=[(str(e['effect_id']),e['controller'],-e['effect_id']) for e in view['chain'] if not e['resolving']]
    options=[key for key,owner,_ in sorted(items,key=lambda x:(x[2],x[0])) if relation=='any' or (relation=='enemy' and owner!=actor) or (relation=='friendly' and owner==actor)]
    if kind=='creature' and any(s['kind'] in ('return_to_hand','exile') for s in card.get('steps',[])):
        return _zone_move_targets(view,options,exile=any(s['kind']=='exile' for s in card['steps']))
    return options


def _expected_chain(view):
    """Public items still on track to resolve, assuming no further responses."""
    cancelled=set();live=[]
    for effect in reversed(view['chain']):
        if effect['effect_id'] in cancelled:continue
        live.append(effect)
        for step in effect['steps']:
            if step['kind']=='negate' and type(step.get('effect_id')) is int:
                cancelled.add(step['effect_id'])
    return tuple(reversed(live))


def _zone_move_targets(view, options, *, exile=False):
    """Public-stat tempo heuristics; no hidden zones or speculative combat resolver."""
    actor=view['you']['player_id'];objects={o['instance_id']:o for o in view['battlefield']}
    committed={s.get('target') for e in _expected_chain(view) for s in e['steps'] if s['kind'] in ('destroy','return_to_hand','exile')}
    combat=view.get('combat');scores={}
    fighting=combat and combat['stage'] in ('attack_responses','final_responses')
    main=view['turn']['active_player']==actor and view['turn']['phase'] in ('MainBefore','MainAfter') and not view['chain']
    blockers=dict(combat.get('blockers',())) if fighting else {}
    for key in options:
        if key in committed:continue
        obj=objects[key];c=obj['creature'];score=0
        if fighting:
            for attacker,defender,challenge in combat['attacks']:
                attack_obj=objects.get(attacker)
                if not attack_obj:continue
                attack=attack_obj['creature']
                guards=[objects[b] for b in blockers.get(attacker,()) if b in objects]
                safe_block=guards and all(not b['creature']['exhausted'] for b in guards) and sum(b['creature']['health']+sum(s['amount'] for s in b['creature']['shields']) for b in guards)>=attack['attack']
                threatened=defender==actor or (challenge in objects and objects[challenge]['controller']==actor)
                if key==attacker and threatened and not safe_block and attack['attack']>0:
                    score=max(score,100+attack['attack'])
                if attack_obj['controller']==actor and 'breakthrough' in attack['keywords'] and key in blockers.get(attacker,()):
                    score=max(score,90+c['health'])
        elif main and (c['attack']>0 or any(o['controller']==actor and o.get('creature') and o['creature']['attack']>0 for o in objects.values())):
            score=c['attack']+min(obj.get('cost',0),8)*2
            if obj['kind']=='creature_token' and not exile:score+=30
            if obj['kind']=='leader' and not exile:score+=20
            if obj['kind']=='creature' and exile:score+=20
        if score>0:scores[key]=score
    return sorted(scores,key=lambda key:(-scores[key],key))


def opening_choice(view):
    own=view.get('you')
    if view.get('phase')!='opening' or not own or own['locked']:return None
    return [c['instance_id'] for c in own['hand'] if c.get('cost',0)>3]


def _useful(view, card):
    actor=view['you']['player_id'];me=next(p for p in view['players'] if p['player_id']==actor)
    steps=card.get('steps',[])
    if any(s['kind']=='discard_then_draw' for s in steps) and len(view['you']['hand'])<2:return False
    if any(s['kind']=='damage' and s.get('target')=='$controller' for s in steps):return False
    # Keep limited healing for low-life emergencies rather than recasting at every scratch.
    if steps and all(s['kind']=='heal' for s in steps) and me['health']>me['max_health']//3:return False
    if card.get('kind')=='permanent' and me['resources']['own_starts']>5 and not card.get('triggered_abilities'):return False
    return True


def choose_move(view):
    own=view.get('you')
    if not own or view.get('result'):return None
    actor=own['player_id'];choice=own['choice'];turn=view['turn'];priority=view['priority']
    if choice:
        kind=choice['kind']
        if kind=='effect_discard':
            card=max(own['hand'],key=lambda c:(c.get('cost',0),c['instance_id']))
            return 'effect_discard',{'card_id':card['instance_id'],'request_id':choice['request_id']}
        if kind=='optional_trigger':
            harmful=any(s['kind']=='damage' and s.get('target')==actor and s.get('amount',0)>0 for s in choice['steps'])
            return 'trigger_choice',{'trigger_id':choice['trigger_id'],'use':not harmful}
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
    reaction=_final_reaction(view)
    if reaction is not None:return reaction
    main=active and turn['phase'] in ('MainBefore','MainAfter') and not view['chain']
    own_leader=next((l for l in view.get('leaders',[]) if l['owner']==actor),None)
    if main and own_leader and own_leader['location']=='reserve' and not own_leader['recovering'] and own_leader['pending_effect_id'] is None:
        payment=exact_payment(view,own_leader['summon_cost'])
        if payment and sum(o['controller']==actor and bool(o.get('creature')) for o in view['battlefield'])<2:
            return 'summon_leader',{'payment':payment}
    combat_response=view.get('combat') and view['combat']['stage'] in ('attack_responses','final_responses')
    if main or view['chain'] or combat_response:
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
