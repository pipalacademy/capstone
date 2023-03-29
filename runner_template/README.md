# Runner Template

Template directory for building a check runner docker image.

Structure of docker container:

```
/
+--- work/
+----+--- checks.py 
+----+--- requirements.txt
+----+--- runner.py
+----+--- repo/  # mounted directory
```


Structure of this repository:

```
/
+--- Dockerfile
+--- README.md
+--- work/
+----+--- checks.py  # default, blank. can be overwritten
+----+--- requirements.txt  # default, blank. can be overwritten
+----+--- runner.py  # must not be overwritten
+----+--- runner-requirements.txt  # must not be overwritten
```

Dockerfile looks like this:

```Dockerfile
FROM python3.10

COPY work /work

RUN pip install -U -r work/requirements.txt work/runner-requirements.txt

ENTRYPOINT ["python3", "runner.py"]
```

`runner.py` takes the check name as a CLI option and the JSON-encoded string of args as the argument.

Example,

```
python3 runner.py -c check-http-status '{"url": "https://example.com"}'
```

When run as a Docker image, it can be run as:

```
docker run --rm checks-runner -c check-http-status '{"url": "https://example.com"}'
```

The runner script will write a JSON to stdout that will indicate the check status:

```
$ docker run --rm checks-runner -c check-http-status '{"url": "https://example.com"}'
{
    "status": "pass",
    "message": null
}
```

Or,

```
$ docker run --rm checks-runner -c check-http-status '{"url": "https://example.com"}'
{
    "status": "fail",
    "message": "expected status code: 200, got status code: 404"
}
```
