"""Class containing function for parsing, validating and using using concept definitions."""

# Python imports.
from abc import ABCMeta
from collections import defaultdict
import json
import re

# User imports.
from ..utilities import cleaners


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

    def __new__(cls, fileConceptDefinitions, conceptSource="FlatFile"):
        """Create a set of concept definitions.

        :param fileConceptDefinitions:  The location of the file containing the concept definitions.
        :type fileConceptDefinitions:   str
        :param conceptSource:           The type of concept definition source file. Valid values are (case insensitive):
                                            flatfile    - for the flat file input format
                                            json        - for the JSON input format
        :type conceptSource:            str
        :return:                        A ConceptCollection subclass determined by the conceptSource parameter.
        :rtype:                         ConceptCollection subclass

        """

        if cls is ConceptCollection:
            # An attempt is being made to create a ConceptDefinition, so determine which subclass to generate.
            if conceptSource.lower() == "flatfile":
                # Generate a _FlatFileDefinitions.
                return super(ConceptCollection, cls).__new__(_FlatFileDefinitions)
            elif conceptSource.lower() == "json":
                # Generate a _JSONDefinitions.
                return super(ConceptCollection, cls).__new__(_JSONDefinitions)
            else:
                # Didn't get one of the permissible
                raise ValueError("{0:s} is not a permissible value for conceptSource".format(str(conceptSource)))
        else:
            # An attempt is being made to create a ConceptDefinition subclass, so create the subclass.
            return super(ConceptCollection, cls).__new__(cls, fileConceptDefinitions)

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
        :return:                The error messages generated during the validation.
        :rtype:                 list

        """

        # Validate the uploaded concept(s). The only real constraint on the the concept file is that at least one
        # concept is defined in the correct format.
        errors = []
        if fileFormat == "json":
            # Validate the input in JSON format.
            try:
                jsonContent = json.loads(uploadContents.read())
                if not jsonContent:
                    # There are no concepts defined in the JSON file.
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
            except ValueError as err:
                # The JSON is not correctly formatted.
                errors.append("Error in {0:s} JSON content - {1:s}."
                              .format("uploaded file" if isFileUploaded else "text area", str(err)))
        else:
            # Validate non-JSON input with the assumption that it is therefore in the flat file format.
            # The only requirements on a flat file is that the first non-whitespace character of the file is a #,
            # that there is some non-whitespace content on that line following the # and that any time a line starts
            # with ## it is followed by positive or negative.
            line = uploadContents.readline()
            lineNumber = 1
            firstCharacterFound = None  # The first character in the file found.
            while line:
                # Loop until you find a character. We know there is contents in the file/text area due to the form
                # validation carried out.
                line = line.strip()
                if line:
                    # The line has non-whitespace characters on it.

                    if line[0] != '%' and not firstCharacterFound:
                        # The first non-whitespace character, that is not in a comment, is on this line.
                        firstCharacterFound = line[0]

                    if line[0] == '#':
                        # Found a line with a concept name on it.
                        if not line[1:].strip():
                            # There was no content on the concept name line.
                            errors.append("Line {0:d} begins with a # but has no concept name on it."
                                          .format(lineNumber))
                    elif line[0] == '$':
                        # Found a control term. Check whether it has valid values.
                        controlTerm = line[1:].strip().split()[0]
                        if controlTerm.lower() not in ["positive", "negative", "search", "output"]:
                            errors.append("The control term {0:s} on line {1:d} is not valid."
                                          .format(controlTerm, lineNumber))
                line = uploadContents.readline()
                lineNumber += 1

            if firstCharacterFound != '#':
                # The first character in the file was not a '#'.
                errors.append("The first non-whitespace character of the {0:s} must be a # not a '{1:s}'."
                              .format("uploaded file" if isFileUploaded else "text area", firstCharacterFound))

        return errors


class _FlatFileDefinitions(ConceptCollection):
    """Create a set of concept definitions from a flat file input source."""

    def __init__(self, fileConceptDefinitions):
        """Initialise the set of concept definitions from a flat file input source.

        Terms and codes for a concept can be specified as negative or positive terms. If there is no header for a set
        of terms/codes (i.e. it is not specified whether they are negative or positive), then they are assumed to
        be positive.

        :param fileConceptDefinitions:  The location of the file containing the concept definitions.
        :type fileConceptDefinitions:   str

        """

        # Initialise the super class.
        super(_FlatFileDefinitions).__init__(fileConceptDefinitions)

        # Compile the needed regular expressions.
        codeCleaner = re.compile("\.+$")  # Used to strip trailing full stops from codes.

        # Extract concept definitions.
        currentConcept = None  # The current concept having its terms/codes extracted.
        currentSection = "Positive"  # Whether the current terms/codes being extracted are positive or negative terms.
        with open(fileConceptDefinitions, 'r') as fidConceptDefinitions:
            for line in fidConceptDefinitions:
                line = line.strip()
                if not line:
                    # The line has no content on it.
                    pass
                elif line[0] == '#':
                    # Found the start of a new concept.
                    currentConcept = line[1:].strip()  # Record the new concept.
                    if currentConcept not in self._concepts:
                        # If the current concept is not in the list of concepts, then add it.
                        self._concepts.append(currentConcept)
                    currentSection = "Positive"  # Reset the default term/code type back to positive.
                elif line[0] == "$":
                    # Found a control term. Check whether it indicates positive or negative aspects of a concept.
                    cleanedLine = line[1:].strip()
                    if cleanedLine.lower() == "positive":
                        currentSection = "Positive"
                    elif cleanedLine.lower() == "negative":
                        currentSection = "Negative"
                elif line[0] == '>':
                    # Found a concept defining code.
                    code = line[1:].strip()
                    # Clean the code. Remove all trailing full stops.
                    code = codeCleaner.sub('', code)
                    self._conceptDefinitions[currentConcept][currentSection]["Codes"].append(code)
                elif line[0] == '%':
                    # Found a comment line.
                    pass
                else:
                    # Found a concept defining term.
                    cleanTerm = cleaners.term_cleaner(line)  # Remove excess whitespace from the term.
                    self._conceptDefinitions[currentConcept][currentSection]["Terms"].append(cleanTerm)


class _JSONDefinitions(ConceptCollection):
    """Create a set of concept definitions from a JSON input source."""

    def __init__(self, fileConceptDefinitions):
        """Initialise the set of concept definitions from a JSON input source.

        :param fileConceptDefinitions:  The location of the file containing the concept definitions.
        :type fileConceptDefinitions:   str

        """

        # Initialise the super class.
        super(_JSONDefinitions).__init__(fileConceptDefinitions)

        # Compile the needed regular expressions.
        codeCleaner = re.compile("\.+$")  # Used to strip trailing full stops from codes.

        # Load the definitions.
        fidConceptDefinitions = open(fileConceptDefinitions, 'r')
        jsonContent = json.load(fidConceptDefinitions)
        fidConceptDefinitions.close()

        # Remove unnecessary fields and convert any term/code values that are dictionaries to lists. The conversion
        # just keeps the keys from the dictionary, but will result in an arbitrary ordering.
        for concept in jsonContent:
            # Iterate through concepts.
            for field in jsonContent[concept]:
                # Iterate through the level where positive and negative fields should be.
                if field in ["Positive", "Negative"]:
                    for definition in jsonContent[concept][field]:
                        # Iterate through the level where term and code fields should be.
                        if definition == "Codes":
                            # Clean the codes to remove training spaces.
                            self._conceptDefinitions[concept][field][definition] = \
                                [codeCleaner.sub('', i) for i in jsonContent[concept][field][definition]]
                        elif definition == "Terms":
                            # Clean the terms to remove excess whitespace.
                            self._conceptDefinitions[concept][field][definition] = \
                                [cleaners.term_cleaner(i) for i in jsonContent[concept][field][definition]]
