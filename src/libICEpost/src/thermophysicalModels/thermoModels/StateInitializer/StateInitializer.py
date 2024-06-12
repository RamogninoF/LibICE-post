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

#Import BaseClass class (interface for base classes)
from typing import Any
from libICEpost.src.base.BaseClass import BaseClass, abstractmethod

from ..thermoMixture.ThermoMixture import ThermoMixture
from ..ThermoState import ThermoState

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################

class StateInitializer(BaseClass):
    """
    Base class  for initialization of ThermoState (used for selection)
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        mix: ThermoMixture
            Reference to the thermodynamic mixture
    """
    
    #########################################################################
    #Properties:
    
    ################################
    
    #########################################################################
    #Class methods and static methods:
    
    #########################################################################
    #Constructor
    @abstractmethod
    def __init__(self, /, *, mix:ThermoMixture) -> None:
        """
        Setting mixture, to be overwritten in child

        Args:
            mix (ThermoMixture): The thermodynamic mixture in the system  (stored as reference)
        """
        #Argument checking:
        try:
            #Type checking
            self.checkType(mix, ThermoMixture, "mix")
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        try:
            self.mix = ThermoMixture
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, f"Failed construction of {self.__class__.__name__} instance", err)
    
    #########################################################################
    #Dunder methods:
    def __call__(self) -> ThermoState:
        """
        Return the initialized thermodynamic state

        Returns:
            ThermoState: the state
        """
        return self.cp.deepcopy(self._state)
    
    #########################################################################
    #Methods:

    
#########################################################################
#Create selection table for the class used for run-time selection of type
StateInitializer.createRuntimeSelectionTable()