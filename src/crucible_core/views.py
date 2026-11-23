"""Allowlisted player/spectator projections. Never serialize MatchState to clients."""
from .match import MatchError, _living, match_combat_view


def project_match(state, viewer=None):
    from .match import _next_optional_trigger,_trigger_order_waiting
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
                          'resolving':effect==priority.resolving,'label':_effect_label(state,effect,spec),'steps':[_public_step(state,s) for s in spec.steps]})
    view={'revision':state.revision,'turn':{'active_player':state.turn.active_player,'turn_id':state.turn.turn_id,
          'phase':state.turn.phase,'recharge':state.turn.recharge,'end_requested':state.turn.end_requested or next(p.cards.end_turn_requested for p in state.players if p.cards.player_id==state.turn.active_player)},
          'players':players,'battlefield':[_object(state,o) for o in state.battlefield],
          'exile':[{**_card(state,i),'owner':next(c.owner for c in state.card_instances if c.instance_id==i)} for i in state.exiled],
          'priority':None if priority is None else {'holder':priority.holder,'status':priority.status,'passes':list(priority.passes)},
          'choice_pending':bool(state.pending or state.triggers or state.discard_needed or (state.combat and state.combat.stage in ('blocking','ordering'))),
          'leaders':_leaders(state),
          'durations':[{'duration_id':d.duration_id,'controller':d.controller,'target_id':d.target_id,'shield_id':d.shield_id,'anchor_player':d.anchor_player,'boundary':d.boundary,'occurrence':d.occurrence,'expiration_steps':[_public_step(state,s) for s in d.expiration_steps]} for d in state.durations],
          'boundary_counts':[{'player_id':b.player_id,'starts':b.starts,'ends':b.ends} for b in state.boundary_counts],
          'chain':chain,'pending_cards':[{**_card(state,c.card_id),'effect_id':c.effect_id,'controller':c.controller} for c in state.pending_cards],'combat':match_combat_view(state,private),
          'result':None if state.result is None else {'kind':state.result.kind,'winner':state.result.winner},
          'events':_public_events(state)}
    if private:
        player=next(p for p in state.players if p.cards.player_id==private)
        view['you']={'player_id':private,'hand':[_card(state,i) for i in player.cards.hand],
                     'choice':_own_choice(state,private)}
    waiting=_next_optional_trigger(state)
    view['trigger_waiting']=waiting.controller if waiting else None
    view['trigger_order_waiting']=list(_trigger_order_waiting(state))
    return view


def _card(state, instance_id):
    record=next((c for c in getattr(state,'card_instances',()) if c.instance_id==instance_id),None)
    view={'instance_id':instance_id}
    if record is not None:
        definition=next(d for d in state.card_definitions if d.key==record.definition_key)
        view.update({'definition_key':definition.key,'kind':definition.kind,'cost':definition.cost,
                     'target_kind':definition.target_kind,'target_relation':definition.target_relation,
                     'steps':[_step(s) for s in definition.steps],'capacity_bonus':definition.capacity_bonus,
                     'triggered_abilities':[{'key':a.key,'event':a.event,'watch':a.watch,'optional':a.optional,'steps':[_step(s) for s in a.steps]} for a in definition.triggered_abilities]})
        if definition.kind=='creature':
            view.update({'attack':definition.attack,'health':definition.health,'keywords':list(definition.keywords)})
    return view


def _object(state, obj):
    view={**_card(state,obj.object_id),'owner':obj.owner,'controller':obj.controller,'kind':obj.kind,
          'attached_to':obj.attached_to,'capacity_bonus':obj.capacity_bonus}
    if obj.kind=='leader':
        leader=next(l for l in state.leaders if l.instance_id==obj.object_id)
        definition=next(d for d in state.leader_definitions if d.key==leader.definition_key)
        view.update({'name':definition.name,'definition_key':definition.key,'cost':definition.summon_cost,
                     'attack':definition.attack,'health':definition.health,'keywords':list(definition.keywords)})
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
    if state.pending:return None
    from .match import _next_optional_trigger
    optional=_next_optional_trigger(state)
    if optional:
        if optional.controller!=actor:return None
        effect=next(e for e in state.effects if e.key==optional.effect_key)
        return {'kind':'optional_trigger','trigger_id':optional.trigger_id,'source_id':optional.source_id,
                'steps':[_public_step(state,s) for s in effect.steps]}
    from .match import _trigger_order_waiting
    own=tuple(t for t in state.triggers if t.controller==actor and t.decision is not False)
    if actor in _trigger_order_waiting(state):
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
    allowed={'damage','heal','required_draw','card_drawn','card_discarded','combat_damage','combat_miss','elimination','departure','defeat',
             'turn_end','turn_start','action_committed','concede_request','start_refill',
             'attacks_declared','blockers_revealed','card_played','card_resolved','card_cancelled','card_returned','card_exiled','card_recovered','effect_negated','leader_summoned','leader_returned','leader_summon_cancelled','leader_ability','leader_summon_committed','duration_expired','prevention_granted','scheduled_boundary'}
    events=[]
    for event in state.events:
        if event.kind not in allowed:continue
        row={'event_id':event.event_id,'kind':event.kind,'subject':event.subject}
        if event.kind in ('card_played','card_returned','card_exiled','card_recovered'):row['card']=_card(state,event.subject)
        if event.kind=='scheduled_boundary' and event.cause in ('Start','End'):row['boundary']=event.cause
        if event.kind=='duration_expired':
            parts=event.cause.rsplit(':',2)
            if len(parts)==3 and parts[0] in state.seat_order and parts[1] in ('Start','End') and parts[2].isdecimal():
                row['expiration']={'anchor_player':parts[0],'boundary':parts[1],'occurrence':int(parts[2])}
        events.append(row)
    return events


def _step(step):
    # Effect types are closed/validated by the coordinator; do not recursively dump.
    from .match import DamagePlayer, HealPlayer, DrawCards, DestroyCreature, ReturnCreatureToHand, ExileCreature, RecoverDiscardCard, GrantCapacity, GrantResources, NegateEffect, GrantShield
    if type(step) is GrantShield:return {'kind':'shield','target':step.target,'amount':step.amount,'duration':step.duration,'anchor_player':step.anchor_player}
    if type(step) is NegateEffect:return {'kind':'negate','effect_id':step.effect_id}
    if type(step) is DestroyCreature:return {'kind':'destroy','target':step.target}
    if type(step) is ReturnCreatureToHand:return {'kind':'return_to_hand','target':step.target}
    if type(step) is ExileCreature:return {'kind':'exile','target':step.target}
    if type(step) is RecoverDiscardCard:return {'kind':'recover','target':step.target}
    labels={DamagePlayer:'damage',HealPlayer:'heal',DrawCards:'draw',GrantCapacity:'capacity',GrantResources:'resources'}
    if type(step) not in labels:raise MatchError('unsupported projected instruction')
    return {'kind':labels[type(step)],'target':step.target,'amount':step.count if type(step) is DrawCards else step.amount}


def _public_step(state, step):
    view=_step(step)
    target=view.get('target')
    public_ids=set(state.seat_order)|{o.object_id for o in state.battlefield}|{l.instance_id for l in state.leaders}
    public_ids.update(c.card_id for c in state.pending_cards)
    public_ids.update(i for p in state.players if not p.eliminated for i in p.cards.discard)
    public_ids.update(state.exiled)
    public_ids.update(e.subject for e in state.events if e.kind in ('departure','defeat','card_played'))
    if target is not None and target not in public_ids:
        view['target']=None
    return view

def _leaders(state):
    from .match import leader_ability_available
    leaders=[]
    for leader in state.leaders:
        definition=next(d for d in state.leader_definitions if d.key==leader.definition_key)
        abilities=[]
        for location,ability in (('reserve',definition.reserve_ability),('battlefield',definition.battle_ability)):
            abilities.append({'key':ability.key,'location':location,'cost':ability.cost,'timing':ability.timing,
                             'target_kind':ability.target_kind,'target_relation':ability.target_relation,
                             'exhaust_source':ability.exhaust_source,'once_per_turn':ability.once_per_turn,
                             'steps':[_step(s) for s in ability.steps],
                             'available':leader_ability_available(state,leader,ability)})
        leaders.append({'instance_id':leader.instance_id,'owner':leader.owner,'definition_key':definition.key,
                        'name':definition.name,'color':definition.color,'location':leader.location,
                        'removals':leader.removals,'recovering':leader.recovering,'pending_effect_id':leader.pending_effect_id,
                        'base_summon_cost':definition.summon_cost,'summon_cost':definition.summon_cost+2*leader.removals,
                        'attack':definition.attack,'health':definition.health,'keywords':list(definition.keywords),'abilities':abilities})
    return leaders


def _effect_label(state, effect, spec):
    leader=next((l for l in state.leaders if l.pending_effect_id==effect.effect_id or l.instance_id==spec.source_id),None)
    if leader:
        definition=next(d for d in state.leader_definitions if d.key==leader.definition_key)
        return f'Summon {definition.name}' if leader.pending_effect_id==effect.effect_id else f'{definition.name}: ability'
    from .match import _trigger_key
    card=next((c for c in state.card_instances if c.instance_id==spec.source_id),None)
    if card:
        definition=next(d for d in state.card_definitions if d.key==card.definition_key)
        for ability in definition.triggered_abilities:
            if spec.key==_trigger_key(card.instance_id,ability.key):return 'Draw trigger' if ability.event=='card_drawn' else 'Discard trigger'
    return spec.key
