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
from libICEpost.src.base.dataStructures.Dictionary import Dictionary

from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture

from libICEpost.Database import _DatabaseClass
from libICEpost.Database.chemistry.thermo import database

from .mixingRules.EquationOfState.EquationOfStateMixing import EquationOfStateMixing
from .mixingRules.Thermo.ThermoMixing import ThermoMixing

from libICEpost.src.thermophysicalModels.specie.thermo.EquationOfState.EquationOfState import EquationOfState
from libICEpost.src.thermophysicalModels.specie.thermo.Thermo.Thermo import Thermo

from . import mixingRules

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class ThermoMixture(Utilities):
    """
    Class for computing thermodynamic data of a mixture.
    
    Attributes:
        mix (Mixture): The composition of the mixture.
        EoS (EquationOfState): The equation of state of the mixture.
        Thermo (Thermo): The thermodynamic model of the mixture.
    """
    
    _mix:Mixture
    """The composition of the mixture"""
    _EoS:EquationOfStateMixing
    """The equation of state of the mixture"""
    _Thermo:ThermoMixing
    """The thermodynamic model of the mixture"""
    _db:_DatabaseClass = database.chemistry.thermo
    """Database of thermodynamic data"""
    
    #########################################################################
    #Properties:

    @property
    def mix(self) -> Mixture:
        """
        The composition of the mixture (Mixture).
        """
        return self._mix
    
    ################################
    @property
    def db(self) -> _DatabaseClass:
        """
        Database of thermodynamic data (reference to database.chemistry.thermo)
        """
        return self._db
    
    ################################
    @property
    def Thermo(self) -> Thermo:
        """
        Thermodynamic data of this mixture.
        """
        return self._Thermo.Thermo
    
    ################################
    @property
    def EoS(self) -> EquationOfState:
        """
        The equation of state of this mixture.

        Returns:
            EquationOfState
        """
        return self._EoS.EoS

    #########################################################################
    #Constructor:
    def __init__(self, mixture: Mixture, thermoType: dict[str,str], **thermoData):
        """
        Construct new instance of thermodynamic model of mixture from the mixture composition and mixingRule
        
        Args:
            mixture (Mixture): The composition of the mixture.
            thermoType (dict[str,str]): The types of thermodynamic models. Required are:
                - Thermo
                - EquationOfState
            **thermoData: Additional data for the thermodynamic models.
        """

        self.checkType(mixture, Mixture, "mixture")
        self.checkMap(thermoType, str, str, "thermoType")

        #Copy the mixture
        self._mix = mixture.copy()
        
        #Lookup the Thermo and EoS types
        thermoType = Dictionary(**thermoType)
        ThermoType = thermoType.lookup("Thermo")
        EoSType = thermoType.lookup("EquationOfState")
        
        #Set the Thermo and EoS
        thermoData:Dictionary = Dictionary(thermoData)
        self._Thermo = mixingRules.ThermoMixing.selector(ThermoType + "Mixing", thermoData.lookupOrDefault(ThermoType + "Dict", Dictionary()).update(mixture=self._mix))
        self._EoS = mixingRules.EquationOfStateMixing.selector(EoSType + "Mixing", thermoData.lookupOrDefault(EoSType + "Dict", Dictionary()).update(mixture=self._mix))
        
        self._Thermo._mix = self._mix #Set the reference to the mixture
        self._EoS._mix = self._mix #Set the reference to the mixture
        
    #########################################################################
    #Operators:
    def __repr__(self) -> str:
        """Dict-like representation with thermodynamic model classes and mixture"""
        out = \
            {
                "EoS":self.EoS.__class__.__name__,
                "Thermo":self.Thermo.__class__.__name__,
                "mixture":self.mix
            }
        return ThermoMixture.__name__ + repr(out)
    
    ####################################
    def __str__(self) -> str:
        """Printing the type of thermodynamic models and the mixture"""
        str = f"Equation of state: {self.EoS.__class__.__name__}\n" + \
              f"Thermo model: {self.Thermo.__class__.__name__}\n" + \
              f"Mixture:\n{self.mix.__str__()}"
        return str
    
    #########################################################################
    #Member functions:
    #NOTE: the derivatives of thermodynamic quantities (p,T,rho) 
    # are defined only in the equation of state, as they are not 
    # affected by the specific thermo. Similarly, hf is only in 
    # thermo.
    
    def update(self, mixture:Mixture=None) -> ThermoMixture:
        """
        Update the mixture composition

        Args:
            mixture (Mixture, optional): The new mixture. Defaults to None.

        Returns:
            ThermoMixture: self
        """
        
        if not mixture is None:
            self._mix.update(mixture.species, mixture.Y, fracType="mass") #Update mixture
            self._Thermo.update(self.mix) #Update Thermo (even if it has same reference, better to update)
            self._EoS.update(self.mix) #Update EoS (even if it has same reference, better to update)
        return self
    
    ################################
    def dcpdT(self, p:float, T:float) -> float:
        """
        dcp/dT [J/kg/K^2]
        """
        return self.Thermo.dcpdT(p, T) + self.EoS.dcpdT(p, T)
        
    ################################
    def ha(self, p:float, T:float) -> float:
        """
        Absolute enthalpy [J/kg]
        """
        try:
            return self.Thermo.ha(p, T) + self.EoS.h(p, T)
        except NotImplementedError:
            #Internal energy-based Thermo
            return self.Thermo.ua(p, T) + p/self.EoS.rho(p, T) + self.EoS.h(p, T)
    
    ################################
    def hs(self, p:float, T:float) -> float:
        """
        Sensible enthalpy [J/kg]
        """
        try:
            return self.Thermo.hs(p, T) + self.EoS.h(p, T)
        except NotImplementedError:
            #Internal energy-based Thermo
            return self.Thermo.us(p, T) + p/self.EoS.rho(p, T) + self.EoS.h(p, T)
    
    ################################
    def ua(self, p:float, T:float) -> float:
        """
        Absolute internal energy [J/kg]
        """
        try:
            return self.Thermo.ua(p, T) + self.EoS.u(p, T)
        except NotImplementedError:
            #Entalpy-based Thermo
            return self.Thermo.ha(p, T) - p/self.EoS.rho(p, T) + self.EoS.u(p, T)
    
    ################################
    def us(self, p:float, T:float) -> float:
        """
        Sensible internal energy [J/kg]
        """
        try:
            return self.Thermo.us(p, T) + self.EoS.u(p, T)
        except NotImplementedError:
            #Entalpy-based Thermo
            return self.Thermo.hs(p, T) - p/self.EoS.rho(p, T) + self.EoS.u(p, T)
    
    ################################
    def cp(self, p:float, T:float) -> float:
        """
        Constant pressure heat capacity [J/kg/K]
        """
        return self.Thermo.cp(p, T) + self.EoS.cp(p, T)
    
    ################################
    def cv(self, p:float, T:float) -> float:
        """
        Constant volume heat capacity [J/kg/K]
        """
        return self.cp(p, T) - self.EoS.cpMcv(p, T)
    
    ################################
    def gamma(self, p:float, T:float) -> float:
        """
        Heat capacity ratio cp/cv [-]
        """
        return self.cp(p, T)/self.cv(p, T)