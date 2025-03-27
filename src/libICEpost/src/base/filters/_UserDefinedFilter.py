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
from typing import Callable, Iterable
import numpy as np
from libICEpost import Dictionary
from libICEpost.src.base.Functions.typeChecking import checkType

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class UserDefinedFilter(Filter):
    """
    User defined filter, where the user defines the filtering function `f(x,y)->(xp,yp)`
    overwriting the `__call__(x,y)` method.
    """
    _function:Callable
    """
    The function `f(x,y)->(xp,yp)` to be used as filter
    """
    #########################################################################
    #Properties:
    @property
    def function(self) -> Callable:
        """
        The function `f(x,y)->(xp,yp)` to be used as filter

        Returns:
            Callable
        """
        return self._function
    
    #########################################################################
    #Class methods and static methods:
    @classmethod
    def fromDictionary(cls, dictionary):
        """
        Create from dictionary with the following entries:
            - `function` (`Callable`): the function `f(x,y)->(xp,yp)` to be used as filter
        """
        #Cast the dictionary to a Dictionary object
        dictionary = Dictionary(dictionary)
        
        #Return the object
        return cls(dictionary.lookup("function"))
    
    #########################################################################
    def __init__(self, function:Callable, *, check=True):
        """
        Initialize the object with the user-defined function `f(x,y)->(xp,yp)`
        to overwrite the `__call__(x,y)` method.
        
        Args:
            function (Callable): the filtering function `f(x,y)->(xp,yp)`
        """
        #Argument checking:
        #Type checking
        checkType(function, Callable, "function")
        
        if check:
            #Assess that the function accepts two arguments of type Iterable[float]
            x_sample = np.linspace(0, 1, 10)
            y_sample = np.linspace(0, 1, 10)
            
            try:
                xp, yp = function(x_sample, y_sample)
            except Exception as e:
                raise ValueError(f"Error assessing that the function accepts two arguments of type Iterable[float]")
        
        self._function = function
    
    #########################################################################
    #Dunder methods:
    def __call__(self, xp:Iterable[float], yp:Iterable[float])-> tuple[np.ndarray[float], np.ndarray[float]]:
        #Type checking and recasting to numpy arrays
        xp, yp = Filter(self, xp, yp)
        
        #Apply the filter
        return self._function(xp, yp)
    
    ###################################
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
    
    #########################################################################
    #Methods:
    

#########################################################################
#Add to selection table of Base
Filter.addToRuntimeSelectionTable(UserDefinedFilter)
