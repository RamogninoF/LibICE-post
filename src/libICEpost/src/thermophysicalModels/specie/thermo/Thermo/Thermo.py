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

from abc import ABCMeta, abstractmethod

from libICEpost.src.base.BaseClass import BaseClass

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class Thermo(BaseClass):
    """
    Base class for computation of thermodynamic properties of chemical specie (cp, cv, ...)
    
    NOTE:
        -> For interal energy-based models, need to implement us (sensible)
        -> For entalpy-based models, need to implement ha (absolute)
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        Rgas: float
            The mass specific gas constant
    """
    
    #########################################################################
    #Constructor:
    def __init__(self, Rgas:float):
        self.checkType(Rgas, float, "Rgas")
        self.Rgas = Rgas
    
    #########################################################################
    #Operators:
    
    ################################
    #Print:
    def __str__(self):
        stringToPrint = ""
        stringToPrint += "Thermodynamic data\n"
        stringToPrint += "Type:\t" + self.TypeName + "\n"
        
        return stringToPrint
    
     #########################################################################
    @abstractmethod
    def cp(self, p:float, T:float) -> float:
        """
        Constant pressure heat capacity [J/kg/K]
        """
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
    
    ################################
    @abstractmethod
    def hf(self) -> float:
        """
        Enthalpy of formation [J/kg]
        """
        pass
    
    ################################
    def ha(self, p:float, T:float) -> float:
        """
        Absolute enthalpy [J/kg]
        """
        #Check argument types
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
            
        raise NotImplementedError(f"Absolute enthalpy not implemented for Thermo class {self.__class__.__name__}")
    
    ################################
    def ua(self, p:float, T:float) -> float:
        """
        Absolute internal energy [J/kg]
        
        us = ua + hf
        """
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
        
        return self.us(p,T) + self.hf()
    
    ################################
    def us(self, p:float, T:float) -> float:
        """
        Sensible internal energy [J/kg]
        """
        #Check argument types
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
            
        raise NotImplementedError(f"Sensible internal energy not implemented for Thermo class {self.__class__.__name__}")
    
    ################################
    def hs(self, p:float, T:float) -> float:
        """
        Sensible enthalpy [J/kg]
        
        hs = ha - hf
        """
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
        
        return self.ha(p,T) - self.hf()
    
    ################################
    @abstractmethod
    def dcpdT(self, p:float, T:float) -> float:
        """
        dcp/dT [J/kg/K^2]
        """
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
        
#############################################################################
Thermo.createRuntimeSelectionTable()
