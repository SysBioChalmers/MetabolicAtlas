function build-stack {
    docker-compose -f docker-compose.yml -f docker-compose-dev.yml build $@
}

function start-stack {
    docker-compose -f docker-compose.yml -f docker-compose-dev.yml up -d
}

function stop-stack {
    docker-compose -f docker-compose.yml -f docker-compose-dev.yml kill
}

function restart-stack {
    stop-stack && start-stack
}

function logs {
    docker-compose -f docker-compose.yml -f docker-compose-dev.yml logs -f $@
}

function db-make-migrations {
    docker exec backend python manage.py makemigrations api
}

function db-migrate {
    docker exec backend python manage.py migrate --database=$@
}

function create-su {
    docker exec -it backend python manage.py createsuperuser
}


echo -e "

Available commands:

\tbuild-stack
\tstart-stack
\tstop-stack
\trestart-stack
\tlogs [container]
\tdb-make-migrations
\tdb-migrate [database]
\tcreate-su
"
