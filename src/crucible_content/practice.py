"""Versioned, engine-validated practice content; separate from the household catalog."""
from dataclasses import dataclass, asdict
import hashlib
import json
from crucible_core.cards import CardDefinition
from crucible_core.match import (DamagePlayer, HealPlayer, DrawCards, DestroyCreature,
    GrantResources, GrantCapacity, NegateEffect, MatchPlayer, new_match)
from crucible_core.turns import DrawPlayer, RefillPolicy


@dataclass(frozen=True)
class PackCard:
    name: str
    color: str
    definition: CardDefinition


@dataclass(frozen=True)
class ReserveIdentity:
    key: str
    name: str
    color: str


@dataclass(frozen=True)
class PracticePack:
    pack_id: str
    version: int
    cards: tuple[PackCard, ...]
    leaders: tuple[ReserveIdentity, ...]
    status: str = 'experimental-practice-content'


def practice_pack():
    names=('Clockwork Pup','Lantern Mouse','Tin Turtle','Paper Falcon','Moss Bear','Pebble Guard',
           'Copper Fox','Moon Rabbit','Thread Giant','Ember Moth','River Otter','Button Badger',
           'Windup Lynx','Pocket Drake','Cloud Whale','Velvet Wolf','Crystal Newt','Clover Golem',
           'Brass Raven','Starlit Ram','Patchwork Lion','Oak Sentinel','Silver Hare','Dawn Colossus')
    profiles=((1,2,1),(1,1,2),(1,0,3),(2,3,2),(2,2,3),(2,1,4),(3,4,3),(3,3,4),(3,2,5))
    cards=[]
    for i,name in enumerate(names):
        cost,attack,health=profiles[i%len(profiles)]
        keywords=() if i<18 else (('challenge',) if i%2 else ('breakthrough',))
        cards.append(PackCard(name,'Generic',CardDefinition(f'unit-{i+1:02}', 'creature',cost+(1 if keywords else 0),
                             attack=attack,health=health,keywords=keywords)))
    spells=(
        ('Spark Volley','action',2,(DamagePlayer('$target',3),),'player','enemy'),
        ('Thunder Pebble','action',3,(DamagePlayer('$target',5),),'player','enemy'),
        ('Quiet Repair','action',4,(HealPlayer('$controller',4),),None,'any'),
        ('Fresh Inspiration','action',2,(DrawCards('$controller',1),),None,'any'),
        ('Unmake','action',5,(DestroyCreature('$target'),),'creature','enemy'),
        ('Sudden Spark','reaction',3,(DamagePlayer('$target',2),),'player','enemy'),
        ('Second Wind','reaction',4,(HealPlayer('$controller',3),),None,'any'),
        ('Interrupt','reaction',3,(NegateEffect('$target'),),'effect','enemy'),
        ('Stored Momentum','action',2,(GrantResources('$controller',3),),None,'any'),
        ('Lasting Growth','action',4,(GrantCapacity('$controller',1),),None,'any'),
    )
    for i,(name,kind,cost,steps,target,relation) in enumerate(spells):
        cards.append(PackCard(name,'Generic',CardDefinition(f'spell-{i+1:02}',kind,cost,steps,target_kind=target,target_relation=relation)))
    for i,name in enumerate(('Workshop Lantern','Root Battery','Memory Well','Beacon Tower','Sun Engine','Crystal Reservoir')):
        cards.append(PackCard(name,'Generic',CardDefinition(f'beacon-{i+1:02}','permanent',3 if i<3 else 5,capacity_bonus=1 if i<3 else 2)))
    return validate_pack(PracticePack('crucible-practice',1,tuple(cards),(
        ReserveIdentity('core-gold','Aster, Practice Core','Gold'),
        ReserveIdentity('core-green','Moss, Practice Core','Green'),
        ReserveIdentity('core-silver','Gear, Practice Core','Silver'))))


def validate_pack(pack):
    if type(pack) is not PracticePack or type(pack.pack_id) is not str or not pack.pack_id or type(pack.version) is not int or pack.version<1:
        raise ValueError('Invalid pack identity')
    if type(pack.cards) is not tuple or len(pack.cards)<40 or type(pack.leaders) is not tuple or not pack.leaders:
        raise ValueError('Pack needs at least forty cards and reserve identities')
    if any(type(c) is not PackCard or type(c.name) is not str or not c.name.strip() or type(c.definition) is not CardDefinition or c.color not in ('Generic','Gold','Green','Silver') for c in pack.cards):
        raise ValueError('Invalid practice card metadata')
    keys=[c.definition.key for c in pack.cards]
    if len(set(keys))!=len(keys) or len({c.name for c in pack.cards})!=len(pack.cards):
        raise ValueError('Duplicate card key/name')
    if any(type(l) is not ReserveIdentity or type(l.key) is not str or not l.key or type(l.name) is not str or not l.name.strip() or l.color not in ('Gold','Green','Silver') for l in pack.leaders) or len({l.key for l in pack.leaders})!=len(pack.leaders):
        raise ValueError('Invalid reserve identity')
    # Reuse engine content validation rather than maintaining a second effect grammar.
    new_match(tuple(MatchPlayer(DrawPlayer(p,30,(),())) for p in ('A','B')),(),(),RefillPolicy(20,1),
              active_player='A',card_definitions=tuple(c.definition for c in pack.cards))
    return pack


def pack_hash(pack):
    return hashlib.sha256(json.dumps(asdict(pack),sort_keys=True,separators=(',',':')).encode()).hexdigest()
