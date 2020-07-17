# To make sure docker-compose is in the path
export PATH=$PATH:/usr/local/bin

function generate-data {
  echo 'Data generation started.'
  sh -ac ' . ./.env; yarn --cwd $DATA_GENERATOR_PATH start $DATA_FILES_PATH'
  echo 'Data generation completed.'
}

function build-stack {
  generate-data
  docker-compose -f docker-compose.yml -f docker-compose-$MET_ATLAS_VERSION.yml build $@
}

function start-stack {
  docker-compose -f docker-compose.yml -f docker-compose-$MET_ATLAS_VERSION.yml up -d
}

function stop-stack {
  docker-compose -f docker-compose.yml -f docker-compose-$MET_ATLAS_VERSION.yml kill
}

function clean-stack {
  docker stop $(docker ps -a -q) || true
  docker rm $(docker ps -a -q) || true
  docker volume prune --force || true
  # The line below was not removing the db container properly
  docker-compose -f docker-compose.yml -f docker-compose-$MET_ATLAS_VERSION.yml down
  docker volume prune -f
}

function logs {
  docker-compose -f docker-compose.yml -f docker-compose-$MET_ATLAS_VERSION.yml logs -f $@
}

function deploy-stack {
  generate-data
  sh -ac ' . ./.env; cp -r $DATA_GENERATOR_PATH/data ./neo4j/import'
  docker-compose -f docker-compose.yml -f docker-compose-prod.yml --context $1 up -d --build
}

echo -e "Available commands:
\tbuild-stack [options for dev instance only]
\tstart-stack
\tstop-stack
\tclean-stack
\tdeploy-stack <CONTEXT> [options for prod instance only]
\tlogs [container]"

if [ "$1" != 'production' ] ; then
  export MET_ATLAS_VERSION=local
  echo 'Sourced for LOCALHOST'
else
  export MET_ATLAS_VERSION=prod
  echo 'Sourced for PRODUCTION'
fi
