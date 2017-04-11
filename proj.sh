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

function build-production {
    docker exec vuedjangostack_frontend_1 npm run build
    rm -rf nginx/static
    mkdir nginx/static
    cp -r frontend/dist/ nginx/
    mv nginx/index.html nginx/static/
    cp -r backend/static/ nginx/static/
    rm -rf frontend/dist
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
\tbuild-production

"
