from dataclasses import asdict
from typing import Any, Dict, Type

import requests
import yaml
from flask import g

from .db import Site
from .tasks import TaskParser, TaskStatus, ValidationError, Validator


class Capstone:
    def __init__(self, app, tasks_file):
        """Capstone instance.

        app: Flask app
        tasks_file: Path to YAML file with tasks
        """
        self.tasks_file = tasks_file

        @app.before_request
        def on_request():
            g.capstone = self

        props = self.load_properties(self.tasks_file)
        self.title = props["title"]
        self.subtitle = props.get("subtitle", "")

        self.config = self.load_config(self.tasks_file)

        self._validators = {}
        self._tasks = None  # hidden because we want to lazy-load with get_tasks()

        # validators
        self.validator(check_not_implemented)
        self.validator(check_webpage_content)

    def validator(self, klass: Type[Validator]):
        """Class decorator to add a class as a Validator
        """
        self._validators[klass.__name__] = klass
        return klass

    def set_config(self, key, value):
        self.config[key] = value

    def load_config(self, path):
        with open(path) as f:
            config = yaml.safe_load(f).get("config", {})

        return config

    def load_properties(self, path):
        with open(path) as f:
            props = yaml.safe_load(f)

        # discard keys tasks and config if they exist
        props.pop("tasks", None)
        props.pop("config", None)

        return props

    def get_tasks(self):
        if self._tasks is None:
            self._tasks = self.load_tasks()

        return self._tasks

    def get_task(self, name):
        for task in self.get_tasks():
            if task.name == name:
                return task

    def load_tasks(self):
        """Loads a list of tasks from a file.
        """
        parser = TaskParser(self.tasks_file, self._validators)
        return parser.load_from_file(self.tasks_file)

    def get_status(self, site):
        """Get status of site by running all validators

        Return value is a dict with keys:
        {tasks: Dict[str, TaskStatus], current_task: str}
        """
        evaluator = Evaluator(site, config=self.config)

        tasks = {}
        for task in self.get_tasks():
            task_status = evaluator.evaluate_task(task)
            tasks[task.name] = asdict(task_status)
            if task_status.status != TaskStatus.PASS:
                break

        return dict(tasks=tasks, current_task=task.name)

    def _get_base_url(self, site_name):
        """Get base URL for a site from its name
        """
        return self.config["base_url"].format(name=site_name)

    def _patch_site(self, site):
        """Any post-processing for a site, after it is fetched from DB
        """
        site.base_url = self._get_base_url(site.name)
        return site

    def new_site(self, name):
        """Create a new site
        """
        current_task = self.get_tasks()[0]
        site = Site.create(name, current_task=current_task.name)
        return self._patch_site(site)

    def get_all_sites(self):
        sites = Site.find_all()
        return [self._patch_site(site) for site in sites]

    def get_site(self, *args, **kwargs):
        site = Site.find(*args, **kwargs)
        return site and self._patch_site(site)


class Evaluator:
    def __init__(self, site: Site, config: Dict[str, Any]):
        self.site = site
        self.config = config

    def evaluate_task(self, task) -> TaskStatus:
        """Evaluate a single task for a site
        """
        print(f"[{self.site.base_url}] evaluating task {task.name}...")

        results = [c.verify(self.site) for c in task.checks]
        print(results)
        if all(c.status == TaskStatus.PASS for c in results):
            status = TaskStatus.PASS
        else:
            status = TaskStatus.FAIL
        return TaskStatus(status, checks=results)


class check_not_implemented(Validator):
    def __init__(self):
        pass

    def __str__(self):
        return "Checks are not yet implemented for this task"

    def validate(self, site):
        raise ValidationError("coming soon...")


class check_webpage_content(Validator):
    def __init__(self, url, expected_text):
        self.url = url
        self.expected_text = expected_text

    def __str__(self):
        return f"Check webpage content: {self.url}"

    def validate(self, site):
        base_url = site.base_url
        url = f"{base_url}{self.url}"
        if self.expected_text not in requests.get(url).text:
            message = f'Text "{self.expected_text}"\nis expected in the web page {url},\nbut it is not found.'
            raise ValidationError(message)
