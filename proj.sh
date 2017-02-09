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

echo -e "

Available commands:

\tbuild-stack
\tstart-stack
\tstop-stack
\trestar-stack
\tlogs

"
