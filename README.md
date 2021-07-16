[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/4276/badge)](https://bestpractices.coreinfrastructure.org/projects/4276)

Welcome to the codebase for the Metabolic Atlas project.  
If you use *Metabolic Atlas* in your scientific work, please cite:
> Robinson, Jonathan L., et al. "An atlas of human metabolism." *Science Signaling* 13.624 (2020) [doi:10.1126/scisignal.aaz1482 ](https://doi.org/10.1126/scisignal.aaz1482 )


## Get started
The front-end uses [Vue.js](https://vuejs.org), with help of [Vue CLI](https://cli.vuejs.org/). The backend uses [ExpressJS](https://expressjs.com/) and [Neo4j](https://neo4j.com/) as the database.  

[Docker](https://www.docker.com/products/docker) and docker-compose are used to manage the dependencies of this project. Start by installing these if they are not present on the system.

If you want to try out the latest features of MetabolicAtlas, change the branch to `develop`.

Apart from the current repository, two additional repositories are required in
order to deploy Metabolic Atlas locally, they are

* [neo4j-data-generation](https://github.com/MetabolicAtlas/neo4j-data-generation): for generating neo4j database
* [data-files](https://github.com/MetabolicAtlas/data-files): contains all the data necessary data (integrated models, maps, FTP repository) using Git LFS

Clone the three required repositories by 

    git clone https://github.com/MetabolicAtlas/MetabolicAtlas
    git clone https://github.com/MetabolicAtlas/neo4j-data-generation
    git clone https://github.com/MetabolicAtlas/data-files && pushd data-files; git lfs pull; popd


In the folder `MetabolicAtlas` that has been cloned, add a `.env` file based on the `.env.sample` file:
```bash
cp .env.sample .env
```
and modify this `.env` file.

The content of the file `.env` that has just been copied from `.env.sample` is shown below. Make sure the paths for `DATA_FILES_PATH` and `DATA_GENERATOR_PATH` are correct for your setup.

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

IP_FILTER=""
```

To load the list of helper commands run:
```bash
source proj.sh
```

Run the helper command that creates the database and builds the Docker images of the project:
```bash
build-stack
```

Finally, start the Docker containers with
```bash
start-stack
```

Given successful deployment, the frontend should be accessible at: `http://localhost/`. If you encounter any problems try looking at the logs `logs api` / `logs frontend`.

## Description of helper commands

* To bootstrap the project: `build-stack`
* To run the project: `start-stack`
* To stop the project: `stop-stack`
* To clean the project (delete containers and volumes): `clean-stack`
* To display real-time logs: `logs [container-name: frontend/api/nginx/neo4j/ftp]`
* To deploy the project: `deploy-stack`
* To (re-)import the Neo4j database: `import-db`

## Licenses

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FMetabolicAtlas%2FMetabolicAtlas.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FMetabolicAtlas%2FMetabolicAtlas?ref=badge_large)
