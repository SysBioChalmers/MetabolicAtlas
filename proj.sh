# To make sure docker-compose is in the path
export PATH=$PATH:/usr/local/bin

function generate-data {
  # enable flag "-q" to force overwritting existing data files
  echo 'Data generation started.'
  source .env && yarn --cwd $DATA_GENERATOR_PATH start $DATA_FILES_PATH "$@"
  /bin/cp -rf $DATA_GENERATOR_PATH/data/* neo4j/import
  /bin/cp  -f $DATA_GENERATOR_PATH/data/hpaRna.json api/src/data/
  /bin/cp  -f $DATA_FILES_PATH/integrated-models/integratedModels.json api/src/data/
  /bin/cp  -f $DATA_FILES_PATH/gemsRepository.json api/src/data/
  /bin/cp -rf $DATA_FILES_PATH/svg api/
  /bin/cp -rf $DATA_FILES_PATH/repository ftp/
  /bin/cp -rf $DATA_FILES_PATH/repository api/
}

function build-stack {
  generate-data
  docker-compose -f docker-compose.yml -f docker-compose-local.yml build $@
}

function start-stack {
  docker-compose -f docker-compose.yml -f docker-compose-local.yml up -d
  docker cp frontend:/project/yarn.lock frontend/yarn.lock
  docker cp api:/project/yarn.lock api/yarn.lock
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
  docker --context $1 compose -f docker-compose.yml -f docker-compose-prod.yml up -d --build --force-recreate
}

function import-db {
  generate-data --reset-db
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
