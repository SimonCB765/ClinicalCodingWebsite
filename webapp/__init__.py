"""Initialisation code for the application."""

# Flask imports.
from flask import Flask, render_template

# Import modules using their blueprint handler variables.
from webapp.mod_concept_discovery import modConceptDiscovery
from webapp.mod_core import modCore


# Define the WSGI application object.
app = Flask(__name__)

# Load the configurations.
app.config.from_object('config.DevelopmentConfig')

# Register blueprint(s).
app.register_blueprint(modConceptDiscovery)
app.register_blueprint(modCore)

# Handle 404 errors.
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Handle 500 errors.
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
