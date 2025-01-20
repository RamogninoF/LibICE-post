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
from .LowPass import LowPass
from .Resample import Resample

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class LowPassAndResample(LowPass, Resample):
    """
    Apply low-pass filter and resampling
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        cutoff (float): Cutoff frequency
        order (int): Order of the filter
        delta (float): Resampling time-step
    """
    
    #########################################################################
    #Class methods and static methods:
    @classmethod
    def fromDictionary(cls, dictionary):
        """
        Create from dictionary.

        {
            delta (float): Resampling time-step
            cutoff (float): cutoff frequency
            order (int): order of the filter
        }
        """
        out = cls\
            (
                **dictionary
            )
        return out
    
    #########################################################################
    def __init__(self, *, delta:float, cutoff:float, order=5):
        """
        delta (float): Resampling time-step
        cutoff (float): The cur-off frequency
        order (int): The order of the filter (default:5)
        """
        Resample.__init__(self, delta)
        LowPass.__init__(self, cutoff, order=order)
    
    #########################################################################
    #Dunder methods:
    def __call__(self, xp:"list[float]", yp:"list[float]")-> "tuple[list[float],list[float]]":
        """
        Filter an array of x,y data with low-pass filter and resampling
        """
        
        return Resample.__call__(self, *LowPass.__call__(self, xp, yp))
    
    ###################################
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(delta:{self.delta}, cutoff:{self.cutoff}, order:{self.order})"
    
#########################################################################
#Add to selection table of Base
Filter.addToRuntimeSelectionTable(LowPassAndResample)
