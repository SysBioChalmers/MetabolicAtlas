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
       * [Build docker images](#build-docker-images)
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

### Add docker environment
Add a `.env` file based on the `.env.sample` file:
```bash
cp .env.sample .env
```
and modify this `.env` file. 

### Load helper commands
To load the list of helper commands:
```bash
source proj.sh
```

### Build docker images
Build and run the project:
```bash
build-stack
start-stack
```

### Start docker container
```bash
start-stack
```

The frontend should be available at: `http://localhost/`. If you encounter any problems try running `restart-stack`, or look at the logs `logs backend` / `logs frontend`.

### Description of helper commands

* To bootstrap the project: `build-stack`
* To run the project: `start-stack`
* To display real-time logs: `logs [container-name: frontend/backend/nginx/db]`
* To stop the project: `stop-stack`
* To import a database: `import-db`

## Licenses

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FMetabolicAtlas%2FMetabolicAtlas.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FMetabolicAtlas%2FMetabolicAtlas?ref=badge_large)
