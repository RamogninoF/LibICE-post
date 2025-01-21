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

from libICEpost import Dictionary
from .EquationOfState import EquationOfState

from dataclasses import dataclass

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
@dataclass
class PerfectGas(EquationOfState):
    """
    Perfect gas equation of state
    
    Attributes:
        Rgas (float): The mass specific gas constant
    """
    
    Rgas:float
    """The mass specific gas constant [J/kg/K]"""
    
    #########################################################################
    @classmethod
    def fromDictionary(cls, dictionary):
        """
        Create from dictionary.
        """
        dictionary = Dictionary(**dictionary)
        return cls(dictionary.lookup("Rgas"))
        
    #########################################################################
    #Operators:
    def __str__(self):
        return super().__str__() + f"Rgas: {self.Rgas}\n"
    
    #####################################
    def __repr__(self):
        R = \
            {
                "Rgas": self.Rgas
            }
        return f"{self.TypeName}{R.__repr__()}"
    
    #####################################
    def __eq__(self, other:PerfectGas):
        self.checkType(other,PerfectGas,"other")
        return self.Rgas == other.Rgas
    
    #####################################
    def __ne__(self, other:PerfectGas):
        self.checkType(other,PerfectGas,"other")
        return self.Rgas != other.Rgas
    
    #####################################
    def __hash__(self):
        return hash(self.__repr__())
    
    #########################################################################
    #Methods:
    def cp(self, p:float, T:float) -> float:
        """
        Constant pressure heat capacity contribution [J/kg/K]
        """
        super().cp(p,T)
        return 0.0
    
    #####################################
    def h(self, p:float, T:float) -> float:
        """
        Enthalpy contribution [J/kg]
        """
        super().h(p,T)
        return 0.0
    
    #####################################
    def u(self, p:float, T:float) -> float:
        """
        Internal energy contribution [J/kg]
        """
        super().u(p,T)
        return 0.0
    
    #####################################
    def rho(self, p:float, T:float) -> float:
        """
        Density [kg/m^3]
        """
        super().rho(p,T)
        return p/(T * self.Rgas)
    
    #####################################
    def T(self, p:float, rho:float) -> float:
        """
        Temperature [K]
        """
        super().T(p,rho)
        return p/(rho * self.Rgas)
    
    #####################################
    def p(self, T:float, rho:float) -> float:
        """
        Pressure [Pa]
        """
        super().p(T,rho)
        return rho * T * self.Rgas
    
    #####################################
    def Z(self, p:float, T:float) -> float:
        """
        Compression factor [-]
        """
        super().Z(p,T)
        return 1.0
    
    #####################################
    def cpMcv(self, p:float, T:float) -> float:
        """
        Difference cp - cv.
        """
        super().cpMcv(p,T)
        return self.Rgas
    
    #####################################
    def dcpdT(self, p, T):
        """
        dcp/dT [J/kg/K^2]
        """
        super().dcpdT(p,T)
        return 0.0
    
    #####################################
    def dpdT(self, p, T):
        """
        dp/dT [Pa/K]
        """
        super().dpdT(p,T)
        return self.rho(p,T)*self.Rgas
    
    #####################################
    def dTdp(self, p, T):
        """
        dT/dp [K/Pa]
        """
        super().dTdp(p,T)
        return self.rho(p,T)*self.Rgas
    
    #####################################
    def drhodp(self, p, T):
        """
        drho/dp [kg/(m^3 Pa)]
        """
        super().drhodp(p,T)
        return 1.0/(self.Rgas * T)
    
    #####################################
    def dpdrho(self, p, T):
        """
        dp/drho [Pa * m^3 / kg]
        """
        super().dpdrho(p,T)
        return (self.Rgas * T)
    
    #####################################
    def drhodT(self, p, T):
        """
        drho/dT [kg/(m^3 K)]
        """
        super().drhodT(p,T)
        return -p/(self.Rgas * (T ** 2.0))
    
    #####################################
    def dTdrho(self, p, T):
        """
        dT/drho [K * m^3 / kg]
        """
        super().dTdrho(p,T)
        return -p/(self.Rgas * (self.rho(p,T) ** 2.0))

#############################################################################
EquationOfState.addToRuntimeSelectionTable(PerfectGas)
