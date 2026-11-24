"""Finite equal-cost public boards; no deployment or policy simulation."""
from dataclasses import replace
from itertools import combinations, combinations_with_replacement, permutations, product
from crucible_core import Attack, CombatError, CombatState, Creature, Player, Shield
from .cli import encode, profiles


def creature_groups(budget=3):
    if type(budget) is not int or not 1 <= budget <= 3:
        raise CombatError('group budget must be an integer from 1 to 3')
    pack = profiles()['profiles']
    for width in range(1, budget + 1):
        for group in combinations_with_replacement(pack, width):
            if sum(p['cost'] for p in group) == budget:
                yield group


def blocker_assignments(attackers, defenders):
    # -1 means unassigned. Permutations cover attacker-selected blocker orders.
    seen = set()
    for targets in product(range(-1, attackers), repeat=defenders):
        for order in permutations(range(defenders)):
            assignment = tuple(tuple(i for i in order if targets[i] == a)
                               for a in range(attackers))
            if assignment not in seen:
                seen.add(assignment)
                yield assignment


CONDITIONS = ('baseline', 'wounded', 'exhausted', 'shielded', 'mixed')


def board_variants(creatures, condition):
    if condition == 'mixed':
        options = []
        for c in creatures:
            states = [c, replace(c, health=1)]
            if c.controller == 'B':
                states.extend([replace(c, exhausted=True),
                               replace(c, shields=(Shield(f'{c.instance_id}-shield', 2),))])
            options.append(tuple(dict.fromkeys(states)))
        yield from product(*options)
    elif condition == 'wounded':
        yield tuple(replace(c, health=1) for c in creatures)
    elif condition == 'exhausted':
        yield tuple(replace(c, exhausted=c.controller == 'B') for c in creatures)
    elif condition == 'shielded':
        yield tuple(replace(c, shields=(Shield(f'{c.instance_id}-shield', 2),))
                    if c.controller == 'B' else c for c in creatures)
    else:
        yield creatures


def group_scenarios(budget=3, condition='baseline', attack_mode='all'):
    if condition not in CONDITIONS:
        raise CombatError('unsupported group condition')
    if attack_mode not in ('all', 'subsets'):
        raise CombatError('attack mode must be all or subsets')
    if condition == 'mixed' and (type(budget) is not int or budget > 2):
        raise CombatError('mixed conditions are bounded to budgets 1–2')
    groups = list(creature_groups(budget))
    for attackers in groups:
        for defenders in groups:
            base = tuple(Creature(f'{side}{i}', side, p['attack'], p['health'], p['health'])
                         for side, group in [('A', attackers), ('B', defenders)]
                         for i, p in enumerate(group))
            for variant, creatures in enumerate(board_variants(base, condition)):
                selections = [tuple(range(len(attackers)))] if attack_mode == 'all' else [
                    selected for size in range(len(attackers) + 1)
                    for selected in combinations(range(len(attackers)), size)]
                for selected in selections:
                    for assignment in blocker_assignments(len(selected), len(defenders)):
                        attacks = tuple(Attack(f'A{attacker}', 'B', tuple(f'B{j}' for j in blockers))
                                        for attacker, blockers in zip(selected, assignment))
                        label = lambda group: '+'.join(p['id'] for p in group)
                        name = (f'budget={budget}; cards/width={len(attackers)}/{len(defenders)}; '
                                f'unused=0/0; {label(attackers)} attacks {label(defenders)}; '
                                f'blocks={assignment}; full HP; ready; no shields; deployment unmodeled')
                        if condition != 'baseline':
                            descriptions = {'wounded': 'all creatures at 1 HP; ready; no shields',
                                            'exhausted': 'full HP; all defenders exhausted; no shields',
                                            'shielded': 'full HP; ready; each defender has 2 prevention',
                                            'mixed': f'mixed board variant {variant}; inspect individual state'}
                            name = name.replace('full HP; ready; no shields', descriptions[condition])
                        if attack_mode == 'subsets':
                            name += '; attacking=' + (','.join(f'A{i}' for i in selected) or 'none')
                        yield encode(CombatState((Player('A'), Player('B')), creatures), attacks, name)
