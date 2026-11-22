"""Finite equal-cost public boards; no deployment or policy simulation."""
from itertools import combinations_with_replacement, permutations, product
from crucible_core import Attack, CombatError, CombatState, Creature, Player
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


def group_scenarios(budget=3):
    groups = list(creature_groups(budget))
    for attackers in groups:
        for defenders in groups:
            creatures = tuple(Creature(f'{side}{i}', side, p['attack'], p['health'], p['health'])
                              for side, group in [('A', attackers), ('B', defenders)]
                              for i, p in enumerate(group))
            for assignment in blocker_assignments(len(attackers), len(defenders)):
                attacks = tuple(Attack(f'A{i}', 'B', tuple(f'B{j}' for j in blockers))
                                for i, blockers in enumerate(assignment))
                label = lambda group: '+'.join(p['id'] for p in group)
                name = (f'budget={budget}; cards/width={len(attackers)}/{len(defenders)}; '
                        f'unused=0/0; {label(attackers)} attacks {label(defenders)}; '
                        f'blocks={assignment}; full HP; ready; no shields; deployment unmodeled')
                yield encode(CombatState((Player('A'), Player('B')), creatures), attacks, name)
