"""Compare exact combat outcomes against a trusted local Git baseline."""
import argparse
from dataclasses import asdict
from itertools import chain
from pathlib import Path
import subprocess
import sys
import types

from crucible_core.combat import resolve_combat
from crucible_sim.cli import matrix_scenarios, decode
from crucible_sim.groups import group_scenarios


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',default='2458747',help='trusted local Git commit')
    args=parser.parse_args()
    old=types.ModuleType('prior_combat')
    sys.modules[old.__name__]=old
    root=Path(__file__).resolve().parents[1]
    source=subprocess.run(['git','show',f'{args.baseline}:src/crucible_core/combat.py'],
                          cwd=root,capture_output=True,check=True).stdout.decode('utf-8')
    exec(compile(source,'prior_combat.py','exec'),old.__dict__)
    count=0
    for scenario in chain(matrix_scenarios(),group_scenarios(2,'mixed','subsets')):
        state,attacks,orders=decode(scenario)
        oldstate=old.CombatState(tuple(old.Player(**asdict(p)) for p in state.players),
            tuple(old.Creature(**{**asdict(c),'shields':tuple(old.Shield(**asdict(s)) for s in c.shields)}) for c in state.creatures))
        expected=asdict(old.resolve_combat(oldstate,tuple(old.Attack(**asdict(a)) for a in attacks),orders))
        actual=asdict(resolve_combat(state,attacks,orders))
        if expected!=actual:
            raise AssertionError(f"Combat changed: {scenario['name']}")
        count+=1
    print(f'{count} exact outcomes match {args.baseline} combat kernel')


if __name__=='__main__':
    main()
