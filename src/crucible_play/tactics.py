"""Bounded, reproducible Unravel decision checks using real engine projections."""
from dataclasses import dataclass,replace
import json
from crucible_core.cards import CardDefinition,CardInstance
from crucible_core.combat import Creature
from crucible_core.match import MatchObject,MatchPlayer,EffectSpec,DestroyCreature,new_match,queue_effect
from crucible_core.turns import DrawPlayer,RefillPolicy
from crucible_core.resources import ResourcePool
from crucible_core.commands import route_command
from crucible_core.views import project_match
from crucible_play.opponent import choose_move
from crucible_core.match import ReturnCreatureToHand,NegateEffect,GrantShield


@dataclass(frozen=True)
class Scenario:
    name: str
    state: object
    expected_target: str | None
    expected_card: str = 'unravel-card'
    ordinary: int = 3
    tokens: tuple = ()
    removes: bool = True


def command(state,actor,kind,**args):
    return route_command(state,actor,{'kind':kind,'args':args,'expected_revision':state.revision})


def round_pass(state):
    for _ in state.priority.seats:state=command(state,state.priority.holder,'pass')
    return state


def creature(identity,owner,attack,health,*,token=False,keywords=()):
    return MatchObject(identity,owner,owner,'creature_token' if token else 'creature',Creature(identity,owner,attack,health,health,keywords=keywords))


def fixture(objects,*,active='A',phase='MainBefore',effects=()):
    spell=CardDefinition('unravel','reaction',3,(ReturnCreatureToHand('$target'),),target_kind='creature',target_relation='enemy')
    definitions=[spell];instances=[CardInstance('unravel-card','unravel','A')]
    for obj in objects:
        if obj.kind=='creature_token':continue
        c=obj.creature;key='printed-'+obj.object_id
        definitions.append(CardDefinition(key,'creature',2,attack=c.attack,health=c.max_health,keywords=c.keywords))
        instances.append(CardInstance(obj.object_id,key,obj.owner))
    players=tuple(MatchPlayer(DrawPlayer(p,30,tuple(p+str(i) for i in range(8)),(),('unravel-card',) if p=='A' else ()),resources=ResourcePool(available=3)) for p in 'ABC')
    return new_match(players,tuple(objects),effects,RefillPolicy(20,1),active_player=active,phase=phase,
        card_definitions=tuple(definitions),card_instances=tuple(instances),shuffle_seed=b'tactical-check-seed-1234')


def attack_window(target='A',*,final=False,breakthrough=False,active='B'):
    attacker=creature('attacker',active,5,5,keywords=('breakthrough',) if breakthrough else ())
    defender=target
    objs=[attacker,creature('idle-giant','C',9,9)]
    if final:objs.append(creature('blocker',defender,1,1 if breakthrough else 20))
    s=fixture(objs,active=active,phase='Combat');s=round_pass(s)
    s=command(s,active,'declare_attacks',attacks=[{'attacker_id':'attacker','target_player':target}])
    if final:
        s=round_pass(s)
        s=command(s,defender,'lock_blockers',assignments=[{'attacker_id':'attacker','blockers':['blocker']}])
    while s.priority.holder!='A':s=command(s,s.priority.holder,'pass')
    return s


def scenarios():
    s=fixture([creature('token','B',2,2,token=True),creature('idle-giant','C',9,9)])
    yield Scenario('remove-token-instead-of-replayable-idle-body',s,'token')
    s=fixture([creature('already-marked','B',5,5)],active='B',effects=(EffectSpec('removal','B',(DestroyCreature('already-marked'),)),))
    s=queue_effect(s,'B','removal',expected_revision=s.revision);s=command(s,'C','pass')
    yield Scenario('avoid-duplicating-pending-removal',s,None)
    yield Scenario('stop-attacker-threatening-self',attack_window(),'attacker')
    yield Scenario('hold-during-other-players-fight',attack_window('C'),None)
    yield Scenario('hold-when-safe-block-already-stops-player-damage',attack_window(final=True),None)
    yield Scenario('stop-breakthrough-through-small-blocker',attack_window(final=True,breakthrough=True),'attacker')
    yield Scenario('remove-blocker-for-own-breakthrough',attack_window('B',final=True,breakthrough=True,active='A'),'blocker')
    yield Scenario('hold-against-zero-attack-body-with-no-own-attackers',fixture([creature('wall','B',0,4)]),None)
    yield from chain_scenarios()
    yield from resource_scenarios()


def resource_scenarios():
    def final(objects,attacks,locks,*,health=5,available=3,ward=False,token=False):
        s=fixture(objects,active='B',phase='Combat');s=round_pass(s)
        s=command(s,'B','declare_attacks',attacks=attacks);s=round_pass(s)
        s=command(s,'A','lock_blockers',assignments=locks)
        if ward:
            d=CardDefinition('ward','reaction',2,(GrantShield('$target',5),),target_kind='creature',target_relation='friendly')
            s=replace(s,card_definitions=s.card_definitions+(d,),card_instances=s.card_instances+(CardInstance('ward-card','ward','A'),))
        s=replace(s,players=tuple(replace(p,cards=replace(p.cards,health=health,hand=p.cards.hand+(('ward-card',) if ward else ())),resources=replace(p.resources,available=available)) if p.cards.player_id=='A' else p for p in s.players))
        if token:s=replace(s,battlefield=s.battlefield+(MatchObject('token-A','A','A','resource_token',resource_value=2),MatchObject('token-C','C','C','resource_token',resource_value=5)))
        while s.priority.holder!='A':s=command(s,s.priority.holder,'pass')
        return s
    def attack(i,challenge=None):return {'attacker_id':i,'target_player':'A',**({'challenge_target':challenge} if challenge else {})}
    def lock(i,guards=()):return {'attacker_id':i,'blockers':list(guards)}
    bodies=[creature('challenger','B',9,9,keywords=('challenge',)),creature('lethal','B',3,3),creature('protected','A',1,20)]
    s=final(bodies,[attack('challenger','protected'),attack('lethal')],[lock('lethal')],health=3)
    yield Scenario('save-player-before-large-challenge-target',s,'lethal')
    bodies=[creature('blocked','B',9,9),creature('lethal','B',4,4),creature('guard','A',1,20)]
    yield Scenario('ignore-large-safely-blocked-attacker',final(bodies,[attack('blocked'),attack('lethal')],[lock('blocked',('guard',)),lock('lethal')],health=4),'lethal')
    bodies=[creature('large','B',5,5),creature('small','B',3,3)]
    yield Scenario('spend-one-removal-to-survive-total-unblocked-damage',final(bodies,[attack('large'),attack('small')],[lock('large'),lock('small')]),'large')
    bodies=[creature('blocked','B',9,9),creature('overflow','B',5,5,keywords=('breakthrough',)),creature('safe-guard','A',1,20),creature('small-guard','A',0,1)]
    for available in (3,2):
        s=final(bodies,[attack('blocked'),attack('overflow')],[lock('blocked',('safe-guard',)),lock('overflow',('small-guard',))],ward=True,available=available,health=4)
        yield Scenario(f'use-cheaper-effective-ward-with-{available}-resources',s,'small-guard','ward-card',2,(),False)
    bodies=[creature('lethal','B',5,5),creature('small','B',1,1),creature('idle','A',9,9)]
    yield Scenario('reserve-bounce-instead-of-useless-cheap-ward',final(bodies,[attack('lethal'),attack('small')],[lock('lethal'),lock('small')],ward=True),'lethal')
    yield Scenario('combine-exact-owned-token-payment-for-lethal-threat',final(bodies,[attack('lethal'),attack('small')],[lock('lethal'),lock('small')],available=1,token=True),'lethal','unravel-card',1,('token-A',))


def chain_scenarios():
    # A's next priority must distinguish removal from countered removal.
    for depth,move_type in tuple((n,DestroyCreature) for n in range(5))+((1,ReturnCreatureToHand),):
        s=attack_window();controller=s.priority.holder
        key='remove-attacker';s=replace(s,effects=s.effects+(EffectSpec(key,controller,(move_type('attacker'),)),))
        s=queue_effect(s,controller,key,expected_revision=s.revision)
        previous=s.priority.chain[-1].effect_id
        for index in range(depth):
            actor=s.priority.holder;key=f'counter-{index}'
            s=replace(s,effects=s.effects+(EffectSpec(key,actor,(NegateEffect(previous),)),))
            s=queue_effect(s,actor,key,expected_revision=s.revision);previous=s.priority.chain[-1].effect_id
        while s.priority.holder!='A':s=command(s,s.priority.holder,'pass')
        yield Scenario(f'{move_type.__name__}-with-{depth}-nested-negates',s,'attacker' if depth%2 else None)


def evaluate(policy=choose_move):
    rows=[]
    for case in scenarios():
        view=project_match(case.state,'A');move=policy(view)
        legal=True
        try:
            if move is None:legal=False
            else:command(case.state,'A',move[0],**move[1])
        except ValueError:legal=False
        expected=('pass',{}) if case.expected_target is None else ('play_card',{'card_id':case.expected_card,'target':case.expected_target,'payment':{'ordinary':case.ordinary,'token_ids':list(case.tokens)}})
        rows.append({'scenario':case.name,'passed':legal and move==expected,'legal':legal,'move':move})
    return {'cases':len(rows),'passed':sum(r['passed'] for r in rows),'legal':sum(r['legal'] for r in rows),'results':rows}


def main():
    report=evaluate();print(json.dumps(report,indent=2))
    return 0 if report['passed']==report['cases'] else 2


if __name__=='__main__':raise SystemExit(main())
