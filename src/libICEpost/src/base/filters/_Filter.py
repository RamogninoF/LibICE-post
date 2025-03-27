#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino (federico.ramognino@polimi.it)
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

#Import BaseClass class (interface for base classes)
from libICEpost.src.base.BaseClass import BaseClass, abstractmethod
from libICEpost.src.base.Functions.typeChecking import checkType, checkArray

#Other imports
import numpy as np
from typing import Iterable

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################

class Filter(BaseClass):
    """
    Base class for filtering data. A Filter objects can be used to filter 
    the data throught the __call__(x, y) method, which returns the filtered 
    (x, y) data.
    """
    
    #########################################################################
    #Properties:
    
    ################################
    
    #########################################################################
    #Class methods and static methods:
    
    #########################################################################
    #Constructor
    
    #########################################################################
    #Dunder methods:
    @abstractmethod
    def __call__(self, xp:Iterable[float], yp:Iterable[float])-> tuple[np.ndarray[float], np.ndarray[float]]:
        """
        Filter an array of x,y data. Returns x sampling points and y coordinates
        
        Args:
            xp (Iterable[float]): x sampling points
            yp (Iterable[float]): y coordinates
            
        Returns:
            tuple[np.ndarray[float], np.ndarray[float]]: x sampling points and y filtered coordinates
        """
        checkArray(xp, float, "xp")
        checkArray(yp, float, "yp")
        
        #cast to numpy arrays
        xp = np.array(xp)
        yp = np.array(yp)
        
        return xp, yp
    
    #########################################################################
    #Methods:
    
#########################################################################
#Create selection table for the class used for run-time selection of type
Filter.createRuntimeSelectionTable()