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

**Step 3: Create database**

```
$ createdb capstone
```

**Step 4: Run db migrations**

```
$ python run.py --migrate
```

**Step 5: Build the docker image for capstone-runner**

```
$ runner/build-and-replace-docker-image.sh
```

**Step 6: Run the dev server**

```
$ python run.py
...
 * Running on http://localhost:5000/
```

Please note that capstone support multi-tenancy and it determines the tenant based on the hostname. For the devserver, use only localhost as the domain. Using 127.0.0.1 does not work.
