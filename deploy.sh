#! /bin/bash

cd `dirname $0`

sudo -u www-data git pull
sudo supervisorctl restart capstone capstone-tasks