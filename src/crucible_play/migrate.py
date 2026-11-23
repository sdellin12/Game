"""Explicit, non-destructive schema-v1/v2 conversion to the current private save."""
import argparse
import hashlib
import json
from pathlib import Path

from .persistence import (SaveError, SaveResult, VERSION, COMPATIBILITY_VERSION, MAX_BYTES,
    MAX_DEPTH, _read_envelope, _canonical, _session_from_document, _write_atomic)

# 9b0f7f5, CPython 3.14: deployed workspace, Git LF checkout, Git CRLF checkout.
# Only reviewed source builds belong here. A save cannot nominate its own converter.
V1_BUILDS={
    '6ff4694495525b0a7c3a09efb28d253ccec7dca159fde2419b7e442b8b39fec4':
        '0dd0b59ddef4f70e435170c5bef0d3a9f456274b7d11641e5f265de8d6bfbfa2',
    '48afdd3d9d8cbfb0c0b7ae2b2ec288231ec74c0c0a853091f92c4734ff962d8a':
        '2d6516c77e1f94ef3c9b2c4872ae86bb2972d271d27bf95846fd3513b7529646',
    '6837094d4847165905219d1f43cdd179806aef7349f1bf84598126abd36907bc':
        '3b92217adddc430a1c046379445101ecc1fb288e8b2d2bc7c5649f785ced28c2',
}
V1_RECORDS=frozenset('''PracticePack PackCard ReserveIdentity CardDefinition CardInstance PendingCard
Shield Creature Player CombatState Attack CombatFlow BoundaryCount TimedEffect LeaderAbility LeaderDefinition LeaderState
LobbyState LobbyPlayer DeckSelection Opening MatchState MatchPlayer MatchEvent MatchResult TriggerSpec TriggerCandidate
Resolution MatchObject EffectSpec ActionSpec DamagePlayer HealPlayer DrawCards DestroyCreature GrantCapacity
GrantResources GrantShield NegateEffect PriorityState PendingEffect ResourcePool Payment DrawPlayer TurnFlow RefillPolicy DrawState'''.split())


V2_RECORDS=V1_RECORDS|{'ReturnCreatureToHand'}
V3_RECORDS=V2_RECORDS|{'ExileCreature','RecoverDiscardCard'}


def _upgrade_payload(value, allowed, depth=0, version=2):
    if depth>MAX_DEPTH:raise SaveError('Legacy snapshot nesting is too deep')
    if type(value) is dict:
        if 'record' in value and value['record'] not in allowed:raise SaveError('Record did not exist in the legacy schema')
        if version<3 and value.get('record')=='TriggerSpec' and value.get('fields',{}).get('event') not in ('defeat','departure','turn_start','turn_end'):
            raise SaveError('Trigger event did not exist in the legacy schema')
        result={key:_upgrade_payload(item,allowed,depth+1,version) for key,item in value.items()}
        if value.get('record')=='MatchState' and version<3:
            fields=result.get('fields')
            if type(fields) is not dict or 'exiled' in fields:raise SaveError('Invalid legacy MatchState fields')
            fields['exiled']={'tuple':[]}
        if value.get('record')=='CardDefinition':
            fields=result.get('fields')
            if type(fields) is not dict or 'triggered_abilities' in fields:raise SaveError('Invalid legacy CardDefinition fields')
            fields['triggered_abilities']={'tuple':[]}
        return result
    if type(value) is list:return [_upgrade_payload(item,allowed,depth+1,version) for item in value]
    return value


def migrate_save(source, destination):
    """Preserve legacy state, add an empty exile zone, publish a separate current file."""
    try:
        source=Path(source);destination=Path(destination)
        if (not destination.name.endswith('.crucible.json') or not destination.parent.is_dir()
                or destination.is_symlink() or source.resolve()==destination.resolve()):
            raise SaveError('Choose a different, new .crucible.json output file')
        if destination.exists():raise SaveError('Migration output already exists; nothing was overwritten')
        doc,_=_read_envelope(source)
        version=doc['schema_version'];rules=None
        if version==1:
            rules=V1_BUILDS.get(doc['runtime_hash'])
            if rules is None:raise SaveError('Unknown v1 build; retain its matching original runtime')
        elif version in (2,3):
            if type(doc['compatibility_version']) is not int or doc['compatibility_version']!=COMPATIBILITY_VERSION:
                raise SaveError('Unsupported legacy gameplay compatibility')
        else:raise SaveError('Converter accepts only schema-v1/v2/v3 input')
        converted={**doc,'schema_version':VERSION,'compatibility_version':COMPATIBILITY_VERSION,
                   'python_runtime':'cpython-3.14' if version==1 else doc['python_runtime'],
                   'payload':_upgrade_payload(doc['payload'],V1_RECORDS if version==1 else V2_RECORDS if version==2 else V3_RECORDS,version=version)}
        session=_session_from_document(converted)
        if version==1 and session._lobby.phase!='lobby' and session._lobby.rules_hash!=rules:
            raise SaveError('Version-1 source/rules provenance mismatch')
        converted['checksum']=hashlib.sha256(_canonical({k:v for k,v in converted.items() if k!='checksum'})).hexdigest()
        data=json.dumps(converted,sort_keys=True,indent=2,allow_nan=False).encode('utf-8')
        if len(data)>MAX_BYTES:raise SaveError('Converted snapshot exceeds size limit')
        _write_atomic(destination,data,replace_existing=False)
        return SaveResult(destination)
    except SaveError:raise
    except (OSError,ValueError,TypeError,AttributeError,KeyError,StopIteration,RecursionError) as exc:
        raise SaveError(f'Could not convert save: {exc}') from None


def main(argv=None):
    parser=argparse.ArgumentParser(description='Convert a known v1 or compatible v2/v3 private save to a new current-schema file; preserve the original.')
    parser.add_argument('source',type=Path);parser.add_argument('destination',type=Path)
    args=parser.parse_args(argv)
    try:result=migrate_save(args.source,args.destination)
    except SaveError as exc:parser.exit(1,f'{exc}\n')
    print(f'Converted to {result.path}; original retained. Load the new file to resume.')


if __name__=='__main__':main()
