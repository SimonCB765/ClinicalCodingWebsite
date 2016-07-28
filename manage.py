"""Setup external scripts."""

# Flask imports
from flask_script import Manager

# User imports.
import database_setup.update_controller
from webapp import app


# Setup the manager.
manager = Manager(app)


@manager.command
def setup_database():
    """Update the contents of the Neo4j database backing the app."""

    # Determine the information needed to access the database.
    databaseURI = app.config["DATABASE_URI"]
    databasePassword = app.config["DATABASE_PASSWORD"]
    databaseUsername = app.config["DATABASE_USERNAME"]

    # Perform the update.
    database_setup.update_controller.main(databaseURI, databaseUsername, databasePassword)

if __name__ == "__main__":
    manager.run()
