"""Presentation for required private choices; identity/order stays engine-owned."""
import tkinter as tk
from tkinter import ttk
from .match_screen import tiles


def render_choice(app,frame,view,choice):
    kind=choice['kind'];paused=view.get('paused',False)
    state='disabled' if paused else 'normal'
    if paused:ttk.Label(frame,text='Paused — resume before confirming this choice.').pack(anchor='w')
    if kind in ('effect_discard','end_discard'):
        count=1 if kind=='effect_discard' else choice['count']
        ttk.Label(frame,text=f'Choose exactly {count} card(s) to discard. Nothing leaves your hand until confirmation.',wraplength=850).pack(anchor='w')
        cards=view['you']['hand'];selected={c['instance_id']:tk.BooleanVar() for c in cards}
        summary=tk.StringVar();ttk.Label(frame,textvariable=summary).pack(anchor='w',pady=5)
        def confirm():
            keys=[key for key,var in selected.items() if var.get()]
            if paused or len(keys)!=count:return
            if kind=='effect_discard':app.send('effect_discard',card_id=keys[0],request_id=choice['request_id'])
            else:app.send('end_discard',cards=keys)
        button=ttk.Button(frame,text='Confirm effect discard' if kind=='effect_discard' else 'Confirm discards',style='Accent.TButton',command=confirm)
        button.pack(anchor='w',pady=5)
        def update(*_):
            n=sum(var.get() for var in selected.values());summary.set(f'{n} / {count} cards selected')
            button.configure(state='normal' if not paused and n==count else 'disabled')
        for variable in selected.values():variable.trace_add('write',update)
        def controls(tile,card):ttk.Checkbutton(tile,text='Discard this card',variable=selected[card['instance_id']],state=state).pack(anchor='w',pady=5)
        area=ttk.Frame(frame);area.pack(fill='x');tiles(app,area,view,cards,controls=controls);update()
    elif kind=='refill':
        player=next(p for p in view['players'] if p['player_id']==app.gate.actor)
        remaining=player['health']-choice['cost'];can_pay=remaining>=choice['minimum_health']
        penalty='Your current turn ends after the effect finishes.' if view['turn']['active_player']==app.gate.actor else 'Your next turn is Recharge.'
        ttk.Label(frame,text=f"Finish drawing {choice['remaining']} card(s): pay {choice['cost']} life to shuffle your discard into your deck.",wraplength=850).pack(anchor='w',pady=5)
        ttk.Label(frame,text=f"Life: {player['health']} → {remaining}. Must keep at least {choice['minimum_health']}. {penalty}",wraplength=850).pack(anchor='w')
        if not can_pay:ttk.Label(frame,text='You cannot afford this refill. Declining eliminates you.',wraplength=850).pack(anchor='w')
        ttk.Button(frame,text=f"Pay {choice['cost']} life and refill",state=state if can_pay else 'disabled',style='Accent.TButton',command=lambda:app.send('refill',pay=True,request_id=choice['request_id'])).pack(anchor='w',pady=6)
        ttk.Button(frame,text='Decline refill (eliminates you)',style='Danger.TButton',state=state,command=lambda:app.send('refill',pay=False,request_id=choice['request_id'])).pack(anchor='w')
    elif kind=='optional_trigger':
        ttk.Label(frame,text='Optional trigger • '+app.public_name(view,choice['source_id']),wraplength=850).pack(anchor='w')
        for step in choice['steps']:ttk.Label(frame,text=app.effect_text(step,view),wraplength=850).pack(anchor='w',pady=3)
        for use,label in ((True,'Use optional trigger'),(False,'Skip optional trigger')):
            ttk.Button(frame,text=label,state=state,style='Accent.TButton' if use else 'TButton',command=lambda value=use:app.send('trigger_choice',trigger_id=choice['trigger_id'],use=value)).pack(anchor='w',pady=5)
    elif kind in ('combat_order','trigger_order'):
        order_panel(app,frame,view,choice)


def order_panel(app,frame,view,choice):
    kind=choice['kind'];paused=view.get('paused',False)
    current=choice['orders'][0] if kind=='combat_order' else {'items':[t['trigger_id'] for t in choice['triggers']]}
    items=list(current['items']);triggers={t['trigger_id']:t for t in choice.get('triggers',[])}
    ttk.Label(frame,text='Damage order • '+app.public_name(view,current['subject']) if kind=='combat_order' else 'Triggered-effect order',style='CardTitle.TLabel',wraplength=850).pack(anchor='w')
    ttk.Label(frame,text='Damage goes from top to bottom.' if kind=='combat_order' else 'Effects resolve from bottom to top. The bottom effect resolves first.',wraplength=850).pack(anchor='w')
    ttk.Label(frame,text='Select a row; Move up/down or Alt+Up/Down changes its position. Confirm submits only this order.',wraplength=850).pack(anchor='w',pady=4)
    listing=tk.Listbox(frame,exportselection=False,height=max(2,min(8,len(items))),font=('Segoe UI',11));listing.pack(fill='x',pady=5)
    def refresh():
        listing.delete(0,'end')
        for index,item in enumerate(items):
            name=app.public_name(view,triggers[item]['source_id']) if kind=='trigger_order' else app.public_name(view,item)
            marker=' • NEXT' if (index==len(items)-1 if kind=='trigger_order' else index==0) else ''
            listing.insert('end',f'{index+1}. {name} • …{str(item)[-6:]}{marker}')
    def move(delta):
        if paused or not listing.curselection():return 'break'
        index=listing.curselection()[0];dest=index+delta
        if 0<=dest<len(items):
            items[index],items[dest]=items[dest],items[index];refresh();listing.selection_set(dest);listing.see(dest)
        return 'break'
    refresh()
    listing.bind('<Alt-Up>',lambda event:move(-1));listing.bind('<Alt-Down>',lambda event:move(1))
    for text,delta in (('Move up',-1),('Move down',1)):
        ttk.Button(frame,text=text,state='disabled' if paused else 'normal',command=lambda d=delta:move(d)).pack(anchor='w')
    def confirm():
        if paused:return
        if kind=='combat_order':app.send('combat_order',subject=current['subject'],order=list(items))
        else:app.send('trigger_order',order=list(items))
    ttk.Button(frame,text='Confirm no triggered effects' if kind=='trigger_order' and not items else 'Confirm this order',style='Accent.TButton',state='disabled' if paused else 'normal',command=confirm).pack(anchor='w',pady=6)
