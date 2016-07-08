"""Handlers for the pages made available by this module."""

# Flask imports.
from flask import render_template


def home():
    """Render the home page."""
    return render_template('mod_concept_discovery/home.html')
