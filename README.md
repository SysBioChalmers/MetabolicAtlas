# Metabolic Atlas
Welcome to the codebase for the Metabolic Atlas project.

## Table of Contents

   * [Software environment](#software-environment)
   * [References](#references)
   * [Prerequisites](#prerequisites)
   * [Get started](#get-started)
       * [Fetch repositories](#fetch-repositories)
       * [Add docker environment](#add-docker-environment)
       * [Load helper commands](#load-helper-commands)
       * [Build the project](#build-the-project)
       * [Start docker containers](#start-docker-containers)
       * [Description of helper commands](#description-of-helper-commands)
   * [Licenses](#licenses)


## Software environment
The front-end uses [Vue.js](https://vuejs.org), with help of [Vue CLI](https://cli.vuejs.org/). The backend uses [Django REST framework](http://www.django-rest-framework.org) with [PostgreSQL](https://www.postgresql.org) as the database.  


## References
If you use *Metabolic Atlas* in your scientific work, please cite:
> Robinson, Jonathan L., et al. "An atlas of human metabolism." *Science Signaling* 13.624 (2020) [doi:10.1126/scisignal.aaz1482 ](https://doi.org/10.1126/scisignal.aaz1482 )

## Prerequisites
Docker, along with docker-compose, is used to manage the dependencies of this project. To install Docker, download it from [here](https://www.docker.com/products/docker) (docker-compose should also be installed).

## Get started

### Fetch repositories
Apart from the current repository, two additional repositories are required in
order to deploy Metabolic Atlas locally, they are

* [neo4j-data-generation](https://github.com/MetabolicAtlas/neo4j-data-generation): for generating neo4j database
* [data-files](https://github.com/MetabolicAtlas/data-files): containing integrated GEMs

Clone the three required repositories by 

    git clone https://github.com/MetabolicAtlas/MetabolicAtlas
    git clone https://github.com/MetabolicAtlas/neo4j-data-generation
    git clone https://github.com/MetabolicAtlas/data-files && pushd data-files; git lfs pull; popd

After that, change to the folder `MetabolicAtlas`

### Add docker environment
In the folder `MetabolicAtlas` that has been cloned, add a `.env` file based on the `.env.sample` file:
```bash
cp .env.sample .env
```
and modify this `.env` file.

The content of the file `.env` that has just been copied from `.env.sample` is shown below. Please change the value of `NEO4J_PASSWORD` with your preference. Other values can be kept as they are if you have fetched the repositories with the instruction in the previous step and haven't changed the folder names. Otherwise, change the location of `DATA_FILES_PATH` and `DATA_GENERATOR_PATH` accordingly.

```
CERTBOT_EMAIL=
SERVER_NAME=localhost
DATA_FILES_PATH=../data-files
DATA_GENERATOR_PATH=../neo4j-data-generation

NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password-unhackable

FTP_MIN_PORT=30000
FTP_MAX_PORT=31000

PORT_NGINX=80
PORT_FRONTEND=81
PORT_NEO4J_1=7474
PORT_NEO4J_2=7687

IP_FILTER="allow 129.16.0.0/16; allow 130.238.0.0/16; deny all;"
```


NOTE: if you want to try out the latest features of MetabolicAtlas, change the branch to `develop` by 
```bash
git checkout develop
```

### Load helper commands
To load the list of helper commands:
```bash
source proj.sh
```

### Build the project
Build databases and docker images of the project by:
```bash
build-stack
```

### Start docker containers
Start docker containers of the project by
```bash
start-stack
```

Given successful deployment, the frontend should be accessible at: `http://localhost/`. If you encounter any problems try running `restart-stack`, or look at the logs `logs backend` / `logs frontend`.

### Description of helper commands

* To bootstrap the project: `build-stack`
* To run the project: `start-stack`
* To display real-time logs: `logs [container-name: frontend/backend/nginx/db]`
* To stop the project: `stop-stack`
* To import a database: `import-db`

## Licenses

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FMetabolicAtlas%2FMetabolicAtlas.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FMetabolicAtlas%2FMetabolicAtlas?ref=badge_large)
