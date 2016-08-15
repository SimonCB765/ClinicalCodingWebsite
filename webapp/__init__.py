"""Initialisation code for the application."""

# Flask imports.
from flask import Flask, render_template
from flask_wtf.csrf import CsrfProtect

# 3rd party imports.
from celery import Celery


# Define the WSGI application object.
app = Flask(__name__)

# Load the configurations.
app.config.from_object('config.DevelopmentConfig')

# Add CSRF protection.
CsrfProtect(app)

# Setup the Celery instance. Do this before blueprints are registeres in order to ensure that the import of
# celeryInstance in the blueprints succeeds.
celeryInstance = Celery(app.name, backend=app.config["CELERY_RESULT_BACKEND"], broker=app.config["CELERY_BROKER_URL"],
                        include=["webapp.mod_codes_from_concepts.long_task"])
celeryInstance.conf.update(app.config)

# Import modules using their blueprint handler variables.
from webapp.mod_codes_from_concepts import modCodesFromConcepts
from webapp.mod_core import modCore

# Register blueprint(s).
app.register_blueprint(modCodesFromConcepts)
app.register_blueprint(modCore)

# Handle 404 errors.
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Handle 500 errors.
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
