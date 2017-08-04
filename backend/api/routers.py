class GemRouter(object):
    def db_for_read(self, model, **hints):
        # print("model.__name__1 %s" % model.__name__)
        if model.__name__ in ['GemGroup', 'GemSample', 'GemReference', 'GemFile', 'Gem', 'GemGroup_reference', 'Gem_files']:
            return 'gems'
        return None

    def db_for_write(self, model, **hints):
        # print("model.__name__2 %s" % model.__name__)
        if model.__name__ in ['GemGroup', 'GemSample', 'GemReference', 'GemFile', 'Gem', 'GemGroup_reference', 'Gem_files']:
            return 'gems'
        # print ("None")
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # print("object1 %s" % obj1)
        if obj1.__class__.__name__ in ['GemGroup', 'GemSample', 'GemReference', 'GemFile', 'Gem']:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name, **hints):
        if model_name in ['gemgroup', 'gemsample', 'gemreference', 'gemfile', 'gem']:
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

