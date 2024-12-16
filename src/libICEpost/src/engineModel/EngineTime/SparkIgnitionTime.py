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

from .EngineTime import EngineTime

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class SparkIgnitionTime(EngineTime):
    """
    Class for spark-ignition time. Derived from engineTime, defines the attribute 
    SA (spark-advance) and sets it for determining the start-of-combustion.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        Variable   |Type       |Unit   |Description
        -----------|-----------|-------|------------------------
        IVC        |float      |CA     |Inlet valve closing
        EVO        |float      |CA     |Inlet valve closing
        SA         |float      |CA     |Spark advance
        n          |float      |rpm    |Rotational speed
        omega      |float      |rad/s  |
    """
    
    #########################################################################
    #Constructor:
    def __init__(self,*args, SA, **argv):
        """
        Construct from keyword arguments containing the following parameters:
        
        [Variable]        | [Type] | [Default] | [Unit] | [Description]
        ------------------|--------|-----------|--------|---------------------
        IVC               | float  | -         | CA     | Inlet valve closing
        EVO               | float  | -         | CA     | Inlet valve closing
        SA                | float  | -         | CA     | Spark advance
        ------------------|--------|-----------|--------|---------------------
        speed             | float  | -         | rpm    | Rotational speed
        
        """
        #Argument checking:
        self.checkType(SA,float,"SA")
        super().__init__(*args,**argv)
        
        self.SA = SA
    
    #########################################################################
    def __str__(self):
        STR = super(self.__class__, self).__str__()
        STR += "\n{:15s} {:15.3f} {:15s}".format("SA", self.SA,"[CAD]")
        
        return STR
    
    #########################################################################
    @property
    def timings(self):
        """
        A dictionary with the relevant timings (IVC, EVO, etc...)

        Returns:
            dict[str:float]
        """
        out = super().timings
        out["SA"] = self.SA
        return out
    
    #########################################################################
    def startOfCombustion(self):
        """
        Instant of start of combustion (overwritten in derived class depending on combustion mode). By default, returns None (motoring condition).
        """
        return self.SA
    
#############################################################################
EngineTime.addToRuntimeSelectionTable(SparkIgnitionTime)
