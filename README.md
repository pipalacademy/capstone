# capstone
Capstone is a framework for building guided programming projects.

## Setup

Run the following steps after cloning the repo.

**Step 1: Setup a virtualenv**

```
$ python -m venv venv
$ source venv/bin/activate
```

**Step 2: Install dependencies**

```
$ pip install -r requirements.txt dev-requirements.txt
$ sudo apt install zip unzip
```

**Step 3: Install Redis as a service**

Refer [this](https://redis.io/docs/getting-started/installation/) for installation instructions.

Set it up as a service with `supervisord`.

```
[program:redis-server]
command=/usr/local/bin/redis-server /etc/redis/redis.conf
user=redis
group=redis
autostart=true
autorestart=unexpected
stderr_logfile=/var/log/supervisor/redis.log
stdout_logfile=/var/log/supervisor/redis-stdout.log
```

Make sure `daemonize` is set to `no` in `redis.conf`.

**Step 4: Create database**

PostgreSQL must be installed. Refer [this](https://www.postgresql.org/download/) for installation instructions.

```
$ createdb capstone
```

**Step 5: Run db migrations**

```
$ python run.py --migrate
```

**Step 6: Build the docker image for capstone-runner**

```
$ runner/build-and-replace-docker-image.sh
```

**Step 7: Start Gitto**

Setup [Gitto](https://github.com/pipalacademy/gitto) and start it.

You can also setup Gitto as a background service.

```
$ # from gitto's directory
$ ./gitto
```

**Step 8: Start the worker**

In another terminal.

```
$ python run.py --tasks
Starting Capstone...
Worker rq:worker:...: started, version 1.x.x
...
```

**Step 9: Run the dev server**

In another terminal.

```
$ python run.py
...
 * Running on http://localhost:5000/
```

Please note that capstone support multi-tenancy and it determines the tenant based on the hostname. For the devserver, use only localhost as the domain. Using 127.0.0.1 does not work.
