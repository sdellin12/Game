"""Directed Salvage Battery hand-pressure cases through real engine commands."""
import json
from crucible_content.practice import practice_pack
from crucible_core.cards import CardInstance
from crucible_core.match import MatchPlayer,EffectSpec,DrawCards,RecoverDiscardCard,new_match,queue_effect
from crucible_core.turns import DrawPlayer,RefillPolicy
from crucible_core.resources import ResourcePool
from crucible_core.views import project_match
from crucible_core.commands import route_command


def command(s,actor,kind,**args):return route_command(s,actor,{'kind':kind,'args':args,'expected_revision':s.revision})


def round_pass(s):
    for _ in s.priority.seats:s=command(s,s.priority.holder,'pass')
    return s


def pressure_case(players=2,excess=1,mode='draw'):
    if type(players) is not int or players not in (2,3,4) or type(excess) is not int or excess not in (1,2,3) or mode not in ('draw','recover'):raise ValueError('Unsupported pressure fixture')
    pack=practice_pack();source=next(c.definition for c in pack.cards if c.definition.key=='beacon-02')
    rows=[];instances=[]
    for actor in 'ABCD'[:players]:
        owned=tuple(CardInstance('battery' if actor=='A' and c.definition.key=='beacon-02' else actor+'-'+c.definition.key,c.definition.key,actor) for c in pack.cards)
        cards=tuple(c.instance_id for c in owned if c.definition_key.startswith('unit-'))
        instances.extend(owned)
        if actor=='A':
            hand=('battery',)+cards[:7];discard=cards[7:7+excess] if mode=='recover' else ()
            deck=tuple(c.instance_id for c in owned if c.instance_id not in hand+discard)
        else:hand=();discard=();deck=tuple(c.instance_id for c in owned)
        rows.append(MatchPlayer(DrawPlayer(actor,30,deck,discard,hand),resources=ResourcePool(available=10)))
    steps=(DrawCards('A',excess),) if mode=='draw' else tuple(RecoverDiscardCard(i) for i in rows[0].cards.discard)
    s=new_match(tuple(rows),(),(EffectSpec('pressure','A',steps),),RefillPolicy(20,1),active_player='A',
        card_definitions=tuple(c.definition for c in pack.cards),card_instances=tuple(instances),shuffle_seed=b'pressure-fixture-1234')
    s=command(s,'A','play_card',card_id='battery',payment={'ordinary':source.cost,'token_ids':[]});s=round_pass(s)
    s=round_pass(queue_effect(s,'A','pressure',expected_revision=s.revision))
    s=round_pass(command(s,'A','end_turn'));choice=project_match(s,'A')['you']['choice']
    selected=[c['instance_id'] for c in project_match(s,'A')['you']['hand'][:choice['count']]]
    s=command(s,'A','end_discard',cards=selected)
    if s.triggers:s=command(s,'A','trigger_order',order=[t['trigger_id'] for t in project_match(s,'A')['you']['choice']['triggers']])
    queued=len(s.priority.chain)
    for _ in range(queued):s=round_pass(s)
    owner=next(p for p in s.players if p.cards.player_id=='A')
    if s.turn.active_player=='A':s=round_pass(s)
    retained=next(p.resources.available for p in s.players if p.cards.player_id=='A')
    observed=sum(e.kind=='card_discarded' for e in s.events)
    return {'players':players,'excess':excess,'mode':mode,'discarded':observed,'queued':queued,
        'hand_count':len(owner.cards.hand),'available':owner.resources.available,
        'retained_after_turn':retained,'expected_available':10-source.cost+excess,'passed':observed==excess and queued==excess and len(owner.cards.hand)==7 and owner.resources.available==10-source.cost+excess and retained==owner.resources.available and s.turn.active_player!='A'}


def evaluate():
    rows=[pressure_case(p,n,m) for p in (2,3,4) for n in (1,2,3) for m in ('draw','recover')]
    return {'cases':len(rows),'passed':sum(r['passed'] for r in rows),'results':rows}


def main():
    report=evaluate();print(json.dumps(report,indent=2));return 0 if report['passed']==report['cases'] else 2


if __name__=='__main__':raise SystemExit(main())
