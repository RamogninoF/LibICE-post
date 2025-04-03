#####################################################################
#                                 DOC                               #
#####################################################################

"""
Define the base class for handling time in an internal combustion engine.
Time is measured in crank angle degrees (CAD) and the class provides methods
for converting between CAD (user time) and seconds (physical time).

Content of the module:
    - `EngineTime` (`class`): Base class for handling time in an internal combustion engine.
    Time is measured in crank angle degrees (CAD) and the class provides methods
    for converting between CAD (user time) and seconds (physical time).
    The specific timings (IVC, EVO, etc...) are defined in the derived classes
    (e.g. `TwoStrokeTime`, `FourStrokeTime`, etc...).

@author: F. Ramognino       <federico.ramognino@polimi.it>
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from .._Time import Time
from libICEpost.src.base.Functions.runtimeWarning import helpOnFail
from libICEpost.src.base.Functions.typeChecking import checkType, checkArray

from libICEpost.src.base.dataStructures.Dictionary import Dictionary, toDictionary
from abc import abstractmethod

from typing import Iterable, Literal
import numpy as np

from ...bases import Engine

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class EngineTime(Time,Engine):
    """
    Base class for handling time in an internal combustion engine.
    Time is measured in crank angle degrees (CAD) and the class provides methods
    for converting between CAD (user time) and seconds (physical time).
    
    Attributes:
        `omega` (`float`): The engine speed [rad/s]
        `n` (`float`): The engine speed [rev/min]
        `timings` (`dict[str,float]`): A dictionary with the relevant timings (IVC, EVO, etc...). 
            These are defined in the derived classes (e.g. `TwoStrokeTime`, `FourStrokeTime`, etc...).
        `TDC` (`float`): The top dead center [CAD]
        `BDC` (`float`): The bottom dead center [CAD]
    """
    
    _n:float
    """The engine speed [rev/min]"""
    
    _TDC:float
    """
    **firing** top dead center reference [CAD]. This is used as a reference for the **theoretical** top dead
    center (not considering the pin-offset), in case there is a shift in the time-frame.
    Therefore, `BDC` is equal to `180 + TDC`.
    """
    
    unitName:str = "CA"
    """
    The name of the unit used for measuring time
    """
    
    units:str = "CAD"
    """
    The unit used for measuring time
    """
    
    #########################################################################
    #Properties:
    @property
    @abstractmethod
    def timings(self):
        """
        A dictionary with the relevant timings (IVC, EVO, etc...)

        Returns:
            dict[str,float]
        """
        return super().timings
    
    @property
    def omega(self) -> float:
        """
        The engine speed [rad/s]

        Returns:
            float
        """
        return self.n * 2.0 * np.pi / 60.0
    
    @property
    def n(self) -> float:
        """
        The engine speed [rev/min]
        """
        return self._n
    
    # Engine speed is unmutable (no setter)
    
    @property
    def TDC(self) -> float:
        """
        The top dead center [CAD]
        """
        return self._TDC
    
    @property
    def BDC(self) -> float:
        """
        The bottom dead center [CAD]
        This is equal to `180 + TDC`
        """
        return 180.0 + self.TDC
    
    @property
    @abstractmethod
    def epsilon(self) -> float:
        """
        The number of power strokes per cycle. This is equal to 2 for a
        two-stroke engine and 4 for a four-stroke engine.
        """
    
    @property
    def period(self) -> float:
        """
        The period of the engine cycle [CAD]. This is equal to 180.0 * epsilon
        """
        return 180.0 * self.epsilon
    
    #########################################################################
    # fromDictionary is implemented in the derived classes (abstract base class)
    
    #########################################################################
    #Constructor:
    @abstractmethod
    def __init__(self, n:float, *args, TDC:float=0, **argv):
        """
        Constructor for the EngineTime class given the engine speed
        (n) and the Time arguments. Derived classes should implement setting
        of the relevant timings (IVC, EVO, etc...) depending on type of engine
        (two-stroke, four-stroke, Wankel etc...).
        
        Args:
            n (float): Engine speed [rev/min]
            TDC (float, optional): **firing** top dead center reference [CAD].
            This is used as a reference for the **theoretical** top dead 
            center (not considering the pin-offset), in case there is a 
            shift in the time-frame. Therefore, `BDC` is equal to
            `180 + TDC`. Defaults to 0.
            *args: Time arguments
            **argv: Time keyword arguments
        """
        #Initialization of the base class:
        super().__init__(*args, **argv)
        
        checkType(n, float, "n")
        checkType(TDC, float, "TDC")
        
        self._n = n
        self._TDC = TDC
    
    #########################################################################
    #Dunder methods:
    def __str__(self):
        STR = super(self.__class__, self).__str__()
        STR += "\n{:15s} {:15.3f} {:15s}".format("n", self.n, "[rev/min]")
        STR += "\n{:15s} {:15.3f} {:15s}".format("TDC", self.TDC, f"[{self.units}]")
        return STR
    
    def __repr__(self):
        return f"{self.__class__.__name__}(n={self.n}, TDC={self.TDC}, startTime={self.startTime}, endTime={self.endTime})"
    
    #########################################################################
    #Methods:
    def userTimeToTime(self, t:float|Iterable[float]) -> float|np.ndarray:
        """
        Converts from CAD to seconds.

        Args:
            t (float | Iterable[float]): Time in CAD

        Returns:
            float|np.ndarray: Time in seconds
        """
        t = super().userTimeToTime(t) # Type checking and casting to np.ndarray
        return t / self.n * 60.0 / 360.0 # [s] = [CAD] / [rev/min] * [s/min] / [CAD/rev]
    
    ##################################
    def timeToUserTime(self, t:float|Iterable[float]) -> float|np.ndarray:
        """
        Converts from seconds to CAD.

        Args:
            t (float | Iterable[float]): Time in seconds
            
        Returns:
            float|np.ndarray: Time in CAD
        """
        t = super().timeToUserTime(t) # Type checking and casting to np.ndarray
        return t * self.n / 60.0 * 360.0 # [CAD] = [s] * [rev/min] / [s/min] * [CAD/rev]
    
    ##################################
    def dTdt(self, t:float|Iterable[float]|None) -> float|np.ndarray:
        """
        Returns the derivative of time with respect to CAD.

        Args:
            t (float | Iterable[float]): Time in CAD
            
        Returns:
            float|np.ndarray: Derivative of time with respect to CAD
        """
        # [CAD/s] = [CAD] * [rev/min] / [s/min] * [CAD/rev]
        return super().dTdt(t) * self.n / 60.0 * 360.0
    
    ##################################
    def cycle(self, t:float|Iterable[float]|None, *, timeFormat:Literal["absolute", "user"]="user") -> float|np.ndarray:
        """
        Returns the cycle number at time t. The cycle starts at the **firing** TDC.
        
        Args:
            t (float | Iterable[float]): Time **in CAD**
            timeFormat (str, optional): The time format. Can be "absolute" or "user".
                If "absolute", the time is in seconds. If "user", the time is in CAD.
                Defaults to "user".
            
        Returns:
            float|np.ndarray: Cycle number
        """
        checkType(t, (float, Iterable), "t", allowNone=True)
        if t is None:
            t = self.time
        if isinstance(t, Iterable):
            checkArray(t, float, "t")
            t = np.array(t)
        
        checkType(timeFormat, str, "timeFormat")
        if timeFormat not in ["absolute", "user"]:
            raise ValueError(f"Invalid timeFormat: {timeFormat}. Must be 'absolute' or 'user'.")
        
        if timeFormat == "absolute":
            t = self.timeToUserTime(t)
        
        # [cycle] = [CAD] / [CAD/cycle]
        return np.floor((t - self.TDC) / self.period)
    
    ##################################
    def fitToCycle(self, t:float|Iterable[float], cycle:int|Iterable[int], *, timeFormat:Literal["absolute", "user"]="user") -> float|np.ndarray:
        """
        Fits the time t to the cycle number. The cycle starts at the BDC
        **after** the **firing** TDC.
        
        Args:
            t (float | Iterable[float]): Time **in CAD**
            cycle (int|Iterable[int]): Cycle number to fit to
            timeFormat (str, optional): The time format. Can be "absolute" or "user".
                If "absolute", the time is in seconds. If "user", the time is in CAD.
                Defaults to "user".
            
        Returns:
            float|np.ndarray: Fitted time. The shape is given by (len(t), len(cycle))
        """
        checkType(t, (float, Iterable), "t")
        if isinstance(t, Iterable):
            checkArray(t, float, "t")
            t = np.array(t)
        
        checkType(cycle, (int, Iterable), "cycle")
        if isinstance(cycle, Iterable):
            checkArray(cycle, int, "cycle")
            cycle = np.array(cycle)
        checkType(timeFormat, str, "timeFormat")
        if timeFormat not in ["absolute", "user"]:
            raise ValueError(f"Invalid timeFormat: {timeFormat}. Must be 'absolute' or 'user'.")
        
        if timeFormat == "absolute":
            t = self.timeToUserTime(t)
        
        # Broadcast t and cycle to the same shape:
        # t = np.broadcast_to(
        #     t.reshape(*t.shape, *np.ones(len(cycle.shape))),
        #     (*t.shape, *cycle.shape))
        # cycle = np.broadcast_to(
        #     cycle.reshape(*np.ones(len(t.shape)), *cycle.shape),
        #     (*t.shape, *cycle.shape))
        
        #Get the original cycle:
        originalCycle = self.cycle(t, timeFormat="user")
        
        #Fit the time to the cycle:
        # [CAD] = [CAD] + [CAD/cycle] * [cycle]
        return t - (originalCycle - cycle) * self.period

#########################################################################
EngineTime.createRuntimeSelectionTable()