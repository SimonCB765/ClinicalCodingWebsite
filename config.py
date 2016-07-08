"""Flask configuration objects."""

# Python imports.
import os


# Define the directory containing the application.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    CSRF_ENABLED = True  # Enable protection against Cross-site Request Forgery (CSRF).
    DEBUG = False  # Disable debug mode.
    TESTING = False  # Disable testing mode.
    CSRF_SESSION_KEY = SECRET_KEY = "secret"  # Setup the csrf and regular Flask secret keys.
    DATABASE_URI = ""


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
