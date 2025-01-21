#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: <N. Surname>       <e-mail>
Last update:        DD/MM/YYYY
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

#load the base class
from .Filter import Filter

#Other imports
import numpy as np

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class Resample(Filter):
    """
    Resampling with constant delta x
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        delta:float
            Resampling interval
    """
    
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
    def fromDictionary(cls, dictionary):
        """
        Create from dictionary.

        {
            delta (float): the spacing
        }
        """
        #Create the dictionary for construction
        Dict = {}
        
        entryList = ["delta"]
        for entry in entryList:
            if not entry in dictionary:
                raise ValueError(f"Mandatory entry '{entry}' not found in dictionary.")
            #Set the entry
            Dict[entry] = dictionary[entry]
        
        #Constructing this class with the specific entries
        out = cls(**Dict)
        return out
    
    #########################################################################
    def __init__(self, delta:float):
        """
        delta (float): The spacing
        """
        #Argument checking:
        #Type checking
        self.checkType(delta, float, "delta")
        self._delta = delta
    
    #########################################################################
    #Dunder methods:
    def __call__(self, xp:"list[float]", yp:"list[float]") -> "tuple[list[float],list[float]]":
        """
        Filter an array of x,y data with constant spacing
        """
        #Construct uniform grid from min(x) to max(x)
        interval = np.arange(xp[0],xp[len(xp)-1]+self.delta, self.delta)
        #Construct linear interpolator
        return interval, np.interp(interval, xp, yp, float("nan"), float("nan"))
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(delta:{self.delta})"
    
    #########################################################################
    #Methods:

#########################################################################
#Add to selection table of Base
Filter.addToRuntimeSelectionTable(Resample)
