"""Update a Neo4j database of concepts."""

# Python imports.
import logging
import os

# 3rd party imports.
import neo4j.v1 as neo

# Globals.
LOGGER = logging.getLogger(__name__)


def main(dirNeo4jData, databaseURI, databaseUsername, databasePassword, formatsSupported=("ReadV2",),
         transactionSize=500, delimiter='\t'):
    """

    :param dirNeo4jData:        The directory containing the files of the formatted data to be loaded into Neo4j.
    :type dirNeo4jData:         str
    :param databaseURI:         The location of the database.
    :type databaseURI:          str
    :param databaseUsername:    The username used to access the database.
    :type databaseUsername:     str
    :param databasePassword:    The password used to access the database.
    :type databasePassword:     str
    :param formatsSupported:    The concept formats (e.g. Read V2) supported by the database.
    :type formatsSupported:     list
    :param transactionSize:     The number of lines from the files to read before committing a transaction.
    :type transactionSize:      int
    :param delimiter:           The delimiter used to split up the fields on each line of the file.
    :type delimiter:            str

    """

    # Get access to the database.
    driver = neo.GraphDatabase.driver(databaseURI, auth=neo.basic_auth(databaseUsername, databasePassword))
    session = driver.session()

    # Create constraints and indices as a single transaction.
    constraintTransaction = session.begin_transaction()

    # Ensure each word is unique (and set up the index as a side effect).
    constraintTransaction.run("CREATE CONSTRAINT ON (word:Word) ASSERT word.word IS UNIQUE")

    # For each concept hierarchy, ensure that all concepts and terms within it are unique (thereby indexing them).
    # Also add an index on the stale attribute
    for i in formatsSupported:
        constraintTransaction.run("CREATE CONSTRAINT ON (concept:{0:s}_Concept) ASSERT concept.id IS UNIQUE".format(i))
        constraintTransaction.run("CREATE CONSTRAINT ON (concept:{0:s}_Term) ASSERT concept.id IS UNIQUE".format(i))
    constraintTransaction.commit()

    #----------------------------------#
    # Update the Words in the Database #
    #----------------------------------#
    # Remove words that are no longer needed.
    transactionLines = 0  # Record of the number of lines used to construct the current transaction.
    with open(os.path.join(dirNeo4jData, "Words_Remove.tsv"), 'r') as fidWordsRemove:
        _ = fidWordsRemove.readline()  # Strip off the header.
        wordTransaction = session.begin_transaction()  # Start the first transaction.
        for line in fidWordsRemove:
            word = line.strip()
            wordTransaction.run("DETACH DELETE (w:Word {{word: \"{0:s}\"}})".format(word))
            transactionLines += 1

            # Determine if a new transaction needs creating.
            if transactionLines == transactionSize:
                wordTransaction.commit()
                wordTransaction = session.begin_transaction()  # Start the next transaction.
                transactionLines = 0
        wordTransaction.commit()  # Commit the final transaction.

    # Add new words.
    transactionLines = 0  # Record of the number of lines used to construct the current transaction.
    with open(os.path.join(dirNeo4jData, "Words_Add.tsv"), 'r') as fidWordsAdd:
        _ = fidWordsAdd.readline()  # Strip off the header.
        wordTransaction = session.begin_transaction()  # Start the first transaction.
        for line in fidWordsAdd:
            word = line.strip()
            wordTransaction.run("CREATE (w:Word {{word: \"{0:s}\"}})".format(word))
            transactionLines += 1

            # Determine if a new transaction needs creating.
            if transactionLines == transactionSize:
                wordTransaction.commit()
                wordTransaction = session.begin_transaction()  # Start the next transaction.
                transactionLines = 0
        wordTransaction.commit()  # Commit the final transaction.

    #----------------------------------#
    # Update the Terms in the Database #
    #----------------------------------#
    # Remove terms that are no longer needed.
    transactionLines = 0  # Record of the number of lines used to construct the current transaction.
    with open(os.path.join(dirNeo4jData, "Terms_Remove.tsv"), 'r') as fidTermsRemove:
        _ = fidTermsRemove.readline()  # Strip off the header.
        termTransaction = session.begin_transaction()  # Start the first transaction.
        for line in fidTermsRemove:
            term, current, prettyDescription, searchableDescription, label = (line.strip()).split(delimiter)
            termTransaction.run("DETACH DELETE (t:{0:s} {{id: \"{1:s}\"}})".format(label, term))
            transactionLines += 1

            # Determine if a new transaction needs creating.
            if transactionLines == transactionSize:
                termTransaction.commit()
                termTransaction = session.begin_transaction()  # Start the next transaction.
                transactionLines = 0
        termTransaction.commit()  # Commit the final transaction.

    # Update existing terms.
    transactionLines = 0  # Record of the number of lines used to construct the current transaction.
    with open(os.path.join(dirNeo4jData, "Terms_Update.tsv"), 'r') as fidTermsUpdate:
        _ = fidTermsUpdate.readline()  # Strip off the header.
        termTransaction = session.begin_transaction()  # Start the first transaction.
        for line in fidTermsUpdate:
            term, current, prettyDescription, searchableDescription, label = (line.strip()).split(delimiter)
            termTransaction.run("MERGE (t:{0:s} {{id: \"{1:s}\"}}) "
                                "SET t = {{current: \"{2:s}\", pretty: \"{3:s}\", searchable: \"{4:s}\"}}"
                                .format(label, term, current, prettyDescription, searchableDescription))
            transactionLines += 1

            # Determine if a new transaction needs creating.
            if transactionLines == transactionSize:
                termTransaction.commit()
                termTransaction = session.begin_transaction()  # Start the next transaction.
                transactionLines = 0
        termTransaction.commit()  # Commit the final transaction.

    # Add new terms.
    transactionLines = 0  # Record of the number of lines used to construct the current transaction.
    with open(os.path.join(dirNeo4jData, "Terms_Add.tsv"), 'r') as fidTermsAdd:
        _ = fidTermsAdd.readline()  # Strip off the header.
        termTransaction = session.begin_transaction()  # Start the first transaction.
        for line in fidTermsAdd:
            term, current, prettyDescription, searchableDescription, label = (line.strip()).split(delimiter)
            termTransaction.run("CREATE (t:{0:s} {{id: \"{1:s}\", pretty: \"{2:s}\", searchable: \"{3:s}\", "
                                "current: \"{4:s}\"}})"
                                .format(label, term, prettyDescription, searchableDescription, current))
            transactionLines += 1

            # Determine if a new transaction needs creating.
            if transactionLines == transactionSize:
                termTransaction.commit()
                termTransaction = session.begin_transaction()  # Start the next transaction.
                transactionLines = 0
        termTransaction.commit()  # Commit the final transaction.

    #-------------------------------------#
    # Update the Concepts in the Database #
    #-------------------------------------#
    # Remove concepts that are no longer needed.
    transactionLines = 0  # Record of the number of lines used to construct the current transaction.
    with open(os.path.join(dirNeo4jData, "Concepts_Remove.tsv"), 'r') as fidConceptsRemove:
        _ = fidConceptsRemove.readline()  # Strip off the header.
        conceptTransaction = session.begin_transaction()  # Start the first transaction.
        for line in fidConceptsRemove:
            concept, current, domain, level, label = (line.strip()).split(delimiter)
            conceptTransaction.run("DETACH DELETE (c:{0:s} {{id: \"{1:s}\"}})".format(label, concept))
            transactionLines += 1

            # Determine if a new transaction needs creating.
            if transactionLines == transactionSize:
                conceptTransaction.commit()
                conceptTransaction = session.begin_transaction()  # Start the next transaction.
                transactionLines = 0
        conceptTransaction.commit()  # Commit the final transaction.

    # Update existing terms.
    transactionLines = 0  # Record of the number of lines used to construct the current transaction.
    with open(os.path.join(dirNeo4jData, "Concepts_Update.tsv"), 'r') as fidConceptsUpdate:
        _ = fidConceptsUpdate.readline()  # Strip off the header.
        conceptTransaction = session.begin_transaction()  # Start the first transaction.
        for line in fidConceptsUpdate:
            concept, current, domain, level, label = (line.strip()).split(delimiter)
            conceptTransaction.run("MERGE (c:{0:s} {{id: \"{1:s}\"}}) "
                                   "SET t = {{current: \"{2:s}\", domain: \"{3:s}\", level: toInt({4:s})}}"
                                   .format(label, concept, current, domain, level))

            # Determine if a new transaction needs creating.
            if transactionLines == transactionSize:
                conceptTransaction.commit()
                conceptTransaction = session.begin_transaction()  # Start the next transaction.
                transactionLines = 0
        conceptTransaction.commit()  # Commit the final transaction.

    # Add new terms.
    transactionLines = 0  # Record of the number of lines used to construct the current transaction.
    with open(os.path.join(dirNeo4jData, "Concepts_Add.tsv"), 'r') as fidConceptsAdd:
        _ = fidConceptsAdd.readline()  # Strip off the header.
        conceptTransaction = session.begin_transaction()  # Start the first transaction.
        for line in fidConceptsAdd:
            concept, current, domain, level, label = (line.strip()).split(delimiter)
            conceptTransaction.run("CREATE (c:{0:s} {{id: \"{1:s}\", current: \"{2:s}\", domain: \"{3:s}\", "
                                   "level: toInt({4:s})}})"
                                   .format(label, concept, current, domain, level))
            transactionLines += 1

            # Determine if a new transaction needs creating.
            if transactionLines == transactionSize:
                conceptTransaction.commit()
                conceptTransaction = session.begin_transaction()  # Start the next transaction.
                transactionLines = 0
        conceptTransaction.commit()  # Commit the final transaction.

    session.close()
