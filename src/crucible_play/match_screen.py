"""Readable local match table; consumes only the session's permitted projection.

Callbacks use the existing command/confirmation path. This module owns no rules,
catalog, saved state, or opponent-hand lookup.
"""
import tkinter as tk
from tkinter import ttk


def action_state(view, actor):
    """Presentation availability; the engine still validates every command."""
    own=view.get('you');priority=view.get('priority');turn=view['turn']
    can_pass=bool(own and not view.get('paused') and not view['result']
        and priority and priority['status']=='priority' and priority['holder']==actor
        and not own['choice'] and not view.get('choice_pending'))
    can_end=can_pass and turn['active_player']==actor and turn['phase'] in ('MainBefore','MainAfter') and not view['chain']
    return can_pass,bool(can_end)


def section(parent, title):
    frame=ttk.LabelFrame(parent,text=title,padding=8)
    frame.pack(fill='x',pady=5)
    return frame


def tiles(app, parent, view, cards, private=False, controls=None):
    """Three bounded columns keep long names/rules inside the scrollable table."""
    for column in range(3):parent.columnconfigure(column,weight=1,uniform='cards')
    for index,card in enumerate(cards):
        tile=ttk.Frame(parent,padding=10,relief='ridge',borderwidth=2)
        tile.grid(row=index//3,column=index%3,sticky='nsew',padx=4,pady=4)
        name=card.get('name') or app.session.card_name(card.get('definition_key',card['instance_id']))
        ttk.Label(tile,text=name,style='CardTitle.TLabel',wraplength=235).pack(anchor='w')
        ttk.Label(tile,text=f"{card['kind'].title()}  |  Cost {card.get('cost','—')}",wraplength=235).pack(anchor='w')
        creature=card.get('creature')
        if creature:
            text=f"{creature['attack']} ATK  |  {creature['health']}/{creature['max_health']} HP"
            text+='\n'+('Exhausted' if creature['exhausted'] else 'Ready')
            text+=' | '+('Can attack' if creature['attack_eligible'] and not creature['attack_used'] and not creature['exhausted'] else 'Attack waiting / used')
            text+=f"\nPrevention: {sum(s['amount'] for s in creature['shields'])}"
            ttk.Label(tile,text=text,wraplength=235).pack(anchor='w',pady=3)
        elif card['kind']=='creature' and 'attack' in card:
            ttk.Label(tile,text=f"{card['attack']} ATK  |  {card['health']} HP").pack(anchor='w',pady=3)
        if card.get('keywords'):ttk.Label(tile,text=', '.join(card['keywords']),wraplength=235).pack(anchor='w')
        if card.get('capacity_bonus'):ttk.Label(tile,text=f"+{card['capacity_bonus']} capacity").pack(anchor='w')
        if card['kind']=='resource_token':ttk.Label(tile,text=f"Resource value: {card['resource_value']}").pack(anchor='w')
        for step in card.get('steps',[]):
            ttk.Label(tile,text=app.effect_text(step,view),wraplength=235).pack(anchor='w',pady=2)
        for ability in card.get('triggered_abilities',[]):
            ttk.Label(tile,text=app.trigger_text(ability,view,card.get('controller')),wraplength=235).pack(anchor='w',pady=2)
        ttk.Label(tile,text=f"Card …{card['instance_id'][-6:]}",wraplength=235).pack(anchor='w')
        if private:
            ttk.Button(tile,text='Inspect / play',command=lambda c=card:app.card_dialog(view,c)).pack(anchor='w',pady=(6,0))
        if controls:controls(tile,card)


def render_match(app, view):
    turn=view['turn'];own=view.get('you');actor=app.gate.actor
    heading=f"Turn {turn['turn_id']}  •  {turn['active_player']}  •  {turn['phase']}"
    if turn['recharge']:heading+='  •  RECHARGE'
    ttk.Label(app.body,text=heading,style='Heading.TLabel').pack(anchor='w')
    ttk.Label(app.body,text=app.next_step(view),wraplength=880).pack(anchor='w',pady=4)
    actions=ttk.Frame(app.body);actions.pack(fill='x',pady=4)
    priority=view['priority']
    ttk.Label(actions,text=f"Viewing: {actor or 'public'}  |  Priority: {priority['holder'] or priority['status']}" if priority else 'Game finished').pack(side='left')
    can_pass,can_end=action_state(view,actor)
    if own and not view['result']:
        ttk.Button(actions,text='Pass / continue phase',state='normal' if can_pass else 'disabled',command=lambda:app.send('pass')).pack(side='left',padx=8)
        ttk.Button(actions,text='End turn',state='normal' if can_end else 'disabled',command=lambda:app.send('end_turn')).pack(side='left')
        ttk.Button(actions,text='Concede...',command=app.concede).pack(side='right')
    if view['result']:
        ttk.Label(app.body,text='Draw' if view['result']['kind']=='draw' else f"{view['result']['winner']} wins",style='Heading.TLabel').pack(anchor='w')
    navigation=ttk.Frame(app.body);navigation.pack(fill='x',pady=4)
    table=app.scrollable(app.body)
    anchors={'battlefield':table}
    def jump(key):
        if key not in anchors or not table.winfo_exists():return
        table.update_idletasks()
        table.scroll_canvas.yview_moveto(anchors[key].winfo_y()/max(1,table.winfo_height()) if anchors[key]!=table else 0)
        app._match_focus=(actor,key)
    for label,key,enabled in (('Go to battlefield','battlefield',True),('Go to hand','hand',bool(own)),('Go to choice','choice',bool(own and own['choice'])),('Go to effects','effects',True),('Go to history','history',True)):
        button=ttk.Button(navigation,text=label,state='normal' if enabled else 'disabled',command=lambda k=key:jump(k))
        button.pack(side='left',padx=(0,6));app._match_navigation[key]=button
    ttk.Label(app.body,text='Keyboard: Alt+1–5 sections • Alt+H hide hand • Tab moves focus • Space selects',wraplength=880).pack(anchor='w')
    if own and own['choice']:
        anchors['choice']=section(table,'Your required choice')
        anchors['choice'].configure(style='Choice.TLabelframe')
        app.render_choice(anchors['choice'],view,own['choice'])
    combat=view.get('combat')
    if combat:
        panel=section(table,'Combat • '+combat['stage'].replace('_',' '))
        blockers=dict(combat.get('blockers',()))
        for attacker,target,challenge in combat['attacks']:
            text=app.public_name(view,attacker)+' → '+(app.public_name(view,challenge) if challenge else target)
            if attacker in blockers:text+=' | Blockers: '+(', '.join(app.public_name(view,b) for b in blockers[attacker]) or 'None')
            ttk.Label(panel,text=text,wraplength=850).pack(anchor='w')
        if combat['stage']=='blocking':ttk.Label(panel,text='Blocker choices stay private until all defenders confirm.').pack(anchor='w')
    chain=section(table,f"Pending effects ({len(view['chain'])})")
    anchors['effects']=chain
    if not view['chain']:ttk.Label(chain,text='No effects waiting.').pack(anchor='w')
    for effect in reversed(view['chain']):
        ttk.Label(chain,text=f"{effect['controller']} • {effect.get('label',effect['effect_key'])} • #{effect['effect_id']}"+(' • resolving' if effect['resolving'] else ''),wraplength=850).pack(anchor='w')
        for step in effect['steps']:ttk.Label(chain,text=app.effect_text(step,view),wraplength=850).pack(anchor='w')
    board=section(table,'Battlefield and players');anchors['battlefield']=board
    for player in view['players']:
        pid=player['player_id'];status='ELIMINATED' if player['eliminated'] else f"{player['health']}/{player['max_health']} life • {player['resources']['available']} resources • Hand {player['hand_count']} • Deck {player['deck_count']}"
        zone=section(board,f"{pid}{' — YOU' if pid==actor else ''} | {status}")
        for leader in view.get('leaders',[]):
            if leader['owner']==pid:
                ttk.Label(zone,text=f"Leader: {leader['name']} • {leader['location']} • Summon {leader['summon_cost']}"+(' • Recovering' if leader['recovering'] else ''),wraplength=850).pack(anchor='w')
        objects=[card for card in view['battlefield'] if card['controller']==pid]
        if objects:tiles(app,section(zone,'Battlefield'),view,objects)
        else:ttk.Label(zone,text='Battlefield empty').pack(anchor='w',pady=4)
    hand=section(table,'Your hand and actions' if own else 'Private hand hidden')
    if own:anchors['hand']=hand
    if not own:ttk.Label(hand,text='Choose a seat and acknowledge the handoff to see your cards.').pack(anchor='w')
    else:
        if not own['choice'] and not view['result']:
            app.leader_panel(hand,view)
            if not view.get('paused') and turn['phase']=='Combat' and view['combat'] is None and priority and priority['status']=='closed' and turn['active_player']==actor:
                app.attack_panel(hand,view)
        ttk.Label(hand,text='Inspect a card, then confirm its payment and target. Inspection does not play it.',wraplength=850).pack(anchor='w',pady=5)
        if own['hand']:tiles(app,section(hand,f"Hand ({len(own['hand'])})"),view,own['hand'],private=True)
        else:ttk.Label(hand,text='Your hand is empty.').pack(anchor='w')
    details=section(table,'Public discard, exile and durations')
    for player in view['players']:
        ttk.Label(details,text=player['player_id']+' discard: '+(', '.join(app.label(c) for c in player.get('discard',[])) or 'Empty'),wraplength=850).pack(anchor='w')
    for card in view.get('exile',[]):ttk.Label(details,text=f"Exile • {card['owner']} • {app.label(card)}",wraplength=850).pack(anchor='w')
    for duration in view.get('durations',[]):ttk.Label(details,text=f"Expires: {duration['anchor_player']} {duration['boundary']} #{duration['occurrence']}",wraplength=850).pack(anchor='w')
    history=section(table,'Recent public history')
    anchors['history']=history
    log=tk.Text(history,height=6,wrap='word',font=('Segoe UI',10))
    log.pack(fill='x')
    for event in view['events'][-30:]:
        who=app.session.card_name(event['card'].get('definition_key','Card')) if 'card' in event else app.public_name(view,event['subject'])
        log.insert('end',f"{event['event_id']}: {event['kind'].replace('_',' ')} • {who}\n")
    log.configure(state='disabled')
    # Bind only this table's widgets, never other windows or the whole application.
    def wheel(event):
        units=-1 if getattr(event,'num',None)==4 else 1 if getattr(event,'num',None)==5 else -int(event.delta/120) if abs(event.delta)>=120 else (-1 if event.delta>0 else 1)
        table.scroll_canvas.yview_scroll(units,'units')
        return 'break'
    def bind_wheel(widget):
        if not isinstance(widget,(tk.Text,ttk.Combobox,ttk.Spinbox)):
            for sequence in ('<MouseWheel>','<Button-4>','<Button-5>'):widget.bind(sequence,wheel)
        for child in widget.winfo_children():bind_wheel(child)
    bind_wheel(table)
    focus=getattr(app,'_match_focus',(actor,'battlefield'))
    key='choice' if own and own['choice'] else focus[1] if focus[0]==actor and focus[1] in anchors else 'battlefield'
    jump(key)
