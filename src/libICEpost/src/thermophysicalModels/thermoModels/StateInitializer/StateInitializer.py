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
    mix:ThermoMixture
    thermoStateClass:str
    _state:ThermoState
    
    #########################################################################
    #Properties:
    
    ################################
    
    #########################################################################
    #Class methods and static methods:
    
    #########################################################################
    #Constructor
    @abstractmethod
    def __init__(self, /, *, mix:ThermoMixture, thermoStateClass:str="ThermoState") -> None:
        """
        Setting mixture, to be overwritten in child

        Args:
            mix (ThermoMixture): The thermodynamic mixture in the system  (stored as reference)
            thermoStateClass (str, optional): The specific ThermoState class to construct. Defaults to "ThermoState".
        """
        #Argument checking:
        self.checkType(mix, ThermoMixture, "mix")
        self.checkType(thermoStateClass, str, "thermoStateClass")
        
        self.mix = mix
        self.thermoStateClass = thermoStateClass
    
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