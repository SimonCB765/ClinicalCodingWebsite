"""Initialise the module."""

# Flask imports.
from flask import Blueprint


# Create the blueprint for this module.
modCore = Blueprint('core', __name__)

# Import after defining modCore, as urls needs to import modCore.
from . import urls
