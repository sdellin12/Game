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
from crucible_core.match import ReturnCreatureToHand,NegateEffect


@dataclass(frozen=True)
class Scenario:
    name: str
    state: object
    expected_target: str | None


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
        expected=('pass',{}) if case.expected_target is None else ('play_card',{'card_id':'unravel-card','target':case.expected_target,'payment':{'ordinary':3,'token_ids':[]}})
        rows.append({'scenario':case.name,'passed':legal and move==expected,'legal':legal,'move':move})
    return {'cases':len(rows),'passed':sum(r['passed'] for r in rows),'legal':sum(r['legal'] for r in rows),'results':rows}


def main():
    report=evaluate();print(json.dumps(report,indent=2))
    return 0 if report['passed']==report['cases'] else 2


if __name__=='__main__':raise SystemExit(main())
