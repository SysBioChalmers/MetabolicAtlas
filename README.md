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

The frontend should be available at: `http://localhost/`, for example: `http://localhost/?tab=3&id=E_3396.
The backend should be available at: `http://localhost/api/`, for example: `http://localhost/api/reaction_components/E_3379/with_interaction_partners`.
There is also a swagger UI for browsing the API at: `http://localhost/swagger`.

If you encounter any problems try running `restart-stack`. or look at the logs `logs backend` / `logs frontend`

### Create the databases

#### Full model databases

Create databases using psql (in the docker container), example for hmr2:

```bash
CREATE DATABASE "hmr2" WITH OWNER 'postgres' ENCODING 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8' TEMPLATE template0;
```

To disconnect all sessions open on a database use:

```bash
SELECT pid, pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'hmr2' AND pid <> pg_backend_pid();
```

Then the data as explained in the above section...

```bash
source postgres.env                               # to load the environment variables

python manage.py makemigrations
python manage.py migrate --database [database] e.g. 'hmr2' (see settings.py)
python manage.py graph_models -a -o ER.png        # will generate a PNG overview of your tables
python manage.py populateDB      # read in the HMR2.0 database, and all associated annotations
python manage.py addNumberOfInteractionPartners [database]   # for each reaction_component calculate the number of interaction partners...

# **deprecated**, expression data are directly requested from HPA
python manage.py expressionDataFromHPA
# not used if no expressionDataFromHPA
python manage.py addTissueOntology                # add the BrendaTissueOntology, this is model independent and should only be added once...
```
(as adapted from `http://eli.thegreenplace.net/2014/02/15/programmatically-populating-a-django-database`)

**deprecated** Login into the database and run the following 3 commands to load the expression data...
```bash
psql -h localhost -p 5432 -U postgres -d hmr2
```
```sql
\copy expression_data(reaction_component, gene_id, gene_name, transcript_id, tissue, cell_type, bto_id, level, expression_type, reliability, source) from '/Users/halena/Documents/Sys2Bio/hma-prototype/database_generation/data/load_antibody_from_HPA_0.csv' csv delimiter ',' quote '"';
\copy expression_data(reaction_component, gene_id, gene_name, transcript_id, tissue, cell_type, bto_id, level, expression_type, reliability, source) from '/Users/halena/Documents/Sys2Bio/hma-prototype/database_generation/data/load_rnaseq_from_HPA_0.csv' delimiter ',';
update reaction_component set short_name=exp.gene_name FROM (SELECT gene_id, gene_name FROM expression_data) AS exp WHERE exp.gene_id = long_name AND short_name is null;  # see if we can add any more protein symbols using the HPA data...
```

Insert all information related to the svg maps, compare the DB and svg maps, shows statistics

```bash
python manage.py addCompartmentInformation database_generation/data/compartmentInfo.tab [database]
```

#### GEMs database

Connect to the corresponding docker container

```bash
docker exec -it $(docker ps -qf "name=metabolicatlas_db2_1")  bash
```

Create the db in psql (-U postgres)

```sql
CREATE DATABASE "gems" WITH OWNER 'postgres' ENCODING 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8' TEMPLATE template0;
```

To import models:

Extract model_files_full.tar.gz (available in the MetabolicAtlas folder on Box) into backend/model_files/ (might not exist) and run:

```bash
python manage.py migrate --database gems
python manage.py getMAModels
```

Follow the instructions at the end to serve the models file from ftp.icsb.chalmers.se.
Note: model files are stored in backend/model_files/FTP, removing this folder will re-download models files from remote locations (http://www.metabolicatlas.org/ and http://biomet-toolbox.chalmers.se/).


To import **public** models from SysbioChalmers Github organization, run:

```bash
python manage.py getGithubModels
```

Watch out the API rate limit (https://developer.github.com/v3/rate_limit/).


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
