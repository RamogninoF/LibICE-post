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

from libICEpost.src.base.BaseClass import BaseClass

from .EquationOfState import EquationOfState

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class PerfectGas(EquationOfState):
    """
    Perfect gas equation of state
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        Rgas: float
            The mass specific gas constant
    """
    
    #########################################################################
    @classmethod
    def fromDictionary(cls, dictionary):
        """
        Create from dictionary.
        """
        try:
            entryList = ["Rgas"]
            for entry in entryList:
                if not entry in dictionary:
                    raise ValueError(f"Mandatory entry '{entry}' not found in dictionary.")
            
            out = cls\
                (
                    dictionary["Rgas"]
                )
            return out
            
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed construction from dictionary", err)
    
    #########################################################################
    #Constructor:
    def __init__(self, Rgas:float):
        """
        Rgas: float
            The mass specific gas constant
        """
        try:
            self.checkType(Rgas, float, "Rgas")
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, "Argument checking failed", err)
        self.Rgas = Rgas
        
    #########################################################################
    #Operators:

    #########################################################################
    def cp(self, p, T):
        """
        Constant pressure heat capacity contribution [J/kg/K]
        """
        super(self.__class__,self).cp(p,T)
        return 0.0
    
    #########################################################################
    def cv(self, p, T):
        """
        Constant volume heat capacity contribution [J/kg/K]
        """
        super(self.__class__,self).cv(p,T)
        return 0.0
    
    #########################################################################
    def h(self, p, T):
        """
        Enthalpy contribution [J/kg]
        """
        super(self.__class__,self).h(p,T)
        return 0.0
    
    #########################################################################
    def rho(self, p, T):
        """
        Density [kg/m^3]
        """
        super(self.__class__,self).rho(p,T)
        return p/(T * self.Rgas)
    
    #########################################################################
    def T(self, p, rho):
        """
        Temperature [K]
        """
        super(self.__class__,self).T(p,rho)
        return p/(rho * self.Rgas)
    
    #########################################################################
    def p(self, T, rho):
        """
        Pressure [Pa]
        """
        super(self.__class__,self).p(T,rho)
        return rho * T * self.Rgas
    
    #########################################################################
    def Z(self, p, T):
        """
        Compression factor [-]
        """
        super(self.__class__,self).Z(p,T)
        return 1.0
    
    #########################################################################
    def dpdT(self, p, T):
        """
        dp/dT [Pa/K]
        """
        super(self.__class__,self).dpdT(p,T)
        return self.rho(p,T)*self.Rgas
    
    #########################################################################
    def dTdp(self, p, T):
        """
        dT/dp [K/Pa]
        """
        super(self.__class__,self).dTdp(p,T)
        return self.rho(p,T)*self.Rgas
    
    #########################################################################
    def drhodp(self, p, T):
        """
        drho/dp [kg/(m^3 Pa)]
        """
        super(self.__class__,self).drhodp(p,T)
        return 1.0/(self.Rgas * T)
    
    #########################################################################
    def dpdrho(self, p, T):
        """
        dp/drho [Pa * m^3 / kg]
        """
        super(self.__class__,self).dpdrho(p,T)
        return (self.Rgas * T)
    
    #########################################################################
    def drhodT(self, p, T):
        """
        drho/dT [kg/(m^3 K)]
        """
        super(self.__class__,self).drhodT(p,T)
        return -p/(self.Rgas * (T ** 2.0))
    
    #########################################################################
    def dTdrho(self, p, T):
        """
        dT/drho [K * m^3 / kg]
        """
        super(self.__class__,self).dTdrho(p,T)
        return -p/(self.Rgas * (self.rho(p,T) ** 2.0))

#############################################################################
EquationOfState.addToRuntimeSelectionTable(PerfectGas)
