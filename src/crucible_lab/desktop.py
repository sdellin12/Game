"""Responsive Tk shell; all simulation work stays in a child process."""
import os
import threading
import queue
import subprocess
import sys
import tempfile
import uuid
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def batch_command(checkpoint, output, control, experiment, budget, limit, condition='baseline', attack_mode='all'):
    if condition not in ('baseline', 'wounded', 'exhausted', 'shielded', 'mixed'):
        raise ValueError('Choose a supported group condition')
    if attack_mode not in ('all', 'subsets'):
        raise ValueError('Choose all or subsets for attacks')
    if condition == 'mixed' and int(budget) > 2:
        raise ValueError('Mixed conditions require budget 1 or 2')
    if experiment == 'matrix' and (condition != 'baseline' or attack_mode != 'all'):
        raise ValueError('Group conditions require the groups experiment')
    if experiment not in ('matrix', 'groups'):
        raise ValueError('Choose matrix or groups')
    if not 1 <= int(budget) <= 3 or int(limit) < 1:
        raise ValueError('Budget must be 1–3 and batch size must be positive')
    prefix = [sys.executable, '--worker'] if getattr(sys, 'frozen', False) else [sys.executable, '-u', '-m', 'crucible_sim.cli']
    return prefix + ['batch',
            '--experiment', experiment, '--condition', condition, '--attack-mode', attack_mode, '--budget', str(budget), '--limit', str(limit),
            '--checkpoint', str(checkpoint), '--output', str(output),
            '--control-file', str(control)]


class LabWindow:
    def __init__(self, root):
        self.root = root
        self.process = None
        self.report = None
        self.closing = False
        self.root.title('The Crucible — Combat Lab')
        self.root.geometry('840x580')
        self.root.minsize(780, 500)
        self.experiment = tk.StringVar(value='matrix')
        self.budget = tk.StringVar(value='3')
        self.condition = tk.StringVar(value='baseline')
        self.attack_mode = tk.StringVar(value='all')
        self.limit = tk.StringVar(value='100')
        self.checkpoint = tk.StringVar()
        self.status = tk.StringVar(value='Choose a checkpoint, then Run / Resume.')
        panel = ttk.Frame(root, padding=16)
        panel.pack(fill='both', expand=True)
        ttk.Label(panel, text='Combat experiments', font=('', 17, 'bold')).pack(anchor='w')
        ttk.Label(panel, text='Exact combat encounters. Full matches and card balance are not established.').pack(anchor='w', pady=8)
        form = ttk.Frame(panel)
        form.pack(fill='x')
        self.fields = []
        for row, (label, variable, values) in enumerate([
            ('Experiment', self.experiment, ('matrix', 'groups')),
            ('Group resource budget', self.budget, ('1', '2', '3')),
            ('New attempts per batch', self.limit, None),
            ('Group condition', self.condition, ('baseline', 'wounded', 'exhausted', 'shielded', 'mixed')),
            ('Attacks', self.attack_mode, ('all', 'subsets')),
        ]):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky='w', pady=4)
            field = ttk.Combobox(form, textvariable=variable, values=values, state='readonly') if values else ttk.Entry(form, textvariable=variable)
            field.grid(row=row, column=1, sticky='ew', padx=10)
            self.fields.append(field)
        ttk.Label(form, text='Checkpoint').grid(row=5, column=0, sticky='w')
        field = ttk.Entry(form, textvariable=self.checkpoint, width=58)
        field.grid(row=5, column=1, sticky='ew', padx=10)
        self.fields.append(field)
        self.browse = ttk.Button(form, text='Choose…', command=self.choose)
        self.browse.grid(row=5, column=2)
        form.columnconfigure(1, weight=1)
        buttons = ttk.Frame(panel)
        buttons.pack(fill='x', pady=14)
        self.start_button = ttk.Button(buttons, text='Run / Resume', command=self.start)
        self.start_button.pack(side='left')
        self.pause = ttk.Button(buttons, text='Pause', command=lambda: self.stop('pause'), state='disabled')
        self.pause.pack(side='left', padx=8)
        self.cancel = ttk.Button(buttons, text='Cancel batch', command=lambda: self.stop('cancel'), state='disabled')
        self.cancel.pack(side='left')
        self.open_button = ttk.Button(buttons, text='Open latest report', command=self.open_report, state='disabled')
        self.open_button.pack(side='right')
        self.inspect_button = ttk.Button(panel, text='Inspect exported replays...', command=self.inspect_replays)
        self.inspect_button.pack(anchor='w', pady=(0, 8))
        ttk.Label(panel, textvariable=self.status, wraplength=730).pack(anchor='w')
        self.log = tk.Text(panel, height=14, wrap='word', state='disabled')
        self.log.pack(fill='both', expand=True, pady=8)
        root.protocol('WM_DELETE_WINDOW', self.close)

    def choose(self):
        path = filedialog.asksaveasfilename(title='Choose existing checkpoint to resume, or name a new one',
                                          defaultextension='.sqlite', confirmoverwrite=False,
                                          filetypes=[('SQLite checkpoint', '*.sqlite')])
        if path:
            self.checkpoint.set(path)

    def start(self):
        if self.process:
            return
        try:
            if not self.checkpoint.get().strip():
                raise ValueError('Choose a checkpoint file first')
            checkpoint = Path(self.checkpoint.get()).expanduser().resolve()
            self.temp = tempfile.TemporaryDirectory(prefix='crucible-control-')
            self.control = Path(self.temp.name) / 'control.txt'
            self.output = checkpoint.parent / 'reports' / uuid.uuid4().hex
            command = batch_command(checkpoint, self.output, self.control,
                                    self.experiment.get(), int(self.budget.get()), int(self.limit.get()), self.condition.get(), self.attack_mode.get())
            self.log_path = Path(self.temp.name) / 'runner.log'
            self.log_file = self.log_path.open('w', encoding='utf-8')
            env = os.environ.copy()
            env["CRUCIBLE_WORKER_LOG"] = str(self.log_path)
            env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1]) + os.pathsep + env.get("PYTHONPATH", "")
            self.process = subprocess.Popen(command, stdout=self.log_file, stderr=subprocess.STDOUT, env=env,
                                            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        except (ValueError, OSError) as exc:
            if hasattr(self, 'log_file'):
                self.log_file.close()
            if hasattr(self, 'temp'):
                self.temp.cleanup()
            messagebox.showerror('Cannot start experiment', str(exc))
            return
        for field in self.fields:
            field.configure(state='disabled')
        self.start_button.configure(state='disabled')
        self.browse.configure(state='disabled')
        self.pause.configure(state='normal')
        self.cancel.configure(state='normal')
        self.status.set('Running. Startup validates saved results before processing new jobs.')
        self.poll()

    def stop(self, request):
        if self.process:
            self.control.write_text(request, encoding='utf-8')
            self.status.set(f'{request.capitalize()} requested. Waiting for saved progress and report export.')

    def poll(self):
        text = self.log_path.read_text(encoding='utf-8', errors='replace')
        self.log.configure(state='normal')
        self.log.delete('1.0', 'end')
        self.log.insert('end', text)
        self.log.see('end')
        self.log.configure(state='disabled')
        code = self.process.poll()
        if code is None:
            self.root.after(150, self.poll)
            return
        self.process = None
        self.log_file.close()
        self.temp.cleanup()
        import json
        summary_path = self.output / 'summary.json'
        try:
            progress = json.loads(summary_path.read_text(encoding='utf-8'))['progress']
            self.status.set(f"{progress['run_status'].replace('_', ' ').capitalize()}: "
                            f"{progress['completed_combats']}/{progress['requested_combats']} completed; "
                            f"{progress['pending_combats']} pending; {progress['error_attempts']} recorded errors.")
        except (OSError, ValueError, KeyError):
            self.status.set(f'Runner stopped (exit {code}). See log for errors; saved jobs remain resumable.')
        report = self.output / 'report.html'
        if report.is_file():
            self.report = report
            self.open_button.configure(state='normal')
        for field in self.fields:
            field.configure(state='readonly' if isinstance(field, ttk.Combobox) else 'normal')
        self.start_button.configure(state='normal')
        self.browse.configure(state='normal')
        self.pause.configure(state='disabled')
        self.cancel.configure(state='disabled')
        if self.closing:
            self.root.destroy()

    def inspect_replays(self):
        directory = filedialog.askdirectory(title='Choose exported run folder',
            initialdir=str(self.report.parent) if self.report else None)
        if not directory:
            return
        self.inspect_button.configure(state='disabled')
        self.status.set('Verifying replays before opening inspector...')
        results = queue.Queue()
        def load():
            from .replay import load_replays
            try:
                results.put((load_replays(directory), None))
            except Exception as exc:
                results.put((None, str(exc)))
        threading.Thread(target=load, daemon=True).start()
        def poll_load():
            try:
                records, error = results.get_nowait()
            except queue.Empty:
                self.root.after(100, poll_load)
                return
            self.inspect_button.configure(state='normal')
            if error:
                self.status.set('Replay verification failed.')
                messagebox.showerror('Cannot inspect replays', error)
            else:
                from .replay import ReplayWindow
                ReplayWindow(self.root, records)
                self.status.set(f'Opened {len(records)} verified public combat replays.')
        self.root.after(100, poll_load)

    def open_report(self):
        if self.report:
            webbrowser.open(self.report.as_uri())

    def close(self):
        if self.process:
            self.closing = True
            self.stop('pause')
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    LabWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()
