#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from collections.abc import Iterable
import numpy as np
import math

from libICEpost.src.base.BaseClass import BaseClass
from libICEpost.src.base.Functions.typeChecking import checkType, checkArray

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class Time(BaseClass):
    """
    Base class for handling time in a post-processing model.
    
    Attibutes:
        - `startTime` (`float`): The start-time for post-processing
        - `endTime` (`float`): The end-time for post-processing
        - `time` (`float`): The current time instant
        - `deltaT` (`float`): Current time-step
        - `oldTime` (`float`): The old time instant
    """
    
    _time:float
    """The current time instant"""
    
    _deltaT:float
    """Current time-step"""
    
    _oldTime:float
    """The old time instant"""
    
    _startTime:float
    """The start time"""
    
    _endTime:float
    """The end time"""
    
    units:str = "s"
    """
    The unit used for measuring time (might be overwritten in derived classes)
    """
    
    #########################################################################
    #Properties:
    @property
    def time(self) -> float:
        """
        The current time instant
        """
        return self._time
    #No setter
    
    @property
    def deltaT(self) -> float:
        """
        Current time-step
        """
        return self._deltaT
    #No setter
    
    @property
    def oldTime(self) -> float:
        """
        The old time instant
        """
        return self._oldTime
    #No setter
    
    @property
    def startTime(self) -> float:
        """
        The start time
        """
        return self._startTime
    
    @startTime.setter
    def startTime(self, value:float):
        checkType(value, float, "startTime")
        self._startTime = value
    
    @property
    def endTime(self) -> float:
        """
        The end time
        """
        return self._endTime
    
    @endTime.setter
    def endTime(self, value:float):
        checkType(value, float, "endTime")
        self._endTime = value
    
    @property
    def timings(self) -> dict[str,float]:
        """
        A dictionary with the relevant timings (here nothing to add, 
        extended in derived classes)
        
        Returns:
            dict[str,float]: A dictionary with the relevant timings
        """
        return {}
    
    #########################################################################
    #Constructor:
    def __init__(self, *, 
                 startTime:float=0.0, 
                 endTime:float=float("inf")):
        """
        Construct from keyword arguments.
        
        Args:
            startTime (float): The start-time for post-processing. Default is 0.0.
            endTime (float): The end-time for post-processing. Default is infinity.
        """
        #Argument checking:
        self.checkType(startTime, float, "startTime")
        self.checkType(endTime, float, "endTime")
        
        #Attributes:
        self._time = None
        self._oldTime = None
        self._deltaT = None
        self._startTime = startTime
        self._endTime = endTime
    
    #########################################################################
    @classmethod
    def fromDictionary(cls, dictionary:dict):
        """
        Construct from dicionary with the following keys:
            - `startTime` (`float`, optional): The start-time for post-processing
            - `endTime` (`float`, optional): The end-time for post-processing
        """
        #Argument checking:
        checkType(dictionary, dict, "dictionary")
        
        #Default values:
        data = {}
        if "startTime" in dictionary: data["startTime"] = dictionary["startTime"]
        if "endTime" in dictionary: data["endTime"] = dictionary["endTime"]
        
        return cls(**data)
    
    #########################################################################
    #Dunder methods
    def __str__(self):
        STR =  "{:15s} {:15s}".format("TypeName", self.TypeName)
        STR += "\n{:15s} {:15.3f} {:15s}".format("startTime", self.startTime, f"[{self.units}]")
        STR += "\n{:15s} {:15.3f} {:15s}".format("endTime", self.endTime, f"[{self.units}]")
        STR += "\n{:15s} {:15.3f} {:15s}".format("time", self.time, f"[{self.units}]")
        
        return STR
    
    ###################################
    def __repr__(self):
        string = f"{self.__class__.__name__}(startTime={self.startTime}, endTime={self.endTime}, units={self.units})"
        return string
    
    ###################################
    #Call method used for iteration over time series:
    def __call__(self, timeList:Iterable[float]):
        """
        Iteration over time steries, from startTime to endTime.

        Args:
            timeList (Iterable[float]): list of times

        Yields:
            float: current time
        """
        #Update start-time to be consistent with the avaliable data:
        self.updateStartTime(timeList)
        
        for CA in timeList:
            if (CA > self.startTime) and (CA <= self.endTime):
                self.time = CA
                self.deltaT = self.time - self.oldTime
                yield CA
                self.oldTime = CA
    
    #########################################################################
    def userTimeToTime(self, t:float|Iterable[float]) -> float|np.ndarray:
        """
        Converts from the time-unit of the model to physical time [s]. 
        Might be overwritten in derived classes. The default implementation 
        returns the input value.

        Args:
            t (float | Iterable[float]): Time in user-time

        Returns:
            float|np.ndarray: Time in seconds
        """
        checkType(t, (float, Iterable), "t")
        if isinstance(t, Iterable):
            checkArray(t, float, "t")
        return t
    
    ###################################
    def timeToUserTime(self, t:float|Iterable[float]) -> float|np.ndarray:
        """
        Converts from physical time [s] to the time-unit of the model. 
        Might be overwritten in derived classes. The default implementation 
        returns the input value.

        Args:
            t (float | Iterable[float]): Time in seconds

        Returns:
            float|np.ndarray: Time in user-time
        """
        checkType(t, (float, Iterable), "t")
        if isinstance(t, Iterable):
            checkArray(t, float, "t")
        return t
    
    ###################################
    def isCombustion(self,CA:float|Iterable[float]=None) -> bool|np.ndarray:
        """
        Check if combustion has started.

        Args:
            CA (float | Iterable[float] | None): Crank angle to check. If None, checks for self.time

        Returns:
            bool|np.ndarray: If combustion started
        """
        if not CA is None:
            checkType(CA, (float, Iterable), "CA")
            if isinstance(CA, Iterable):
                checkArray(CA, float, "CA")
        else:
            CA = self.time
        
        if not self.startOfCombustion() is None:
            out = (np.array(CA) > self.startOfCombustion()) if isinstance(CA, Iterable) else (CA > self.startOfCombustion())
            return out
        else:
            return np.zeros_like(CA, dtype=bool) if isinstance(CA, Iterable) else False
    
    ###################################
    def startOfCombustion(self) -> float|None:
        """
        Instant of start of combustion (overwritten in derived class). By default, returns None (no combustion).
        """
        return None
    
    ###################################
    def updateStartTime(self, timeList:Iterable[float]) -> None:
        """
        Update the start-time to be consistent with the avaliable data

        Args:
            timeList (Iterable[float]): The avaliable time series
        """
        checkArray(timeList, float, "timeList")
        
        timeList = np.array(timeList)
        self.startTime = timeList[timeList >= self.startTime][0]
        self.time = self.startTime
        self.oldTime = self.startTime
    
#############################################################################
Time.createRuntimeSelectionTable()
