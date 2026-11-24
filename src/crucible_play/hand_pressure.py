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


def pressure_case(players=2,excess=1,mode='draw',*,source_key='beacon-02',decisions=None):
    if type(players) is not int or players not in (2,3,4) or type(excess) is not int or excess not in (1,2,3) or mode not in ('draw','recover'):raise ValueError('Unsupported pressure fixture')
    if source_key not in ('beacon-02','beacon-03'):raise ValueError('Unsupported pressure source')
    archive=source_key=='beacon-03'
    decisions=tuple(True for _ in range(excess)) if decisions is None else decisions
    if type(decisions) is not tuple or len(decisions)!=excess or any(type(x) is not bool for x in decisions):raise ValueError('Expected one boolean decision per discard')
    pack=practice_pack();source=next(c.definition for c in pack.cards if c.definition.key==source_key)
    rows=[];instances=[]
    for actor in 'ABCD'[:players]:
        owned=tuple(CardInstance('battery' if actor=='A' and c.definition.key==source_key else actor+'-'+c.definition.key,c.definition.key,actor) for c in pack.cards)
        cards=tuple(c.instance_id for c in owned if c.definition_key.startswith('unit-'))
        instances.extend(owned)
        if actor=='A':
            opening=7 if players==2 else 6
            hand=('battery',)+cards[:opening];discard=cards[opening:opening+excess] if mode=='recover' else ()
            deck=tuple(c.instance_id for c in owned if c.instance_id not in hand+discard)
        else:hand=();discard=();deck=tuple(c.instance_id for c in owned)
        rows.append(MatchPlayer(DrawPlayer(actor,30,deck,discard,hand),resources=ResourcePool(natural_capacity=10)))
    steps=(DrawCards('A',excess),) if mode=='draw' else tuple(RecoverDiscardCard(i) for i in rows[0].cards.discard)
    s=new_match(tuple(rows),(),(EffectSpec('pressure','A',steps),),RefillPolicy(20,1),active_player='A',
        card_definitions=tuple(c.definition for c in pack.cards),card_instances=tuple(instances),shuffle_seed=b'pressure-fixture-1234',managed_turns=True,phase='Start')
    while s.turn.phase!='MainBefore':s=round_pass(s)
    s=command(s,'A','play_card',card_id='battery',payment={'ordinary':source.cost,'token_ids':[]});s=round_pass(s)
    s=round_pass(queue_effect(s,'A','pressure',expected_revision=s.revision))
    s=round_pass(command(s,'A','end_turn'));choice=project_match(s,'A')['you']['choice']
    selected=[c['instance_id'] for c in project_match(s,'A')['you']['hand'][:choice['count']]]
    s=command(s,'A','end_discard',cards=selected)
    if archive:
        for use in decisions:
            choice=project_match(s,'A')['you']['choice']
            s=command(s,'A','trigger_choice',trigger_id=choice['trigger_id'],use=use)
    if s.triggers:s=command(s,'A','trigger_order',order=[t['trigger_id'] for t in project_match(s,'A')['you']['choice']['triggers']])
    queued=len(s.priority.chain)
    for _ in range(queued):s=round_pass(s)
    owner=next(p for p in s.players if p.cards.player_id=='A')
    if s.turn.active_player=='A':s=round_pass(s)
    retained=next(p.resources.available for p in s.players if p.cards.player_id=='A')
    observed=sum(e.kind=='card_discarded' for e in s.events)
    if archive:
        for _ in range(200):
            if s.turn.active_player=='A' and s.turn.phase=='Start':break
            if s.priority.status=='closed':s=command(s,s.turn.active_player,'declare_attacks',attacks=[])
            else:s=command(s,s.priority.holder,'pass')
        else:raise RuntimeError('Next own Start was not reached')
        refilled=next(p.resources.available for p in s.players if p.cards.player_id=='A')
        accepted=sum(decisions)
        return {'players':players,'excess':excess,'mode':mode,'decisions':decisions,'discarded':observed,'queued':queued,
            'available_before_refill':owner.resources.available,'permanent_bonus':owner.resources.permanent_bonus,
            'next_start_available':refilled,'passed':observed==excess and queued==accepted and len(owner.cards.hand)==7
            and owner.resources.available==10-source.cost and owner.resources.permanent_bonus==accepted and refilled==11+accepted}
    return {'players':players,'excess':excess,'mode':mode,'discarded':observed,'queued':queued,
        'hand_count':len(owner.cards.hand),'available':owner.resources.available,
        'retained_after_turn':retained,'expected_available':10-source.cost+excess,'passed':observed==excess and queued==excess and len(owner.cards.hand)==7 and owner.resources.available==10-source.cost+excess and retained==owner.resources.available and s.turn.active_player!='A'}


def evaluate():
    rows=[pressure_case(p,n,m) for p in (2,3,4) for n in (1,2,3) for m in ('draw','recover')]
    return {'cases':len(rows),'passed':sum(r['passed'] for r in rows),'results':rows}


def evaluate_archive():
    rows=[pressure_case(p,n,m,source_key='beacon-03',decisions=d) for p in (2,3,4) for n in (1,2,3)
          for m in ('draw','recover') for d in ((True,)*n,(False,)*n,tuple(i%2==0 for i in range(n)))]
    return {'cases':len(rows),'passed':sum(r['passed'] for r in rows),'results':rows}


def main():
    reports={'salvage':evaluate(),'archive':evaluate_archive()};print(json.dumps(reports,indent=2));return 0 if all(r['passed']==r['cases'] for r in reports.values()) else 2


if __name__=='__main__':raise SystemExit(main())
