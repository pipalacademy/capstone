# Runner

Runner will run the checks for a project.

## Usage

Use `python run.py` with flags:

```
python run.py --capstone-url https://capstone-staging.pipal.in --project-name rajdhani --username alice --capstone-token abcd1234
```

Flags:
* `--capstone-url` [required]: URL of capstone instance
* `--capstone-token`, `-t` [required]: API token for capstone instance
* `--project-name`, `-p` [required]: Name of project
* `--username`, `-u` [required]: Username of user
* `--output`, `-o` [optional]: Filesystem path to write JSON output to

### Run checks inside docker container:

1. Build docker image

```
docker build . -t capstone-runner
```

2. Run image with volume mount and `--output` option

```
docker run --rm -v ./output.json:/output.json capstone-runner --capstone-url https://capstone-staging.pipal.in --project-name rajdhani --username alice --capstone-token abcd1234 --output output.json
```

## Result

Result will be a JSON of the form:

```json
{
    ...,
    "ok": true,
    "log": "...",
    "tasks": [
        {
            ...,
            "checks": [
                {
                    ...,
                    "status": "pass",
                    "message": null
                },
                {
                    ...,
                    "status": "fail",
                    "message": "check failed: ..."
                }
            ]
        }
    ]
}
```

There could be other metadata but if the "ok" is true, tasks and checks
are guaranteed to be there in the above format. There could be extra keys
where there are objects.

log will definitely be non-null when ok is not true. In that case, log
will have information about why the result is not ok. For example, if
cloning the git repository fails, then log will have information about
that.
