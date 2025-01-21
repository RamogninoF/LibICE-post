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

from libICEpost.src.base.BaseClass import BaseClass, abstractmethod

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class EquationOfState(BaseClass):
    """
    Class handling thermodynamic equation of state
    """
    
    #########################################################################
    #Constructor:
    def __init__(self):
        """
        Base (virtual) class: does not support instantiation.
        """
        pass
    #########################################################################
    #Operators:
    
    ################################
    #Print:
    def __str__(self):
        stringToPrint = ""
        stringToPrint += f"Equation of state class\n"
        stringToPrint += "Type:\t" + self.TypeName + "\n"
        
        return stringToPrint
    
    ##############################
    #Representation:
    def __repr__(self):
        return f"{self.TypeName}()"

     #########################################################################
    @abstractmethod
    def cp(self, p:float, T:float) -> float:
        """
        Constant pressure heat capacity contribution [J/kg/K]
        """
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
    
    #########################################################################
    @abstractmethod
    def h(self, p:float, T:float) -> float:
        """
        Enthalpy contribution [J/kg]
        """
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
            
    #########################################################################
    @abstractmethod
    def u(self, p:float, T:float) -> float:
        """
        Internal energy contribution [J/kg]
        """
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
    
    #########################################################################
    @abstractmethod
    def rho(self, p:float , T:float) -> float:
        """
        Density [kg/m^3]
        """
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
    
    #########################################################################
    @abstractmethod
    def T(self, p:float, rho:float) -> float:
        """
        Temperature [K]
        """
        self.checkType(p, float, "p")
        self.checkType(rho, float, "rho")
            
    #########################################################################
    @abstractmethod
    def p(self, T:float, rho:float) -> float:
        """
        pressure [Pa]
        """
        self.checkType(T, float, "T")
        self.checkType(rho, float, "rho")
    
    #########################################################################
    @abstractmethod
    def Z(self, p:float, T:float) -> float:
        """
        Compression factor [-]
        """
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
    
    #########################################################################
    @abstractmethod
    def cpMcv(self, p:float, T:float) -> float:
        """
        Difference cp - cv.
        """
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
            
    #########################################################################
    @abstractmethod
    def dcpdT(self, p, T):
        """
        dcp/dT [J/kg/K^2]
        """
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
    
    #########################################################################
    @abstractmethod
    def dpdT(self, p, T):
        """
        dp/dT [Pa/K]
        """
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
    
    #########################################################################
    @abstractmethod
    def dTdp(self, p, T):
        """
        dT/dp [K/Pa]
        """
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
    
    #########################################################################
    @abstractmethod
    def drhodp(self, p, T):
        """
        drho/dp [kg/(m^3 Pa)]
        """
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
    
    #########################################################################
    @abstractmethod
    def dpdrho(self, p, T):
        """
        dp/drho [Pa * m^3 / kg]
        """
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
    
    #########################################################################
    @abstractmethod
    def drhodT(self, p, T):
        """
        drho/dT [kg/(m^3 K)]
        """
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")
    
    #########################################################################
    @abstractmethod
    def dTdrho(self, p, T):
        """
        dT/drho [K * m^3 / kg]
        """
        self.checkType(p, float, "p")
        self.checkType(T, float, "T")

#############################################################################
#Generate selection table
EquationOfState.createRuntimeSelectionTable()