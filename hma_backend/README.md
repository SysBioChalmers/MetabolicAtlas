# Table of Contents

1. [About](#about)
2. [Prerequisites](#prerequisites)
3. [Configuration](#configuration)
4. [API](#api)
5. [Examples](#examples)


# About

This is a REST backend for accessing metabolic models and their
components. This application is a part of the Human Metabolic Atlas.


# Prerequisites

* Python 3
* A PostgreSQL database

Set up a virtual environment and install dependencies:

```bash
$ pyvenv /path/to/hma_backend_venv
$ source /path/to/hma_backend_venv/bin/activate
$ pip install -r requirements.txt
```
in order to get it working on a mac you need to do 'brew install postgresql'

## Testing

To run the tests, `coverage` must be installed:

```bash
$ pip install -r requirements_testing.txt
$ pip install -r requirements_import.txt # and as stated above, just one time!
```


# Configuration

The application is configured using environment variables:

| Name         | Description                  |
|--------------|------------------------------|
| DB_USER      | PostgreSQL user              |
| DB_PASS      | Password for PostgreSQL user |
| DB_NAME      | Database name                |
| DB_SERVICE   | Database hostname/IP         |
| DB_PORT      | Database port                |
| FLASK_CONFIG | Application environment      |


# Running

The default `make` target starts up the application in a development
environment.

Tests are executed by running `make test`.


# Database migrations

Make your changes to `hma_backend/models.py` and then run the
following:

```bash
$ python manage.py db migrate
# edit the generated migration to make sure everything's correct
# once that's done, run the following to upgrade the database:
$ python manage.py db upgrade
```

For more information about migrations, see [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/).

# API

A definition of the API is available at `/api/v1/spec`, use
[Swagger UI](https://github.com/swagger-api/swagger-ui) to explore it:

```bash
$ git clone https://github.com/swagger-api/swagger-ui.git
$ cd swagger-ui/dist
$ vim index.html # set $url to "http://<hma server>/api/v1/spec"
$ python3 -m http.server
```

Then open up [http://localhost:8000](http://localhost:8000) in your
browser.


# Examples

To get an idea of what the backend can provide, here are some example
queries to get you started:

## List interaction partners

Interaction partners are reaction components that are part of the same
reaction. Here are three different examples to give you an idea of the
size difference in the responses:

```bash
# 91 lines
$ curl http://<server>/api/v1/reaction_components/E_2571/interaction_partners
# 569 lines
$ curl http://<server>/api/v1/reaction_components/E_3125/interaction_partners
# 5966 lines
$ curl http://<server>/api/v1/reaction_components/M_m02040s/interaction_partners
```

## Get connected metabolites

Given an enzyme with an ENSEMBL gene identifier, we can get a list of
the metabolites that occur in the reactions that the enzyme is a part
of. The response can also include expression data, if the query
parameter `include_expressions` is set to `true`. E.g.:

```bash
# expressions as a link to another resource, 96 lines
$ curl http://<server>/api/v1/enzymes/ENSG00000164303/connected_metabolites
# expressions as a list, 2320 lines
$ curl http://<server>/api/v1/enzymes/ENSG00000164303/connected_metabolites?include_expressions=true
```

## Get expression data

There are a few different ways of getting expression data. So far, we
have seen one of them (as part of the `connected_metabolites`
resource). Here are two other ways:

```bash
# By reaction component ID
$ curl  http://<server>/api/v1/reaction_components/E_3125/expressions
# We can filter on tissue
$ curl  http://<server>/api/v1/reaction_components/E_3125/expressions?tissue=adrenal
# And on expression type (`rnaseq`, `ABP`, and `Staining`)
$ curl  http://<server>/api/v1/reaction_components/E_3125/expressions?tissue=adrenal&expression_type=staining
# By ENSGID
$ curl http://<server>/api/v1/expressions/ENSG00000180011
# We can filter on tissue
$ curl http://<server>/api/v1/expressions/ENSG00000180011?tissue=adrenal
# And on expression type (`rnaseq`, `ABP`, and `Staining`)
$ curl http://<server>/api/v1/expressions/ENSG00000180011?tissue=adrenal%20gland&expression_type=staining
```

The `tissue` and `expression_type` query parameters can be used when
querying the `connected_metabolite` resource too.
