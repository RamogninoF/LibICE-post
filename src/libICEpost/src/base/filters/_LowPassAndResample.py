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
from ._LowPass import LowPass
from ._Resample import Resample

from libICEpost import Dictionary
from libICEpost.src.base.Functions.typeChecking import checkType
from libICEpost.src.base.Functions.runtimeWarning import helpOnFail
from typing import Iterable

import numpy as np

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class LowPassAndResample(LowPass, Resample):
    """
    A Butterworth low-pass filter with a given cutoff frequency and order, followed by resampling
    over a regular grid with a given spacing.
    """
    
    #########################################################################
    #Class methods and static methods:
    @classmethod
    @helpOnFail
    def fromDictionary(cls, dictionary):
        """
        Create from dictionary with the following entries:
            - `delta` (`float`): the spacing
            - `cutoff` (`float`): the cut-off frequency
            - `order` (`int`, optional): the order of the filter. Default is 5.
        """
        #Cast the dictionary to a Dictionary object
        dictionary = Dictionary(dictionary)
        
        #Get the entries
        D = {}
        D["delta"] = dictionary.lookup("delta")
        D["cutoff"] = dictionary.lookup("cutoff")
        if "order" in dictionary: D["order"] = dictionary.lookup("order")
        
        #Return the object
        return cls(**D)
    
    #########################################################################
    def __init__(self, *, delta:float, cutoff:float, order:int=5):
        """
        Create a low-pass filter with a given cut-off frequency and order, followed by resampling
        over a regular grid with a given spacing (`delta`).
        
        Args:
            delta (float): Resampling time-step
            cutoff (float): The cur-off frequency
            order (int, optional): The order of the filter. Default is 5.
        """
        Resample.__init__(self, delta)
        LowPass.__init__(self, cutoff, order=order)
    
    #########################################################################
    #Dunder methods:
    def __call__(self, xp:Iterable[float], yp:Iterable[float])-> tuple[np.ndarray[float], np.ndarray[float]]:
        
        #Call the resampling on the low-pass filtered data
        return Resample.__call__(self, *LowPass.__call__(self, xp, yp))
    
    ###################################
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(delta:{self.delta}, cutoff:{self.cutoff}, order:{self.order})"
    
    def __str__(self) -> str:
        return self.__repr__()
    
#########################################################################
#Add to selection table of Base
Filter.addToRuntimeSelectionTable(LowPassAndResample)
