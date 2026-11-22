"""Immutable local setup transactions; partial redraws lock before public reveal."""
from dataclasses import dataclass, replace
import hashlib
import json
import random
import secrets
from pathlib import Path
from .cards import CardInstance
from .match import MatchPlayer, new_match
from .turns import DrawPlayer, RefillPolicy
from crucible_content.practice import validate_pack, pack_hash

@dataclass(frozen=True)
class DeckSelection:
    name: str
    color: str
    leader_key: str
    card_keys: tuple[str, ...]


@dataclass(frozen=True)
class LobbyPlayer:
    player_id: str
    name: str
    deck: DeckSelection | None = None
    ready: bool = False


@dataclass(frozen=True)
class Opening:
    player_id: str
    hand: tuple[str, ...]
    deck: tuple[str, ...]
    instances: tuple[CardInstance, ...]


@dataclass(frozen=True)
class LobbyState:
    players: tuple[LobbyPlayer, ...]
    pack: object
    seed: bytes
    revision: int = 0
    phase: str = 'lobby'
    opening: tuple[Opening, ...] = ()
    redraw_locks: tuple = ()
    redraw_counts: tuple = ()
    order: tuple[str, ...] = ()
    rules_hash: str | None = None
    content_hash: str | None = None
    match: object | None = None


def _rng(lobby, purpose):
    return random.Random(hashlib.sha256(lobby.seed+purpose.encode()).digest())


def new_lobby(roster, pack, *, seed=None):
    validate_pack(pack)
    if type(roster) is not tuple or not 2<=len(roster)<=4 or any(type(p) is not tuple or len(p)!=2 or any(type(v) is not str or not v.strip() for v in p) for p in roster):
        raise ValueError('Choose two through four named practice seats')
    if len({p[0] for p in roster})!=len(roster):raise ValueError('Duplicate player ID')
    seed=secrets.token_bytes(32) if seed is None else seed
    if type(seed) is not bytes or len(seed)<16:raise ValueError('Private setup seed required')
    return LobbyState(tuple(LobbyPlayer(*p) for p in roster),pack,seed)


def _check(lobby, actor, revision, phase):
    if type(revision) is not int or revision!=lobby.revision or lobby.phase!=phase:
        raise ValueError('Setup command unavailable or stale')
    player=next((p for p in lobby.players if p.player_id==actor),None)
    if player is None:raise ValueError('Unknown setup seat')
    return player


def validate_deck(pack, deck):
    if type(deck) is not DeckSelection or type(deck.name) is not str or not deck.name.strip() or type(deck.card_keys) is not tuple or len(deck.card_keys)!=40 or len(set(deck.card_keys))!=40:
        raise ValueError('Deck requires forty distinct card definitions')
    cards={c.definition.key:c for c in pack.cards}
    leader=next((l for l in pack.leaders if l.key==deck.leader_key),None)
    if leader is None or deck.color!=leader.color or any(k not in cards or cards[k].color not in ('Generic',deck.color) for k in deck.card_keys):
        raise ValueError('Deck/leader color or card selection is invalid')


def select_deck(lobby, actor, deck, *, expected_revision):
    _check(lobby,actor,expected_revision,'lobby')
    validate_deck(lobby.pack,deck)
    return replace(lobby,players=tuple(replace(p,deck=deck,ready=False) if p.player_id==actor else p for p in lobby.players),revision=lobby.revision+1)


def set_ready(lobby, actor, ready, *, expected_revision):
    p=_check(lobby,actor,expected_revision,'lobby')
    if type(ready) is not bool or p.deck is None:raise ValueError('Select a legal deck first')
    validate_deck(lobby.pack,p.deck)
    return replace(lobby,players=tuple(replace(p,ready=ready) if p.player_id==actor else p for p in lobby.players),revision=lobby.revision+1)


def _rules_hash():
    digest=hashlib.sha256()
    for source in sorted(Path(__file__).parent.glob('*.py')):
        digest.update(source.name.encode());digest.update(source.read_bytes())
    return digest.hexdigest()


def begin_opening(lobby, actor, *, expected_revision):
    _check(lobby,actor,expected_revision,'lobby')
    if actor!=lobby.players[0].player_id or not all(p.ready and p.deck for p in lobby.players):
        raise ValueError('Host can start once all seats are ready')
    opening=[]
    for p in lobby.players:
        validate_deck(lobby.pack,p.deck)
        instances=tuple(CardInstance(hashlib.sha256(lobby.seed+json.dumps((p.player_id,key)).encode()).hexdigest()[:24],key,p.player_id) for key in p.deck.card_keys)
        cards=[c.instance_id for c in instances]
        _rng(lobby,'opening:'+p.player_id).shuffle(cards)
        opening.append(Opening(p.player_id,tuple(cards[:5]),tuple(cards[5:]),instances))
    return replace(lobby,opening=tuple(opening),phase='opening',revision=lobby.revision+1,
                   rules_hash=_rules_hash(),content_hash=pack_hash(lobby.pack))


def lock_redraw(lobby, actor, rejected, *, expected_revision):
    _check(lobby,actor,expected_revision,'opening')
    own=next(p for p in lobby.opening if p.player_id==actor)
    if actor in dict(lobby.redraw_locks) or type(rejected) is not tuple or len(set(rejected))!=len(rejected) or any(i not in own.hand for i in rejected):
        raise ValueError('Select original opening cards once; confirm keep with an empty choice')
    lobby=replace(lobby,redraw_locks=lobby.redraw_locks+((actor,rejected),),revision=lobby.revision+1)
    if len(lobby.redraw_locks)<len(lobby.players):return lobby
    # All choices are locked before any counts/results or starting seat are revealed.
    choices=dict(lobby.redraw_locks);final=[]
    for opening in lobby.opening:
        rejected=choices[opening.player_id];count=len(rejected)
        replacements=opening.deck[:count]
        remaining=list(opening.deck[count:]+rejected)
        if rejected:_rng(lobby,'redraw:'+opening.player_id).shuffle(remaining)
        hand=tuple(i for i in opening.hand if i not in rejected)+replacements
        final.append(replace(opening,hand=hand,deck=tuple(remaining)))
    start=_rng(lobby,'starting-seat').randrange(len(lobby.players))
    order=tuple(p.player_id for p in lobby.players[start:]+lobby.players[:start])
    by_id={p.player_id:p for p in final}
    players=tuple(MatchPlayer(DrawPlayer(p,30,by_id[p].deck,(),by_id[p].hand)) for p in order)
    match=new_match(players,(),(),RefillPolicy(20,1),active_player=order[0],phase='Start',managed_turns=True,
                    card_definitions=tuple(c.definition for c in lobby.pack.cards),
                    card_instances=tuple(c for p in final for c in p.instances),
                    shuffle_seed=hashlib.sha256(lobby.seed+b'match-refills').digest())
    return replace(lobby,phase='match',opening=tuple(final),order=order,match=match,
                   redraw_counts=tuple((p.player_id,len(choices[p.player_id])) for p in lobby.players))


def project_lobby(lobby, viewer=None):
    if viewer is not None and viewer not in tuple(p.player_id for p in lobby.players):raise ValueError('Unknown viewer')
    roster=[]
    for p in lobby.players:
        leader=next((l for l in lobby.pack.leaders if p.deck and l.key==p.deck.leader_key),None)
        roster.append({'player_id':p.player_id,'name':p.name,'ready':p.ready,
                       'deck_name':p.deck.name if p.deck else None,'color':p.deck.color if p.deck else None,
                       'leader':{'key':leader.key,'name':leader.name,'color':leader.color} if leader else None})
    view={'phase':lobby.phase,'revision':lobby.revision,'host':lobby.players[0].player_id,'players':roster,
          'turn_order':list(lobby.order) if lobby.order else None,
          'redraw_counts':dict(lobby.redraw_counts) if lobby.redraw_counts else None,
          'rules_hash':lobby.rules_hash,'content_hash':lobby.content_hash,
          'pack':{'id':lobby.pack.pack_id,'version':lobby.pack.version}}
    if lobby.phase=='opening':
        view['waiting']='Opening choices are being confirmed'
        if viewer:
            own=next(p for p in lobby.opening if p.player_id==viewer)
            instances={c.instance_id:c for c in own.instances};cards={c.definition.key:c for c in lobby.pack.cards}
            view['you']={'player_id':viewer,'locked':viewer in dict(lobby.redraw_locks),
                         'hand':[{'instance_id':i,'definition_key':instances[i].definition_key,'name':cards[instances[i].definition_key].name} for i in own.hand]}
    return view
