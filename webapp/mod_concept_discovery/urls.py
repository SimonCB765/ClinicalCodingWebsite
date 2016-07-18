"""URL endpoints for the pages made available by this blueprint."""

# User imports.
from . import modConceptDiscovery, views


# Home page.
modConceptDiscovery.add_url_rule('/', 'home', view_func=views.home)

# Concept upload page.
modConceptDiscovery.add_url_rule('/upload_concepts', 'upload_concepts', methods=["GET", "POST"],
                                 view_func=views.upload_concepts)
