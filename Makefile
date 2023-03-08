
DEPLOY_HOST=capstone@capstone.k8x.in

deploy:
	ssh $(DEPLOY_HOST) capstone/deploy.sh