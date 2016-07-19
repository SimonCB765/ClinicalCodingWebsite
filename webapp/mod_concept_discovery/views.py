"""Handlers for the pages made available by this blueprint."""

# Python imports.
import io

# Flask imports.
from flask import current_app, render_template

# 3rd party imports.
import neo4j.v1 as neo

# User imports.
from . import forms
from . import validate_concept_file


def home():
    """Render the home page."""
    return render_template('mod_concept_discovery/home.html')


def upload_concepts():
    """Render and process the page for uploading concepts to be defined."""
    uploadForm = forms.ConceptUploadForm()

    if uploadForm.validate_on_submit():
        # A POST request was made and the form was successfully validated.

        # Determine the content that was uploaded, and record some information about it.
        # Wrap the text area's content in StringIO in order to enable file-like operations on it, and to keep it in
        # line with how the uploaded file content is accessed.
        isFileUploaded = bool(uploadForm.conceptFile.data)
        if isFileUploaded:
            # A file was uploaded.
            filename = uploadForm.conceptFile.data.filename
            fileFormat = (filename.rsplit('.', 1)[1]).lower()
            uploadContents = io.TextIOWrapper(uploadForm.conceptFile.data, newline=None)
        else:
            # Text was entered in the text area.
            filename = "ConceptDefinitions"
            fileFormat = "txt"
            uploadContents = io.StringIO(uploadForm.conceptText.data, newline=None)

        # Ensure that the format of the uploaded file is correct.
        if fileFormat not in current_app.config["ALLOWED_EXTENSIONS"]:
            # The format of the file is not one of the accepted ones.
            uploadForm.conceptSubmit.errors.append(
                "Uploaded {0:s} file is not in one of the accepted formats - {1:s} or {2:s}.".format(
                    fileFormat, ", ".join(current_app.config["ALLOWED_EXTENSIONS"][:-1]),
                    current_app.config["ALLOWED_EXTENSIONS"][-1]))
            return render_template("mod_concept_discovery/upload_concepts.html", form=uploadForm)

        # Validate the uploaded concept(s). The only real constraint on the the concept file is that at least one
        # concept is defined in the correct format.
        isValidContents, errorMessage = validate_concept_file.main(uploadContents, fileFormat, isFileUploaded)

        if not isValidContents:
            # Found an error in the uploaded file or text area.
            uploadForm.conceptSubmit.errors.append(errorMessage)
            return render_template("mod_concept_discovery/upload_concepts.html", form=uploadForm)

        # All fields in the form have been validated, so concept discovery can begin.
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
