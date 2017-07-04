# Tutorial for a multi-database setup



## Introduction

This is a guide that explains the steps in creating a multiple-database setup for the Metabolic Atlas project.

It specifically illustrates the process of adding a new `postgres` docker image to a docker-compose setup that already has a PostgreSQL database. This image will contain two separate databases in it. This is followed by an integration to the `backend` service that runs django. A database router is provided for the convenience of working with different databases (database operations will automatically go to the right database without having to manually specify the database name).

For more details on using multiple databases with django, see https://docs.djangoproject.com/en/1.11/topics/db/multi-db



## Step 1: Add the new docker service

In the `docker-compose.yml` file, add the following service:

```yams
  db2:
    image: postgres
    env_file: db2_postgres.env
    ports:
      - "5433:5432"
    networks:
      - net-tier
```

Note that the port is mapped from `5432` inside the service to `5433` in the host machine. This is to avoid port conflict with the existing `db` service that is already using the `5432` port.

Make the following changes to the `backend` service section. The `- `indicates a line to be removed and `+` indicates lines that are added.

```yaml
   backend:
     depends_on:
       - db
-    env_file: postgres.env
+      - db2
+    env_file:
+      - postgres.env
+      - db2_postgres.env
```



## Step 2: Add the new environment file

Contents of `db2_postgres.env`:

```
POSTGRES_DB2_USER=postgres
POSTGRES_DB2_PASSWORD=postgres
POSTGRES_DB2_GEMS_DB=gems
POSTGRES_DB2_TILES_DB=tiles
```



## Step 3: Create the new databases

Rebuild and restart the project:

```bash
build-stack && restart-stack
```

Log into the new `db2` image instance:

```bash
docker exec -it $(docker ps -qf "name=metabolicatlas_db2_1") psql -U postgres
```

Create the new databases:

```sql
CREATE DATABASE gems WITH OWNER postgres ENCODING 'utf-8';
CREATE DATABASE tiles WITH OWNER postgres ENCODING 'utf-8';
```



## Step 4: Django integration

Update the `DATABASES` section in `backend/metabolicatlas/settings.py` to include the new databases:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': 5432,
    },
    'gems': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB2_GEMS_DB'),
        'USER': os.getenv('POSTGRES_DB2_USER'),
        'PASSWORD': os.getenv('POSTGRES_DB2_PASSWORD'),
        'HOST': 'db2',
        'PORT': 5432,
    },
    'tiles': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB2_TILES_DB'),
        'USER': os.getenv('POSTGRES_DB2_USER'),
        'PASSWORD': os.getenv('POSTGRES_DB2_PASSWORD'),
        'HOST': 'db2',
        'PORT': 5432,
    }
}
```

Add a `DATABASE_ROUTERS` section to `backend/metabolicatlas/settings.py` (this ensures which models go to which database):

```python
# Database routers

DATABASE_ROUTERS = [
    'api.routers.GemRouter',
    'api.routers.TileRouter',
    'api.routers.ApiRouter'
]
```

Create a new `backend/api/routers.py `file and add the logic for the database router:

```python
class GemRouter(object):
    def db_for_read(self, model, **hints):
        if model.__name__ == 'Gem':
            return 'gems'
        return None

    def db_for_write(self, model, **hints):
        if model.__name__ == 'Gem':
            return 'gems'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1.__name__ == 'Gem':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name, **hints):
        if model_name == 'gem':
            return db == 'gems'
        return None


class TileRouter(object):
    def db_for_read(self, model, **hints):
        if model.__name__ == 'Tile':
            return 'tiles'
        return None

    def db_for_write(self, model, **hints):
        if model.__name__ == 'Tile':
            return 'tiles'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1.__name__ == 'Tile':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name, **hints):
        if model_name == 'tile':
            return db == 'tiles'
        return None


class ApiRouter(object):
    def db_for_read(self, model, **hints):
        return 'default'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name, **hints):
        return db != 'gems' and db != 'tiles'
```

Add the new models in `backend/api/models`:

```python
#
# From gems db
#
class Gem(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200, null=True)
    organism = models.CharField(max_length=200, null=True)
    tissue = models.CharField(max_length=200, null=True)
    celltype = models.CharField(max_length=200, null=True)
    cellline = models.CharField(max_length=200, null=True)
    path = models.CharField(max_length=200, null=True)
    maintained = models.CharField(max_length=200, null=True)
    pubmed = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = "gems"

#
# From tiles db
#
class Tile(models.Model):
    reaction_component_id = models.CharField(max_length=50, primary_key=True)
    tile_name = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = "tiles"
```

Finally, update the `db-migrate` helper function defined in `proj.sh` to include the new databases:

```bash
function db-migrate {
    docker exec metabolicatlas_backend_1 python manage.py migrate
    docker exec metabolicatlas_backend_1 python manage.py migrate --database=gems
    docker exec metabolicatlas_backend_1 python manage.py migrate --database=tiles
}
```

That's it! Don't forget to source the updated `proj.sh` file and test setting up the new databases:

```bash
source proj.sh
build-stack && restart-stack
db-make-migrations
db-migrate
```

