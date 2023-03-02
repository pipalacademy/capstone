"""tq - simple task queue
"""
import time
import json
from pathlib import Path
import datetime
from dataclasses import dataclass, asdict
import traceback
from . import config

FUNCTIONS = {}

def task_function(f):
    FUNCTIONS[f.__name__] = f
    return f

@dataclass
class Task:
    key: str
    name: str
    timestamp: str
    kwargs: dict
    status: str = "pending"

    @property
    def path(self):
        return Path(config.tasks_dir) / self.status / self.key

    @property
    def func(self):
        return FUNCTIONS[self.name]

    @classmethod
    def new(cls, name, kwargs):
        t = str(time.time()).replace(".", "-")
        ts = datetime.datetime.utcnow().isoformat()
        key = f"{name}-{t}"
        return cls(key=key, name=name, timestamp=ts, kwargs=kwargs)

    @classmethod
    def from_path(cls, path):
        data = json.loads(path.read_text())
        return cls(
            key=data['key'],
            name=data['name'],
            timestamp=data['timestamp'],
            kwargs=data['kwargs'])

    def __repr__(self):
        return f"<Task:{self.key} @{self.timestamp}>"

    def dict(self):
        return asdict(self)

    def save(self):
        print("save", self.dict())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.dict()))

    def delete(self):
        self.path.unlink(missing_ok=True)

    def run(self):
        try:
            self.func(**self.kwargs)
        except Exception as e:
            traceback.print_exc()
            self.mark_failed()
        else:
            self.mark_done()

    def mark_failed(self):
        self._set_status("failed")

    def mark_done(self):
        self._set_status("done")

    def _set_status(self, status):
        if status == self.status:
            return
        old_path = self.path
        self.status = status
        new_path = self.path
        new_path.parent.mkdir(parents=True, exist_ok=True)
        old_path.rename(new_path)

    @classmethod
    def get_pending_tasks(cls):
        root = Path(config.tasks_dir) / "pending"
        if not root.exists():
            return []
        tasks = [Task.from_path(p) for p in root.iterdir()]
        return sorted(tasks, key=lambda t: t.timestamp)

def add_task(name, **kwargs):
    task = Task.new(name, kwargs)
    print("created task", task)
    task.save()

def run_pending_tasks():
    for t in Task.get_pending_tasks():
        print(t, t.kwargs)
        t.run()

def run_pending_tasks_in_loop():
    while True:
        run_pending_tasks()
        time.sleep(1)
