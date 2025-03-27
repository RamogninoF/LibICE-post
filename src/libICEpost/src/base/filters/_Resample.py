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
from typing import Iterable

from libICEpost.src.base.Functions.typeChecking import checkType
from libICEpost.src.base.Functions.runtimeWarning import helpOnFail
from libICEpost import Dictionary

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class Resample(Filter):
    """
    Resampling over a uniform grid with constant delta x.
    """
    
    _delta:float
    """The discretization spacing"""
    
    #########################################################################
    #Properties:
    @property
    def delta(self) -> float:
        """
        The discretization spacing

        Returns:
            float
        """
        return self._delta
    
    #########################################################################
    #Class methods and static methods:
    @classmethod
    @helpOnFail
    def fromDictionary(cls, dictionary):
        """
        Create from dictionary with the following entries:
            - `delta` (`float`): the spacing
        
        Args:
            dictionary (dict): the dictionary with the entries
        
        Returns:
            `Resample`: the Resample object
        """
        #Cast the dictionary to a Dictionary object
        dictionary = Dictionary(**dictionary)
        
        #Constructing this class with the specific entries
        return cls(delta=dictionary.lookup("delta"))
    
    #########################################################################
    def __init__(self, delta:float):
        """
        Initialize the Resample object with the spacing.
        
        Args:
            delta (float): The spacing of the grid
        """
        #Argument checking:
        #Type checking
        checkType(delta, float, "delta")
        if delta <= 0:
            raise ValueError(f"delta must be positive. Got {delta}")
        self._delta = delta
    
    #########################################################################
    #Dunder methods:
    def __call__(self, xp:Iterable[float], yp:Iterable[float])-> tuple[np.ndarray[float], np.ndarray[float]]:
        #Type checking and recasting to numpy arrays
        xp, yp = Filter.__call__(self, xp, yp)
        
        #Construct uniform grid from min(x) to max(x)
        interval = np.arange(xp[0],xp[len(xp)-1]+self.delta, self.delta)
        
        #Construct linear interpolator
        return interval, np.interp(interval, xp, yp, float("nan"), float("nan"))
    
    #########################################################################
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(delta:{self.delta})"
    
    def __str__(self) -> str:
        return self.__repr__()
    
    #########################################################################
    #Methods:

#########################################################################
#Add to selection table of Base
Filter.addToRuntimeSelectionTable(Resample)
