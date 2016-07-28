"""Code to initiate the database updating."""

# Python imports.
import os
import sys

# User imports.
dirCurrent = os.path.dirname(os.path.join(os.getcwd(), __file__))  # Directory containing this file.
if __package__ == "database_setup":
    # If the package is database_setup, then relative imports are needed.
    from . import ontology_parsing
else:
    # The code was not called from within the webapp directory using 'python -m database_setup'. Therefore, we need to
    # add the top level directory to the search path and use absolute imports.
    dirTopLevel = os.path.abspath(os.path.join(dirCurrent, os.pardir))
    sys.path.append(dirTopLevel)
    from database_setup import ontology_parsing


# Run the parsing.
dirData = os.path.abspath(os.path.join(dirCurrent, "Data"))
dirNeo4jData = os.path.join(dirData, "Neo4jData")
os.makedirs(dirNeo4jData, exist_ok=True)  # Create the directory to hold the data needed for the Neo4j database.
readV2Files = [os.path.join(dirData, "Current", "ReadV2Data.gz"), os.path.join(dirData, "Previous", "ReadV2Data.gz")]
ontology_parsing.main(dirNeo4jData, readV2Files)
