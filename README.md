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

The frontend should be available at: `http://localhost:8080/`, for example: `http://localhost:8080/closest-interaction-partners/E_3379`.

 The backend should be available at: `http://localhost:8000/api/`, for example: `http://localhost:8000/api/reaction_components/E_3379/with_interaction_partners`.

There is also a swagger UI for browsing the API at: `http://localhost:8000/`.

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
A simplified version of gitflow is used. The three kinds of branches are:

1. the `master` branch
2. the `develop` branch
3. `feature/<FEATURE_NAME>` branches

Whenever you start working on a new feature, create a feature branch called `feature/<FEATURE_NAME>` based on the `develop` branch.

```bash
$ git checkout develop
$ git checkout -b feature/<FEATURE_NAME>
```

After you are done with the feature, make a [pull request](https://github.com/SysBioChalmers/hma-prototype/compare) from the `feature/<FEATURE_NAME>` branch to the `develop` branch. After the pull request has been reviewd and merged, the `feature/<FEATURE_NAME>` branch can be deleted.

When it is time to deploy a new version, create a [pull request](https://github.com/SysBioChalmers/hma-prototype/compare) from `develop` to `master`. After reviewing and merging the pull request, create a `tag` to mark the current version and push it to github. The `tag` name should be `v` followed with the version number, for example `v1.1`.

```bash
$ git checkout master
$ git tag v1.1
& git push origin v1.1
```

For more details on working with branches, take a look at the excellent [guide](https://guides.github.com/introduction/flow/) provide by Github.