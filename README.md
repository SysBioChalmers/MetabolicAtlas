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
$ cp postgres.env.sample postgres.env
```

Modify the `postgres.env`

### To get a list of helper commands

```bash
$ source proj.sh
```

### Build and run the project

```bash
$ build-stack
```

```bash
$ start-stack
```

### Import the database

connect to the container:

```
docker exec -it $(docker ps -qf "name=metabolicatlas_db_1")  bash
```

create the database:
```
drop database hma;
CREATE DATABASE "hma"
    WITH OWNER "postgres"
    ENCODING 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE template0;
```
Then exit the container and run:

```bash
$ docker exec -i $(docker ps -qf "name=metabolicatlas_db_1") psql -U postgres hma < PATH_TO_DB_FILE
```

The frontend should be available at: `http://localhost/`, for example: `http://localhost/?tab=3&reaction_component_id=E_3396&enzyme_id=ENSG00000180011&metabolite_rcid=M_m00001c`.

 The backend should be available at: `http://localhost/api/`, for example: `http://localhost/api/reaction_components/E_3379/with_interaction_partners`.

There is also a swagger UI for browsing the API at: `http://localhost/swagger`.

If you encounter any problems try running `restart-stack`.

#### To create the database (done by Lena)

The rest could simply load the database as explained in the above section...

```bash
$ source postgres.env                               # to load the environment variables

python manage.py makemigrations
python manage.py migrate
python manage.py graph_models -a -o ER.png        # will generate a PNG overview of your tables
python manage.py populateDB      # read in the HMR database, and all associated annotations
python manage.py addTissueOntology                # add the BrendaTissueOntology, this is model independent and should only be added once...
python manage.py addNumberOfInteractionPartners   # for each reaction_component calculate the number of interaction partners...
python manage.py expressionDataFromHPA
```
(as adapted from `http://eli.thegreenplace.net/2014/02/15/programmatically-populating-a-django-database`)

Log into the database and run the following 3 commands to load the expression data...
```bash
psql -h localhost -p 5432 -U postgres -d hma
```
```sql
\copy expression_data(reaction_component, gene_id, gene_name, transcript_id, tissue, cell_type, bto_id, level, expression_type, reliability, source) from '/Users/halena/Documents/Sys2Bio/hma-prototype/database_generation/data/load_antibody_from_HPA_0.csv' csv delimiter ',' quote '"';
\copy expression_data(reaction_component, gene_id, gene_name, transcript_id, tissue, cell_type, bto_id, level, expression_type, reliability, source) from '/Users/halena/Documents/Sys2Bio/hma-prototype/database_generation/data/load_rnaseq_from_HPA_0.csv' delimiter ',';
update reaction_component set short_name=exp.gene_name FROM (SELECT gene_id, gene_name FROM expression_data) AS exp WHERE exp.gene_id = long_name AND short_name is null;  # see if we can add any more protein symbols using the HPA data...
```

Make a database dump of the content of the database
```bash
pg_dump -h localhost -p 5432 -U postgres -d hma > ../database_generation/hma_v5.db
```

(takes about 15 minutes + 15 to prepare the expression data)

### The GEMs database
```bash
$ docker exec -i $(docker ps -qf "name=metabolicatlas_db2_1") psql -U postgres gems < PATH_TO_DB_FILE
```

### All helper commands

```bash
$ source proj.sh
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
