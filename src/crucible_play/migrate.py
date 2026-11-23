"""Explicit, non-destructive converter for the published first private-save build."""
import argparse
import hashlib
import json
from pathlib import Path

from .persistence import (SaveError, SaveResult, VERSION, COMPATIBILITY_VERSION, MAX_BYTES,
    _read_envelope, _canonical, _session_from_document, _write_atomic)

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


def _check_v1_records(value):
    if type(value) is dict:
        if 'record' in value and value['record'] not in V1_RECORDS:raise SaveError('Record did not exist in the v1 build')
        for item in value.values():_check_v1_records(item)
    elif type(value) is list:
        for item in value:_check_v1_records(item)


def migrate_save(source, destination):
    """Validate v1, add the reviewed gameplay contract, and exclusively publish v2."""
    try:
        source=Path(source);destination=Path(destination)
        if (not destination.name.endswith('.crucible.json') or not destination.parent.is_dir()
                or destination.is_symlink() or source.resolve()==destination.resolve()):
            raise SaveError('Choose a different, new .crucible.json output file')
        if destination.exists():raise SaveError('Migration output already exists; nothing was overwritten')
        doc,_=_read_envelope(source)
        if doc['schema_version']!=1:raise SaveError('Converter accepts only schema-v1 input')
        rules=V1_BUILDS.get(doc['runtime_hash'])
        if rules is None:raise SaveError('Unknown v1 build; retain its matching original runtime')
        _check_v1_records(doc['payload'])
        converted={**doc,'schema_version':VERSION,'compatibility_version':COMPATIBILITY_VERSION,'python_runtime':'cpython-3.14'}
        session=_session_from_document(converted)
        if session._lobby.phase!='lobby' and session._lobby.rules_hash!=rules:
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
    parser=argparse.ArgumentParser(description='Convert a known v1 private save to a new v2 file; preserve the original.')
    parser.add_argument('source',type=Path);parser.add_argument('destination',type=Path)
    args=parser.parse_args(argv)
    try:result=migrate_save(args.source,args.destination)
    except SaveError as exc:parser.exit(1,f'{exc}\n')
    print(f'Converted to {result.path}; original retained. Load the new file to resume.')


if __name__=='__main__':main()
