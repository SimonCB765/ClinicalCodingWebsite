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
