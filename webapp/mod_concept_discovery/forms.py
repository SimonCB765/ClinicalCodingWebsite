"""Classes for forms used by this blueprint."""

# Python imports.
import io

# Flask imports.
from flask import current_app
from flask_wtf import Form

# 3rd party imports.
from wtforms import FileField, RadioField, SelectMultipleField, SubmitField, TextAreaField, widgets
from wtforms.validators import DataRequired, ValidationError

# User imports.
from .ConceptCollection import ConceptCollection


def concept_definitions_validator(form, field):
    """Validate the concept definitions."""

    isFileUploaded = bool(form.conceptFile.data)
    isTextEntered = bool(form.conceptText.data)
    if isFileUploaded and isTextEntered:
        # Concepts were uploaded as a file and text.
        raise ValidationError("Only one source of concepts can be provided.")
    elif not isFileUploaded and not isTextEntered:
        # No concepts were uploaded.
        raise ValidationError("No source of concepts was provided.")
    else:
        # Concepts were provided, so validate them.

        # Determine the content that was uploaded, and record some information about it.
        # Wrap the text area's content in StringIO in order to enable file-like operations on it, and to keep it in
        # line with how the uploaded file content is accessed.
        if isFileUploaded:
            # A file was uploaded.
            filename = form.conceptFile.data.filename
            fileFormat = (filename.rsplit('.', 1)[1]).lower()
            uploadContents = io.TextIOWrapper(form.conceptFile.data, newline=None)
        else:
            # Text was entered in the text area.
            filename = "ConceptDefinitions"
            fileFormat = form.textAreaType.data
            uploadContents = io.StringIO(form.conceptText.data, newline=None)

        # Ensure that the format of the uploaded file is correct.
        allowedExtensions = current_app.config["ALLOWED_EXTENSIONS"]
        if fileFormat not in allowedExtensions:
            # The format of the file is not one of the accepted ones.
            raise ValidationError("Uploaded {0:s} file is not in one of the accepted formats - {1:s} or {2:s}."
                                  .format(fileFormat, ", ".join(allowedExtensions[:-1]), allowedExtensions[-1]))

        # Validate the uploaded concept(s). The only real constraint on the the concept file is that at least one
        # concept is defined in the correct format.
        errors = ConceptCollection.validate_concept_file(uploadContents, fileFormat, isFileUploaded)

        if errors:
            # Found an error in the uploaded file or text area.
            if not isFileUploaded:
                form.conceptSubmit.errors.append("Errors found while validating the pasted text.")
            else:
                form.conceptSubmit.errors.append("Errors found while validating the uploaded file.")
            form.conceptSubmit.errors.extend(errors)


class MultiCheckboxField(SelectMultipleField):
    """A multiple select element that displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of the enclosed checkbox fields.

    """

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ConceptUploadForm(Form):
    """Class representing the form for uploading information about the concepts to find codes for."""

    conceptText = TextAreaField()
    textAreaType = RadioField("Concept format:", choices=[("txt", "Flat File"), ("json", "JSON")], default="txt")
    conceptFile = FileField()
    codeFormats = MultiCheckboxField(choices=[("CTV3", "CTV3"), ("ReadV2", "Read v2"), ("SNOMED_CT", "SNOMED-CT")],
                                     default="ReadV2",
                                     validators=[DataRequired(message="At least one code format must be selected.")])
    conceptSubmit = SubmitField("Upload Concepts", validators=[concept_definitions_validator])
