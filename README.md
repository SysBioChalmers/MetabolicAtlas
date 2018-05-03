# Metabolic Atlas

## Introduction

Welcome to the codebase for the Metabolic Atlas project.

The front-end uses [Vue.js](https://vuejs.org), with help of [webpack](https://webpack.js.org) and [yarn](https://yarnpkg.com/en/).

The back-end uses [Django REST framework](http://www.django-rest-framework.org) with [PostgreSQL](https://www.postgresql.org) as the database.

To learn more about the project, please visit the [wiki](https://github.com/SysBioChalmers/hma-prototype/wiki).

## Prerequisites
Docker, along with docker-compose, is used to manage the dependencies of this project.

To install docker, download it from [here](https://www.docker.com/products/docker) (docker-compose should be installed along with the process).


## Get started

Add a `postgres.env` file based on the `postgres.env.sample` file:

```bash
cp postgres.env.sample postgres.env
```

Modify the `postgres.env`

### To get a list of helper commands

```bash
source proj.sh
```

### Build and run the project

```bash
build-stack
```

```bash
start-stack
```

The frontend should be available at: `http://localhost/`, for example: `http://localhost/?tab=3&id=E_3396.`
The backend should be available at: `http://localhost/api/`, for example: `http://localhost/api/reaction_components/E_3379/with_interaction_partners`.
There is also a swagger UI for browsing the API at: `http://localhost/swagger`.

If you encounter any problems try running `restart-stack`. or look at the logs `logs backend` / `logs frontend`

### Create the databases

The Full models databases are mapping public models (supposedly) inserted into the GEMs database, thus GEMs database should be built prior the Full models databases.

#### GEMs database

Connect to the corresponding DB docker container (db2)

```bash
docker exec -it $(docker ps -qf "name=metabolicatlas_db2_1")  bash
```

To disconnect all sessions open on a database use:

```bash
SELECT pid, pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'gems' AND pid <> pg_backend_pid();
```

Create the db in psql (-U postgres)

```sql
CREATE DATABASE "gems" WITH OWNER 'postgres' ENCODING 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8' TEMPLATE template0;
```

To import models:

Extract model_files_full.tar.gz (available in the MetabolicAtlas folder on Box) into backend/model_files/ (might not exist) and run in the **backend container**:

```bash
python manage.py makemigrations
python manage.py migrate --database gems
python manage.py getMAModels
```

Follow the instructions displayed at the end to serve the models file from ftp.icsb.chalmers.se.
Note: model files are stored in backend/model_files/FTP, removing this folder will re-download models files from remote locations (http://www.metabolicatlas.org/ and http://biomet-toolbox.chalmers.se/).


To import **public** models from SysbioChalmers Github organization, run:

```bash
python manage.py getGithubModels
```

Watch out the API rate limit (https://developer.github.com/v3/rate_limit/).

#### Full model databases

Create databases using psql (in the docker container), example for hmr2:

```bash
CREATE DATABASE "hmr2" WITH OWNER 'postgres' ENCODING 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8' TEMPLATE template0;
```

To disconnect all sessions open on a database use:

```bash
SELECT pid, pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'hmr2' AND pid <> pg_backend_pid();
```

Then connect to the **backend container** and run:

```bash
source postgres.env                               # to load the environment variables

python manage.py makemigrations
python manage.py migrate --database [database] e.g. 'hmr2' (see settings.py)
python manage.py graph_models -a -o ER.png        # will generate a PNG overview of your tables (optional)
python manage.py populateDB [ensembl_version] [database]      # insert SBML information and annotations in the specified database, e.g. '89' for Ensembl
python manage.py addNumberOfInteractionPartners [database]   # for each reaction_component calculate and store the number of interaction partners...
```

(as adapted from `http://eli.thegreenplace.net/2014/02/15/programmatically-populating-a-django-database`)

Insert all information related to the svg maps, compare the DB and svg maps, shows statistics

```bash
python manage.py addCompartmentInformation database_generation/data/compartmentInfo.tab [database]
```

### dump databases

#### Full model databases

```bash
docker exec -it $(docker ps -qf "name=metabolicatlas_db_1")  pg_dump -U postgres -d hmr2 --create -T 'auth_*' -T 'django_*' > hmr2.db
```

#### GEMs database

```bash
docker exec -i $(docker ps -qf "name=metabolicatlas_db2_1") pg_dump -U postgres -d gems --create -T 'auth_*' -T 'django_*' > /home/cholley/Downloads/gems.db
```

### Import databases

```bash 
docker exec -i $(docker ps -qf "name=metabolicatlas_db_1") psql -U postgres hmr2 < PATH_TO_DB_FILE 
``` 

```bash
docker exec -i $(docker ps -qf "name=metabolicatlas_db2_1") psql -U postgres gems < PATH_TO_DB_FILE
```

### All helper commands

```bash
source proj.sh
```

Then you will get access to the following commands:

* To bootstrap the project: `$ build-stack`
* To run the project: `$ start-stack`
* To display real-time logs: `$ logs`
* To stop the project: `stop-stack`
* To create new migrationfiles: `db-make-migrations`
* To run a database migration: `db-migrate`
* To create a django superuser: `create-su`


## Collaboration
For details on using github, please visit the [sysbio wiki](http://wiki.sysbio.chalmers.se/mediawiki/index.php/Development_guidelines#Github).
