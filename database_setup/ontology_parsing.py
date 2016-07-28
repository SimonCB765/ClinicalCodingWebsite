"""Functions to generate the files needed to load the concept hierarchies into Neo4j."""

# Python imports.
import gzip
import os
import re

# User imports.
from webapp.utilities import cleaners


def main(dirNeo4jData, readV2Files):
    """Parse the ontology data files and generate the outputs needed by the Neo4j data loader.

    :param dirNeo4jData:    The directory containing the files of the formatted data to be loaded into Neo4j.
    :type dirNeo4jData:     str
    :param readV2Files:     The locations where the current and previous version of the Read V2 ontology can be found.
    :type readV2Files:      list

    """

    # Create the output locations for the Neo4j data files.
    fileAddConcepts = os.path.join(dirNeo4jData, "Concepts_Add.tsv")
    fileAddTerms = os.path.join(dirNeo4jData, "Terms_Add.tsv")
    fileAddWords = os.path.join(dirNeo4jData, "Words_Add.tsv")
    fileAddRelationships = os.path.join(dirNeo4jData, "Relationships_Add.tsv")
    fileUpdateConcepts = os.path.join(dirNeo4jData, "Concepts_Update.tsv")
    fileUpdateTerms = os.path.join(dirNeo4jData, "Terms_Update.tsv")
    fileUpdateRelationships = os.path.join(dirNeo4jData, "Relationships_Update.tsv")
    fileRemoveConcepts = os.path.join(dirNeo4jData, "Concepts_Remove.tsv")
    fileRemoveTerms = os.path.join(dirNeo4jData, "Terms_Remove.tsv")
    fileRemoveWords = os.path.join(dirNeo4jData, "Words_Remove.tsv")
    fileRemoveRelationships = os.path.join(dirNeo4jData, "Relationships_Remove.tsv")

    # Generate the Neo4j data.
    with open(fileAddConcepts, 'w') as fidAddConcepts, open(fileUpdateConcepts, 'w') as fidUpdateConcepts, \
            open(fileRemoveConcepts, 'w') as fidRemoveConcepts, open(fileAddTerms, 'w') as fidAddTerms, \
            open(fileUpdateTerms, 'w') as fidUpdateTerms, open(fileRemoveTerms, 'w') as fidRemoveTerms, \
            open(fileAddWords, 'w') as fidAddWords, open(fileRemoveWords, 'w') as fidRemoveWords, \
            open(fileAddRelationships, 'w') as fidAddRelationships, \
            open(fileUpdateRelationships, 'w') as fidUpdateRelationships, \
            open(fileRemoveRelationships, 'w') as fidRRemoveRelationships:
        # Add the headers for the Neo4j files.
        for i in [fidAddConcepts, fidUpdateConcepts, fidRemoveConcepts]:
            i.write("ID\tCurrent\tDomain\tLevel\tLabels\n")
        for i in [fidAddTerms, fidUpdateTerms, fidRemoveTerms]:
            i.write("ID\tCurrent\tPretty\tSearchable\tLabels\n")
        for i in [fidAddWords, fidRemoveWords]:
            i.write("Word\tLabels\n")
        for i in [fidAddRelationships, fidUpdateRelationships, fidRRemoveRelationships]:
            i.write("Node_1\tNode_1_Label\tNode_2\tNode_2_Label\tType\tRelationship_Labels\n")

        # The words may occur in multiple ontologies, so must be recorded across them (unlike the concepts and terms).
        allCurrentWords = set()
        allPreviousWords = set()

        # Parse the Read V2 data.
        currentConcepts, currentTerms, currentWords, currentRelationships = parse_ReadV2(readV2Files[0])
        previousConcepts, previousTerms, previousWords, previousRelationships = parse_ReadV2(readV2Files[1])

        # Add the words found to the records of the words in the current and previous hierarchies.
        allCurrentWords |= currentWords
        allPreviousWords |= previousWords

        # Record the concept updates needed.
        conceptsToAdd = currentConcepts.keys() - previousConcepts.keys()
        conceptsToAdd = [currentConcepts[i] for i in sorted(conceptsToAdd)]
        fidAddConcepts.write('\n'.join(conceptsToAdd))
        fidAddConcepts.write('\n')
        conceptsToUpdate = [currentConcepts[i] for i in currentConcepts
                            if i in previousConcepts and currentConcepts[i] != previousConcepts[i]]
        fidUpdateConcepts.write('\n'.join(conceptsToUpdate))
        fidUpdateConcepts.write('\n')
        conceptsToRemove = previousConcepts.keys() - currentConcepts.keys()
        conceptsToRemove = ["{0:s}\t\t\t\t\t\t\tReadV2_Concept".format(i) for i in conceptsToRemove]
        fidRemoveConcepts.write('\n'.join(conceptsToRemove))
        fidRemoveConcepts.write('\n')

        # Record the term updates needed.
        termsToAdd = currentTerms.keys() - previousTerms.keys()
        termsToAdd = [currentTerms[i] for i in termsToAdd]
        fidAddTerms.write('\n'.join(termsToAdd))
        fidAddTerms.write('\n')
        termsToUpdate = [currentTerms[i] for i in currentTerms
                         if i in previousTerms and currentTerms[i] != previousTerms[i]]
        fidUpdateTerms.write('\n'.join(termsToUpdate))
        fidUpdateTerms.write('\n')
        termsToRemove = previousTerms.keys() - currentTerms.keys()
        termsToRemove = ["{0:s}\t\t\t\t\t\t\tReadV2_Term".format(i) for i in termsToRemove]
        fidRemoveTerms.write('\n'.join(termsToRemove))
        fidRemoveTerms.write('\n')

        # Record the relationship updates needed.
        relationshipsToAdd = currentRelationships.keys() - previousRelationships.keys()
        relationshipsToAdd = [currentRelationships[i] for i in relationshipsToAdd]
        fidAddRelationships.write('\n'.join(relationshipsToAdd))
        fidAddRelationships.write('\n')
        relationshipsToUpdate = [currentRelationships[i] for i in currentRelationships
                                 if i in previousRelationships and currentRelationships[i] != previousRelationships[i]]
        fidUpdateRelationships.write('\n'.join(relationshipsToUpdate))
        fidUpdateRelationships.write('\n')
        relationshipsToRemove = previousRelationships.keys() - currentRelationships.keys()
        relationshipsToRemove = [previousRelationships[i] for i in relationshipsToRemove]
        fidRRemoveRelationships.write('\n'.join(relationshipsToRemove))
        fidRRemoveRelationships.write('\n')

        # Determine the words to add and remove.
        wordsToAdd = allCurrentWords - allPreviousWords
        wordsToAdd = ["{0:s}\tWord".format(i) for i in wordsToAdd]
        fidAddWords.write('\n'.join(wordsToAdd))
        wordsToRemove = allPreviousWords - allCurrentWords
        wordsToRemove = ["{0:s}\tWord".format(i) for i in wordsToRemove]
        fidRemoveWords.write('\n'.join(wordsToRemove))


def parse_CTV3():
    pass


def parse_ReadV2(fileReadV2Data):
    """Identify the concepts, terms, words and relationships in a version of the Read V2 ontology.

    :param fileReadV2Data:  The location where the Read V2 ontology data can be found.
    :type fileReadV2Data:   str
    :return:                The concepts, terms, words and relationships needed to model the Read V2 hierarchy.
    :rtype:                 set, set, set, list

    """

    # Create the collection of concepts (and their domains), terms, words and relationships.
    concepts = dict()
    domains = dict()
    terms = dict()
    words = set()
    relationships = dict()

    # Compile the regular expression needed.
    wordFinder = re.compile("\s+")  # Expression to split words based on arbitrary whitespace between them.
    bracketFinder = re.compile("(\[.*?\])\s*")  # Used to remove bracketed contents in a description.

    # Parse the Read V2 data.
    with gzip.open(fileReadV2Data, 'r') as fidReadV2Data:
        for line in fidReadV2Data:
            # Lines are delimited by commas, with each entry on the line enclosed in quotes. For example:
            # "MELLITUS","02","Type 1 diabetes mellitus","","","00","EN","C10E.","0"
            line = str(line.strip(), "utf-8")  # Convert bytes string to UTF-8.
            chunks = line.split('","')
            chunks[0] = chunks[0][1:]  # Strip the " at the stat of the first entry.
            chunks[-1] = chunks[-1][:-1]  # Strip the " at the end of the last entry.

            # Get the elements of the entry that are of interest. These would be the concept ID, term ID and the
            # longest recorded term description. The term IDs are problematic, as they are specific to a given concept
            # and not unique across the whole hierarchy. For example, the primary term for every concept has ID 00.
            # To get around this we append the concept ID to the front of each term ID.
            conceptID = chunks[7].replace('.', '')  # Remove trailing full stops from the concept ID.
            termIDRoot = chunks[5]
            termID = "{0:s}_{1:s}".format(conceptID, termIDRoot)
            description = chunks[4] if chunks[4] else (chunks[3] if chunks[3] else chunks[2])
            descriptionLower = description.lower()

            # Determine the words the term contains.
            # First, alter descriptions that start with something like [V]XXX by removing the [V] so that the XXX can
            # be matched as a real word.
            # Second, split the description into words using whitespace as a delimiter.
            # Third, clean the set of words.
            splittableDescription = descriptionLower
            isBracketedStart = bracketFinder.match(splittableDescription)
            if isBracketedStart:
                splittableDescription = splittableDescription[isBracketedStart.span()[1]:]
            termWords = cleaners.input_word_cleaner(wordFinder.split(splittableDescription))
            words = words.union(termWords)

            # Record the term's attributes. Read V2 has no concept of non-current terms, so all are current.
            terms[termID] = "{0:s}\ttrue\t{1:s}\t{2:s}\tReadV2_Term".format(termID, description, descriptionLower)

            # Record the concept's attributes. Read V2 has no concept of non-current concepts, so all are current.
            # The domain of a concept is the primary description of the top level singe character concept for the given
            # concept (e.g. C for C10E). This will not always be known at the time a concept is being recorded, so will
            # be gathered after the file is processed.
            concepts[conceptID] = "{0:s}\ttrue\t{1:s}\t{2:d}\tReadV2_Concept".format(conceptID, "{0:s}", len(conceptID))

            # Add the relationships between the term and the words it contains.
            for i in termWords:
                key = tuple(sorted([termID, i]))
                relationships[key] = "{0:s}\tReadV2_Term\t{1:s}\tWord\t\tContains".format(termID, i)

            # Add the relationship between the concept and the term. For every concept, term ID 00 indicates the
            # primary term, and all other terms are secondary.
            key = tuple(sorted([conceptID, termID]))
            relationships[key] = "{0:s}\tReadV2_Concept\t{1:s}\tReadV2_Term\t\tDescribedBy,{2:s}".format(
                conceptID, termID, "Primary" if termIDRoot == "00" else '')

            # Add the relationship between the code and its parent. Read V2 parent relationships do not have a 'type',
            # so each parent relationship is given the default type parent.
            if len(conceptID) > 1:
                # If the concept consists of at least 2 characters, then it has a parent and is therefore the child of
                # that parent.
                key = tuple(sorted([conceptID, conceptID[:-1]]))
                relationships[key] = "{0:s}\tReadV2_Concept\t{1:s}\tReadV2_Concept\tparent\tParent".format(
                    conceptID, conceptID[:-1])
            elif termIDRoot == "00":
                # The code is only one character long, and therefore is the domain for all codes below it.
                domains[conceptID] = description

    # Add the domain information to the concepts.
    for i in concepts:
        concepts[i] = concepts[i].format(domains["{0:s}".format(i[0])])

    return concepts, terms, words, relationships


def SNOMED_CT():
    pass
