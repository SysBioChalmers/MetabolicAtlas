function build-stack {
    docker-compose -p vue-django-stack build $@
}

function start-stack {
    docker-compose -p vue-django-stack up -d
}

function stop-stack {
    docker-compose -p vue-django-stack kill
}


function restart-stack {
    stop-stack && start-stack
}

function logs {
    docker-compose -p vue-django-stack logs -f $@
}

function db-make-migrations {
    docker exec vuedjangostack_backend_1 python manage.py makemigrations api
}

function db-migrate {
    docker exec vuedjangostack_backend_1 python manage.py migrate
}

function create-su {
    docker exec -it vuedjangostack_backend_1 python manage.py createsuperuser
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
