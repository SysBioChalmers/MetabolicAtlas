class GemodelRouter(object):
    def db_for_read(self, model, **hints):
        # print("model.__name__1 %s" % model.__name__)
        if model.__name__ in ['GEModelSet', 'GEModelSample', 'GEModelReference', 'GEModelFile', 'GEModel', 'GEModelSet_reference', 'GEModel_files']:
            return 'gems'
        return None

    def db_for_write(self, model, **hints):
        # print("model.__name__2 %s" % model.__name__)
        if model.__name__ in ['GEModelSet', 'GEModelSample', 'GEModelReference', 'GEModelFile', 'GEModel', 'GEModelSet_reference', 'GEModel_files']:
            return 'gems'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # print("object1 %s" % obj1)
        if obj1.__class__.__name__ in ['GEModelSet', 'GEModelSample', 'GEModelReference', 'GEModelFile', 'GEModel']:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name, **hints):
        # print("model_name %s" % model_name)
        if model_name in ['gemodelset', 'gemodelsample', 'gemodelreference', 'gemodelfile', 'gemodel']:
            return db == 'gems'
        return None


class TileRouter(object):
    def db_for_read(self, model, **hints):
        if hasattr(model, 'name') and model.__name__ in ['Tile', 'TileSubsystem']:
            return 'tiles'
        return None

    def db_for_write(self, model, **hints):
        if hasattr(model, 'name') and model.__name__ == ['Tile', 'TileSubsystem']:
            return 'tiles'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if hasattr(obj1, '__name__') and obj1.__name__ == ['Tile', 'TileSubsystem']:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name, **hints):
        if model_name in ['tile', 'tilesubsystem']:
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
