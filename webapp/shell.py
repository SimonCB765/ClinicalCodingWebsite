"""Script to open a console within the Flask environment."""

# Python imports.
import os
import readline
from pprint import pprint

# Flask imports.
from flask import *

# User imports.
from webapp import *

os.environ["PYTHONINSPECT"] = "True"