"""Private, versioned local snapshots with strict JSON records and atomic replacement."""
import base64
from dataclasses import dataclass, fields, replace
from functools import lru_cache
import hashlib
import importlib.util
import json
import marshal
import os
from pathlib import Path
import sys
import tempfile
import types
import typing
import uuid

from crucible_content.practice import PracticePack, PackCard, ReserveIdentity, validate_pack, pack_hash
from crucible_core.cards import CardDefinition, CardInstance, PendingCard
from crucible_core.combat import Shield, Creature, Player, CombatState, Attack
from crucible_core.combat_flow import CombatFlow
from crucible_core.durations import BoundaryCount, TimedEffect
from crucible_core.leaders import LeaderAbility, LeaderDefinition, LeaderState
from crucible_core.lobby import (LobbyState, LobbyPlayer, DeckSelection, Opening,
    new_lobby, begin_opening, lock_redraw, validate_deck)
from crucible_core.match import (MatchState, MatchPlayer, MatchEvent, MatchResult, TriggerSpec,
    TriggerCandidate, Resolution, MatchObject, EffectSpec, ActionSpec, DamagePlayer,
    HealPlayer, DrawCards, DestroyCreature, ReturnCreatureToHand, GrantCapacity, GrantResources, GrantShield,
    NegateEffect, validate_match, _steps_valid)
from crucible_core.priority import PriorityState, PendingEffect
from crucible_core.resources import ResourcePool, Payment
from crucible_core.turns import DrawPlayer, TurnFlow, RefillPolicy, DrawState, _check_choice

FORMAT='crucible-harness-private-save'
VERSION=2
# Increment when existing instructions/state/shuffle semantics become incompatible.
COMPATIBILITY_VERSION=1
MAX_BYTES=16*1024*1024
MAX_DEPTH=64
_RECORDS={c.__name__:c for c in (PracticePack,PackCard,ReserveIdentity,CardDefinition,CardInstance,PendingCard,
    Shield,Creature,Player,CombatState,Attack,CombatFlow,BoundaryCount,TimedEffect,LeaderAbility,LeaderDefinition,LeaderState,
    LobbyState,LobbyPlayer,DeckSelection,Opening,MatchState,MatchPlayer,MatchEvent,MatchResult,TriggerSpec,TriggerCandidate,
    Resolution,MatchObject,EffectSpec,ActionSpec,DamagePlayer,HealPlayer,DrawCards,DestroyCreature,GrantCapacity,
    GrantResources,GrantShield,ReturnCreatureToHand,NegateEffect,PriorityState,PendingEffect,ResourcePool,Payment,DrawPlayer,TurnFlow,RefillPolicy,DrawState)}


class SaveError(ValueError):
    pass


@dataclass(frozen=True)
class SaveResult:
    path: Path
    backup: Path | None = None
    unchanged: bool = False


def runtime_fingerprint():
    digest=hashlib.sha256(f'{FORMAT}:{VERSION}:{sys.implementation.name}:{sys.version_info[:2]}'.encode())
    modules=('cards','combat','combat_flow','commands','coverage','durations','leaders','lobby','match','priority','resources','turns','views')
    for name in tuple('crucible_core.'+m for m in modules)+('crucible_play.opponent',):
        spec=importlib.util.find_spec(name)
        if spec is None or spec.loader is None:raise SaveError('Cannot identify this game runtime')
        origin=Path(spec.origin) if spec.origin else None
        if origin is not None and origin.suffix=='.py' and origin.is_file():data=origin.read_bytes()
        else:
            code=spec.loader.get_code(name)
            if code is None:raise SaveError('Cannot fingerprint this game build')
            data=marshal.dumps(code)
        digest.update(name.encode());digest.update(data)
    return digest.hexdigest()


def python_runtime():
    # stdlib shuffle behavior is not promised across Python minor releases.
    return f'{sys.implementation.name}-{sys.version_info.major}.{sys.version_info.minor}'


@lru_cache(maxsize=None)
def _hints(cls):return typing.get_type_hints(cls)


def _conforms(value, hint):
    if hint is object or hint is typing.Any:return True
    if hint is type(None):return value is None
    origin=typing.get_origin(hint);args=typing.get_args(hint)
    if origin in (types.UnionType,typing.Union):return any(_conforms(value,a) for a in args)
    if origin is tuple:
        if type(value) is not tuple:return False
        if len(args)==2 and args[1] is Ellipsis:return all(_conforms(v,args[0]) for v in value)
        return len(value)==len(args) and all(_conforms(v,h) for v,h in zip(value,args))
    return type(value) is hint


def _encode(value, depth=0):
    if depth>MAX_DEPTH:raise SaveError('Snapshot nesting is too deep')
    if value is None or type(value) in (str,int,bool):return value
    if type(value) is bytes:return {'bytes':base64.b64encode(value).decode('ascii')}
    if type(value) is tuple:return {'tuple':[_encode(v,depth+1) for v in value]}
    cls=type(value)
    if cls.__name__ not in _RECORDS or _RECORDS[cls.__name__] is not cls:raise SaveError('Unsupported snapshot record')
    return {'record':cls.__name__,'fields':{f.name:_encode(getattr(value,f.name),depth+1) for f in fields(cls)}}


def _decode(value, depth=0):
    if depth>MAX_DEPTH:raise SaveError('Snapshot nesting is too deep')
    if value is None or type(value) in (str,int,bool):return value
    if type(value) is not dict:raise SaveError('Invalid snapshot value')
    if set(value)=={'bytes'}:
        if type(value['bytes']) is not str:raise SaveError('Invalid byte record')
        return base64.b64decode(value['bytes'],validate=True)
    if set(value)=={'tuple'}:
        if type(value['tuple']) is not list:raise SaveError('Invalid tuple record')
        return tuple(_decode(v,depth+1) for v in value['tuple'])
    if set(value)!={'record','fields'} or type(value['record']) is not str or value['record'] not in _RECORDS:
        raise SaveError('Unknown snapshot record type')
    cls=_RECORDS[value['record']];values=value['fields']
    if type(values) is not dict or set(values)!={f.name for f in fields(cls)}:raise SaveError('Unknown or missing snapshot fields')
    decoded={k:_decode(v,depth+1) for k,v in values.items()}
    if any(not _conforms(decoded[k],h) for k,h in _hints(cls).items()):raise SaveError('Invalid snapshot field type')
    return cls(**decoded)


def _canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('utf-8')


def _object(pairs):
    value={}
    for key,item in pairs:
        if key in value:raise SaveError('Duplicate JSON key')
        value[key]=item
    return value


def _read_envelope(path):
    with Path(path).open('rb') as stream:data=stream.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES:raise SaveError('Save file is too large')
    def invalid_number(value):raise SaveError('Nonfinite JSON number')
    doc=json.loads(data.decode('utf-8'),object_pairs_hook=_object,parse_constant=invalid_number)
    if type(doc) is not dict or doc.get('format')!=FORMAT:raise SaveError('Not a Crucible private save')
    version=doc.get('schema_version')
    if type(version) is not int or version not in (1,VERSION):raise SaveError('Unsupported save version; original file was not changed')
    expected={'format','schema_version','runtime_hash','content_hash','payload','checksum'}
    if version==VERSION:expected.update(('compatibility_version','python_runtime'))
    if set(doc)!=expected:raise SaveError('Unknown or missing envelope fields')
    if any(not _hash_value(doc[key]) for key in ('runtime_hash','content_hash','checksum')):raise SaveError('Invalid save fingerprint')
    checksum=doc['checksum'];body={k:v for k,v in doc.items() if k!='checksum'}
    if type(checksum) is not str or checksum!=hashlib.sha256(_canonical(body)).hexdigest():raise SaveError('Save checksum does not match')
    return doc,data


def _hash_value(value):
    return type(value) is str and len(value)==64 and all(c in '0123456789abcdef' for c in value)


def _validate_pending(state):
    if any(type(e.event_id) is not int or not 0<e.event_id<state.next_event_id for e in state.events) or len({e.event_id for e in state.events})!=len(state.events):raise SaveError('Invalid event IDs')
    if tuple(e.event_id for e in state.events)!=tuple(sorted(e.event_id for e in state.events)):raise SaveError('Out-of-order event IDs')
    effects={e.key:e for e in state.effects}
    trigger_ids={t.trigger_id for t in state.triggers}
    if len(trigger_ids)!=len(state.triggers) or any(type(t.trigger_id) is not int or not 0<t.trigger_id<state.next_trigger_id or t.controller not in state.priority.seats or t.effect_key not in effects or effects[t.effect_key].controller!=t.controller or not any(e.event_id==t.event_id for e in state.events) for t in state.triggers):raise SaveError('Invalid pending triggers')
    confirmed=[]
    for actor,order in state.trigger_orders:
        own={t.trigger_id for t in state.triggers if t.controller==actor}
        if actor in confirmed or not own or type(order) is not tuple or len(order)!=len(own) or set(order)!=own:raise SaveError('Invalid trigger order confirmation')
        confirmed.append(actor)
    if state.rotation_queue and (state.end_stage!='done' or state.turn.phase not in ('End','Finished') or state.rotation_queue[-1][1]!='Turn' or any(k=='Turn' for _,k in state.rotation_queue[:-1]) or len(state.rotation_queue)>2*len(state.seat_order)+1):raise SaveError('Invalid boundary transition')
    pending=state.pending
    if pending is None:return
    _steps_valid(pending.steps,state.seat_order,())
    if type(pending.index) is not int or not 0<=pending.index<=len(pending.steps):raise SaveError('Invalid instruction cursor')
    if pending.effect_id is not None:
        effect=state.priority.resolving if state.priority else None
        if effect is None or effect.effect_id!=pending.effect_id or effects[effect.effect_key].steps!=pending.steps or pending.controller!=effect.controller:raise SaveError('Resolving item/cursor mismatch')
    elif not (pending.cleanup or state.start_stage=='cleanup' or state.rotation_queue or state.turn.phase in ('Start','Draw')):raise SaveError('Unregistered boundary cursor')
    if pending.draw:
        draw=pending.draw
        _check_choice(draw,draw.request_id,draw.revision)
        player=next(p for p in state.players if p.cards.player_id==draw.player.player_id)
        if draw.player!=player.cards or draw.turn!=state.turn or draw.policy!=state.policy or pending.index>=len(pending.steps):raise SaveError('Refill snapshot does not match live state')
        step=pending.steps[pending.index]
        if type(step) is not DrawCards or step.target!=draw.player.player_id:raise SaveError('Refill cursor target mismatch')


def _validate_lobby(lobby, bots):
    if type(lobby) is not LobbyState or type(bots) is not tuple or any(type(a) is not str for a in bots) or len(set(bots))!=len(bots):raise SaveError('Invalid saved session')
    roster=tuple((p.player_id,p.name) for p in lobby.players)
    base=new_lobby(roster,lobby.pack,seed=lobby.seed)
    if not set(bots)<={p.player_id for p in lobby.players} or type(lobby.revision) is not int or lobby.revision<0:raise SaveError('Invalid computer seats/revision')
    validate_pack(lobby.pack)
    for player in lobby.players:
        if player.deck:validate_deck(lobby.pack,player.deck)
        if player.ready and player.deck is None:raise SaveError('Ready seat has no deck')
    if lobby.phase=='lobby':
        if lobby.opening or lobby.redraw_locks or lobby.redraw_counts or lobby.order or lobby.match is not None or lobby.rules_hash is not None or lobby.content_hash is not None:raise SaveError('Lobby contains premature match data')
        return
    if lobby.phase not in ('opening','match') or not _hash_value(lobby.rules_hash) or lobby.content_hash!=pack_hash(lobby.pack):raise SaveError('Invalid frozen rules/content provenance')
    base=replace(base,players=lobby.players,revision=lobby.revision)
    expected=begin_opening(base,lobby.players[0].player_id,expected_revision=base.revision)
    for item in lobby.redraw_locks:
        if type(item) is not tuple or len(item)!=2 or type(item[0]) is not str or type(item[1]) is not tuple:raise SaveError('Invalid opening lock')
        expected=lock_redraw(expected,item[0],item[1],expected_revision=expected.revision)
    if (lobby.phase,lobby.opening,lobby.order,lobby.redraw_counts)!=(expected.phase,expected.opening,expected.order,expected.redraw_counts):raise SaveError('Opening cards/order are inconsistent')
    if lobby.phase=='opening':
        if lobby.match is not None:raise SaveError('Opening has premature match state')
        return
    if type(lobby.match) is not MatchState:raise SaveError('Missing authoritative match')
    state=lobby.match;original=expected.match
    if (state.seat_order!=lobby.order or state.starting_player!=lobby.order[0] or not state.managed_turns
            or state.card_definitions!=original.card_definitions or state.leader_definitions!=original.leader_definitions
            or state.card_instances!=original.card_instances or state.shuffle_seed!=original.shuffle_seed):raise SaveError('Frozen match definitions/instances changed')
    validate_match(state);_validate_pending(state)


def _publish_new(temp, path):
    # Windows rename refuses an occupied destination; POSIX rename would replace it.
    if os.name=='nt':os.rename(temp,path)
    else:os.link(temp,path)


def _write_atomic(path, data, *, replace_existing=True):
    temp=None
    try:
        with tempfile.NamedTemporaryFile(prefix='.'+path.name+'.',suffix='.tmp',dir=path.parent,delete=False) as stream:
            temp=Path(stream.name);stream.write(data);stream.flush();os.fsync(stream.fileno())
        if replace_existing:
            os.replace(temp,path);temp=None
        else:
            # Publish complete bytes without replacing a concurrently created destination.
            _publish_new(temp,path)
    finally:
        if temp is not None:temp.unlink(missing_ok=True)


def save_session(session, path):
    try:
        path=Path(path)
        if not path.name.endswith('.crucible.json') or not path.parent.is_dir() or path.is_symlink():raise SaveError('Choose a regular .crucible.json file in an existing folder')
        current=runtime_fingerprint()
        if session.runtime_hash!=current:raise SaveError('Runtime changed; retain the matching source/build before saving')
        bots=tuple(sorted(session.bots));lobby=session._lobby
        _validate_lobby(lobby,bots)
        body={'format':FORMAT,'schema_version':VERSION,'compatibility_version':COMPATIBILITY_VERSION,'python_runtime':python_runtime(),'runtime_hash':current,'content_hash':pack_hash(lobby.pack),
              'payload':{'lobby':_encode(lobby),'bots':list(bots)}}
        data=json.dumps({**body,'checksum':hashlib.sha256(_canonical(body)).hexdigest()},sort_keys=True,indent=2,allow_nan=False).encode('utf-8')
        if len(data)>MAX_BYTES:raise SaveError('Snapshot exceeds save size limit')
        backup=None
        if path.exists():
            _,old=_read_envelope(path)
            if old==data:return SaveResult(path,unchanged=True)
            backup=path.with_name(path.name+'.backup-'+uuid.uuid4().hex)
            _write_atomic(backup,old)
        _write_atomic(path,data)
        return SaveResult(path,backup)
    except SaveError:raise
    except (OSError,ValueError,TypeError,AttributeError,KeyError,StopIteration,RecursionError) as exc:
        raise SaveError(f'Could not save this session: {exc}') from None


def _session_from_document(doc):
    if doc['schema_version']!=VERSION:raise SaveError('Version 1 needs explicit conversion: python -m crucible_play.migrate INPUT OUTPUT')
    if type(doc['compatibility_version']) is not int or doc['compatibility_version']!=COMPATIBILITY_VERSION:
        raise SaveError('Unsupported gameplay compatibility version; retain the original save/build')
    if doc['python_runtime']!=python_runtime():raise SaveError('Save requires its matching Python implementation/major.minor version')
    payload=doc['payload']
    if type(payload) is not dict or set(payload)!={'lobby','bots'} or type(payload['bots']) is not list:raise SaveError('Invalid saved payload')
    lobby=_decode(payload['lobby']);bots=tuple(payload['bots'])
    if type(lobby) is not LobbyState or doc['content_hash']!=pack_hash(lobby.pack):raise SaveError('Content checksum mismatch')
    _validate_lobby(lobby,bots)
    from .session import HarnessSession
    session=object.__new__(HarnessSession)
    session._lobby=lobby;session.bots=frozenset(bots);session.runtime_hash=runtime_fingerprint();session.paused=True
    return session


def load_session(path):
    try:
        doc,_=_read_envelope(path)
        return _session_from_document(doc)
    except SaveError:raise
    except (OSError,ValueError,TypeError,AttributeError,KeyError,StopIteration,RecursionError) as exc:
        raise SaveError(f'Invalid or unreadable save: {exc}') from None
