"""Versioned, engine-validated practice content; separate from the household catalog."""
from dataclasses import dataclass, asdict
import hashlib
import json
from crucible_core.leaders import LeaderAbility, LeaderDefinition
from crucible_core.cards import CardDefinition,TriggeredAbility
from crucible_core.match import (DamagePlayer, HealPlayer, DrawCards, DestroyCreature, ReturnCreatureToHand, ExileCreature, RecoverDiscardCard,
    GrantResources, GrantCapacity, NegateEffect, GrantShield, MatchPlayer, new_match)
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
    definition: LeaderDefinition


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
        ('Unravel','reaction',3,(ReturnCreatureToHand('$target'),),'creature','enemy'),
        ('Quiet Repair','action',4,(HealPlayer('$controller',4),),None,'any'),
        ('Fresh Inspiration','action',2,(DrawCards('$controller',1),),None,'any'),
        ('Banish','action',6,(ExileCreature('$target'),),'creature','enemy'),
        ('Brace for Impact','reaction',2,(GrantShield('$target',3),),'creature','friendly'),
        ('Enduring Ward','reaction',3,(GrantShield('$target',2,'next_start','$controller'),),'creature','friendly'),
        ('Interrupt','reaction',3,(NegateEffect('$target'),),'effect','enemy'),
        ('Second Chance','action',3,(RecoverDiscardCard('$target'),),'discard','friendly'),
        ('Lasting Growth','action',4,(GrantCapacity('$controller',1),),None,'any'),
    )
    for i,(name,kind,cost,steps,target,relation) in enumerate(spells):
        cards.append(PackCard(name,'Generic',CardDefinition(f'spell-{i+1:02}',kind,cost,steps,target_kind=target,target_relation=relation)))
    for i,name in enumerate(("Scholar's Lantern",'Salvage Battery','Archive Well','Beacon Tower','Sun Engine','Crystal Reservoir')):
        triggers=(TriggeredAbility('insight' if i==0 else 'salvage','card_drawn' if i==0 else 'card_discarded',(GrantResources('$controller',1),),optional=i==0),) if i<2 else ()
        if i==2:triggers=(TriggeredAbility('archive','card_discarded',(GrantCapacity('$controller',1),),optional=True),)
        cards.append(PackCard(name,'Generic',CardDefinition(f'beacon-{i+1:02}','permanent',4 if i<2 else 5,capacity_bonus=1 if i<3 else 2,triggered_abilities=triggers)))
    return validate_pack(PracticePack('crucible-practice',9,tuple(cards),(
        ReserveIdentity('core-gold','Aster, Practice Core','Gold',LeaderDefinition('core-gold','Aster, Practice Core','Gold',4,3,5,
            LeaderAbility('core-repair',3,(HealPlayer('$controller',3),)),
            LeaderAbility('guiding-bolt',2,(DamagePlayer('$target',1),),target_kind='player',target_relation='enemy',exhaust_source=True))),
        ReserveIdentity('core-green','Moss, Practice Core','Green',LeaderDefinition('core-green','Moss, Practice Core','Green',4,2,6,
            LeaderAbility('root-memory',4,(GrantCapacity('$controller',1),)),
            LeaderAbility('renewal',2,(HealPlayer('$controller',2),)))),
        ReserveIdentity('core-silver','Gear, Practice Core','Silver',LeaderDefinition('core-silver','Gear, Practice Core','Silver',4,4,4,
            LeaderAbility('scouting-lens',3,(DrawCards('$controller',1),)),
            LeaderAbility('overload',3,(DamagePlayer('$target',3),),target_kind='player',target_relation='enemy',exhaust_source=True))))))


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
    if any(type(l.definition) is not LeaderDefinition or (l.key,l.name,l.color)!=(l.definition.key,l.definition.name,l.definition.color) for l in pack.leaders):
        raise ValueError('Leader identity/definition mismatch')
    # Reuse engine content validation rather than maintaining a second effect grammar.
    new_match(tuple(MatchPlayer(DrawPlayer(p,30,(),())) for p in ('A','B')),(),(),RefillPolicy(20,1),
              active_player='A',card_definitions=tuple(c.definition for c in pack.cards),leader_definitions=tuple(l.definition for l in pack.leaders))
    return pack


def pack_hash(pack):
    def normalized(value):
        if isinstance(value,dict):return {k:normalized(v) for k,v in value.items() if not ((k=='triggered_abilities' and v==()) or (k=='optional' and v is False))}
        if isinstance(value,(tuple,list)):return [normalized(v) for v in value]
        return value
    data=asdict(pack)
    # Old resource-only authored packs retain their original hashes. asdict loses
    # instruction types, so distinguish the newly admitted, same-shaped rewards.
    for card,encoded in zip(pack.cards,data['cards']):
        for ability,encoded_ability in zip(card.definition.triggered_abilities,encoded['definition']['triggered_abilities']):
            for step,encoded_step in zip(ability.steps,encoded_ability['steps']):
                if type(step) in (HealPlayer,GrantCapacity):encoded_step['instruction']=type(step).__name__
    return hashlib.sha256(json.dumps(normalized(data),sort_keys=True,separators=(',',':')).encode()).hexdigest()
