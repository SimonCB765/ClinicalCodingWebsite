"""Classes for forms used by this blueprint."""

# Flask imports.
from flask_wtf import Form

# 3rd party imports.
from wtforms import FileField, SelectMultipleField, SubmitField, TextAreaField, widgets
from wtforms.validators import DataRequired, ValidationError


def concept_definitions_validator(form, field):
    """Validate that either the text box or the file upload has content, but not both."""

    isFileUploaded = form.conceptFile.data
    isTextEntered = form.conceptText.data
    if isFileUploaded and isTextEntered:
        # Concepts were uploaded as a file and text.
        raise ValidationError("Only one source of concepts can be provided.")
    elif not isFileUploaded and not isTextEntered:
        # No concepts were uploaded.
        raise ValidationError("No source of concepts was provided.")


class MultiCheckboxField(SelectMultipleField):
    """A multiple select element that displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of the enclosed checkbox fields.

    """

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ConceptUploadForm(Form):
    """Class representing the form for uploading information about the concepts to find codes for."""

    conceptFile = FileField()
    codeFormats = MultiCheckboxField("codeFormats",
                                     choices=[("CTV3", "CTV3"), ("ReadV2", "Read v2"), ("SNOMED_CT", "SNOMED-CT")],
                                     default="ReadV2",
                                     validators=[DataRequired(message="At least one code format must be selected.")])
    conceptText = TextAreaField()
    conceptSubmit = SubmitField("Upload Concepts", validators=[concept_definitions_validator])
