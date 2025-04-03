#####################################################################
#                                 DOC                               #
#####################################################################

"""
Time for four-stroke engines.

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
class FourStrokeEngineTime(EngineTime):
    """
    Four-stroke engine time class. This defines the timings IVO, IVC, EVO, EVC.
    """
    
    _IVC:float|None
    """The intake valve closing timing [CAD]"""
    _EVO:float|None
    """The exhaust valve opening timing [CAD]"""
    _IVO:float|None
    """The intake valve opening timing [CAD]"""
    _EVC:float|None
    """The exhaust valve closing timing [CAD]"""
    
    #########################################################################
    #Properties:
    @property
    def timings(self):
        """
        A dictionary with the relevant timings (IVC, EVO, etc...)

        Returns:
            dict[str,float]
        """
        timings = super().timings
        timings["IVC"] = self.IVC
        timings["EVO"] = self.EVO
        if not self.IVO is None: timings["IVO"] = self.IVO
        if not self.EVC is None: timings["EVC"] = self.EVC
        return timings
    
    @property
    def epsilon(self) -> float:
        return 4.0
    
    ##########################################################
    # Timings:
    @property
    def IVC(self) -> float:
        """
        The intake valve closing timing [CAD].
        """
        return self._IVC
    
    @property
    def EVO(self) -> float:
        """
        The exhaust valve opening timing [CAD].
        """
        return self._EVO
    
    @property
    def IVO(self) -> float:
        """
        The intake valve opening timing [CAD].
        """
        return self._IVO
    
    @property
    def EVC(self) -> float:
        """
        The exhaust valve closing timing [CAD].
        """
        return self._EVC
    
    # Timings are unmutable (no setter)
    
    @property
    def overlap(self) -> float:
        """
        The overlap timing [CAD]. This is defined as the time between IVO and EVC.
        """
        if self.IVO is None or self.EVC is None: return np.nan
        return self.EVC - self.IVO
    
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
        - `IVO` (float, optional): Intake valve opening timing [CAD].
        - `IVC` (float): Intake valve closing timing [CAD].
        - `EVO` (float): Exhaust valve opening timing [CAD].
        - `EVC` (float, optional): Exhaust valve closing timing [CAD].
        
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
        D.update(IVC=dictionary.lookup("IVC", varType=float))
        D.update(EVO=dictionary.lookup("EVO", varType=float))
        #Optional parameters:
        if "TDC" in dictionary: D.update(TDC=dictionary.lookup("TDC", varType=float))
        if "IVO" in dictionary: D.update(IVO=dictionary.lookup("IVO", varType=float))
        if "EVC" in dictionary: D.update(EVC=dictionary.lookup("EVC", varType=float))
        
        return cls(**D)
    
    #########################################################################
    #Constructor:
    def __init__(self, *, n:float, IVC:float, EVO:float,
                 IVO:float=None, EVC:float=None, TDC:float=0.0):
        """
        Constructor for the FourStrokeEngineTime class, given the
        engine speed (n) and the timings (IVC, EVO, IVO, EVC).
        Only the IVC and EVO timings are mandatory, since they define
        the start and end of the combustion processing.
        The IVO and EVC timings are optional, but they can be used
        to define the intake and exhaust processes, along with some
        plots.
        
        **Note**: Timings of each valve must be defined in the same 
        time-frame, i.e. IVC must be greater than IVO, and EVC must 
        be greater than EVO.
        
        Args:
            n (float): Engine speed [rev/min]
            IVC (float): Intake valve closing timing [CAD].
            EVO (float): Exhaust valve opening timing [CAD].
            IVO (float, optional): Intake valve opening timing [CAD].
            EVC (float, optional): Exhaust valve closing timing [CAD].
            TDC (float, optional): Top dead center reference [CAD]. This is used as a 
                reference for the **theoretical** top dead center (not considering 
                the pin-offset), in case there is a shift in the time-frame.
        """
        #Initialization of the base class:
        super().__init__(n=n, TDC=TDC)
        
        #Argument checking:
        checkType(IVC, float, "IVC")
        checkType(EVO, float, "EVO")
        checkType(IVO, float, "IVO", allowNone=True)
        checkType(EVC, float, "EVC", allowNone=True)
        
        #Check that IVO < IVC and EVO < EVC:
        if not IVO is None:
            if IVO > IVC:
                raise ValueError("IVO must come before IVC")
            if IVC - EVO > self.period:
                raise ValueError(f"IV opening time (IVC - IVO = {IVC - IVO}) is greater than the period ({self.period})")
        if not EVC is None:
            if EVO > EVC:
                raise ValueError("EVO must come before EVC")
            if EVC - EVO > self.period:
                raise ValueError(f"EV opening time (EVC - EVO = {EVC - EVO}) is greater than the period ({self.period})")
        
        #Fit the timings to cycle 0:
        IVC = self.fitToCycle(IVC, 0)
        EVO = self.fitToCycle(EVO, 0)
        if not IVO is None: IVO = self.fitToCycle(IVO, 0)
        if not EVC is None: EVC = self.fitToCycle(EVC, 0)
        
        #Setting timings:
        self._IVO = IVO
        self._IVC = IVC
        self._EVO = EVO
        self._EVC = EVC
        
        #Setting start and end time:
        self._startTime = self.IVC
        self._endTime = self.EVO
    
    #########################################################################
    #Dunder methods:
    def __str__(self):
        STR = super().__str__()
        STR += "\n{:15s} {:15.3f} {:15s}".format("IVC", self.IVC, f"[{self.units}]")
        STR += "\n{:15s} {:15.3f} {:15s}".format("EVO", self.EVO, f"[{self.units}]")
        if not self.IVO is None: STR += "\n{:15s} {:15.3f} {:15s}".format("IVO", self.IVO, f"[{self.units}]")
        if not self.EVC is None: STR += "\n{:15s} {:15.3f} {:15s}".format("EVC", self.EVC, f"[{self.units}]")
        STR += "\n{:15s} {:15.3f} {:15s}".format("period", self.period, f"[{self.units}]")
        return STR
    
    def __repr__(self):
        return f"{self.__class__.__name__}(n={self.n}, IVC={self.IVC}, EVO={self.EVO}, IVO={self.IVO}, EVC={self.EVC}, startTime={self.startTime}, endTime={self.endTime})"

##########################################################################
EngineTime.addToRuntimeSelectionTable(FourStrokeEngineTime)