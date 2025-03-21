#!/bin/bash

echo 'create docker-volumes/postgres-db-data'
mkdir -p docker-volumes/postgres-db-data

echo 'create docker-volumes/pgadmin-data'
mkdir -p docker-volumes/pgadmin-data

echo 'export .env variables'
set -o allexport
source .env
set +o allexport