export PATH := $(PWD)/venv/bin:$(PATH)

.PHONY: venv
venv:
	test -f venv/bin/python || python -m venv venv
	pip install -r requirements.txt -r dev-requirements.txt

run:
	python run.py --migrate
	./nomad-scripts/start-jobs.sh
	honcho start

test:
	./runtests.sh
