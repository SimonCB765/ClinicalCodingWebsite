"""URL endpoints for the pages made available by this blueprint."""

# User imports.
from . import modCore, views


# Home page.
modCore.add_url_rule('/', 'home', view_func=views.home)
