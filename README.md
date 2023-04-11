# capstone
Capstone is a framework for building guided programming projects.

## Setup

These instructions are to setup a dev instance on Linux/Mac.

**Step 1: Install system software**

Capstone requires the following system software:

* zip
* unzip
* PostgreSQL
* Redis

If you are using Ubuntu/Debian Linux, you can install them using:

```
$ sudo apt-get install zip unzip postgresql redis-server
```

If you are using Mac OS X:

* https://postgres.app/ is the simplest way to install Postgres. See [macOS packages page on postgres documentation] for other alternatives.
* See [Installing Redis on Mac OS X](https://redis.io/docs/getting-started/installation/install-redis-on-mac-os/) for instructions for installing Redis.

**Step 2: Create Postgres database**

Create a postgres database.

```
$ createdb capstone
```

This expects you to have a postgres user with your username with privilages to create a database. You can set that up using:

```
$ sudo -u postgres createuser -s $USER
```

**Step 3: Setup a virtualenv**

Run the following command in the working directory after cloning the repo.

```
$ make venv
```

You can also update the virtualenv by running the same command.

**Step 4: Start the services**

```
$ make run
```

The application will be live at <http://localhost:5000/>.

Please note that capstone support multi-tenancy and it determines the tenant based on the hostname. For the devserver, use only localhost as the domain. Using 127.0.0.1 does not work.
