"""Flask configuration objects."""

# Python imports.
import os


# Define the directory containing the application.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    CSRF_ENABLED = True  # Enable protection against Cross-site Request Forgery (CSRF).
    DATABASE_PASSWORD = "root"
    DATABASE_URI = ""
    DATABASE_USERNAME = "neo4j"
    DEBUG = False  # Disable debug mode.
    TESTING = False  # Disable testing mode.
    WTF_CSRF_SECRET_KEY = SECRET_KEY = "Some Random Secret String"  # Setup the csrf and regular Flask secret keys.


class ProductionConfig(Config):
    DATABASE_URI = "bolt://ec2-52-209-72-113.eu-west-1.compute.amazonaws.com:7687"


class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URI = "bolt://localhost:7687/"


class TestingConfig(Config):
    TESTING = True
