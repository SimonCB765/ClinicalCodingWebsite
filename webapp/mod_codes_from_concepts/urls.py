"""URL endpoints for the pages made available by this blueprint."""

# User imports.
from . import modCodesFromConcepts, views


# Concept upload page.
modCodesFromConcepts.add_url_rule('/', 'get_codes', methods=["GET", "POST"],
                                  view_func=views.get_codes)

# Extraction task status polling url.
modCodesFromConcepts.add_url_rule('/extraction_task_status/<taskID>', 'extraction_task_status', methods=["GET"],
                                  view_func=views.extraction_task_status)

# Concept and viewer update task status polling url.
modCodesFromConcepts.add_url_rule('/update_task_status/<taskID>', 'update_task_status', methods=["GET"],
                                  view_func=views.update_task_status)
