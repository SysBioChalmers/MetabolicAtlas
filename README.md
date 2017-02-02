# HMA Backend Prototype

## About

This is a prototype for deploying the backend part of the Human
Metabolic Atlas using Docker. PostgreSQL for storage, nginx as proxy,
and gunicorn to serve the Flask app.

Structure and inspiration taken from [0].

[0] https://realpython.com/blog/python/dockerizing-flask-with-compose-and-machine-from-localhost-to-the-cloud/


## Prerequisites

* [VirtualBox](https://www.virtualbox.org/)
* [Docker](https://docs.docker.com/engine/) (v1.9.0)
* [Docker Compose](https://docs.docker.com/compose/) (v1.5.0)
* [Docker Machine](https://docs.docker.com/machine/) (v0.5.0)
* libpq-dev (needed for psycopg2)


## Setting up

First, we'll need to download the additional data sources:

```bash
$ wget http://www.metabolicatlas.org/assets/hmr/HMRcollection2_00.xml-f0de1f951d16f78abf131cece19f8af7.zip
$ wget http://v14.proteinatlas.org/download/normal_tissue.csv.zip
$ wget http://v14.proteinatlas.org/download/transcript_rna_tissue.tsv.zip
```

(In addition to this, you might also want to a file specifying
currency metabolites. More on that below.)

Unzip the files and place them in the `hma_backend/import/`
folder. You will also need a file that maps ENSGIDs to HGNC symbols
(which will be used as short_name for the ReactionComponents). Place
it in the same folder.

Next step is to spin up the containers. In the root directory, execute
the following:

```bash
$ docker-machine create -d virtualbox dev
$ eval "$(docker-machine env dev)"
$ docker-compose build
$ docker-compose up -d
$ psql -h `docker-machine ip dev` -p 5432 -U postgres --password -d hma -c "create extension pg_trgm;"
$ docker-compose run --rm backend /usr/local/bin/python create_db.py
```

After that, we'll populate the database. First, we need to install
some additional Python libraries:

```bash
$ docker-compose run --rm backend /usr/local/bin/pip install -r requirements_import.txt
```

The actual import is done in four steps:


### First step - Import GEM file

```bash
$ docker-compose run --rm backend /usr/local/bin/python populate_db.py import/HMRdatabase2_00.xml
```


### Second step - Import HPA expression data

```bash
$ source dev_env.sh # this let's us connect to the db directly
$ cd hma_backend
# this takes some time
$ python generate_abp_expr_csv.py import/HMRdatabase2_00.xml \
    import/normal_tissue.csv
$ cat abp_expr_*.csv > abp.expr.csv && rm abp_expr_*.csv
# this takes even longer time
$ python generate_rnaseq_expr_csv.py import/HMRdatabase2_00.xml \
    import/transcript_rna_tissue.tsv
$ cat rnaseq_expr_*.csv > rnaseq_expr.csv && rm rnaseq_expr_*.csv
```

Next, we load the CSV files into the database:

```bash
$ psql -h `docker-machine ip dev` -p 5432 -U postgres --password hma \
    -c "\copy expression_data from abp.expr.csv delimiter ',';"
$ psql -h `docker-machine ip dev` -p 5432 -U postgres --password hma \
    -c "\copy expression_data from rnaseq_expr.csv delimiter ',';"
```


### Third step - Update reaction components with new data

The expression data that we loaded contains information that we want
to include in the reaction components in the database (`short_name`
and `component_type`). We run this to make the updates:

```bash
$ docker-compose run --rm backend /usr/local/bin/python \
    update_component_info.py import/HMRdatabase2_00.xml
$ docker-compose run --rm backend /usr/local/bin/python \
	add_short_names.py import/ensembl78_hgnc_symbol.hsapiens.tab
```


### Fourth step - Import currency metabolites

A "currency metabolite" is a metabolite that has multiple uses in
different reactions/pathways, such as ATP and NAD. To import currency
metabolites, we require a file with the following structure:

```
MetaboliteID1,ReactionID1,...,ReactionIDn
...
```

E.g.:

```
m00003c,HMR_0685,HMR_0686,HMR_0687,HMR_0688,HMR_0689,HMR_0690,HMR_0691,HMR_0692
m00004c,HMR_0545,HMR_0546,HMR_0547,HMR_0548,HMR_0549,HMR_0550,HMR_0551,HMR_0552,HMR_0553
m00006c,HMR_0545,HMR_0546,HMR_0547,HMR_0548,HMR_0549,HMR_0550,HMR_0551,HMR_0552,HMR_0553
m00007c,HMR_0545,HMR_0546,HMR_0547,HMR_0548,HMR_0549,HMR_0550,HMR_0551,HMR_0552,HMR_0553
```

Note that the lines do not have to have the same number of columns, we
don't care about the number of reaction IDs, we'll import all of them
for each line.

(Note that the IDs are of the form used by CobraPy, meaning the IDs
are not prefixed with "M_" or "R_" like they are in the GEM file.)

To import the currency metabolites, run the following:

```bash
$ docker-compose run --rm backend /usr/local/python add_currency_metabolites.py \
    import/currency_metabolites.txt
```

(Provided that you placed the file specifying the currency metabolites
in the hma_backend/import folder before you built the container
images.)


## Usage

Once everything is up, the backend application is available on port 80
on the virtual machine (use `docker-machine ip` to get the IP
address).

E.g.:

```bash
$ curl -v `docker-machine ip dev`
```
