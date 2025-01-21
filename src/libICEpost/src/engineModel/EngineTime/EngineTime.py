#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from collections.abc import Iterable
import numpy as np
import math

from libICEpost.src.base.BaseClass import BaseClass

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class EngineTime(BaseClass):
    """
    Base class for handling engine timings during cycle.
    
    Attibutes:
        - IVC (float): Inlet valve closing [CA]
        - EVO (float): Inlet valve closing [CA]
        - n (float): Rotational speed [rpm]
        - omega (float): Rotational speed [rad/s]
        - time (float): The current time instant [CA]
        - deltaT (float): Current time-step [CA]
        - oldTime (float): The old time instant [CA]
        - startTime (float): The start-time for post-processing [CA]
        - endTime (float): The end-time for post-processing [CA]
    """
    
    time:float
    """The current time instant"""
    
    deltaT:float
    """Current time-step"""
    
    oldTime:float
    """The old time instant"""
    
    startTime:float
    """The start time"""
    
    endTime:float
    """The end time"""
    
    #########################################################################
    #Constructor:
    def __init__(self,speed, *, IVC:float, EVO:float, startTime:float=None, endTime:float=None):
        """
        Construct from keyword arguments.
        
        Args:
            IVC (float): Inlet valve closing [CA]
            EVO (float): Inlet valve closing [CA]
            speed (float): Rotational speed [rpm]
            startTime (float, optional): The start-time for post-processing [CA]. If None, set to IVC. Defaults to None.
            endTime (float, optional): The end-time for post-processing [CA]. If None, set to EVO. Defaults to None.
        """
        #Argument checking:
        self.checkType(IVC, float, "IVC")
        self.checkType(EVO, float, "EVO")
        self.checkType(speed, float, "speed")
        
        if not startTime is None:
            self.checkType(startTime, float, "startTime")
        else:
            startTime = IVC
            
        if not endTime is None:
            self.checkType(endTime, float, "endTime")
        else:
            endTime = EVO
        
        self.n = speed
        self.omega = speed / 60.0 * 2.0 * math.pi
        self.IVC = IVC
        self.EVO = EVO
        self.startTime = startTime
        self.endTime = endTime
        
        self.time = None
        self.oldTime = None
    
    ######################################
    #NOTE: overwrite in child class if necessary
    @property
    def timings(self) -> dict[str,float]:
        """
        A dictionary with the relevant timings (IVC, EVO, etc...)

        Returns:
            dict[str,float]
        """
        return {"IVC":self.IVC, "EVO":self.EVO}
    
    #########################################################################
    @classmethod
    def fromDictionary(cls, dictionary:dict):
        """
        Construct from dicionary
        """
        return cls(**dictionary)
    
    #########################################################################
    @property
    def dCAdt(self) -> float:
        """
        conversion ratio from CA to s
        """
        return (self.n * 6.0)
    
    #########################################################################
    #Dunder methods
    def __str__(self):
        STR =  "{:15s} {:15s}".format("TypeName", self.TypeName)
        STR += "\n{:15s} {:15.3f} {:15s}".format("n", self.n,"[rpm]")
        STR += "\n{:15s} {:15.3f} {:15s}".format("omega", self.omega,"[rad/s]")
        STR += "\n{:15s} {:15.3f} {:15s}".format("startTime", self.startTime,"[CAD]")
        STR += "\n{:15s} {:15.3f} {:15s}".format("endTime", self.endTime,"[CAD]")
        STR += "\n{:15s} {:15.3f} {:15s}".format("IVC", self.IVC,"[CAD]")
        STR += "\n{:15s} {:15.3f} {:15s}".format("EVO", self.EVO,"[CAD]")
        
        return STR
    
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
    #CA to Time:
    def CA2Time(self,CA:float|Iterable[float]) -> float|np.ndarray:
        """
        Converts CA to time [s]

        Args:
            CA (float | Iterable[float]): Time in CA

        Returns:
            float|np.ndarray: Time in seconds
        """
        self.checkType(CA, (float, Iterable), "CA")
        if isinstance(CA, Iterable) and not isinstance(CA, np.ndarray):
            self.checkArray(CA, float, "CA")
            return np.array(CA)/self.dCAdt
        else:
            return CA/self.dCAdt
    
    ###################################
    #Time to CA:
    def Time2CA(self,t:float|Iterable[float]) -> float|np.ndarray:
        """
        Converts time [s] to CA

        Args:
            t (float | Iterable[float]): Time in seconds

        Returns:
            float|np.ndarray: time in CA
        """
        self.checkType(t, (float, Iterable), "t")
        if isinstance(t, Iterable) and not isinstance(t, np.ndarray):
            self.checkArray(t, float, "t")
            return np.array(t)*self.dCAdt
        else:
            return t*self.dCAdt
    
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
            self.checkType(CA, (float, Iterable), "CA")
            if isinstance(CA, Iterable):
                self.checkArray(CA, float, "CA")
        else:
            CA = self.time
        
        if not self.startOfCombustion() is None:
            out = (CA > self.startOfCombustion())
            return np.array(out) if isinstance(CA, Iterable) else out
        else:
            return False
    
    ###################################
    def startOfCombustion(self) -> float|None:
        """
        Instant of start of combustion (overwritten in derived class depending on combustion mode). By default, returns None (motoring condition).
        """
        return None
    
    ###################################
    def isClosedValves(self,CA:float|Iterable[float]=None) -> bool|np.ndarray:
        """
        Check if at closed valves (after IVC and before EVO)

        Args:
            CA (float | Iterable[float] | None): Cranc angle to check. If None, checks for self.time

        Returns:
            bool|np.ndarray: If at closed valves
        """
        if not CA is None:
            self.checkType(CA, (float, Iterable), "CA")
            if isinstance(CA, Iterable):
                self.checkArray(CA, float, "CA")
        else:
            CA = self.time
        
        if isinstance(CA, Iterable):
            out = (np.array(CA >= self.IVC) & np.array(CA <= self.EVO))
        else:
            out = ((CA >= self.IVC) and (CA <= self.EVO))
        return out

    ###################################
    def updateStartTime(self, timeList:Iterable[float]) -> None:
        """
        Update the start-time to be consistent with the avaliable data

        Args:
            timeList (Iterable[float]): The avaliable time series
        """
        self.checkType(timeList, Iterable, "timeList")
        
        timeList = np.array(timeList)
        self.startTime = timeList[timeList >= self.startTime][0]
        self.time = self.startTime
        self.oldTime = self.startTime
    
#############################################################################
EngineTime.createRuntimeSelectionTable()
