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

from src.base.BaseClass import BaseClass

from .EquationOfState import EquationOfState

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class PerfectGas(EquationOfState):
    """
    Perfect gas equation of state
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        chem: Molecule
            Chemical specie for which the thermodynamic properties are defined
    """
    
    #########################################################################
    #Constructor:
    def __init__(self, chem):
        """
        chem: Molecule
            Chemical specie for which the thermodynamic properties are defined
        """
        super(self.__class__, self).__init__(chem)
        
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
        return p/(T * self.chem.Rgas())
    
    #########################################################################
    def T(self, p, rho):
        """
        Temperature [K]
        """
        super(self.__class__,self).T(p,rho)
        return p/(rho * self.chem.Rgas())
    
    #########################################################################
    def p(self, T, rho):
        """
        Pressure [Pa]
        """
        super(self.__class__,self).p(T,rho)
        return rho * T * self.chem.Rgas()
    
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
        return self.rho(p,T)*self.chem.Rgas()
    
    #########################################################################
    def dTdp(self, p, T):
        """
        dT/dp [K/Pa]
        """
        super(self.__class__,self).dTdp(p,T)
        return self.rho(p,T)*self.chem.Rgas()
    
    #########################################################################
    def drhodp(self, p, T):
        """
        drho/dp [kg/(m^3 Pa)]
        """
        super(self.__class__,self).drhodp(p,T)
        return 1.0/(chem.Rgas() * T)
    
    #########################################################################
    def dpdrho(self, p, T):
        """
        dp/drho [Pa * m^3 / kg]
        """
        super(self.__class__,self).dpdrho(p,T)
        return (chem.Rgas() * T)
    
    #########################################################################
    def drhodT(self, p, T):
        """
        drho/dT [kg/(m^3 K)]
        """
        super(self.__class__,self).drhodT(p,T)
        return -p/(chem.Rgas() * (T ** 2.0))
    
    #########################################################################
    def dTdrho(self, p, T):
        """
        dT/drho [K * m^3 / kg]
        """
        super(self.__class__,self).dTdrho(p,T)
        return -p/(chem.Rgas() * (self.rho(p,T) ** 2.0))

#############################################################################
EquationOfState.addToRuntimeSelectionTable("PerfectGas")
