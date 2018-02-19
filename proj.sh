function build-stack {
    docker-compose -p metabolicatlas build $@
}

function start-stack {
    docker-compose -p metabolicatlas up -d
}

function stop-stack {
    docker-compose -p metabolicatlas kill
}


function restart-stack {
    stop-stack && start-stack
}

function logs {
    docker-compose -p metabolicatlas logs -f $@
}

function db-make-migrations {
    docker exec metabolicatlas_backend_1 python manage.py makemigrations api
}

function db-migrate {
    docker exec metabolicatlas_backend_1 python manage.py migrate
    docker exec metabolicatlas_backend_1 python manage.py migrate --database=gems
    docker exec metabolicatlas_backend_1 python manage.py migrate --database=tiles
}

function create-su {
    docker exec -it metabolicatlas_backend_1 python manage.py createsuperuser
}


echo -e "

Available commands:

\tbuild-stack
\tstart-stack
\tstop-stack
\trestart-stack
\tlogs
\tdb-make-migrations
\tdb-migrate
\tcreate-su

"
