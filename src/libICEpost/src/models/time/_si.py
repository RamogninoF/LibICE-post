#####################################################################
#                                 DOC                               #
#####################################################################

"""
Define the base class for spark-ignition times and a factory function
to create a spark-ignition time class from a given time class.

Content of the module:
    - `SparkIgnitionTime` (`class`): An abstract base-class for spark-ignition times.
    - `createSparkIgnitionTime` (`function`): A factory function to create a 
    spark-ignition time class from a given time class.

@author: F. Ramognino       <federico.ramognino@polimi.it>
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from ._Time import Time

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class SparkIgnitionTime(Time):
    """
    An abstract base-class for spark-ignition times. This can used for 
    assessing inheritance for a SI time class (every SI time class created
    by the factory function `createSparkIgnitionTime` is a subclass of this
    class).
    
    Attibutes:
        - `SA` (`float`): The spark advance
    """
    #########################################################################
    #Properties:
    @property
    def SA(self) -> float:
        """
        The spark advance
        
        Returns:
            float
        """
        return self._SA
    
    @SA.setter
    def SA(self, value:float):
        """
        Set the spark advance
        
        Args:
            value (float): The spark advance
        """
        self.checkType(value,float,"SA")
        self._SA = value

    @property
    def timings(self):
        """
        A dictionary with the relevant timings (IVC, EVO, etc...)

        Returns:
            dict[str,float]
        """
        out = super().timings
        out["SA"] = self.SA
        return out
    
    #########################################################################
    #Constructor:
    def __init__(self, SA:float, *args, **argv):
        """
        Construct from spark advance (SA).
        
        Args:
            SA (float): The spark advance
            *args: Time arguments
            **argv: Time keyword arguments
        """
        #Argument checking:
        super().__init__(*args,**argv)
        
        self.SA = SA
    
    #########################################################################
    def __str__(self):
        STR = super(self.__class__, self).__str__()
        STR += f"\nSpark advance: {self.SA} [{self.units}]"
    
    #########################################################################
    def startOfCombustion(self):
        """
        Instant of start of combustion (overwritten in derived class depending on combustion mode). By default, returns None (motoring condition).
        """
        soc = super().startOfCombustion()
        soc = self.SA if not soc is None else min(soc,self.SA)
        return soc

def createSparkIgnitionTime(time:type[Time]):
    """
    Create a SparkIgnitionTime subclass of a given Time-derived class and add
    it to its runtime selection table. This is a factory function.
    
    Args:
        time (type[Time]): The base class
    """
    
    if not issubclass(time,Time):
        raise TypeError("The input class must be a subclass of Time")
    
    #Create the subclass:
    class siTime(time, SparkIgnitionTime):
        """
        Class for spark-ignited systems. This defines the time instant of 
        spark ignition (SA) as the start of combustion.
        
        Attibutes:
            - `SA` (`float`): The spark advance
        """
    
    siTime.__name__ = f"SparkIgnition{time.__name__}"
    
    #Add to runtime selection table:
    time.addToRuntimeSelectionTable(siTime)
    
    return siTime