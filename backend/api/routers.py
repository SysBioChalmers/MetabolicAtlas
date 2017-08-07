class GemodelRouter(object):
    def db_for_read(self, model, **hints):
        if hasattr(model, 'name') and model.__name__ == 'GEModel':
            return 'gems'
        return None

    def db_for_write(self, model, **hints):
        if hasattr(model, 'name') and model.__name__ == 'GEModel':
            return 'gems'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if hasattr(obj1, '__name__') and obj1.__name__ == 'GEModel':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name, **hints):
        if model_name == 'gemodel':
            return db == 'gems'
        return None


class TileRouter(object):
    def db_for_read(self, model, **hints):
        if hasattr(model, 'name') and model.__name__ == 'Tile':
            return 'tiles'
        return None

    def db_for_write(self, model, **hints):
        if hasattr(model, 'name') and model.__name__ == 'Tile':
            return 'tiles'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if hasattr(obj1, '__name__') and obj1.__name__ == 'Tile':
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
