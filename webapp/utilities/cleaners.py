"""Functions to clean various strings needed by the application."""

# Python imports.
import re


def input_word_cleaner(words):
    """Clean a collection of words to remove stop words, undesirable punctuation, etc.

    :param words:   The collection of words to clean.
    :type words:    list
    :return:        The cleaned words.
    :rtype:         list

    """

    # Identify start and stop punctuation to remove.
    endPunctuation = {'.', ',', '-', '+', '*', '%', '&', ':', ';', '?', '!', '[', ']', '{', '}', '(', ')', "'", '=',
                      '"'}

    # Identify the words (e.g. stop words) and hanging punctuation that should be removed.
    wordsToRemove = {'a', "an", "are", "as", "at", "be", "by", "for", "from", "in", "is", "it", "of", "on", "that",
                     "the", "this", "to", "was", "with", "the"}
    wordsToRemove |= endPunctuation

    # Strip words that need removing, and convert all " to ' as " can not be in a Neo4j property value.
    subsetWords = [i for i in words if i not in wordsToRemove]

    # Clean start and end punctuation.
    cleanedWords = []
    for i in subsetWords:
        while i and i[0] in endPunctuation:
            i = i[1:]
        while i and i[-1] in endPunctuation:
            i = i[:-1]
        if i:
            # If there is anything left of the word, then record it.
            cleanedWords.append(i)

    return cleanedWords


def term_cleaner(term):
        """Clean a term by turning consecutive whitespace into a single space.

        Whitespace within quotations is not altered. For example,
        '  the    dog \t\t  " jumped   over   the    "     fence    '
        becomes:
        'the dog " jumped   over   the    " fence'

        :param term:    The term to clean.
        :type term:     str
        :return:        The cleaned term.
        :rtype:         str

        """

        findWhitespace = re.compile("\s+")  # Used to replace white space.

        currentTermIndex = 0  # The current position in the string to begin the whitespace removal at.
        newTerm = ""  # The new whitespace stripped term being constructed.
        for i in re.finditer('(".*?")', term.strip()):
            # Find all sections of non-overlapping quoted characters (matching starts form the left).
            # For each match we take the characters between it and the end of the previous match and convert any
            # whitespace into a single space.
            subString = findWhitespace.sub(' ', term[currentTermIndex:i.span()[0]])
            newTerm += subString + i.group()  # Added the whitespace subbed string and the match to the new term.
            currentTermIndex = i.span()[1] + 1
        subString = findWhitespace.sub(' ', term[currentTermIndex:])  # Substitute in the string after the final match.
        newTerm += subString
        return newTerm
