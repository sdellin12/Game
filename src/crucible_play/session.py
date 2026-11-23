"""Server-side session adapter and explicit local handoff gate."""
from crucible_content.practice import practice_pack
from crucible_core.lobby import (new_lobby, DeckSelection, select_deck, set_ready, begin_opening, lock_redraw, project_lobby)
from crucible_core.commands import route_command
from crucible_core.views import project_match


class HarnessSession:
    def __init__(self, names=('Player 1','Player 2'), *, seed=None, pack=None, bots=()):
        self.bots=frozenset(bots)
        if not self.bots<=set(f'P{i+1}' for i in range(len(names))):raise ValueError('Unknown computer seat')
        self._lobby=new_lobby(tuple((f'P{i+1}',name) for i,name in enumerate(names)),pack or practice_pack(),seed=seed)

    def view(self, actor=None):
        lobby=project_lobby(self._lobby,actor)
        for player in lobby['players']:player['computer']=player['player_id'] in self.bots
        if self._lobby.phase!='match':return lobby
        view=project_match(self._lobby.match,actor)
        view['setup']=lobby
        return view

    def choose_deck(self, actor, leader_key, *, expected_revision):
        leader=next((l for l in self._lobby.pack.leaders if l.key==leader_key),None)
        if leader is None:raise ValueError('Choose a reserve identity')
        deck=DeckSelection('Practice Forty',leader.color,leader.key,tuple(c.definition.key for c in self._lobby.pack.cards[:40]))
        self._lobby=select_deck(self._lobby,actor,deck,expected_revision=expected_revision)

    def ready(self, actor, ready, *, expected_revision):
        self._lobby=set_ready(self._lobby,actor,ready,expected_revision=expected_revision)

    def start(self, actor, *, expected_revision):
        self._lobby=begin_opening(self._lobby,actor,expected_revision=expected_revision)

    def redraw(self, actor, rejected, *, expected_revision):
        self._lobby=lock_redraw(self._lobby,actor,tuple(rejected),expected_revision=expected_revision)

    def send(self, actor, packet):
        if self._lobby.phase!='match':raise ValueError('Finish opening choices first')
        state=route_command(self._lobby.match,actor,packet)
        from dataclasses import replace
        self._lobby=replace(self._lobby,match=state)

    def step_opponent(self):
        """At most one authoritative action; never passes or chooses for a human."""
        from .opponent import choose_move, opening_choice
        public=self.view()
        for actor in sorted(self.bots):
            view=self.view(actor)
            if public.get('phase')=='lobby':
                own=next(p for p in view['players'] if p['player_id']==actor)
                if own['deck_name'] is None:
                    self.choose_deck(actor,'core-gold',expected_revision=view['revision']);return True
                if not own['ready']:
                    self.ready(actor,True,expected_revision=view['revision']);return True
            elif public.get('phase')=='opening':
                rejected=opening_choice(view)
                if rejected is not None:
                    self.redraw(actor,rejected,expected_revision=view['revision']);return True
            else:
                move=choose_move(view)
                if move:
                    kind,args=move
                    self.send(actor,{'kind':kind,'args':args,'expected_revision':view['revision']});return True
        return False

    def leaders(self):
        return tuple({'key':l.key,'name':l.name,'color':l.color} for l in self._lobby.pack.leaders)

    def card_name(self, key):
        # Public catalog metadata only; no lookup from private instance ID.
        name=next((c.name for c in self._lobby.pack.cards if c.definition.key==key),None)
        return name or next((l.name for l in self._lobby.pack.leaders if l.key==key),key)


class HotseatGate:
    def __init__(self):
        self.actor=None
        self.pending=None

    def request(self, actor):
        self.actor=None
        self.pending=actor

    def unlock(self):
        if self.pending is None:raise ValueError('Choose a seat first')
        self.actor=self.pending
        self.pending=None

    def hide(self):
        self.actor=None
        self.pending=None
