"""Allowlisted player/spectator projections. Never serialize MatchState to clients."""
from .match import MatchError, _living, match_combat_view


def project_match(state, viewer=None):
    if viewer is not None and (type(viewer) is not str or viewer not in state.seat_order):
        raise MatchError('unknown viewer')
    private=viewer if viewer in _living(state) else None
    players=[]
    for p in state.players:
        cards=p.cards
        row={'player_id':cards.player_id,'health':cards.health,'max_health':p.max_health,
             'eliminated':p.eliminated,'hand_count':len(cards.hand),'deck_count':len(cards.deck),
             'resources':{'natural_capacity':p.resources.natural_capacity,'permanent_bonus':p.resources.permanent_bonus,
                          'available':p.resources.available,'own_starts':p.resources.own_starts},
             'recharge_due':cards.recharge_due}
        # Eliminated players' zones are inaccessible, including to their old session.
        if not p.eliminated:
            row['discard']=[_card(state,i) for i in cards.discard]
        players.append(row)
    priority=state.priority
    chain=[]
    if priority:
        for effect in priority.chain+((priority.resolving,) if priority.resolving else ()):
            spec=next(e for e in state.effects if e.key==effect.effect_key)
            chain.append({'effect_id':effect.effect_id,'controller':effect.controller,
                          'effect_key':spec.key,'source_id':spec.source_id,
                          'resolving':effect==priority.resolving,'steps':[_public_step(state,s) for s in spec.steps]})
    view={'revision':state.revision,'turn':{'active_player':state.turn.active_player,'turn_id':state.turn.turn_id,
          'phase':state.turn.phase,'recharge':state.turn.recharge,'end_requested':state.turn.end_requested or next(p.cards.end_turn_requested for p in state.players if p.cards.player_id==state.turn.active_player)},
          'players':players,'battlefield':[_object(state,o) for o in state.battlefield],
          'priority':None if priority is None else {'holder':priority.holder,'status':priority.status,'passes':list(priority.passes)},
          'chain':chain,'pending_cards':[{**_card(state,c.card_id),'effect_id':c.effect_id,'controller':c.controller} for c in state.pending_cards],'combat':match_combat_view(state,private),
          'result':None if state.result is None else {'kind':state.result.kind,'winner':state.result.winner},
          'events':_public_events(state)}
    if private:
        player=next(p for p in state.players if p.cards.player_id==private)
        view['you']={'player_id':private,'hand':[_card(state,i) for i in player.cards.hand],
                     'choice':_own_choice(state,private)}
    return view


def _card(state, instance_id):
    record=next((c for c in getattr(state,'card_instances',()) if c.instance_id==instance_id),None)
    view={'instance_id':instance_id}
    if record is not None:
        definition=next(d for d in state.card_definitions if d.key==record.definition_key)
        view.update({'definition_key':definition.key,'kind':definition.kind,'cost':definition.cost,
                     'target_kind':definition.target_kind,'target_relation':definition.target_relation,
                     'steps':[_step(s) for s in definition.steps],'capacity_bonus':definition.capacity_bonus})
        if definition.kind=='creature':
            view.update({'attack':definition.attack,'health':definition.health,'keywords':list(definition.keywords)})
    return view


def _object(state, obj):
    view={**_card(state,obj.object_id),'owner':obj.owner,'controller':obj.controller,'kind':obj.kind,
          'attached_to':obj.attached_to,'capacity_bonus':obj.capacity_bonus}
    if obj.kind=='resource_token':view['resource_value']=obj.resource_value
    if obj.creature:
        c=obj.creature
        view['creature']={'attack':c.attack,'health':c.health,'max_health':c.max_health,
             'exhausted':c.exhausted,'attack_eligible':c.attack_eligible,'attack_used':c.attack_used,
             'keywords':list(c.keywords),'shields':[{'shield_id':s.shield_id,'amount':s.amount,'expiry_rank':s.expiry_rank} for s in c.shields]}
    view['abilities']=[{'key':a.key,'cost':a.resource_cost,'timing':a.timing,'exhaust_source':a.exhaust_source,
                       'once_per_turn':a.once_per_turn,'steps':[_public_step(state,s) for e in state.effects if e.key==a.effect_key for s in e.steps]} for a in state.actions if a.source_id==obj.object_id]
    return view


def _own_choice(state, actor):
    draw=state.pending.draw if state.pending else None
    if draw and draw.player.player_id==actor:
        return {'kind':'refill','request_id':draw.request_id,'remaining':draw.remaining,
                'cost':draw.policy.life_cost,'minimum_health':draw.policy.minimum_health_after_payment}
    own=tuple(t for t in state.triggers if t.controller==actor)
    if own and actor not in dict(state.trigger_orders):
        return {'kind':'trigger_order','triggers':[{'trigger_id':t.trigger_id,'source_id':t.source_id,'effect_key':t.effect_key} for t in own]}
    if state.discard_needed and state.turn.active_player==actor:
        return {'kind':'end_discard','count':state.discard_needed}
    if state.combat:
        from .combat_flow import required_orders
        from .match import _combat_snapshot
        flow=state.combat
        if flow.stage=='blocking' and actor in flow.defenders:
            return {'kind':'blockers','locked':actor in dict(flow.locks)}
        if flow.stage=='ordering':
            choices=[{'subject':subject,'items':list(items)} for subject,owner,items in required_orders(_combat_snapshot(state),flow) if owner==actor]
            if choices:return {'kind':'combat_order','orders':choices}
    return None


def _public_events(state):
    # Deliberately omit raw causes, private draw records and unknown future events.
    allowed={'damage','heal','required_draw','combat_damage','combat_miss','elimination','departure','defeat',
             'turn_end','turn_start','action_committed','concede_request','start_refill',
             'attacks_declared','blockers_revealed','card_played','card_resolved','card_cancelled','effect_negated'}
    events=[]
    for event in state.events:
        if event.kind not in allowed:continue
        row={'event_id':event.event_id,'kind':event.kind,'subject':event.subject}
        if event.kind=='card_played':row['card']=_card(state,event.subject)
        events.append(row)
    return events


def _step(step):
    # Effect types are closed/validated by the coordinator; do not recursively dump.
    from .match import DamagePlayer, HealPlayer, DrawCards, DestroyCreature, GrantCapacity, GrantResources, NegateEffect
    if type(step) is NegateEffect:return {'kind':'negate','effect_id':step.effect_id}
    if type(step) is DestroyCreature:return {'kind':'destroy','target':step.target}
    labels={DamagePlayer:'damage',HealPlayer:'heal',DrawCards:'draw',GrantCapacity:'capacity',GrantResources:'resources'}
    if type(step) not in labels:raise MatchError('unsupported projected instruction')
    return {'kind':labels[type(step)],'target':step.target,'amount':step.count if type(step) is DrawCards else step.amount}


def _public_step(state, step):
    view=_step(step)
    target=view.get('target')
    public_ids=set(state.seat_order)|{o.object_id for o in state.battlefield}
    public_ids.update(c.card_id for c in state.pending_cards)
    public_ids.update(e.subject for e in state.events if e.kind in ('departure','defeat','card_played'))
    if target is not None and target not in public_ids:
        view['target']=None
    return view
