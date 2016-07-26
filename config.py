"""Flask configuration objects."""

# Python imports.
import os


# Define the directory containing the application.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    ALLOWED_EXTENSIONS = ["csv", "json", "tsv", "txt"]
    CELERY_BROKER_URL = "amqp://"
    CELERY_RESULT_BACKEND = "rpc://"
    CSRF_ENABLED = True  # Enable protection against Cross-site Request Forgery (CSRF).
    DATABASE_PASSWORD = "root"
    DATABASE_URI = ""
    DATABASE_USERNAME = "neo4j"
    DEBUG = False  # Disable debug mode.
    TESTING = False  # Disable testing mode.
    WTF_CSRF_SECRET_KEY = SECRET_KEY = "Some Random Secret String"  # Setup the csrf and regular Flask secret keys.


class ProductionConfigLocal(Config):
    """Production configuration when running Neo4j locally."""
    DATABASE_URI = "bolt://localhost:7687/"


class ProductionConfigRemote(Config):
    """Production configuration when running Neo4j remotely.

    The URI will need filling in with the correct instance.

    """
    DATABASE_URI = "bolt://ec2-**-***-**-***.eu-west-1.compute.amazonaws.com:7687"


class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URI = "bolt://localhost:7687/"


class TestingConfig(Config):
    TESTING = True
