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

import numpy as np
import math

from libICEpost.src.base.BaseClass import BaseClass

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
    def CA2Time(self,CA):
        """
        CA:     float / list<float/int>
            Crank angle
        
        Converts CA to time [s]
        """
        try:
            if isinstance(CA, list):
                return [ca/self.dCAdt for ca in CA]
            else:
                return CA/self.dCAdt
        except BaseException as err:
            self.fatalErrorInClass(self.CA2Time, "", err)
    
    ###################################
    #Time to CA:
    def Time2CA(self,t):
        """
        CA:     float / list<float/int>
            Crank angle
            
        Converts time [s] to CA
        """
        try:
            if isinstance(t, list):
                return [T*self.dCAdt for T in t]
            else:
                return t*self.dCAdt
        except BaseException as err:
            self.fatalErrorInClass(self.Time2CA, "", err)
    
    ###################################
    def isCombustion(self,CA):
        """
        CA:     float
            Crank angle
            
        Check if combustion has started. To be overwritten by derived classes
        """
        try:
            self.checkType(CA, float, "CA")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.isCombustion, err)
        
        if not self.startOfCombustion() is None:
            return CA > self.startOfCombustion()
        else:
            return False
    
    ###################################
    def startOfCombustion(self):
        """
        Instant of start of combustion (overwritten in derived class depending on combustion mode). By default, returns None (motoring condition).
        """
        return None
    
    ###################################
    def isClosedValves(self,CA):
        """
        CA:     float
            Crank angle
            
        Check if at closed valves (avter IVC and before EVO)
        """
        try:
            self.checkType(CA, float, "CA")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.isCombustion, err)
            
        return ((CA >= self.IVC) and (CA <= self.EVO))

    ###################################
    def updateStartTime(self, timeList:list[float]) -> None:
        """
        Update the start-time to be consistent with the avaliable data

        Args:
            timeList (list[float]): The avaliable time series
        """
        timeList = np.array(timeList)
        self.startTime = timeList[timeList >= self.startTime][0]
        self.time = self.startTime
        self.oldTime = None
    
#############################################################################
EngineTime.createRuntimeSelectionTable()
