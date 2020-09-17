#!/usr/bin/env bash

pushd ../

source setenv.sh

echo "Installing POWA"

POSTGRES_CONTAINER_ID="$(docker ps --filter "volume=/backup" --format "{{.ID}}")"
docker exec "${POSTGRES_CONTAINER_ID}" sh -c "PGPASSWORD=$DOCKER_PG_PASSWORD /usr/bin/psql -U contrax1 -d contrax1 -c 'CREATE EXTENSION IF NOT EXISTS hypopg;'"
docker exec "${POSTGRES_CONTAINER_ID}" sh -c "PGPASSWORD=$DOCKER_PG_PASSWORD /usr/bin/psql -U contrax1 -c 'CREATE DATABASE powa;'"
docker exec "${POSTGRES_CONTAINER_ID}" sh -c "PGPASSWORD=$DOCKER_PG_PASSWORD /usr/bin/psql -U contrax1 -d powa -c 'CREATE EXTENSION IF NOT EXISTS pg_stat_statements;'"
docker exec "${POSTGRES_CONTAINER_ID}" sh -c "PGPASSWORD=$DOCKER_PG_PASSWORD /usr/bin/psql -U contrax1 -d powa -c 'CREATE EXTENSION IF NOT EXISTS btree_gist;'"
docker exec "${POSTGRES_CONTAINER_ID}" sh -c "PGPASSWORD=$DOCKER_PG_PASSWORD /usr/bin/psql -U contrax1 -d powa -c 'CREATE EXTENSION IF NOT EXISTS powa;'"
docker exec "${POSTGRES_CONTAINER_ID}" sh -c "PGPASSWORD=$DOCKER_PG_PASSWORD /usr/bin/psql -U contrax1 -d powa -c 'CREATE EXTENSION IF NOT EXISTS pg_qualstats;'"
docker exec "${POSTGRES_CONTAINER_ID}" sh -c "PGPASSWORD=$DOCKER_PG_PASSWORD /usr/bin/psql -U contrax1 -d powa -c 'CREATE EXTENSION IF NOT EXISTS pg_stat_kcache;'"
docker exec "${POSTGRES_CONTAINER_ID}" sh -c "PGPASSWORD=$DOCKER_PG_PASSWORD /usr/bin/psql -U contrax1 -d powa -c 'CREATE EXTENSION IF NOT EXISTS hypopg;'"
sleep 5
docker kill $POSTGRES_CONTAINER_ID
