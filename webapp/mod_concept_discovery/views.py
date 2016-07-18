"""Handlers for the pages made available by this blueprint."""

# Flask imports.
from flask import render_template

# User imports.
from . import forms


def home():
    """Render the home page."""
    return render_template('mod_concept_discovery/home.html')


def upload_concepts():
    """Render and process the page for uploading concepts to be defined."""
    uploadForm = forms.ConceptUploadForm()

    if uploadForm.validate_on_submit():
        # A POST request was made and the form was successfully validated.
        return "Submission successful."
    return render_template("mod_concept_discovery/upload_concepts.html", form=uploadForm)
