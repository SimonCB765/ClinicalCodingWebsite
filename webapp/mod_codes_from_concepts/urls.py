"""URL endpoints for the pages made available by this blueprint."""

# User imports.
from . import modCodesFromConcepts, views


# Concept upload page.
modCodesFromConcepts.add_url_rule('/', 'get_codes', methods=["GET", "POST"],
                                  view_func=views.get_codes)

# Task status polling url.
modCodesFromConcepts.add_url_rule('/task_status/<taskID>', 'task_status', methods=["GET"],
                                  view_func=views.task_status)