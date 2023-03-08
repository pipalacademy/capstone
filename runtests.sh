#! /bin/bash

set -e

if [ -z "$TEST_DATABASE_URL" ]
then
	dropdb capstone_test --if-exists
	createdb capstone_test
	export TEST_DATABASE_URL=postgres:///capstone_test
fi

export DATABASE_URL=$TEST_DATABASE_URL

python run.py --migrate

export PYTHONPATH=.
pytest "$@"