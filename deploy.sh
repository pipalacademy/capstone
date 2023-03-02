#! /bin/bash

cd `dirname $0`

git pull
sudo supervisorctl restart capstone capstone-tasks