"""Pure session-bound command adapter. Transport authentication/persistence is external."""
from dataclasses import replace
import hashlib
import random
from .combat import Attack
from .resources import Payment
from . import match as engine


class CommandError(ValueError):
    pass


def _fields(value, required, optional=()):
    if type(value) is not dict or not set(required)<=set(value) or set(value)-set(required)-set(optional):
        raise CommandError('invalid command fields')


def _ids(value, integer=False):
    kind=int if integer else str
    if type(value) is not list or any(type(i) is not kind or (i<1 if integer else not i) for i in value):
        raise CommandError('invalid ID list')
    return tuple(value)


def _payment(value):
    _fields(value,('ordinary','token_ids'))
    if type(value['ordinary']) is not int or value['ordinary']<0:raise CommandError('invalid payment')
    return Payment(value['ordinary'],_ids(value['token_ids']))


def route_command(state, session_actor, command):
    """Returns server-only next state. Send project_match(next_state, actor) to clients."""
    if type(session_actor) is not str or session_actor not in engine._living(state):
        raise CommandError('session cannot act')
    _fields(command,('kind','expected_revision','args'))
    kind=command['kind'];revision=command['expected_revision'];args=command['args']
    if type(kind) is not str or type(revision) is not int or revision!=state.revision:
        raise CommandError('invalid/stale command')
    actor=session_actor
    try:
        if kind in ('pass','end_turn'):
            _fields(args,())
            if kind=='end_turn' and (state.turn.phase not in ('MainBefore','MainAfter') or engine._blocked(state)
                    or state.priority is None or state.priority.status!='priority' or state.priority.holder!=actor or state.priority.chain):
                raise CommandError('command unavailable')
            action=engine.pass_match if kind=='pass' else engine.request_match_end
            result=action(state,actor,expected_revision=revision)
        elif kind=='concede':
            _fields(args,('confirmed',))
            if args['confirmed'] is not True:raise CommandError('confirmation required')
            result=engine.concede(state,actor,expected_revision=revision)
        elif kind=='activate':
            _fields(args,('key','payment'))
            if type(args['key']) is not str:raise CommandError('invalid ability key')
            result=engine.submit_action(state,actor,args['key'],_payment(args['payment']),expected_revision=revision)
        elif kind=='declare_attacks':
            _fields(args,('attacks',))
            if type(args['attacks']) is not list:raise CommandError('invalid attacks')
            attacks=[]
            for a in args['attacks']:
                _fields(a,('attacker_id','target_player'),('challenge_target',))
                if any(type(a[k]) is not str or not a[k] for k in a):raise CommandError('invalid attack ID')
                attacks.append(Attack(a['attacker_id'],a['target_player'],challenge_target=a.get('challenge_target')))
            result=engine.declare_match_attacks(state,actor,tuple(attacks),expected_revision=revision)
        elif kind=='lock_blockers':
            _fields(args,('assignments',))
            if type(args['assignments']) is not list:raise CommandError('invalid blockers')
            assignments=[]
            for item in args['assignments']:
                _fields(item,('attacker_id','blockers'))
                if type(item['attacker_id']) is not str:raise CommandError('invalid attacker')
                assignments.append((item['attacker_id'],_ids(item['blockers'])))
            result=engine.lock_match_blockers(state,actor,tuple(assignments),expected_revision=revision)
        elif kind=='combat_order':
            _fields(args,('subject','order'))
            if type(args['subject']) is not str:raise CommandError('invalid order subject')
            result=engine.choose_match_combat_order(state,actor,args['subject'],_ids(args['order']),expected_revision=revision)
        elif kind=='trigger_order':
            _fields(args,('order',))
            result=engine.choose_trigger_order(state,actor,_ids(args['order'],True),expected_revision=revision)
        elif kind=='end_discard':
            _fields(args,('cards',))
            result=engine.choose_end_discards(state,actor,_ids(args['cards']),expected_revision=revision)
        elif kind=='refill':
            _fields(args,('pay','request_id'))
            if type(args['pay']) is not bool or type(args['request_id']) is not int:raise CommandError('invalid refill choice')
            engine._check(state,revision)
            draw=state.pending.draw if state.pending else None
            if draw is None or draw.player.player_id!=actor or draw.request_id!=args['request_id']:
                raise CommandError('command unavailable')
            shuffled=()
            if args['pay']:
                if state.shuffle_seed is None:raise CommandError('server shuffle seed required')
                digest=hashlib.sha256(state.shuffle_seed+str(state.shuffle_counter).encode()).digest()
                cards=list(draw.player.discard)
                random.Random(digest).shuffle(cards)
                shuffled=tuple(cards)
            result=engine.choose_refill(state,actor,pay=args['pay'],shuffled_discard=shuffled,
                                       expected_request_id=args['request_id'],expected_revision=revision)
            if args['pay']:result=replace(result,shuffle_counter=state.shuffle_counter+1)
        elif kind=='summon_leader':
            _fields(args,('payment',))
            result=engine.summon_leader(state,actor,_payment(args['payment']),expected_revision=revision)
        elif kind=='leader_ability':
            _fields(args,('key','payment'),('target',))
            if type(args['key']) is not str or ('target' in args and type(args['target']) is not str):raise CommandError('invalid leader ability')
            result=engine.activate_leader(state,actor,args['key'],_payment(args['payment']),target=args.get('target'),expected_revision=revision)
        elif kind=='play_card':
            _fields(args,('card_id','payment'),('target',))
            if type(args['card_id']) is not str or ('target' in args and type(args['target']) is not str):
                raise CommandError('invalid card/target')
            result=engine.play_card(state,actor,args['card_id'],_payment(args['payment']),target=args.get('target'),expected_revision=revision)
        else:
            raise CommandError('unknown player command')
        # Selecting a chain item is server work, never an exposed "resolve anything" command.
        if result.priority and result.priority.status=='resolving' and result.pending is None:
            result=engine.resolve_current(result,expected_revision=result.revision)
        engine.validate_match(result)
        return result
    except (engine.MatchError,ValueError) as exc:
        if isinstance(exc,CommandError):raise
        raise CommandError('command unavailable') from None
