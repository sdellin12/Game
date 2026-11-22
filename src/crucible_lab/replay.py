"""Verified public-combat replay browser."""
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from crucible_sim.cli import verify


def load_replays(directory):
    directory = Path(directory)
    verify(directory)
    return [json.loads(line) for line in (directory / 'results.jsonl').read_text(encoding='utf-8').splitlines()]


def replay_text(record):
    lines = [record['input'].get('name', 'Combat'), f"Job: {record['job_id']}",
             'Public combat snapshot — response windows already closed.', '', 'BEFORE']
    def board(state):
        return ([f"Player {p['player_id']}: {p['health']} HP" for p in state['players']] +
                [f"{c['instance_id']} ({c['controller']}): {c['attack']} ATK, {c['health']}/{c['max_health']} HP; "
                 f"exhausted={c.get('exhausted', False)}; shields={c.get('shields', [])}"
                 for c in state['creatures']])
    lines.extend(board(record['input']['state']))
    lines.extend(['', 'DECLARATIONS', json.dumps(record['input']['attacks'], indent=2), '', 'DAMAGE EVENTS (simultaneous)'])
    for event in record['result']['events']:
        lines.append(f"{', '.join(event['source_ids'])} -> {event['target_id']}: "
                     f"raw {event['raw']}, modified {event['modified']}, "
                     f"prevented {event['prevented']}, health damage {event['health_damage']}")
    lines.extend(['', 'AFTER', *board(record['result']['state']),
                  'Defeated: ' + ', '.join(record['result']['defeated_creatures']),
                  'Misses: ' + ', '.join(record['result']['misses']),
                  'Lethal players (diagnostic only): ' + ', '.join(record['result']['lethal_players'])])
    return '\n'.join(lines)


class ReplayWindow:
    def __init__(self, parent, records):
        self.records = records
        self.window = tk.Toplevel(parent)
        self.window.title('The Crucible — Verified combat replays')
        self.window.geometry('1100x650')
        frame = ttk.Frame(self.window, padding=12)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text=f'{len(records)} verified encounters. Select a scenario; damage events resolve simultaneously.').pack(anchor='w')
        self.query = tk.StringVar()
        ttk.Label(frame, text='Filter by scenario name or job ID').pack(anchor='w', pady=(8, 0))
        ttk.Entry(frame, textvariable=self.query).pack(fill='x')
        panes = ttk.Panedwindow(frame, orient='horizontal')
        panes.pack(fill='both', expand=True, pady=8)
        left = ttk.Frame(panes); right = ttk.Frame(panes)
        panes.add(left, weight=1); panes.add(right, weight=2)
        self.list = tk.Listbox(left, exportselection=False, width=42)
        scroll = ttk.Scrollbar(left, orient='vertical', command=self.list.yview)
        self.list.configure(yscrollcommand=scroll.set)
        horizontal = ttk.Scrollbar(left, orient='horizontal', command=self.list.xview)
        self.list.configure(xscrollcommand=horizontal.set)
        scroll.pack(side='right', fill='y'); horizontal.pack(side='bottom', fill='x')
        self.list.pack(fill='both', expand=True)
        self.detail = tk.Text(right, wrap='word', state='disabled')
        detail_scroll = ttk.Scrollbar(right, orient='vertical', command=self.detail.yview)
        self.detail.configure(yscrollcommand=detail_scroll.set)
        detail_scroll.pack(side='right', fill='y'); self.detail.pack(fill='both', expand=True)
        self.list.bind('<<ListboxSelect>>', self.select)
        self.query.trace_add('write', self.filter)
        self.filter()

    def filter(self, *_):
        query = self.query.get().casefold()
        self.visible = [i for i, r in enumerate(self.records)
                        if query in (r['input'].get('name', '') + r['job_id']).casefold()]
        self.list.delete(0, 'end')
        for i in self.visible:
            self.list.insert('end', self.records[i]['input'].get('name', self.records[i]['job_id']))
        self.detail.configure(state='normal'); self.detail.delete('1.0', 'end'); self.detail.configure(state='disabled')
        if self.visible:
            self.list.selection_set(0)
            self.select()

    def select(self, *_):
        selected = self.list.curselection()
        if selected:
            text = replay_text(self.records[self.visible[selected[0]]])
            self.detail.configure(state='normal')
            self.detail.delete('1.0', 'end'); self.detail.insert('1.0', text)
            self.detail.configure(state='disabled')
