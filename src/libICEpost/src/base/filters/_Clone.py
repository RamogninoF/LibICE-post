#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino (federico.ramognino@polimi.it)
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

#load the base class
from ._Filter import Filter

#Other imports
import numpy as np

from libICEpost import Dictionary
from libICEpost.src.base.Functions.runtimeWarning import helpOnFail

from typing import Iterable

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class Clone(Filter):
    """
    A filter that does nothing. It is used to clone the data without
    any modification.
    """
    
    #########################################################################
    #Properties:
    
    #########################################################################
    #Class methods and static methods:
    @classmethod
    @helpOnFail
    def fromDictionary(cls, dictionary):
        """
        Create from dictionary (nothing needed).
        
        Args:
            dictionary (dict): the dictionary with the entries
        
        Returns:
            `Clone`: the Clone filter object
        """
        return cls()
    
    #########################################################################
    def __init__(self):
        """
        Create an empty filter.
        """
        #Nothing to do
    
    #########################################################################
    #Dunder methods:
    def __call__(self, xp:Iterable[float], yp:Iterable[float])-> tuple[np.ndarray[float], np.ndarray[float]]:
        #Type checking and recasting to numpy arrays
        xp, yp = Filter.__call__(self, xp, yp)
        
        #Just clone
        return xp, yp
    

#########################################################################
#Add to selection table of Base
Filter.addToRuntimeSelectionTable(Clone)
