"""Card-based combat assignment. Selections stay local until batch confirmation."""
import tkinter as tk
from tkinter import ttk
from .match_screen import tiles


def assign_cards(app,frame,view,cards,options,submit,button_text,verb):
    state='disabled' if view.get('paused') else 'normal'
    selected={card['instance_id']:tk.IntVar(value=0) for card in cards}
    summary=tk.StringVar(value=f'0 {verb} selected')
    def update(*_):summary.set(f"{sum(v.get()!=0 for v in selected.values())} {verb} selected")
    for variable in selected.values():variable.trace_add('write',update)
    ttk.Label(frame,textvariable=summary).pack(anchor='w',pady=4)
    def confirm():submit({key:options[key][variable.get()][1] for key,variable in selected.items()})
    ttk.Button(frame,text=button_text,command=confirm,state=state).pack(anchor='w',pady=5)
    if not cards:ttk.Label(frame,text='No eligible creatures. Confirm to continue without assignments.').pack(anchor='w')
    def controls(tile,card):
        key=card['instance_id']
        for index,(label,_) in enumerate(options[key]):
            ttk.Radiobutton(tile,text=label,variable=selected[key],value=index,state=state).pack(anchor='w',pady=2)
    card_area=ttk.Frame(frame);card_area.pack(fill='x')
    tiles(app,card_area,view,cards,controls=controls)


def attack_panel(app,frame,view):
    ttk.Label(frame,text='Choose a target on each attacking card. Unselected cards stay back. Confirm the whole attack together.',wraplength=850).pack(anchor='w',pady=6)
    cards=[];options={}
    for obj in view['battlefield']:
        creature=obj.get('creature')
        if not creature or obj['controller']!=app.gate.actor or creature['exhausted'] or not creature['attack_eligible'] or creature['attack_used']:continue
        cards.append(obj);key=obj['instance_id']
        options[key]=[('Stay back',None)]+[(f"Attack {p['player_id']}",{'attacker_id':key,'target_player':p['player_id']}) for p in view['players'] if not p['eliminated'] and p['player_id']!=app.gate.actor]
        if 'challenge' in creature['keywords']:
            options[key]+=[(f"Challenge {app.public_name(view,o['instance_id'])}\n{o['controller']} • …{o['instance_id'][-6:]}",{'attacker_id':key,'target_player':o['controller'],'challenge_target':o['instance_id']}) for o in view['battlefield'] if o.get('creature') and o['controller']!=app.gate.actor]
    assign_cards(app,frame,view,cards,options,lambda choices:app.send('declare_attacks',attacks=[c for c in choices.values() if c is not None]),'Confirm all attacks / no attacks','attackers')


def blocker_panel(app,frame,view,choice):
    if choice['locked']:
        ttk.Label(frame,text='Blockers locked. Hide your hand before passing to the next defender.',wraplength=850).pack(anchor='w')
        return
    attacks=[a for a in view['combat']['attacks'] if a[1]==app.gate.actor and a[2] is None]
    challenged={a[2] for a in view['combat']['attacks'] if a[2]}
    cards=[o for o in view['battlefield'] if o.get('creature') and o['controller']==app.gate.actor and o['instance_id'] not in challenged]
    ttk.Label(frame,text='Assign your creatures to incoming attackers. Choices stay private and reveal together after all defenders lock.',wraplength=850).pack(anchor='w',pady=5)
    options={o['instance_id']:[('Do not block',None)]+[(f"Block {app.public_name(view,a[0])}\n…{a[0][-6:]}",a[0]) for a in attacks] for o in cards}
    def submit(choices):
        app.send('lock_blockers',assignments=[{'attacker_id':a[0],'blockers':[key for key,target in choices.items() if target==a[0]]} for a in attacks])
    assign_cards(app,frame,view,cards,options,submit,'Lock complete blocker choice / no blocks','blockers')
