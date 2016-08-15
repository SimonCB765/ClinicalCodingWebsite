"""Initialise the module."""

# Flask imports.
from flask import Blueprint


# Create the blueprint for this module.
modCodesFromConcepts = Blueprint('codesFromConcepts', __name__, url_prefix='/codes_from_concepts')

# Import after defining modCodesFromConcepts, as urls needs to import modCodesFromConcepts.
from . import urls
