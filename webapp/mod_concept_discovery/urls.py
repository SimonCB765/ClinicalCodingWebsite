"""URL endpoints for the pages made available by this blueprint."""

# User imports.
from . import modConceptDiscovery, views


# Concept upload page.
modConceptDiscovery.add_url_rule('/', 'upload_concepts', methods=["GET", "POST"],
                                 view_func=views.upload_concepts)

# Concept result viewing page.
modConceptDiscovery.add_url_rule('/<taskID>', 'view_concepts', methods=["GET"],
                                 view_func=views.view_concepts)

# Task status polling url.
modConceptDiscovery.add_url_rule('/task_status/<taskID>', 'task_status', methods=["GET"],
                                 view_func=views.task_status)
