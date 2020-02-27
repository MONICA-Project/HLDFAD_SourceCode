#!/bin/sh

# NOTE: this command must be called with 

set -x

if [ -z "$1" ]; then
  echo "Missing Environment Choice. It must be local, prod or dev"
  exit
else
  echo "Environment Variable passed: $1"
  CONF="$1"
fi

source ${PWD}/repo_paths.sh

FILENAME_SETTINGS=$CONF.py
FOLDER_DOCKER_LOGS=$PATH_CODE/logs

if [ -f $PATH_REPO/docker-compose.override.yml ]; then rm $PATH_REPO/docker-compose.override.yml; fi
if [ -f $PATH_REPO/.env ]; then rm $PATH_REPO/.env; fi
if [ ! -d $FOLDER_DOCKER_LOGS ]; then mkdir -p $FOLDER_DOCKER_LOGS; fi

ln -s $PATH_REPO/environment/.env.$CONF $PATH_REPO/.env
if [ -f $PATH_REPO/environment/docker-compose.override.yml.$CONF ]; then ln -s $PATH_REPO/environment/docker-compose.override.yml.$CONF $PATH_REPO/docker-compose.override.yml; fi


