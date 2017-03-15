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

#### To get a list of helper commands

```bash
$ source proj.sh
```

#### Build and run the project

```bash
$ build-stack
```

```bash
$ start-stack
```

#### Import the database

```bash
$ docker exec -i $(docker ps -qf "name=vuedjangostack_db_1") psql -U postgres hma < PATH_TO_DB_FILE
```

#### The database needs a small modification

```bash
docker exec -it $(docker ps -qf "name=vuedjangostack_db_1") psql -U DB_USERNAME DB_NAME
```

```sql
ALTER TABLE expression_data RENAME COLUMN id TO reaction_component;
ALTER TABLE expression_data DROP CONSTRAINT expression_data_pkey;
ALTER TABLE expression_data ADD COLUMN id SERIAL PRIMARY KEY;
```

Use `Cmd + D` to exit the psql shell. At this point everything should be up and running.

The frontend should be available at: `http://localhost/`, for example: `http://localhost/?tab=3&reaction_component_id=E_3396&enzyme_id=ENSG00000180011`.

 The backend should be available at: `http://localhost/api/`, for example: `http://localhost/api/reaction_components/E_3379/with_interaction_partners`.

There is also a swagger UI for browsing the API at: `http://localhost/swagger`.

If you encounter any problems try running `restart-stack`.

#### All helper commands

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