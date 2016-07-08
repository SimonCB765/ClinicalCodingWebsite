"""URL endpoints for the pages made available by this module."""

# User imports.
from . import modConceptDiscovery, views


# Home page.
modConceptDiscovery.add_url_rule('/', 'home', view_func=views.home)
