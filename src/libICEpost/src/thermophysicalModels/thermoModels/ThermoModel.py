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

from __future__ import annotations

from libICEpost.src.base.Utilities import Utilities

from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture
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
    _state:ThermoState
    """The current thermodynamic state"""
    
    _ThermoStateClass:ThermoState = ThermoState
    """The ThermoState class used for this engine model"""
    
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
        
        return self._state.copy()
    
    #########################################################################
    #Class methods
    
    #########################################################################
    #Constructor:
    def __init__(self,
                 mixture:ThermoMixture,
                 *,
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
        
        #Mixture:
        self.checkType(mixture, ThermoMixture, "mixture")
        self._mixture = mixture
        
        #Initialize state:
        self.initializeState(mass=mass,pressure=pressure,volume=volume,temperature=temperature,density=density)
            
    #########################################################################
    #Operators:
    
    #########################################################################
    #Methods:
    def initializeState(self, /, *,
            mixture:Mixture=None,
            mass:float=None,
            pressure:float=None,
            volume:float=None,
            temperature:float=None,
            density:float=None)->ThermoModel:
        """
        Initialize the state of the system through a StateInitializer.

        Args:
            mixture (Mixture, optional): The mixture composition in the system. Defaults to None.
            mass (float, optional): [kg]. Defaults to None.
            pressure (float, optional): [Pa]. Defaults to None.
            volume (float, optional): [m^3]. Defaults to None.
            temperature (float, optional): [K]. Defaults to None.
            density (float, optional): [kg/m^3]. Defaults to None.

        Returns:
            ThermoModel: self
        """
        stateDict = \
            {
                "m":mass,
                "p":pressure,
                "V":volume,
                "T":temperature,
                "rho":density
            }
        
        #Mixture
        if not mixture is None:
            self.checkType(mixture, Mixture, "mixture")
            self._mixture.update(mixture=mixture)
        
        #Remove None entries:
        stateDict = {key:stateDict[key] for key in stateDict if not (stateDict[key] is None)}
        
        if len(stateDict) > 0:
            #Retrieve initializer:
            initializerType = "".join(sorted([key for key in stateDict],key=str.lower))
            stateDict["mix"] = self.mixture
            stateDict["thermoStateClass"] = self._ThermoStateClass.__name__
            self._state:ThermoState = StateInitializer.selector(initializerType,stateDict)()
        else:
            self._state:ThermoState = self._ThermoStateClass()
    
    ################################
    def update(self, /, *,
        mixture:Mixture=None,
        pressure:float=None,
        volume:float=None,
        temperature:float=None,
        dQ_in:float=0.0,
        dm_in:float=0.0)->tuple[float,float]:
        """
        Update state of the system based on control variables through 
        keyword arguments.

        Args:
            mixture (Mixture, optional): The mixture composition in the system. Defaults to None.
            pressure (float, optional): [Pa]. Defaults to None.
            volume (float, optional): [m^3]. Defaults to None.
            temperature (float, optional): [K]. Defaults to None.
            dQ_in (float, optional): Entering heat. Defaults to 0.0.
            dm_in (float, optional): Entering mass. Defaults to 0.0.
            
            TODO: dQ_in, dm_in

        Returns:
            tuple[float,float]: dQ_in and dm_in
        """
        #TODO:
        # handling also heat exchanges dQ_in (polythropic transformation? Independent variable from p,T,V).
        
        #Mixture
        if not mixture is None:
            self.checkType(mixture, Mixture, "mixture")
            self._mixture.update(mixture=mixture)
        
        #Update mass
        self._state.m += dm_in
        
        #Update p,V,T
        if sum([int(v is None) for v in [pressure, temperature,volume]]) == 2:
            raise ValueError("Supply two of (p,V,T)")
        
        #Update volume (and density)
        if not (volume is None):
            self._state.V = volume
            self._state.rho = self._state.m/self._state.V
            
            #Update pressure
            if not (pressure is None):
                self._state.p = pressure
                self._state.T = self.mixture.EoS.T(self._state.p, self._state.rho)
            else:
                #Update from temperature
                self._state.T = temperature
                self._state.p = self.mixture.EoS.p(self._state.T, self._state.rho)
        
        else:
            #Update from pressure and temperature
            self._state.p = pressure
            self._state.T = temperature
            
            self._state.rho = self.mixture.EoS.rho(self._state.p, self._state.T)
            self._state.V = self._state.m/self._state.rho
    ################################
    
#########################################################################