# To make sure docker-compose is in the path
export PATH=$PATH:/usr/local/bin

function generate-data {
  echo 'Data generation started.'
  sh -ac ' . ./.env && yarn --cwd $DATA_GENERATOR_PATH start $DATA_FILES_PATH "$@" && cp -r $DATA_GENERATOR_PATH/data/ ./neo4j/import'
}

function build-stack {
  generate-data
  docker-compose -f docker-compose.yml -f docker-compose-local.yml build $@
}

function start-stack {
  docker-compose -f docker-compose.yml -f docker-compose-local.yml up -d
}

function stop-stack {
  docker-compose -f docker-compose.yml -f docker-compose-local.yml kill
}

function clean-stack {
  docker stop $(docker ps -a -q) || true
  docker rm $(docker ps -a -q) || true
  docker volume prune --force || true
}

function logs {
  docker-compose -f docker-compose.yml -f docker-compose-local.yml logs -f $@
}

function deploy-stack {
  generate-data
  docker-compose -f docker-compose.yml -f docker-compose-prod.yml --context $1 up -d --build
}

function import-db {
  generate-data --reset-db
  source .env
  docker exec -it neo4j bash -c "cypher-shell -u ${NEO4J_USERNAME} -p ${NEO4J_PASSWORD} --format plain --file import/import.cypher"
}

echo -e "Available commands:
\tbuild-stack
\tstart-stack
\tstop-stack
\tclean-stack
\tdeploy-stack <CONTEXT>
\timport-db
\tlogs [container]"
