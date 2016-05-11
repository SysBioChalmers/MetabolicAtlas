from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from hma_backend import app, db
from hma_backend.models import MetabolicModel, Author, Compartment
from hma_backend.models import Reaction, ReactionComponent, ExpressionData


migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


if __name__ == "__main__":
    manager.run()
