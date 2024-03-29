#! /bin/bash

set -e

INTEGRATION=false  # whether to run integration tests
TEMP_ARGS=()  # args to pass to pytest

for arg in "$@"
do
    if [ "$arg" == "--integration" ]
    then
        INTEGRATION=true
    else
        TEMP_ARGS+=("$arg")
    fi
done

set -- "${TEMP_ARGS[@]}"  # set $@ to TEMP_ARGS

# database

if [ -z "$TEST_DATABASE_URL" ]
then
	dropdb capstone_test --if-exists
	createdb capstone_test
	export TEST_DATABASE_URL=postgres:///capstone_test
fi

export DATABASE_URL=$TEST_DATABASE_URL

python run.py --migrate

# nomad

if [ "$INTEGRATION" = true ]
then
    if [ -z "$TEST_NOMAD_NAMESPACE" ]
    then
      # stop all existing jobs in namespace, delete namespace, then recreate it
      nomad job status -no-color -namespace=capstone-test | awk 'NR>1 {print $1}' | xargs -r nomad job stop -namespace=capstone-test -purge
      nomad namespace delete capstone-test || true
      nomad namespace apply -description "Instances for testing" capstone-test
      export TEST_NOMAD_NAMESPACE=capstone-test
    fi

    export NOMAD_NAMESPACE=$TEST_NOMAD_NAMESPACE
    export NOMAD_VAR_gitto_port=17878
    export NOMAD_VAR_registry_port=17979
    export NOMAD_VAR_nginx_port=18080

    ./nomad-scripts/start-jobs.sh

    export CAPSTONE_DOCKER_REGISTRY=localhost:$NOMAD_VAR_registry_port
    export CAPSTONE_GITTO_BASE_URL=http://localhost:$NOMAD_VAR_gitto_port
fi

# run tests

export CAPSTONE_TEST=1
export CAPSTONE_API_TOKEN=test123
export PYTHONPATH=.

if [ "$INTEGRATION" = true ]
then
    pytest --mypy  "$@"
else
    echo "Skipping integration tests"
    pytest --mypy -k "not integration" "$@"
fi
