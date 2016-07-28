"""Code to initiate the database updating."""

# Python imports.
import os

# User imports.
from . import ontology_parsing
from . import update_database


def main(databaseURI, databaseUsername, databasePassword):
    """

    :param databaseURI:         The location of the database.
    :type databaseURI:          str
    :param databaseUsername:    The username used to access the database.
    :type databaseUsername:     str
    :param databasePassword:    The password used to access the database.
    :type databasePassword:     str

    """

    # Run the parsing.
    dirCurrent = os.path.dirname(os.path.join(os.getcwd(), __file__))  # Directory containing this file.
    dirData = os.path.abspath(os.path.join(dirCurrent, "Data"))
    dirNeo4jData = os.path.join(dirData, "Neo4jData")
    os.makedirs(dirNeo4jData, exist_ok=True)  # Create the directory to hold the data needed for the Neo4j database.
    readV2Files = [os.path.join(dirData, "Current", "ReadV2Data.gz"), os.path.join(dirData, "Previous", "ReadV2Data.gz")]
    ontology_parsing.main(dirNeo4jData, readV2Files)

    # Update the database.
    update_database.main(dirNeo4jData, databaseURI, databaseUsername, databasePassword)
