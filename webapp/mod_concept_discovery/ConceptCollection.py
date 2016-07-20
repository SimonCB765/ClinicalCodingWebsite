"""Class containing function for parsing, validating and using using concept definitions."""

# Python imports.
from abc import ABCMeta
from collections import defaultdict
import json
import logging

# Globals.
LOGGER = logging.getLogger(__name__)


class ConceptCollection(metaclass=ABCMeta):
    """Class of concept definitions and associated methods.

    The concept definitions are stored as a JSON object (a Python dictionary), with the form:
    {
        "Concept1":
            {
                "Positive": {"Codes": ["C10", "B3%"], "Terms": ['"type 2" diabetes']},
                "Negative": {"Codes": [], "Terms": ['blood pressure']}
            },
        "Concept2":
            {
                "Positive": {"Codes": ["XXX", "YYY"], "Terms": []},
                "Negative": {"Codes": ["AAA..", "B...."], "Terms": ["type 1", "type 2", 'kidney disease']}
            },
        ...
    }

    """

    def __init__(self, fileConceptDefinitions):
        """Initialise the concepts and their definitions."""

        # Record the concepts in the order that they appear in the concept definition file, and initialise the
        # dictionary of concept definitions.
        self._concepts = []  # The concepts recorded in the order that they appear in the concept definition file.
        self._conceptDefinitions = defaultdict(lambda: {"Positive": {"Codes": [], "Terms": []},
                                                        "Negative": {"Codes": [], "Terms": []}})

    @staticmethod
    def validate_concept_file(uploadContents, fileFormat, isFileUploaded):
        """Function to validate a file of concept definitions.

        :param uploadContents:  The contents of the concept definition file.
        :type uploadContents:   io.StringIO or io.TextIOWrapper
        :param fileFormat:      The format that the concept definitions take.
        :type fileFormat:       str
        :param isFileUploaded:  Whether the concept definitions come from an uploaded file or a text area.
        :type isFileUploaded:   bool
        :return:                Whether the concept definitions are valid, and the associated error message.
        :rtype:                 bool, str

        """

        # Validate the uploaded concept(s). The only real constraint on the the concept file is that at least one
        # concept is defined in the correct format.
        isValidContents = True
        errors = []
        if fileFormat == "json":
            # Validate the input in JSON format.
            try:
                jsonContent = json.loads(uploadContents.read())
                if not jsonContent:
                    # There are no concepts defined in the JSON file.
                    isValidContents = False
                    errors.append("The file of concepts must contain terms for at least one concept.")
                else:
                    # There are concepts defined, so make sure their definitions have the correct fields. This
                    # means that each concept must have some positive terms/codes defined, and that each positive and
                    # negative field must have either terms or codes defined for it.
                    for i in jsonContent:
                        # Check the positive and negative entries for this concept.
                        try:
                            positiveFields = jsonContent[i].get("Positive", None)
                            negativeFields = jsonContent[i].get("Negative", None)
                            if positiveFields is None:
                                # No positive entries found for this concept.
                                errors.append("No field named \"Positive\" found for concept {0:s}.".format(i))
                            elif not {"Codes", "Terms"} & set(positiveFields):
                                # The positive portion of the concept definition has neither terms nor codes defined.
                                errors.append("No field named \"Codes\" or \"Terms\" found in the \"Positive\" field "
                                              "of concept {0:s}.".format(i))
                            if negativeFields and not {"Codes", "Terms"} & set(negativeFields):
                                # The negative portion of the concept definition is present but has neither terms
                                # nor codes defined.
                                errors.append("No field named \"Codes\" or \"Terms\" found in the \"Negative\" field "
                                              "of concept {0:s}.".format(i))
                        except AttributeError:
                            # The concept is not associated with a dictionary.
                            errors.append("The value for concept {0:s} is not a dictionary.".format(i))
                    isValidContents = not errors
            except ValueError as err:
                # The JSON is not correctly formatted.
                isValidContents = False
                errors.append("Error in {0:s} JSON content - {1:s}."
                              .format("uploaded file" if isFileUploaded else "text area", str(err)))
        else:
            # Validate non-JSON input with the assumption that it is therefore in the flat file format.
            # The only requirements on a flat file is that the first non-whitespace character of the file is a # and
            # that there is some non-whitespace content on that line following the #.
            line = uploadContents.readline()
            firstCharacterFound = None  # The first character in the file found.
            contentOnFirstLine = False
            while line and not firstCharacterFound:
                # Loop until you find a character. We know there is contents in the file/text area due to the form
                # validation carried out.
                line = line.strip()
                if line:
                    # The line has non-whitespace characters on it.
                    firstCharacterFound = line[0]
                    contentOnFirstLine = len(line) > 1  # Test for other non-whitespace characters on the line.
                line = uploadContents.readline()
            if firstCharacterFound != '#':
                # The first character in the file was not a '#'.
                isValidContents = False
                errors.append("The first non-whitespace character of the {0:s} must be a # not a '{1:s}'."
                              .format("uploaded file" if isFileUploaded else "text area", firstCharacterFound))
            elif not contentOnFirstLine:
                # There was not valid content on the first line, and therefore no first concept.
                isValidContents = False
                errors.append("The first line with content must contain non-whitespace characters after the #.")

        return isValidContents, errors
