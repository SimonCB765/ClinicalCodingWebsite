"""Handlers for the pages made available by this blueprint."""

# Flask imports.
from flask import render_template


def home():
    """Render the home page."""
    return render_template("mod_core/home.html")
