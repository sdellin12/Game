"""Descriptive ranges across enumerated combat choices, never win estimates."""
from collections import defaultdict
import json


def comparison_summary(records):
    groups = defaultdict(list)
    for record in records:
        scenario = record['input']
        # Preserve wounds, readiness, shields and keywords as distinct boards.
        key = json.dumps({'state': scenario['state'],
                          'attackers': sorted(a['attacker_id'] for a in scenario['attacks'])}, sort_keys=True)
        groups[key].append(record)
    rows = []
    for key, records in sorted(groups.items()):
        first = records[0]['input']
        creatures = first['state']['creatures']
        attackers = {a['attacker_id'] for a in first['attacks']}
        sides = {c['controller'] for c in creatures if c['instance_id'] in attackers}
        if len(sides) != 1:
            continue  # Multi-controller attacks need a separate presentation.
        attacking_side = next(iter(sides))
        friendly = [c for c in creatures if c['controller'] == attacking_side]
        opposing = [c for c in creatures if c['controller'] != attacking_side]
        def board(cards):
            def label(c):
                tags = []
                if c.get('exhausted'):
                    tags.append('exhausted')
                shield = sum(s['amount'] for s in c.get('shields', []))
                if shield:
                    tags.append(f'shield {shield}')
                tags.extend(c.get('keywords', []))
                return f"{c['attack']}/{c['health']}" + (f" ({', '.join(tags)})" if tags else '')
            return ' + '.join(label(c) for c in cards)
        def losses(record, cards):
            defeated = set(record['result']['defeated_creatures'])
            return sum(c['instance_id'] in defeated for c in cards)
        damages = [sum(e['health_damage'] for e in r['result']['events']
                       if e['target_kind'] == 'player') for r in records]
        a_losses = [losses(r, friendly) for r in records]
        d_losses = [losses(r, opposing) for r in records]
        outcomes = {}
        for record, damage, lost_a, lost_d in zip(records, damages, a_losses, d_losses):
            outcome = outcomes.setdefault((damage, lost_a, lost_d), {
                'player_damage': damage, 'attacker_losses': lost_a, 'defender_losses': lost_d,
                'encounters': 0, 'example_job_id': record['job_id']})
            outcome['encounters'] += 1
        rows.append({'attacking_board': board(friendly), 'defending_board': board(opposing),
                     'attacking_cards': len(friendly), 'defending_cards': len(opposing),
                     'encounters': len(records), 'player_damage_range': [min(damages), max(damages)],
                     'attacker_losses_range': [min(a_losses), max(a_losses)],
                     'defender_losses_range': [min(d_losses), max(d_losses)],
                     'outcomes': [outcomes[k] for k in sorted(outcomes)],
                     'example_job_id': records[0]['job_id']})
    return {'interpretation': 'Observed ranges over exported encounters only. Choices are not probabilities; ranges are not jointly attainable guarantees. Partial runs may omit choices. Boards show ATK/current HP; inspect replay inputs for statuses. No match wins or balance ranking.',
            'matchups': rows}
