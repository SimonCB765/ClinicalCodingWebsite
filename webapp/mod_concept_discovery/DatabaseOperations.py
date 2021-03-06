"""Class for running concept related queries on a Neo4j database of clinical codes."""

# 3rd party imports.
import neo4j.v1 as neo


class DatabaseOperations(object):
    """Class defining high level queries to run on a Neo4j database of clinical code."""

    def __init__(self, databaseAddress, username, password):
        """Initialise an object.

        :param databaseAddress:     The location of the database to connect to.
        :type databaseAddress:      str
        :param username:            The username used to access the database.
        :type username:             str
        :param password:            The password associated with the username.
        :type password:             str

        """

        self._databaseAddress = databaseAddress
        self._username = username
        self._password = password

    def get_codes_from_phrases(self, phrases, codeFormats):
        """Get the codes that have a description where all the supplied quoted phrases match.

        Each entry in quoted should contain a set of phrase strings, all of which must be found in a given
        code's description before the code will be returned for that entry.

        The search is case insensitive.

        :param phrases:     Sets of phrases. Each entry should contain a set of phrases, all of which must be found in
                                a code's description before the code is deemed a match.
        :type phrases:      list
        :param codeFormats: The code formats to look through when extracting descriptions. Acceptable values are
                                "ReadV2", "CTV3" and "SNOMED_CT".
        :type codeFormats:  list
        :return:            A list of dictionaries. The list contains one element per entry in phrases, with the
                                returned list at index i containing the result for entry phrases[i]. The ith returned
                                dictionary will contain a subset of the entries in codeFormats as its keys. An entry
                                from codeFormats is present as a key when a code from that hierarchy contained all the
                                phrases in phrases[i]. For example:
                                words = [["kidney disease"], ["fOo foo", "BaR"], ["type 1", "diabetes"]]
                                codeFormats = ["ReadV2", "CTV3"]
                                result = [
                                            {"ReadV2": {"A", "B", "C"}},
                                            {},
                                            {"ReadV2": {"X", "Y"}, "CTV3": {"C1", "C2", "C3", "X", "Y"}}
                                         ]
                                These results would indicate that the phrase "kidney disease" were found in three
                                code descriptions in the ReadV2 hierarchy (A, B and C), but none in the CTV3 hierarchy.
                                The phrases "foo foo" and "bar" were found together in no code descriptions.
                                The phrases "type 1" and "diabetes" were found together in descriptions of codes in both
                                the ReadV2 and CTV3 hierarchies.
        :rtype:             list

        """

        # Get access to the database.
        driver = neo.GraphDatabase.driver(self._databaseAddress, auth=neo.basic_auth(self._username, self._password))
        session = driver.session()

        # Go through each set of phrases and select only the codes that contain all phrases in their description.
        returnValue = []
        for i in phrases:
            uniquePhrases = set([j.lower() for j in i])  # Remove any duplicate phrases and make them all lowercase.
            queryResults = {}
            for j in codeFormats:
                result = session.run("MATCH (c:{0:s}) -[:DescribedBy]-> (t:{1:s}) "
                                     "WHERE ALL(phrase IN ['{1:s}'] WHERE t.searchable CONTAINS phrase) "
                                     "RETURN c.code AS code"
                                     .format("{0:s}_Concept".format(j), "{0:s}_Term".format(j),
                                             "', '".join(uniquePhrases)))
                queryResults[j] = {k["code"] for k in result}

            # Record the codes with a description that contains all the words in the current bag of words.
            returnValue.append(queryResults)

        # Close the session.
        session.close()

        return returnValue

    def get_codes_from_words(self, words, codeFormats):
        """Get codes based on bags of words.

        Each entry in words should contain a list of words, all of which must be present in a code's description
        before the code will be returned for that entry. The search is case insensitive.

        :param words:       The words to find codes for. Each entry should contain a list of words, all of which must be
                                present in a code's description before the code is deemed to be a match. Each word is
                                assumed to be a string.
        :type words:        list
        :param codeFormats: The code formats to look through when extracting descriptions. Acceptable values are
                                "ReadV2", "CTV3" and "SNOMED_CT".
        :type codeFormats:  list
        :return:            A list of dictionaries. The list contains one element per entry in words, with the returned
                                list at index i containing the result for entry words[i]. Each returned dictionary
                                will contain a subset of the entries in codeFormats as its keys. An entry from
                                codeFormats is present as a key when a code from that hierarchy contained all the words
                                in the bag. For example:
                                words = [["kidney", "disease"], ["fOo", "BaR"], ["type", "diabetes"]]
                                codeFormats = ["ReadV2", "CTV3"]
                                result = [
                                            {"ReadV2": {"A", "B", "C"}},
                                            {},
                                            {"ReadV2": {"X", "Y"}, "CTV3": {"C1", "C2", "C3", "X", "Y"}}
                                         ]
                                These results would indicate that the words "kidney" and "disease" were found in three
                                code descriptions in the ReadV2 hierarchy (A, B and C), but none in the CTV3 hierarchy.
                                The words "foo" and "bar" were found together in no code descriptions.
                                The words "type" and "diabetes" were found together in descriptions of codes in both
                                the ReadV2 and CTV3 hierarchies.
        :rtype:             list

        """

        # Get access to the database.
        driver = neo.GraphDatabase.driver(self._databaseAddress, auth=neo.basic_auth(self._username, self._password))
        session = driver.session()

        # Go through each bag of words and select only the codes that contain all words in the bag in their description.
        returnValue = []
        for i in words:
            # Find all codes that have a relationship with every word in the bag of words. The method used here relies
            # on each word having a unique node.
            wordBag = {j.lower() for j in i}  # Remove any duplicate words and convert all words to lowercase.
            queryResults = {}
            for j in codeFormats:
                result = session.run("MATCH (c:{0:s}) -[:DescribedBy]-> (:{1:s}) -[:Contains]-> (w:Word) "
                                     "WHERE w.word IN ['{2:s}'] "
                                     "WITH c.code AS code, COLLECT(w.word) AS words "
                                     "WHERE length(words) = {3:d} "
                                     "RETURN code"
                                     .format("{0:s}_Concept".format(j), "{0:s}_Term".format(j),
                                             "', '".join(wordBag), len(wordBag)))
                queryResults[j] = {k["code"] for k in result}

            # Record the codes with a description that contains all the words in the current bag of words.
            returnValue.append(queryResults)

        # Close the session.
        session.close()

        return returnValue

    def get_descriptions(self, codes, codeFormats):
        """Get the descriptions of a list of codes.

        :param codes:       The codes to extract the descriptions for.
        :type codes:        list
        :param codeFormats: The code formats to look through when extracting descriptions. Acceptable values are
                                "ReadV2", "CTV3" and "SNOMED_CT".
        :type codeFormats:  list
        :return:            The descriptions of the input codes. Each input code is treated as a key in the returned
                                dictionary. The value associated with a code is a dictionary mapping the codeFormats
                                to the description of the code in that format. For example:
                                codes = ["A", "B", "C"]
                                codeFormats = ["ReadV2", "CTV3"]
                                return = {
                                            "A": {"ReadV2": "XXX"},
                                            "B": {"CTV3": "YYY"},
                                            "C": {"ReadV2": "ZZZ-0", "CTV3": "ZZZ-00"}
                                         }
                                Code A was only present in the Read v2 hierarchy, B in the CTV3 hierarchy and C in both.
        :rtype:             dict

        """

        # Get access to the database.
        driver = neo.GraphDatabase.driver(self._databaseAddress, auth=neo.basic_auth(self._username, self._password))
        session = driver.session()

        # Get the descriptions.
        descriptions = {i: {} for i in codes}
        for i in codeFormats:
            result = session.run("MATCH (c:{0:s}) -[r:DescribedBy]-> (t:{1:s}) "
                                 "WHERE c.code IN ['{2:s}'] "
                                 "RETURN c.code AS code, t.pretty AS description"
                                 .format("{0:s}_Concept".format(i), "{0:s}_Term".format(i), "', '".join(codes)))
            for j in result:
                descriptions[j["code"]][i] = j["description"]

        # Close the session.
        session.close()

        # Generate the return values.
        return descriptions
