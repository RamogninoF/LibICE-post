#####################################################################
#                                 DOC                               #
#####################################################################

"""
Time for two-stroke engines.

@author: F. Ramognino       <federico.ramognino@polimi.it>
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from ._EngineTime import EngineTime
from libICEpost.src.base.Functions.runtimeWarning import helpOnFail
from libICEpost.src.base.Functions.typeChecking import checkType

from libICEpost.src.base.dataStructures.Dictionary import Dictionary, toDictionary

from typing import Iterable
import numpy as np

from ...bases import Engine

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class TwoStrokeEngineTime(EngineTime):
    """
    Two-stroke engine time class. This defines the timings IPO, IPC, EPO, EPC.
    """
    
    #########################################################################
    #Properties:
    @property
    def timings(self):
        """
        A dictionary with the relevant timings (IPO, IPC, EPO, EPC)

        Returns:
            dict[str,float]
        """
        timings = super().timings
        timings["IPC"] = self.IPC
        timings["EPO"] = self.EPO
        timings["IPO"] = self.IPO
        timings["EPC"] = self.EPC
        return timings
    
    @property
    def epsilon(self) -> float:
        return 2.0
    
    ##########################################################
    # Timings:
    @property
    def IPC(self) -> float:
        """
        The intake port closing timing [CAD].
        """
        return self._IPC
    
    @property
    def EPO(self) -> float:
        """
        The exhaust port opening timing [CAD].
        """
        return self._EPO
    
    @property
    def IPO(self) -> float:
        """
        The intake port opening timing [CAD].
        """
        return self._IPO
    
    @property
    def EPC(self) -> float:
        """
        The exhaust port closing timing [CAD].
        """
        return self._EPC
    
    # Timings are unmutable (no setter)
    
    #########################################################################
    @classmethod
    @helpOnFail
    def fromDictionary(cls, dictionary):
        """
        Construct from a dictionary containing:
        - `n` (float): Engine speed [rev/min]
        - `TDC` (float): **firing** top dead center [CAD]. This is used as a 
            reference for the **theoretical** top dead center (not considering 
            the pin-offset), in case there is a shift in the time-frame.
        - `IPC` (float): Intake port closing timing [CAD].
        - `EPO` (float): Exhaust port opening timing [CAD].
        
        Args:
            dictionary (dict): Dictionary with the relevant parameters.

        Returns:
            FourStrokeEngineTime: Instance of the class.
        """
        dictionary = toDictionary(dictionary)
        
        #Fetch the parameters:
        D = dict()
        #Mandatory parameters:
        D.update(n=dictionary.lookup("n", varType=float))
        D.update(IPC=dictionary.lookup("IPC", varType=float))
        D.update(EPO=dictionary.lookup("EPO", varType=float))
        
        #Optional parameters:
        if "TDC" in dictionary: D.update(TDC=dictionary.lookup("TDC", varType=float))
        
        return cls(**D)
    
    #########################################################################
    #Constructor:
    def __init__(self, *, n:float, IPC:float, EPO:float, TDC:float=0.0):
        """
        Constructor for the TwoStrokeEngineTime class, given the
        engine speed (n) and the timings (IPC and EPO).
        The IPO and EPC are calculated from the IPC and EPO, knowing 
        that they are symmetric with respect to the TDC.
        
        Args:
            n (float): Engine speed [rev/min]
            IPC (float): Intake port closing timing [CAD].
            EPO (float): Exhaust port opening timing [CAD].
            TDC (float, optional): Top dead center reference [CAD]. This is used as a 
                reference for the **theoretical** top dead center (not considering 
                the pin-offset), in case there is a shift in the time-frame.
        """
        #Initialization of the base class:
        super().__init__(n=n, TDC=TDC)
        
        #Argument checking:
        checkType(IPC, float, "IPC")
        checkType(EPO, float, "EPO")
        
        #Clamp the timings to cycle 0:
        #Fit the timings to cycle 0:
        IPC = self.fitToCycle(IPC, 0)
        EPO = self.fitToCycle(EPO, 0)
        
        #Compute the IPO and EPC:
        IPO = self.TDC + self.period - IPC
        EPC = self.TDC + self.period - EPO
        IPO = self.fitToCycle(IPO, 0)
        EPC = self.fitToCycle(EPC, 0)
        
        #Setting timings:
        self._IPC = IPC
        self._EPO = EPO

        #Setting start and end time:
        self._startTime = IPC
        self._endTime = EPO
        
    #########################################################################
    #Dunder methods:
    def __str__(self):
        STR = super().__str__()
        STR += "\n{:15s} {:15.3f} {:15s}".format("IPC", self.IPC, f"[{self.units}]")
        STR += "\n{:15s} {:15.3f} {:15s}".format("EPO", self.EPO, f"[{self.units}]")
        STR += "\n{:15s} {:15.3f} {:15s}".format("IPO", self.IPO, f"[{self.units}]")
        STR += "\n{:15s} {:15.3f} {:15s}".format("EPC", self.EPC, f"[{self.units}]")
        return STR
    
    def __repr__(self):
        return f"{self.__class__.__name__}(n={self.n}, IVC={self.IVC}, EVO={self.EVO}, IVO={self.IVO}, EVC={self.EVC}, startTime={self.startTime}, endTime={self.endTime})"

##########################################################################
EngineTime.addToRuntimeSelectionTable(TwoStrokeEngineTime)