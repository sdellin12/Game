"""Private play review with exact-payment feedback; engine remains authoritative."""
import tkinter as tk
from tkinter import ttk
from .match_screen import action_state, section


def card_dialog(app,view,card,command='play_card'):
    app.close_inspections()
    actor=app.gate.actor;revision=view['revision']
    popup=tk.Toplevel(app.root);popup.title('Review card and payment');popup.transient(app.root)
    popup.geometry('660x700');popup.minsize(570,440);popup.grab_set()
    footer=ttk.Frame(popup,padding=10);footer.pack(side='bottom',fill='x')
    frame=app.scrollable(popup)
    ttk.Label(frame,text=app.label(card),style='Heading.TLabel',wraplength=560).pack(anchor='w',padx=10,pady=10)
    if card['kind']=='creature':ttk.Label(frame,text='Enters ready to block; waits until your next Start to attack.',wraplength=550).pack(anchor='w',padx=10)
    if card.get('capacity_bonus'):ttk.Label(frame,text=f"Adds {card['capacity_bonus']} capacity; available at the next refill.",wraplength=550).pack(anchor='w',padx=10)
    for step in card.get('steps',[]):ttk.Label(frame,text=app.effect_text(step,view),wraplength=550).pack(anchor='w',padx=10,pady=3)
    for ability in card.get('triggered_abilities',[]):ttk.Label(frame,text=app.trigger_text(ability,view),wraplength=550).pack(anchor='w',padx=10,pady=3)
    player=next((p for p in view['players'] if p['player_id']==actor),None)
    available=player['resources']['available'] if player else 0
    payment=section(frame,f"Payment • Cost {card['cost']} • Available resources {available}")
    ttk.Label(payment,text='Pay the exact cost. Selected resource tokens are consumed.',wraplength=550).pack(anchor='w')
    ttk.Label(payment,text='Ordinary resources to pay').pack(anchor='w',pady=(6,0))
    amount=tk.StringVar(value=str(min(card['cost'],available)))
    ttk.Spinbox(payment,from_=0,to=available,textvariable=amount,width=7).pack(anchor='w')
    tokens=[]
    for obj in view['battlefield']:
        if obj['kind']=='resource_token' and obj['controller']==actor:
            variable=tk.BooleanVar();tokens.append((obj['instance_id'],obj['resource_value'],variable))
            ttk.Checkbutton(payment,text=f"Use token …{obj['instance_id'][-6:]} • {obj['resource_value']} resources",variable=variable).pack(anchor='w',pady=3)
    options=app.target_options(view,card)
    if card.get('target_kind')=='effect':
        effects={str(e['effect_id']):e for e in view['chain']}
        options=[(f"#{key} • {effects[key]['controller']} • {effects[key].get('label','Pending effect')}",key) for _,key in options]
    elif card.get('target_kind')=='player':
        health={p['player_id']:p['health'] for p in view['players']}
        options=[(f'{label} • {health[key]} life',key) for label,key in options]
    target=tk.StringVar(value='')
    if card.get('target_kind'):
        targets=section(frame,'Choose a target')
        ttk.Label(targets,text='Select one target before confirming.' if options else 'No valid target is currently available.',wraplength=550).pack(anchor='w')
        for index,(label,_) in enumerate(options):
            ttk.Radiobutton(targets,text=label,variable=target,value=str(index)).pack(anchor='w',pady=3)
    summary=tk.StringVar();feedback=tk.StringVar()
    ttk.Label(footer,textvariable=summary,wraplength=610).pack(anchor='w')
    ttk.Label(footer,textvariable=feedback,wraplength=610).pack(anchor='w',pady=4)
    def review():
        try:ordinary=int(amount.get())
        except ValueError:return None,'Enter a whole-number resource payment.'
        if not 0<=ordinary<=available:return None,f'Ordinary payment must be between 0 and {available}.'
        chosen=[key for key,_,variable in tokens if variable.get()]
        total=ordinary+sum(value for _,value,variable in tokens if variable.get())
        target_label=options[int(target.get())][0] if target.get().isdigit() and int(target.get())<len(options) else None
        summary.set(f"Pay {ordinary} ordinary + {total-ordinary} token resources = {total}/{card['cost']}. Remaining ordinary: {available-ordinary}."+ (f' Target: {target_label}.' if target_label else ''))
        if app.gate.actor!=actor or app.session.view(actor)['revision']!=revision:return None,'The game changed. Close this review and inspect again.'
        if app.session.paused or view.get('paused'):return None,'Game paused. Resume before confirming.'
        can_act,_=action_state(view,actor)
        if not can_act:return None,'Wait until you have priority and required choices are finished.'
        if command=='leader_ability':
            if not card.get('available',False):return None,'This leader ability is not available now.'
        elif command=='summon_leader' or card['kind']!='reaction':
            if view['turn']['active_player']!=actor or view['turn']['phase'] not in ('MainBefore','MainAfter') or view['chain']:
                return None,'Play this during your Main phase with no pending effects.'
        if total!=card['cost']:return None,f"{'Add' if total<card['cost'] else 'Remove'} {abs(total-card['cost'])} resources to pay the exact cost."
        if card.get('target_kind') and target_label is None:return None,'Choose a target before confirming.'
        args={'payment':{'ordinary':ordinary,'token_ids':chosen}}
        if command=='play_card':args['card_id']=card['instance_id']
        elif command=='leader_ability':args['key']=card['ability_key']
        if card.get('target_kind'):args['target']=options[int(target.get())][1]
        return args,'Ready to confirm. The engine checks timing, targets and payment.'
    def update(*_):
        summary.set('')
        args,message=review();feedback.set(message)
        confirm.configure(state='normal' if args is not None else 'disabled')
    def submit():
        args,message=review()
        if args is None:feedback.set(message);confirm.configure(state='disabled');return
        if app.send(command,**args):
            if popup.winfo_exists():popup.destroy()
        else:feedback.set(app.notice.get())
    confirm=ttk.Button(footer,text='Confirm play and payment',command=submit);confirm.pack(side='left',pady=5)
    ttk.Button(footer,text='Cancel',command=popup.destroy).pack(side='right',pady=5)
    for variable in [amount,target]+[v for _,_,v in tokens]:variable.trace_add('write',update)
    update()
