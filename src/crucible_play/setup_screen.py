"""Guided lobby and private opening choices; all writes use session transactions."""
import tkinter as tk
from tkinter import ttk
from .match_screen import section, tiles


def render_lobby(app, view):
    ttk.Label(app.body,text='Set up your match',style='Heading.TLabel').pack(anchor='w')
    ttk.Label(app.body,text='1  Choose a seat     →     2  Select a reserve identity and ready     →     3  Host deals',wraplength=850).pack(anchor='w',pady=6)
    table=app.scrollable(app.body)
    for player in view['players']:
        panel=section(table,f"{player['player_id']} • {player['name']}"+(' • Computer' if player.get('computer') else ''))
        leader=player['leader']['name'] if player['leader'] else 'Choose a reserve identity'
        ttk.Label(panel,text=f"{player['deck_name'] or 'No deck selected'} • {leader} • {'READY' if player['ready'] else 'Not ready'}",wraplength=850).pack(anchor='w')
    actor=app.gate.actor
    if not actor:
        ttk.Label(table,text='Choose your human seat above, then acknowledge the handoff to continue.',wraplength=850).pack(anchor='w',pady=10)
        return
    own=next(p for p in view['players'] if p['player_id']==actor)
    panel=section(table,f"Your setup • {actor}")
    leaders=app.session.leaders()
    selected=tk.StringVar(value=own['leader']['key'] if own['leader'] else leaders[0]['key'])
    state='disabled' if view.get('paused') else 'normal'
    ttk.Label(panel,text='The practice deck is supplied. Choose its reserve identity, apply it, then Ready.',wraplength=850).pack(anchor='w')
    for leader in leaders:
        ttk.Radiobutton(panel,text=f"{leader['name']} • {leader['color']}",variable=selected,value=leader['key'],state=state).pack(anchor='w',pady=3)
    ttk.Button(panel,text='Apply deck and reserve identity',state=state,command=lambda:app.perform(
        lambda:app.session.choose_deck(actor,selected.get(),expected_revision=view['revision']))).pack(anchor='w',pady=5)
    ttk.Button(panel,text='Not ready' if own['ready'] else 'Ready',state=state if own['leader'] and own['deck_name'] else 'disabled',command=lambda:app.perform(
        lambda:app.session.ready(actor,not own['ready'],expected_revision=view['revision']))).pack(anchor='w',pady=5)
    waiting=[p['name'] for p in view['players'] if not p['ready']]
    ttk.Label(panel,text='Waiting for: '+', '.join(waiting) if waiting else 'Everyone is ready. The host can deal.',wraplength=850).pack(anchor='w')
    if actor==view['host']:
        ttk.Button(panel,text='Deal opening hands',state=state if not waiting else 'disabled',command=lambda:app.perform(
            lambda:app.session.start(actor,expected_revision=view['revision']))).pack(anchor='w',pady=8)
    else:ttk.Label(panel,text=f"Host {view['host']} deals after everyone is ready.").pack(anchor='w')


def render_opening(app, view):
    ttk.Label(app.body,text='Choose your opening hand',style='Heading.TLabel').pack(anchor='w')
    ttk.Label(app.body,text='Mark any cards to replace once, then lock your choice. Keep all by leaving every card unmarked. Counts and the starting player reveal after everyone locks.',wraplength=850).pack(anchor='w',pady=6)
    own=view.get('you')
    if not own:
        app.close_inspections()
        ttk.Label(app.body,text='Choose your seat and acknowledge the handoff. '+view['waiting'],wraplength=850).pack(anchor='w')
        return
    if own['locked']:
        ttk.Label(app.body,text='Your opening choice is locked. Waiting for the other seats; hide your hand before passing the computer.',wraplength=850).pack(anchor='w')
        return
    selected={c['instance_id']:tk.BooleanVar() for c in own['hand']}
    summary=tk.StringVar(value='Keeping all cards')
    def update(*_):
        count=sum(v.get() for v in selected.values())
        summary.set(f'Replacing {count} of {len(selected)} cards' if count else 'Keeping all cards')
    for variable in selected.values():variable.trace_add('write',update)
    ttk.Label(app.body,textvariable=summary).pack(anchor='w')
    ttk.Button(app.body,text='Lock opening choice',state='disabled' if view.get('paused') else 'normal',command=lambda:app.perform(
        lambda:app.session.redraw(app.gate.actor,[key for key,var in selected.items() if var.get()],expected_revision=view['revision']))).pack(anchor='w',pady=5)
    def controls(tile,card):
        ttk.Checkbutton(tile,text='Replace this card',variable=selected[card['instance_id']],state='disabled' if view.get('paused') else 'normal').pack(anchor='w',pady=6)
    tiles(app,app.scrollable(app.body),view,own['hand'],controls=controls)
