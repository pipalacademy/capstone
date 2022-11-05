import web
import json
import datetime

from . import config


db_uri = config.db_uri
db = web.database(db_uri)


class Site:
    def __init__(self, row):
        self.id = row.id
        self.name = row.name
        self.current_task = row.current_task
        self.score = row.score
        self.created = self.parse_timestamp(row.created)
        self.last_updated = self.parse_timestamp(row.last_updated)

        # more data attributes, that are to be set externally
        self.base_url = None

    def parse_timestamp(self, timestamp):
        return datetime.datetime.fromisoformat(timestamp)

    @classmethod
    def find_all(cls):
        rows = db.select("site", order="score desc")
        return [cls(row) for row in rows]

    @classmethod
    def find(cls, name):
        row = db.where("site", name=name).first()
        if row:
            return cls(row)

    @classmethod
    def create(cls, name, **kwargs):
        id = db.insert("site", name=name, score=0, **kwargs)
        row = db.select("site", where="id=$id", vars={"id": id}).first()
        return cls(row)

    def set_userdata(self, key, value):
        if self.get_userdata(key):
            db.update("site_userdata",
                      value=value,
                      where="site_id=$self.id and key=$key",
                      vars=locals())
        else:
            db.insert("site_userdata",
                      site_id=self.id,
                      key=key,
                      value=value)

    def get_userdata(self, key):
        row = db.where("site_userdata", site_id=self.id, key=key).first()
        return row and row.value

    def is_task_done(self, task_name):
        rows = db.where("task", site_id=self.id, name=task_name)
        return bool(rows)

    def mark_task_as_done(self, task_name):
        self.add_changelog("task-done", f"Completed task {task_name}.")
        db.insert("completed_tasks", site_id=self.id, task=task_name)

    def get_changelog(self):
        rows = db.where("changelog", site_id=self.id, order="timestamp desc")
        return [self._process_changelog(row) for row in rows]

    def _process_changelog(self, row):
        row.timestamp = self.parse_timestamp(row.timestamp)
        return row

    def add_changelog(self, type, message):
        db.insert("changelog", site_id=self.id, type=type, message=message)

    def _update(self, **kwargs):
        db.update("site", **kwargs, where="id=$id", vars={"id": self.id})

    def update_score(self):
        rows = db.where("task", site_id=self.id).list()
        score = len(rows)
        self._update(score=score)

    def update_status(self, status):
        self.add_changelog("deploy", "Deployed the site")
        self._update(current_task=status['current_task'])

        for task_name, task_status in status['tasks'].items():
            self.update_task_status(task_name, task_status)

        self.update_score()

    def has_task(self, name):
        return db.where("task", site_id=self.id, name=name).first() is not None

    def get_task_status(self, name):
        task_status = db.where("task", site_id=self.id, name=name).first()
        if task_status:
            task_status.checks = json.loads(task_status.checks)
        return task_status

    def update_task_status(self, name, task_status):
        status = task_status['status']
        checks = json.dumps(task_status['checks'])
        if self.has_task(name):
            db.update("task",
                status=status,
                checks=checks,
                where="name=$name and site_id=$site_id",
                vars={"name": name, "site_id": self.id})
        else:
            db.insert("task",
                site_id=self.id,
                name=name,
                status=status,
                checks=checks)


class User:
    def __init__(self, row):
        self.id = row.id
        self.username = row.username

    @classmethod
    def find_all(cls):
        rows = db.select("user")
        return [cls(row) for row in rows]

    @classmethod
    def find(cls, **kwargs):
        row = db.where("user", **kwargs).first()
        if row:
            return cls(row)

    @classmethod
    def create(cls, **kwargs):
        id = db.insert("user", **kwargs)
        row = db.select("user", where="id=$id", vars={"id": id}).first()
        return cls(row)
