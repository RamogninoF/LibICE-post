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
from scipy.signal import butter, filtfilt, freqz

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class LowPass(Filter):
    """
    Apply low-pass filter
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        cutoff:float
            Cutoff frequency
        
        order:int
            Order of the filter
    """
    
    #########################################################################
    #Properties:
    @property
    def cutoff(self) -> float:
        """
        cutoff frequency

        Returns:
            float
        """
        return self._cutoff
    
    @property
    def order(self) -> int:
        """
        Order of the filter

        Returns:
            int
        """
        return self._order
    
    #########################################################################
    #Class methods and static methods:
    @classmethod
    def fromDictionary(cls, dictionary):
        """
        Create from dictionary.

        {
            cutoff (float): cutoff frequency
            order (int): order of the filter
        }
        """
        try:
            #Create the dictionary for construction
            Dict = {}
            
            entryList = ["cutoff"]
            for entry in entryList:
                if not entry in dictionary:
                    raise ValueError(f"Mandatory entry '{entry}' not found in dictionary.")
                #Set the entry
                Dict[entry] = dictionary[entry]
            
            #Constructing this class with the specific entries
            out = cls\
                (
                    **Dict
                )
            return out
        
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed construction from dictionary", err)
    
    #########################################################################
    def __init__(self, cutoff:float, *, order=5):
        """
        cutoff (float): The cur-off frequency
        order (int): The order of the filter (default:5)
        """
        #Argument checking:
        try:
            #Type checking
            self.checkType(cutoff, float, "cutoff")
            self.checkType(order, int, "order")

        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        try:
            self._cutoff = cutoff
            self._order = order
            
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, "Failed construction of filter", err)
    
    #########################################################################
    #Dunder methods:
    def __call__(self, xp:"list[float]", yp:"list[float]")-> "tuple[list[float],list[float]]":
        """
        Filter an array of x,y data with low-pass filter
        """
        #Resample on uniform grid with step equal to the minimum step
        delta = min(np.array(xp[1:])-np.array(xp[:(len(xp)-1)]))
        res_x = np.arange(xp[0],xp[len(xp)-1], delta)
        res_y = np.interp(res_x, xp, yp, float("nan"), float("nan"))
        
        #Apply filter:
        filt_y = self._butter_lowpass_filter(res_y, self.cutoff, 1./delta, self.order).T
        filt_x = np.linspace(xp[0],xp[len(xp)-1], len(filt_y))
        
        return filt_x, filt_y
    
    ###################################
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(cutoff:{self.cutoff}, order:{self.order})"
    
    #########################################################################
    #Methods:
    def _butter_lowpass(self, cutoff:float, fs:float, order:int=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    ###################################
    def _butter_lowpass_filter(self, data:"list[float]", cutoff:float, fs:float, order:int=5):
        b, a = self._butter_lowpass(cutoff, fs, order=order)
        y = filtfilt(b, a, data)
        return y

#########################################################################
#Add to selection table of Base
Filter.addToRuntimeSelectionTable(LowPass)
