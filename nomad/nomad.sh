#! /bin/bash
#
# Script to start Nomad 
#

exec sudo nomad agent -dev -bind 0.0.0.0 
