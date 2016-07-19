"""Handlers for the pages made available by this blueprint."""

# Flask imports.
from flask import current_app, render_template

# 3rd party imports.
import neo4j.v1 as neo

# User imports.
from . import forms


def home():
    """Render the home page."""
    return render_template('mod_concept_discovery/home.html')


def upload_concepts():
    """Render and process the page for uploading concepts to be defined."""
    uploadForm = forms.ConceptUploadForm()

    if uploadForm.validate_on_submit():
        # A POST request was made and the form was successfully validated. Concept discovery can therefore begin.
        databasePassword = current_app.config["DATABASE_PASSWORD"]
        databaseURI = current_app.config["DATABASE_URI"]
        databaseUsername = current_app.config["DATABASE_USERNAME"]

        driver = neo.GraphDatabase.driver(databaseURI,
                                          auth=neo.basic_auth(databaseUsername, databasePassword),
                                          encrypted=False)
        session = driver.session()
        result = session.run("MATCH (n) RETURN count(n) AS num")
        session.close()

        numOfNodes = [i["num"] for i in result][0]

        return "Submission successful. Returned {0:d} nodes from the database located at: {1:s}."\
            .format(numOfNodes, databaseURI)
    return render_template("mod_concept_discovery/upload_concepts.html", form=uploadForm)
