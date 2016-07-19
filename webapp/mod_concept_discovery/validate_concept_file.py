"""Function to validate a file of concept definitions."""


def main(uploadContents, fileFormat, isFileUploaded):
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
    errorMessage = ""
    if fileFormat == "json":
        # Validate the input in JSON format.
        pass
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
            errorMessage = "The first non-whitespace character of the {0:s} must be a # not a '{1:s}'."\
                .format("uploaded file" if isFileUploaded else "text area", firstCharacterFound)
        elif not contentOnFirstLine:
            # There was not valid content on the first line, and therefore no first concept.
            isValidContents = False
            errorMessage = "The first line with content must contain non-whitespace characters after the #."

    return isValidContents, errorMessage
