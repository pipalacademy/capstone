
DEPLOY_HOST=capstone@capstone.k8x.in

export PATH := $(PWD)/venv/bin:$(PATH)

deploy:
	ssh $(DEPLOY_HOST) capstone/deploy.sh

.PHONY: venv
venv:
	test -f venv/bin/python || python -m venv venv
	pip install -r requirements.txt -r dev-requirements.txt

run:
	python run.py --migrate
	honcho start

test:
	./runtests.sh
