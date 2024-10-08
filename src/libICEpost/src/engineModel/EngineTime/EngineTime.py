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

from libICEpost.src.base.BaseClass import BaseClass, abstractmethod

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class EngineTime(BaseClass):
    """
    Base class for handling engine geometrical parameters during cycle.
    
    NOTE: Crank angles are defined with 0 CAD at FIRING TDC
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        
        [Variable] | [Type]     | [Unit] | [Description]
        -----------|------------|--------|-------------------------------------------
        startTime  | float(None)| CA     | The start-time for post-processing.
                   |            |        | If None, uses IVC
        IVC        | float      | CA     | Inlet valve closing
        EVO        | float      | CA     | Inlet valve closing
        -----------|------------|--------|-------------------------------------------
        n          | float      | rpm    | Rotational speed
        omega      | float      | rad/s  | 
    """
    
    """The current time instant"""
    time:float
    
    """Current time-step"""
    deltaT:float
    
    """The old time instant"""
    oldTime:float
    
    """The start time"""
    startTime:float
    
    """The end time"""
    endTime:float
    
    #########################################################################
    #Constructor:
    def __init__(self,speed, *, IVC, EVO, startTime=None, endTime:float=None):
        """
        Construct from keyword arguments containing the following parameters:
        
        [Variable]        | [Type] | [Default] | [Unit] | [Description]
        ------------------|--------|-----------|--------|----------------------------------
        startTime         | float  | None      | CA     | The start-time for post-processing.
                          |        |           |        | If None, uses IVC
        endTime           | float  | None      | CA     | The start-time for post-processing.
                          |        |           |        | If None, uses EVO
        IVC               | float  | -         | CA     | Inlet valve closing
        EVO               | float  | -         | CA     | Inlet valve closing
        ------------------|--------|-----------|--------|----------------------------------
        speed             | float  | -         | rpm    | Rotational speed
        
        """
        #Argument checking:
        try:
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
                
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        try:
            self.n = speed
            self.omega = speed / 60.0 * 2.0 * math.pi
            self.IVC = IVC
            self.EVO = EVO
            self.startTime = startTime
            self.endTime = endTime
            
            self.time = None
            self.oldTime = None
            
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, "Construction failed", err)
    
    ######################################
    #NOTE: overwrite in child class if necessary
    @property
    def timings(self) -> dict[str:float]:
        """
        A dictionary with the relevant timings (IVC, EVO, etc...)

        Returns:
            dict[str:float]
        """
        return {"IVC":self.IVC, "EVO":self.EVO}
    
    #########################################################################
    @classmethod
    def fromDictionary(cls, dictionary):
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
    def __call__(self, timeList:list[float]):
        """
        Iteration over time steries, from startTime to endTime.

        Args:
            timeList (list[float]): list of times

        Yields:
            float: current time
        """
        self.oldTime = max(self.startTime, timeList[0])
        
        for CA in timeList:
            if (CA > self.startTime) and (CA <= self.endTime):
                self.time = CA
                self.deltaT = self.time - self.oldTime
                yield CA
                self.oldTime = CA
    
    #########################################################################
    #CA to Time:
    def CA2Time(self,CA:float|Iterable) -> float|np.ndarray[float]:
        """
        Converts CA to time [s]

        Args:
            CA (float | Iterable): Time in CA

        Returns:
            float|np.ndarray[float]: Time in seconds
        """
        try:
            if isinstance(CA, list):
                return np.array([ca/self.dCAdt for ca in CA])
            else:
                return CA/self.dCAdt
        except BaseException as err:
            self.fatalErrorInClass(self.CA2Time, "Failed conversion from CA to time", err)
    
    ###################################
    #Time to CA:
    def Time2CA(self,t:float|Iterable) -> float|np.ndarray:
        """
        Converts time [s] to CA

        Args:
            t (float | Iterable): Time in seconds

        Returns:
            float|np.ndarray: time in CA
        """
        try:
            if isinstance(t, list):
                return np.array([T*self.dCAdt for T in t])
            else:
                return t*self.dCAdt
        except BaseException as err:
            self.fatalErrorInClass(self.Time2CA, "Failed conversion from time to CA", err)
    
    ###################################
    def isCombustion(self,CA:float|Iterable=None) -> bool|np.ndarray[bool]:
        """
        Check if combustion has started.

        Args:
            CA (float | Iterable | None): Cranc angle to check. If None, checks for self.time

        Returns:
            bool|np.ndarray[bool]: If combustion started
        """
        try:
            if not CA is None:
                self.checkTypes(CA, (float, Iterable), "CA")
            else:
                CA = self.time
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.isCombustion, err)
        
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
    def isClosedValves(self,CA:float|Iterable=None) -> bool|np.ndarray[bool]:
        """
        Check if at closed valves (after IVC and before EVO)

        Args:
            CA (float | Iterable | None): Cranc angle to check. If None, checks for self.time

        Returns:
            bool|np.ndarray[bool]: If at closed valves
        """
        try:
            if not CA is None:
                self.checkTypes(CA, (float, Iterable), "CA")
            else:
                CA = self.time
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.isCombustion, err)
        
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
        timeList = np.array(timeList)
        self.startTime = timeList[timeList >= self.startTime][0]
        self.time = self.startTime
        self.oldTime = None
    
#############################################################################
EngineTime.createRuntimeSelectionTable()
