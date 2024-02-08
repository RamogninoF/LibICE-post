"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023

database (variables are stored at sourcing of the packages)
"""

import os
from ._DatabaseClass import _DatabaseClass

location = os.path.dirname(__file__) + "/"

database = _DatabaseClass("database")

#TODO:
#Reformat the whole structure so that:
#   1)  every _DatabaseClass instance has an interface method 
#       from_file(file_name, file_format, entries=None) which 
#       redirects the user to a specific loader (e.g. from_json) 
#       which by default rise NotImplementedError.
#       Then, redefine every portion of the database as a subclass
#       of _DatabaseClass whith specific 'from_<file_format>' methods.
#   2)  In the solver, add a method with which the user can add new 
#       entries to the database exploiting these features.