"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023

database (variables are stored at sourcing of the packages)
"""

import os
from ._DatabaseClass import _DatabaseClass

location = os.path.dirname(__file__) + "/"

database = _DatabaseClass("database")