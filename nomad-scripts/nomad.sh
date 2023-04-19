#! /bin/bash
#
# Script to start Nomad 
#

# Generates nomad.conf

NOMAD_ROOT=`dirname $0`
ROOT=`realpath $NOMAD_ROOT/..`
echo $ROOT

NOMAD_CONFIG=$ROOT/data/nomad.conf
GIT_ROOT=$ROOT/data/git

mkdir -p $ROOT/data/git

echo "generating $NOMAD_CONFIG ..."
echo "setting GIT_ROOT to $GIT_ROOT"

cat > $NOMAD_CONFIG <<END
client {
  host_volume "git-volume" {
    path      = "$GIT_ROOT"
    read_only = false
  }
} 
END

exec sudo nomad agent -dev -bind 0.0.0.0  -config $NOMAD_CONFIG
