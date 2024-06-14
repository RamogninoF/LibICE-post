#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023
"""

# Necessito:
# 1) Definire lo stato del sistema (dataclass?)
# 2) Metodi update() _update() per aggiornare il sistema e propagare in basso, eventualmente fornendo un nuovo stato (tramite dizionario? dataclass?)

# Nelle classi derivate devo:
# 1) Definire metodo _update()
# 2) Definire I/O dei parametri (properties) che a loro volta aggiornino lo stato

#####################################################################
#                               IMPORT                              #
#####################################################################

from __future__ import annotations

from libICEpost.src.base.Utilities import Utilities
# from libICEpost.src.base.BaseClass import BaseClass, abstractmethod

from .thermoMixture.ThermoMixture import ThermoMixture
from .StateInitializer.StateInitializer import StateInitializer
from .ThermoState import ThermoState

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class ThermoModel(Utilities): #(BaseClass):
    """
    Base class for handling a thermodynamic model
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    """
    #########################################################################
    #Properties:
    @property
    def mixture(self)-> ThermoMixture:
        """
        Reference to the mixture in the system

        Returns:
            ThermoMixture: thermodynamic mixture
        """
        return self._mixture
    
    @property
    def state(self) -> ThermoState:
        """
        return current state of the system (read-only)

        Returns:
            ThermoState: dataClass for the thermodynamic state of the system
        """
        
        return self.cp.deepcopy(self._state)
    
    
    #########################################################################
    # @classmethod
    # def fromDictionary(cls, dictionary):
    #     """
    #     Construct thermodynamic model from mixture and current state of 
    #     the system. Check StateInitializer child classes for available
    #     initializing procedures available.
        
    #     Construct from dictionary like:
    #     {
    #         mixture (ThermoMixture): The thermodynamic mixture in the system  (stored as reference)
    #         mass (float, optional): [kg]. Defaults to None.
    #         pressure (float, optional): [Pa]. Defaults to None.
    #         volume (float, optional): [m^3]. Defaults to None.
    #         temperature (float, optional): [K]. Defaults to None.
    #         density (float, optional): [kg/m^3]. Defaults to None.
    #     }
    #     """
    #     return cls(**dictionary)
    
    #########################################################################
    #Constructor:
    def __init__(self, /, *, 
                 mixture:ThermoMixture,
                 mass:float=None,
                 pressure:float=None,
                 volume:float=None,
                 temperature:float=None,
                 density:float=None) -> None:
        """
        Construct thermodynamic model from mixture and current state of 
        the system. Check StateInitializer child classes for available
        initializing procedures available.

        Args:
            mixture (ThermoMixture): The thermodynamic mixture in the system  (stored as reference)
            mass (float, optional): [kg]. Defaults to None.
            pressure (float, optional): [Pa]. Defaults to None.
            volume (float, optional): [m^3]. Defaults to None.
            temperature (float, optional): [K]. Defaults to None.
            density (float, optional): [kg/m^3]. Defaults to None.
        """
        
        try:
            #Mixture:
            self.checkType(mixture, ThermoMixture, "mixture")
            self._mixture = mixture
            
            #Initialize state:
            stateDict = \
                {
                    "mix":mixture,
                    "m":mass,
                    "p":pressure,
                    "V":volume,
                    "T":temperature,
                    "rho":density
                }
            
            #Remove None entries:
            stateDict = {key:stateDict[key] for key in stateDict if not (stateDict[key] is None)}
            
            #Retrieve initializer:
            initializerType = "".join(sorted([key for key in stateDict]))
            self._state = StateInitializer.selector(initializerType,stateDict)()
        
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, f"Failed constructing instance of class {self.__class__.__name__}", err)
            
    #########################################################################
    #Operators:
    
    ################################
    
    #########################################################################
    #Methods:
    def update(self, /, *,
        mixture:ThermoMixture=None,
        mass:float=None,
        pressure:float=None,
        volume:float=None,
        temperature:float=None,
        density:float=None)->ThermoModel:
        """
        Update state of the system based on control variables through 
        keyword arguments.

        Args:
            mixture (ThermoMixture, optional): The thermodynamic mixture in the system. Defaults to None.
            mass (float, optional): [kg]. Defaults to None.
            pressure (float, optional): [Pa]. Defaults to None.
            volume (float, optional): [m^3]. Defaults to None.
            temperature (float, optional): [K]. Defaults to None.
            density (float, optional): [kg/m^3]. Defaults to None.
            
            TODO: dQ_in, dm_in, mixture_in

        Returns:
            ThermoModel: self
        """
        #TODO:
        # define energy and mass equations to update the state. The source and 
        # sink terms are defined with the change of state variables (delta m and delta T)
        
        pass
    
    ################################
    
#########################################################################
#Create selection table:
# ThermoModel.createRuntimeSelectionTable()