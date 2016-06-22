#!/bin/bash

export DEBUG=true
export DB_USER=postgres
export DB_PASS=postgres
export DB_NAME=hma
#export DB_SERVICE=$(docker-machine ip dev)
export DB_SERVICE=localhost
#export DB_PORT=5432
export DB_PORT=5433
