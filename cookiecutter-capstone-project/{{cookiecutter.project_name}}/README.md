# Capstone Project Template

This is the directory structure:

```
/
|-- repo/  # -> starter code for learners
|---+-- Dockerfile  # -> for deploying learners' code
|---+-- README.md
|-- capstone.yml  # -> project information
|-- checks.py  # -> custom checks. entrypoint to run checks locally, and validate the project directory
|-- requirements.txt  # -> python dependencies required to run the checks. these can be used in checks.py
+-- README.md  # -> you are here
```

## Setup

You'll have to install some dependencies first, such as the `capstone_checker` module.
`requirements.txt` lists these.

You might want to create a virtual env first:

```
python3 -m venv venv
source venv/bin/activate
```

## Usage

### Validate contents of project directory

Validate that all necessary files and directories are present, and that `capstone.yml` is valid.

```
python checks.py validate
```

### Run checks on a local app

When authoring a project, you can verify that the checks are working as expected by running them against a local
app directory.

```
python checks.py run --app-url http://localhost:8080 --app-dir ./solution-app
```

You can specify the exact task that you want to run checks for. Copy the task name from `capstone.yml` and pass it
as the `--task` option.

```
python checks.py run --task task-name --app-url http://localhost:8080 --app-dir ./solution-app
```
