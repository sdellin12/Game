"""Small hotseat desktop client. All rule decisions go through projected views/commands."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .session import HarnessSession, HotseatGate
from .persistence import save_session, load_session, SaveError


class PlayWindow:
    def __init__(self, root, session=None):
        self.root=root
        self.session=session or HarnessSession(bots=('P2',))
        self._bot_timer=None;self._bot_steps=0;self._bot_error=False
        self.root.bind('<Destroy>',self._destroyed,add='+')
        self.gate=HotseatGate()
        self.root.title('The Crucible - Local Rules Harness')
        self.root.geometry('1120x820');self.root.minsize(950,700)
        self.root.protocol('WM_DELETE_WINDOW',self.close)
        style=ttk.Style(root);style.theme_use('clam')
        style.configure('TFrame',background='#edf3f5')
        style.configure('TLabel',background='#edf3f5',foreground='#173747',font=('Segoe UI',10))
        style.configure('Heading.TLabel',font=('Segoe UI',16,'bold'))
        style.configure('TButton',padding=6)
        outer=ttk.Frame(root,padding=14);outer.pack(fill='both',expand=True)
        ttk.Label(outer,text='THE CRUCIBLE  /  LOCAL RULES HARNESS',style='Heading.TLabel').pack(anchor='w')
        ttk.Label(outer,text='Practice against computer seats, or use local hotseat play. Leader summons and recovery are enabled.').pack(anchor='w',pady=(2,8))
        bar=ttk.Frame(outer);bar.pack(fill='x')
        ttk.Label(bar,text='Seats').pack(side='left')
        self.count=tk.IntVar(value=len(self.session.view()['players']));ttk.Spinbox(bar,from_=2,to=4,width=3,textvariable=self.count).pack(side='left',padx=4)
        self.new_button=ttk.Button(bar,text='New lobby',command=self.new_lobby);self.new_button.pack(side='left')
        self.computer_mode=tk.BooleanVar(value=bool(self.session.bots))
        ttk.Checkbutton(bar,text='New lobby: computers in P2-P4',variable=self.computer_mode).pack(side='left',padx=8)
        ttk.Button(bar,text='Hide private hand / public view',command=self.hide).pack(side='right')
        bar=ttk.Frame(outer);bar.pack(fill='x',pady=(6,0))
        ttk.Button(bar,text='Save game...',command=self.save_game).pack(side='left',padx=(8,2))
        ttk.Button(bar,text='Load game...',command=self.load_game).pack(side='left',padx=2)
        self.resume_button=ttk.Button(bar,text='Resume saved game',command=self.resume_game)
        self.resume_button.pack(side='left',padx=2)
        self.seatbar=ttk.Frame(outer);self.seatbar.pack(fill='x',pady=8)
        self.notice=tk.StringVar(value='Choose a seat to select a deck and reserve identity.')
        ttk.Label(outer,textvariable=self.notice,wraplength=1030).pack(anchor='w',pady=(0,8))
        self.body=ttk.Frame(outer);self.body.pack(fill='both',expand=True)
        self.render();self._schedule_bots()

    def _destroyed(self, event):
        if event.widget==self.root and self._bot_timer is not None:
            try:self.root.after_cancel(self._bot_timer)
            except tk.TclError:pass
            self._bot_timer=None

    def _schedule_bots(self):
        if self.session.bots and not self.session.paused and self._bot_timer is None and not self._bot_error:
            self._bot_timer=self.root.after(200,self._pump_bots)

    def _pump_bots(self):
        self._bot_timer=None
        try:
            if self.session.step_opponent():
                self._bot_steps+=1
                self.render()
                if self._bot_steps>=200 and not self.session.view().get('result'):raise ValueError('Computer action limit reached; inspect the game or start a new lobby.')
            else:self._bot_steps=0
        except ValueError as exc:
            self._bot_error=True;self.notice.set(f'Computer stopped: {exc}');return
        self._schedule_bots()

    def close(self):
        if self.session.view().get('phase')!='lobby' and not messagebox.askyesno('Close local game','Close this local game? Changes since your last save will be lost.',parent=self.root):return
        self.root.destroy()

    def new_lobby(self):
        try:count=self.count.get()
        except tk.TclError:return self.error('Choose 2 through 4 seats.')
        if not 2<=count<=4:return self.error('Choose 2 through 4 seats.')
        current=self.session.view()
        if (current.get('phase')!='lobby' or any(p.get('deck_name') for p in current['players'])) and not messagebox.askyesno('New local lobby','Discard this local session and start a new lobby?',parent=self.root):return
        self.session=HarnessSession(tuple(f'Player {i+1}' for i in range(count)),bots=tuple(f'P{i+1}' for i in range(1,count)) if self.computer_mode.get() else ())
        self._bot_error=False;self._bot_steps=0;self._schedule_bots()
        self.gate.hide();self.notice.set('New lobby. Each seat selects a reserve identity and confirms Ready.');self.render()

    def _suspend_for_file(self):
        paused=self.session.paused
        self.session.paused=True
        if self._bot_timer is not None:
            self.root.after_cancel(self._bot_timer);self._bot_timer=None
        self.gate.hide();self.render()
        return paused

    def save_game(self):
        paused=self._suspend_for_file()
        try:
            path=filedialog.asksaveasfilename(parent=self.root,title='Save privately - includes every hand',
                initialfile='Crucible game.crucible.json',defaultextension='.crucible.json',
                filetypes=[('Crucible private save','*.crucible.json')])
            if not path:return
            result=save_session(self.session,path)
            self.notice.set('Private game saved.'+(' Previous snapshot retained as a backup.' if result.backup else ''))
        except (SaveError,OSError) as exc:self.notice.set(str(exc))
        finally:
            self.session.paused=paused;self.render();self._schedule_bots()

    def load_game(self):
        paused=self._suspend_for_file();old=self.session
        try:
            path=filedialog.askopenfilename(parent=self.root,title='Load a private game or retained backup',
                filetypes=[('Crucible saves/backups','*.crucible.json*')])
            if not path:return
            candidate=load_session(path)
            if not messagebox.askyesno('Load saved game','Replace this local session with the validated save? It opens paused with hands hidden.',parent=self.root):return
            self.install_loaded(candidate)
            self.notice.set('Loaded privately and paused. Choose your seat; Resume saved game when ready.')
        except (SaveError,OSError) as exc:self.notice.set(str(exc))
        finally:
            if self.session is old:self.session.paused=paused
            self.render();self._schedule_bots()

    def install_loaded(self, candidate):
        self.session=candidate;self.session.paused=True
        self.gate.hide();self._bot_steps=0;self._bot_error=False
        self.count.set(len(candidate.view()['players']));self.computer_mode.set(bool(candidate.bots))

    def resume_game(self):
        self.session.resume();self._bot_error=False;self._bot_steps=0
        self.notice.set('Saved game resumed. Private hands still require seat confirmation.')
        self.render();self._schedule_bots()

    def hide(self):
        self.gate.hide();self.notice.set('Public view. Private cards are hidden.');self.render()

    def seat(self, actor):
        if actor in self.session.bots:return self.error('Computer hands stay private. Choose a human seat.')
        self.gate.request(actor);self.notice.set(f'Pass the computer to {actor}. Private cards stay hidden until they continue.');self.render()

    def unlock(self):
        self.gate.unlock();self.notice.set(f'Viewing {self.gate.actor}. Hide the hand before handing over the computer.');self.render()

    def error(self, text):
        self.notice.set(text)

    def perform(self, callback):
        try:callback()
        except ValueError as exc:self.error(str(exc));return False
        self._bot_steps=0
        self.notice.set('Confirmed.');self.render();self._schedule_bots();return True

    def send(self, kind, **args):
        actor=self.gate.actor
        view=self.session.view(actor)
        return self.perform(lambda:self.session.send(actor,{'kind':kind,'expected_revision':view['revision'],'args':args}))

    def render(self):
        # Destroy private widgets and tentative choices on every handoff/refresh.
        for frame in (self.body,self.seatbar):
            for child in frame.winfo_children():child.destroy()
        view=self.session.view(self.gate.actor)
        self.resume_button.configure(state='normal' if self.session.paused else 'disabled')
        roster=view.get('setup',view)['players']
        for player in roster:
            ttk.Button(self.seatbar,text=f"Computer {player['player_id']}" if player.get('computer') else f"View {player.get('name',player['player_id'])}",
                       state='disabled' if player.get('computer') else 'normal',command=lambda p=player['player_id']:self.seat(p)).pack(side='left',padx=(0,6))
        if self.gate.pending:
            panel=ttk.Frame(self.body,padding=30);panel.pack(fill='x')
            ttk.Label(panel,text=f'Pass to {self.gate.pending}',style='Heading.TLabel').pack(anchor='w')
            ttk.Label(panel,text='Other players should look away before continuing.').pack(anchor='w',pady=10)
            ttk.Button(panel,text=f'I am {self.gate.pending} - continue',command=self.unlock).pack(anchor='w')
            return
        if view.get('phase')=='lobby':self.render_lobby(view)
        elif view.get('phase')=='opening':self.render_opening(view)
        else:self.render_match(view)

    def render_lobby(self, view):
        ttk.Label(self.body,text='Lobby',style='Heading.TLabel').pack(anchor='w')
        for p in view['players']:
            leader=p['leader']['name'] if p['leader'] else 'not selected'
            ttk.Label(self.body,text=f"{p['name']}  |  {p['deck_name'] or 'No deck'}  |  {leader}  |  {'READY' if p['ready'] else 'Not ready'}").pack(anchor='w',pady=5)
        ttk.Label(self.body,text='Practice Forty: 24 creatures, 10 Actions/Reactions, 6 capacity permanents. Test refill cost: 20 life.',wraplength=900).pack(anchor='w',pady=10)
        if self.gate.actor:
            leaders=self.session.leaders();selected=tk.StringVar(value=next((p['leader']['name'] for p in view['players'] if p['player_id']==self.gate.actor and p['leader']),leaders[0]['name']))
            ttk.Label(self.body,text='Your reserve identity (deck uses Generic cards)').pack(anchor='w')
            ttk.Combobox(self.body,textvariable=selected,values=[l['name'] for l in leaders],state='readonly',width=36).pack(anchor='w',pady=5)
            def choose():
                key=next(l['key'] for l in leaders if l['name']==selected.get())
                self.perform(lambda:self.session.choose_deck(self.gate.actor,key,expected_revision=view['revision']))
            ttk.Button(self.body,text='Select Practice Forty + reserve identity',command=choose).pack(anchor='w',pady=5)
            own=next(p for p in view['players'] if p['player_id']==self.gate.actor)
            ttk.Button(self.body,text='Not ready' if own['ready'] else 'Ready',
                command=lambda:self.perform(lambda:self.session.ready(self.gate.actor,not own['ready'],expected_revision=view['revision']))).pack(anchor='w',pady=5)
            if self.gate.actor==view['host']:
                ttk.Button(self.body,text='Deal opening hands',command=lambda:self.perform(lambda:self.session.start(self.gate.actor,expected_revision=view['revision']))).pack(anchor='w',pady=10)
        else:ttk.Label(self.body,text='Choose a seat above to make its selection.').pack(anchor='w',pady=15)

    def render_opening(self, view):
        ttk.Label(self.body,text='Opening hand - one partial redraw',style='Heading.TLabel').pack(anchor='w')
        ttk.Label(self.body,text='Choose cards to replace, or confirm Keep all. Counts and starting player reveal only after all seats lock.').pack(anchor='w',pady=8)
        own=view.get('you')
        if not own:
            for popup in self.root.winfo_children():
                if isinstance(popup,tk.Toplevel):popup.destroy()
        if not own:ttk.Label(self.body,text=view['waiting']).pack(anchor='w');return
        if own['locked']:ttk.Label(self.body,text='Your opening choice is locked. Hide your hand and pass to the next seat.').pack(anchor='w');return
        listing=tk.Listbox(self.body,selectmode='multiple',exportselection=False,height=7,font=('Segoe UI',12))
        listing.pack(fill='x',pady=10)
        for c in own['hand']:listing.insert('end',c['name'])
        ttk.Button(self.body,text='Confirm selected replacements / Keep all if none',command=lambda:self.perform(
            lambda:self.session.redraw(self.gate.actor,[own['hand'][i]['instance_id'] for i in listing.curselection()],expected_revision=view['revision']))).pack(anchor='w')

    def label(self, card):
        name=card.get('name') or self.session.card_name(card.get('definition_key',card.get('instance_id','Card')))
        stats=f" | {card['attack']}/{card['health']}" if 'attack' in card else ''
        return f"{name} | {card.get('kind','card')} | cost {card.get('cost',0)}{stats}"

    def render_match(self, view):
        turn=view['turn'];priority=view['priority']
        title=f"Turn {turn['turn_id']}  |  {turn['active_player']}  |  {turn['phase']}"
        if turn['recharge']:title+='  |  RECHARGE'
        ttk.Label(self.body,text=title,style='Heading.TLabel').pack(anchor='w')
        setup=view['setup']
        ttk.Label(self.body,text='Turn order: '+' > '.join(setup['turn_order'])+'  |  Replaced: '+', '.join(f'{p}: {n}' for p,n in setup['redraw_counts'].items())).pack(anchor='w',pady=4)
        for p in view['players']:
            status='ELIMINATED' if p['eliminated'] else f"{p['health']} life | {p['resources']['available']} resources | hand {p['hand_count']} | deck {p['deck_count']}"
            ttk.Label(self.body,text=f"{p['player_id']}: {status}").pack(anchor='w')
        if view['result']:
            text='Draw' if view['result']['kind']=='draw' else f"{view['result']['winner']} wins"
            ttk.Label(self.body,text=text,style='Heading.TLabel').pack(anchor='w',pady=12)
        ttk.Label(self.body,text=self.next_step(view),wraplength=1000).pack(anchor='w',pady=(5,0))
        notebook=ttk.Notebook(self.body);notebook.pack(fill='both',expand=True,pady=8)
        table=ttk.Frame(notebook,padding=8);private_page=ttk.Frame(notebook,padding=8);history=ttk.Frame(notebook,padding=8)
        notebook.add(table,text='Public table');notebook.add(private_page,text='Your hand / choices');notebook.add(history,text='Public history')
        private=self.scrollable(private_page)
        board=tk.Text(table,wrap='word',height=12,font=('Segoe UI',11));board.pack(fill='both',expand=True)
        for leader in view.get('leaders',[]):board.insert('end',f"{leader['owner']} leader: {leader['name']} | {leader['location']} | summon {leader['summon_cost']} | {'recovering until own Start' if leader['recovering'] else 'not recovering'}\n")
        board.insert('end','\nBATTLEFIELD\n')
        for o in view['battlefield']:
            c=o.get('creature')
            details=f"{c['attack']} ATK | {c['health']}/{c['max_health']} HP | prevention {sum(s['amount'] for s in c['shields'])} | {'exhausted' if c['exhausted'] else 'ready'} | {'may attack' if c['attack_eligible'] and not c['attack_used'] else 'attack waiting/used'}" if c else f"+{o['capacity_bonus']} capacity"
            board.insert('end',f"{o['controller']} | {self.label(o)} | {details} | {o['instance_id'][-6:]}\n")
            for ability in o.get('triggered_abilities',[]):board.insert('end','  '+self.trigger_text(ability,view,o['controller'])+'\n')
        for duration in view.get('durations',[]):
            board.insert('end',f"Duration {duration['duration_id']}: expires at {duration['anchor_player']} {duration['boundary']} #{duration['occurrence']}\n")
        board.insert('end','\nPENDING\n')
        pending={c['effect_id']:c for c in view['pending_cards']}
        for effect in view['chain']:
            name=self.label(pending[effect['effect_id']]) if effect['effect_id'] in pending else effect.get('label',effect['effect_key'])
            if name in ('Draw trigger','Discard trigger'):name=self.public_name(view,effect['source_id'])+': '+name
            board.insert('end',f"#{effect['effect_id']} {effect['controller']}: {name} | {'; '.join(self.effect_text(step,view) for step in effect['steps'])}\n")
        for p in view['players']:
            if 'discard' in p:board.insert('end',f"\n{p['player_id']} discard: "+', '.join(self.session.card_name(c.get('definition_key','Card')) for c in p['discard'])+'\n')
        board.insert('end','\nEXILE\n')
        for card in view.get('exile',[]):board.insert('end',f"{card['owner']} | {self.label(card)} | {card['instance_id'][-6:]}\n")
        board.configure(state='disabled')
        log=tk.Text(history,wrap='word',height=14);log.pack(fill='both',expand=True)
        for event in view['events'][-100:]:
            who=self.session.card_name(event['card'].get('definition_key','Card')) if 'card' in event else self.public_name(view,event['subject'])
            detail=f" ({event['boundary']})" if 'boundary' in event else f" at {event['expiration']['anchor_player']} {event['expiration']['boundary']}" if 'expiration' in event else ''
            log.insert('end',f"{event['event_id']}: {event['kind'].replace('_',' ')} - {who}{detail}\n")
        log.configure(state='disabled')
        toolbar=ttk.Frame(self.body);toolbar.pack(fill='x')
        ttk.Label(toolbar,text=f"Priority: {priority['holder'] or priority['status']}" if priority else 'Game finished').pack(side='left')
        if view.get('you') and not view['result']:
            ttk.Button(toolbar,text='Pass / continue phase',command=lambda:self.send('pass'),state='normal' if not view.get('paused') and priority and priority['status']=='priority' and priority['holder']==self.gate.actor and not view['you']['choice'] and not view.get('choice_pending') else 'disabled').pack(side='left',padx=8)
            ttk.Button(toolbar,text='End turn',command=lambda:self.send('end_turn'),state='normal' if not view.get('paused') and priority and priority['status']=='priority' and priority['holder']==self.gate.actor and turn['active_player']==self.gate.actor and turn['phase'] in ('MainBefore','MainAfter') and not view['chain'] and not view['you']['choice'] and not view.get('choice_pending') else 'disabled').pack(side='left')
            ttk.Button(toolbar,text='Concede...',command=self.concede).pack(side='right')
        own=view.get('you')
        if not own:ttk.Label(private,text='Private cards are hidden. Choose a seat and acknowledge the handoff.').pack(anchor='w');return
        if own['choice']:
            self.render_choice(private,view,own['choice']);notebook.select(private_page);return
        self.leader_panel(private,view)
        ttk.Label(private,text='Select a card to inspect and confirm a play. Targets/payments stay private until confirmation.').pack(anchor='w')
        cards=own['hand'];listing=tk.Listbox(private,exportselection=False,height=8,font=('Segoe UI',11));listing.pack(fill='x',pady=6)
        for c in cards:listing.insert('end',self.label(c))
        ttk.Button(private,text='Inspect / play selected card',command=lambda:self.card_dialog(view,cards[listing.curselection()[0]]) if listing.curselection() else self.error('Choose a card first.')).pack(anchor='w')
        if turn['phase']=='Combat' and view['combat'] is None and priority and priority['status']=='closed' and turn['active_player']==self.gate.actor:
            self.attack_panel(private,view);notebook.select(private_page)
        else:notebook.select(private_page)

    def next_step(self, view):
        if view.get('paused'):return 'Loaded game is paused. Resume saved game to continue.'
        if view['result']:return 'Game finished. Use New lobby to play again.'
        if view.get('trigger_waiting'):return f"{view['trigger_waiting']}: choose whether to use the optional trigger."
        if view.get('trigger_order_waiting'):return 'Confirm triggered-effect order: '+', '.join(view['trigger_order_waiting'])+'.'
        combat=view.get('combat')
        if combat and combat['stage']=='blocking':return 'Defenders: take your seats and lock blockers privately. They reveal together.'
        if combat and combat['stage']=='ordering':return 'The relevant attacking/defending seat must confirm damage order.'
        if view['priority'] and view['priority']['holder']:return f"{view['priority']['holder']} has priority: pass or respond."
        if view['turn']['phase']=='Combat' and combat is None:return f"{view['turn']['active_player']}: take your seat and declare all attacks, or choose no attacks."
        return 'A required choice is waiting. Take the affected seat to finish it.'

    def scrollable(self, parent):
        canvas=tk.Canvas(parent,highlightthickness=0,background='#edf3f5')
        scrollbar=ttk.Scrollbar(parent,orient='vertical',command=canvas.yview)
        scrollbar.pack(side='right',fill='y');canvas.pack(side='left',fill='both',expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)
        inner=ttk.Frame(canvas)
        window=canvas.create_window(0,0,anchor='nw',window=inner)
        inner.bind('<Configure>',lambda event:canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>',lambda event:canvas.itemconfigure(window,width=event.width))
        return inner

    def concede(self):
        if messagebox.askyesno('Concede','Leave this local game permanently?',parent=self.root):self.send('concede',confirmed=True)

    def target_options(self, view, card):
        actor=self.gate.actor;kind=card.get('target_kind');relation=card.get('target_relation','any')
        choices=[]
        if kind=='player':choices=[(p['player_id'],p['player_id'],p['player_id']) for p in view['players'] if not p['eliminated']]
        elif kind=='creature':choices=[(f"{o['controller']} / {self.session.card_name(o.get('definition_key',o['instance_id']))} / {o['instance_id'][-6:]}",o['instance_id'],o['controller']) for o in view['battlefield'] if o.get('creature')]
        elif kind=='discard':choices=[(f"{self.session.card_name(c['definition_key'])} / {c['instance_id'][-6:]}",c['instance_id'],p['player_id']) for p in view['players'] if p['player_id']==actor for c in p.get('discard',[]) if c.get('definition_key')]
        elif kind=='effect':choices=[(f"#{e['effect_id']} / {e['controller']} / {e['effect_key']}",str(e['effect_id']),e['controller']) for e in view['chain'] if not e['resolving']]
        return [(name,key) for name,key,owner in choices if relation=='any' or (relation=='friendly' and owner==actor) or (relation=='enemy' and owner!=actor)]

    def public_name(self, view, identity):
        leader=next((l for l in view.get('leaders',[]) if l['instance_id']==identity),None)
        if leader:return leader['name']
        obj=next((o for o in view['battlefield'] if o['instance_id']==identity),None)
        if obj:
            leader=next((l for l in view.get('leaders',[]) if l['instance_id']==identity),None)
            return leader['name'] if leader else self.session.card_name(obj.get('definition_key',identity))
        reveal=next((e['card'] for e in view['events'] if e.get('card',{}).get('instance_id')==identity),None)
        if reveal:return self.session.card_name(reveal.get('definition_key',identity))
        return identity

    def trigger_text(self, ability, view, controller=None):
        who=controller or 'you';verb='draw' if ability['event']=='card_drawn' else 'discard'
        if controller:verb+='s'
        event=f'{verb} a card'+(' from your hand' if not controller and ability['event']=='card_discarded' else '')
        if any(s['kind']!='resources' for s in ability['steps']):
            steps=[dict(s,target=controller or '$controller') for s in ability['steps']]
            reward=' '.join(self.effect_text(s,view) for s in steps)
            choice=f'{who} may apply these rewards: ' if ability.get('optional') else ''
            return f'When {who} {event}, {choice}{reward}'
        amount=sum(s['amount'] for s in ability['steps'])
        reward=(f'{controller} may gain' if controller else 'you may gain') if ability.get('optional') else (f'{controller} gains' if controller else 'gain')
        reward+=f" {amount} resource"+('s' if amount!=1 else '')
        return f'When {who} {event}, {reward}.'

    def effect_text(self, step, view):
        target=step.get('target');amount=step.get('amount',0)
        who='you' if target=='$controller' else 'the chosen target' if target=='$target' else self.public_name(view,target) if target else 'the previous target'
        kind=step['kind']
        if kind=='shield':return f"Give {who} {amount} prevention until "+('this turn ends.' if step['duration']=='turn_end' else 'your next Start.')
        if kind=='damage':return f'Deal {amount} damage to {who}.'
        if kind=='heal':return f'Restore {amount} life to {who}.'
        if kind=='draw':return f'{who.capitalize()} draw {amount} card(s).'
        if kind=='capacity':return f'Permanently add {amount} resource capacity for {who}; available at the next refill.'
        if kind=='resources':return f'{who.capitalize()} gain {amount} resources now.'
        if kind=='destroy':return f'Defeat {who}.'
        if kind=='return_to_hand':return f"Return {who} to its owner's hand. Tokens disappear; leaders return to reserve."
        if kind=='exile':return f'Exile {who}. Tokens disappear; leaders return to reserve.'
        if kind=='recover':return f'Return {who} from your discard to your hand.'
        if kind=='negate':return 'Negate the chosen pending effect.' if step['effect_id']=='$target' else f"Negate pending effect #{step['effect_id']}."
        return kind

    def leader_panel(self, frame, view):
        leader=next((l for l in view.get('leaders',[]) if l['owner']==self.gate.actor),None)
        if not leader:return
        ttk.Label(frame,text=f"{leader['name']} | {leader['location']} | current summon cost {leader['summon_cost']}").pack(anchor='w',pady=5)
        if leader['recovering']:ttk.Label(frame,text='Recovering until your next Start; reserve abilities and summoning are unavailable.').pack(anchor='w')
        if leader['location']=='reserve' and not leader['recovering'] and leader['pending_effect_id'] is None:
            card={**leader,'kind':'leader','cost':leader['summon_cost'],'steps':[]}
            ttk.Button(frame,text='Inspect / summon leader',command=lambda c=card:self.card_dialog(view,c,'summon_leader')).pack(anchor='w')
        for ability in leader['abilities']:
            label=f"{ability['location'].title()} - {ability['key'].replace('-',' ').title()} ({ability['cost']})"
            card={**ability,'name':label,'kind':'leader ability','ability_key':ability['key']}
            ttk.Button(frame,text=label,command=lambda c=card:self.card_dialog(view,c,'leader_ability'),state='normal' if ability['available'] else 'disabled').pack(anchor='w',pady=2)

    def card_dialog(self, view, card, command='play_card'):
        popup=tk.Toplevel(self.root);popup.title('Confirm leader action' if command!='play_card' else 'Confirm card play');popup.transient(self.root);popup.grab_set()
        frame=ttk.Frame(popup,padding=18);frame.pack(fill='both',expand=True)
        ttk.Label(frame,text=self.label(card),wraplength=520).pack(anchor='w')
        if card['kind']=='creature':ttk.Label(frame,text='Enters ready. Can block immediately; waits until your next Start to attack.',wraplength=520).pack(anchor='w',pady=5)
        if card['kind']=='permanent':ttk.Label(frame,text=f"Adds {card['capacity_bonus']} capacity while in play; available on your next refill.",wraplength=520).pack(anchor='w',pady=5)
        for step in card.get('steps',[]):ttk.Label(frame,text=self.effect_text(step,view),wraplength=520).pack(anchor='w',pady=3)
        for ability in card.get('triggered_abilities',[]):ttk.Label(frame,text=self.trigger_text(ability,view),wraplength=520).pack(anchor='w',pady=3)
        ttk.Label(frame,text='Ordinary resources to pay').pack(anchor='w',pady=(10,0))
        amount=tk.IntVar(value=card['cost']);ttk.Spinbox(frame,from_=0,to=99,textvariable=amount,width=6).pack(anchor='w')
        tokens=[]
        for obj in view['battlefield']:
            if obj['kind']=='resource_token' and obj['controller']==self.gate.actor:
                selected=tk.BooleanVar();tokens.append((obj['instance_id'],selected))
                ttk.Checkbutton(frame,text=f"Token {obj['instance_id']} ({obj['resource_value']})",variable=selected).pack(anchor='w')
        options=self.target_options(view,card);target=tk.StringVar(value=options[0][0] if options else '')
        if card.get('target_kind'):
            ttk.Label(frame,text='Target').pack(anchor='w',pady=(10,0))
            ttk.Combobox(frame,values=[label for label,_ in options],textvariable=target,state='readonly',width=54).pack(anchor='w')
        def confirm():
            try:ordinary=amount.get()
            except tk.TclError:return self.error('Enter a whole-number payment.')
            args={'payment':{'ordinary':ordinary,'token_ids':[i for i,v in tokens if v.get()]}}
            if command=='play_card':args['card_id']=card['instance_id']
            elif command=='leader_ability':args['key']=card['ability_key']
            if card.get('target_kind'):
                chosen=next((key for label,key in options if label==target.get()),None)
                if chosen is None:return self.error('No valid target is selected.')
                args['target']=chosen
            if self.send(command,**args):popup.destroy()
        ttk.Button(frame,text='Confirm play and payment',command=confirm,state='disabled' if view['result'] or view.get('paused') else 'normal').pack(anchor='w',pady=12)
        ttk.Button(frame,text='Cancel',command=popup.destroy).pack(anchor='w')

    def attack_panel(self, frame, view):
        ttk.Label(frame,text='Declare all attacks together (or confirm no attacks)').pack(anchor='w',pady=(12,4))
        rows=[]
        for obj in view['battlefield']:
            c=obj.get('creature')
            if not c or obj['controller']!=self.gate.actor or c['exhausted'] or not c['attack_eligible'] or c['attack_used']:continue
            choices=[('Do not attack',None)]
            choices += [(f"Attack {p['player_id']}",{'attacker_id':obj['instance_id'],'target_player':p['player_id']}) for p in view['players'] if not p['eliminated'] and p['player_id']!=self.gate.actor]
            if 'challenge' in c['keywords']:
                choices += [(f"Challenge {other['instance_id'][-6:]} ({other['controller']})",{'attacker_id':obj['instance_id'],'target_player':other['controller'],'challenge_target':other['instance_id']}) for other in view['battlefield'] if other.get('creature') and other['controller']!=self.gate.actor]
            selected=tk.StringVar(value=choices[0][0]);rows.append((selected,choices))
            row=ttk.Frame(frame);row.pack(fill='x')
            ttk.Label(row,text=self.session.card_name(obj.get('definition_key',obj['instance_id']))).pack(side='left')
            ttk.Combobox(row,values=[label for label,_ in choices],textvariable=selected,state='readonly',width=34).pack(side='right')
        ttk.Button(frame,text='Confirm all attacks / no attacks',command=lambda:self.send('declare_attacks',attacks=[value for var,choices in rows for label,value in choices if label==var.get() and value is not None])).pack(anchor='w',pady=6)

    def render_choice(self, frame, view, choice):
        kind=choice['kind']
        if kind=='optional_trigger':
            ttk.Label(frame,text='Optional trigger from '+self.public_name(view,choice['source_id']),wraplength=850).pack(anchor='w')
            for step in choice['steps']:ttk.Label(frame,text=self.effect_text(step,view),wraplength=850).pack(anchor='w')
            for use,label in ((True,'Use optional trigger'),(False,'Skip optional trigger')):
                ttk.Button(frame,text=label,state='disabled' if view.get('paused') else 'normal',command=lambda value=use:self.send('trigger_choice',trigger_id=choice['trigger_id'],use=value)).pack(anchor='w',pady=5)
        elif kind=='refill':
            penalty='This turn will end.' if view['turn']['active_player']==self.gate.actor else 'Your next turn will be Recharge.'
            ttk.Label(frame,text=f"Deck exhausted. Pay {choice['cost']} life to refill and finish drawing. {penalty}",wraplength=850).pack(anchor='w',pady=8)
            ttk.Button(frame,text=f"Pay {choice['cost']} life and refill",command=lambda:self.send('refill',pay=True,request_id=choice['request_id'])).pack(anchor='w',pady=5)
            ttk.Button(frame,text='Decline refill (eliminates you)',command=lambda:self.send('refill',pay=False,request_id=choice['request_id'])).pack(anchor='w')
        elif kind=='end_discard':
            ttk.Label(frame,text=f"Choose exactly {choice['count']} cards to discard.").pack(anchor='w')
            cards=view['you']['hand'];listing=tk.Listbox(frame,selectmode='multiple',exportselection=False,height=10);listing.pack(fill='x',pady=8)
            for c in cards:listing.insert('end',self.label(c))
            ttk.Button(frame,text='Confirm discards',command=lambda:self.send('end_discard',cards=[cards[i]['instance_id'] for i in listing.curselection()])).pack(anchor='w')
        elif kind=='blockers':
            if choice['locked']:ttk.Label(frame,text='Blockers locked. Hide your hand and pass to the next defender.').pack(anchor='w');return
            attacks=[a for a in view['combat']['attacks'] if a[1]==self.gate.actor and a[2] is None]
            challenged={a[2] for a in view['combat']['attacks'] if a[2]}
            choices=[('Do not block',None)]+[(f"Block {a[0][-6:]}",a[0]) for a in attacks]
            rows=[]
            ttk.Label(frame,text='Each defender chooses privately. All assignments reveal together.').pack(anchor='w',pady=5)
            for obj in view['battlefield']:
                if not obj.get('creature') or obj['controller']!=self.gate.actor or obj['instance_id'] in challenged:continue
                row=ttk.Frame(frame);row.pack(fill='x',pady=3)
                selected=tk.StringVar(value=choices[0][0]);rows.append((obj['instance_id'],selected))
                ttk.Label(row,text=self.label(obj)).pack(side='left')
                ttk.Combobox(row,values=[label for label,_ in choices],textvariable=selected,state='readonly',width=30).pack(side='right')
            def lock():
                assigned={a[0]:[] for a in attacks}
                for blocker,var in rows:
                    target=next(value for label,value in choices if label==var.get())
                    if target:assigned[target].append(blocker)
                self.send('lock_blockers',assignments=[{'attacker_id':a,'blockers':ids} for a,ids in assigned.items()])
            ttk.Button(frame,text='Lock complete blocker choice / no blocks',command=lock).pack(anchor='w',pady=8)
        elif kind in ('combat_order','trigger_order'):
            orders=choice['orders'] if kind=='combat_order' else [{'subject':None,'items':[t['trigger_id'] for t in choice['triggers']]}]
            current=orders[0];items=list(current['items'])
            ttk.Label(frame,text='Effects resolve from bottom to top.' if kind=='trigger_order' else 'Assign damage from top to bottom.').pack(anchor='w')
            if kind=='trigger_order' and not items:
                ttk.Label(frame,text='No triggered effects were selected. Confirm to continue.').pack(anchor='w')
                ttk.Button(frame,text='Confirm no triggered effects',command=lambda:self.send('trigger_order',order=[])).pack(anchor='w',pady=6)
                return
            listing=tk.Listbox(frame,exportselection=False,height=min(10,len(items)));listing.pack(fill='x',pady=6)
            for item in items:listing.insert('end',str(item))
            def move(delta):
                if not listing.curselection():return
                index=listing.curselection()[0];dest=index+delta
                if not 0<=dest<len(items):return
                items[index],items[dest]=items[dest],items[index]
                listing.delete(0,'end')
                for item in items:listing.insert('end',str(item))
                listing.selection_set(dest)
            ttk.Button(frame,text='Move up',command=lambda:move(-1)).pack(anchor='w')
            ttk.Button(frame,text='Move down',command=lambda:move(1)).pack(anchor='w')
            ttk.Button(frame,text='Confirm this order',command=lambda:self.send('combat_order',subject=current['subject'],order=items) if kind=='combat_order' else self.send('trigger_order',order=items)).pack(anchor='w',pady=6)


def main():
    root=tk.Tk();PlayWindow(root);root.mainloop()


if __name__=='__main__':main()
