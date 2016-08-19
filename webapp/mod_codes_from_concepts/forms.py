"""Classes for forms used by this blueprint."""

# Python imports.
import io

# Flask imports.
from flask import current_app
from flask_wtf import Form

# 3rd party imports.
from wtforms import FileField, RadioField, SelectMultipleField, StringField, SubmitField, TextAreaField, widgets
from wtforms.validators import ValidationError

# User imports.
from .ConceptCollection import ConceptCollection


def concept_definitions_validator(form, field):
    """Validate the concept definitions."""

    if bool(form.multiConceptFile.data) and not form.saveDefinition.data:
        # A file containing multiple concepts was uploaded and the user didn't click save.
        filename = form.multiConceptFile.data.filename
        fileFormat = (filename.rsplit('.', 1)[1]).lower()
        uploadContents = io.TextIOWrapper(form.multiConceptFile.data, newline=None)

        # Ensure that the format of the uploaded file is correct.
        allowedExtensions = current_app.config["ALLOWED_EXTENSIONS"]
        if fileFormat not in allowedExtensions:
            # The format of the file is not one of the accepted ones.
            raise ValidationError("Uploaded {0:s} file is not in one of the accepted formats - {1:s} or {2:s}."
                                  .format(fileFormat, ", ".join(allowedExtensions[:-1]), allowedExtensions[-1]))

        # Validate the uploaded concept(s). The only real constraint on the the concept file is that at least one
        # concept is defined in the correct format.
        errors = ConceptCollection.validate_concept_file(uploadContents, fileFormat, True)

        if errors:
            # Found an error in the uploaded file.
            form.conceptSubmit.errors.append("Errors found while validating the uploaded file.")
            form.conceptSubmit.errors.extend(errors)

        uploadContents.seek(0)  # Reset the stream back to the start so that it can be properly validated.
        uploadContents.detach()  # Detach the buffer to prevent TextIOWrapper closing the underlying file.
    else:
        # No file was uploaded. We are therefore going off of the free text entered in the form. This text has no
        # format associated with it, so is automatically valid. However, there still must be some content in one
        # of the fields and a name for the concept.
        conceptCodes = form.codes.data
        posTerms = form.positiveTerms.data
        negTerms = form.negativeTerms.data

        if not (conceptCodes or posTerms or negTerms):
            # No concept definition information has been supplied.
            if not form.conceptName.data:
                # The concept was not given a name.
                raise ValidationError("No name or concept defining terms/codes provided.")
            else:
                raise ValidationError("No concept defining terms or codes were provided.")
        elif not form.conceptName.data:
            # The concept was not given a name.
            raise ValidationError("No name for the concept was provided.")


class MultiCheckboxField(SelectMultipleField):
    """A multiple select element that displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of the enclosed checkbox fields.

    """

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ConceptDefinitionForm(Form):
    """Class representing the form for uploading information about the concepts to find codes for."""

    codes = TextAreaField("Additional Codes")
    codeFormats = RadioField(choices=[("ReadV2", "Read v2"), ("CTV3", "CTV3"), ("SNOMED_CT", "SNOMED-CT")],
                             default="ReadV2")
    conceptName = StringField("Concept Name")
    extractCodes = SubmitField("Extract Codes")
    multiConceptFile = FileField()
    negativeTerms = TextAreaField("Negative Terms")
    positiveTerms = TextAreaField("Positive Terms")
    saveDefinition = SubmitField("Save Definition")
    updateDefinition = SubmitField("Update Definition", validators=[concept_definitions_validator])
