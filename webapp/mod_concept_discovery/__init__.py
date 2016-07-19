"""Initialise the module."""

# Flask imports.
from flask import Blueprint


# Create the blueprint for this module.
modConceptDiscovery = Blueprint('conceptDiscovery', __name__, url_prefix='/concept_discovery')

# Import after defining modConceptDiscovery, as urls needs to import modConceptDiscovery.
from . import urls
