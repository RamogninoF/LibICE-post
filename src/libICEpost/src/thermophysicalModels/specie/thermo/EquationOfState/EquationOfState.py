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
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        None
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
        R = \
            {
                "type": self.TypeName
            }
        return R.__repr__()

     #########################################################################
    @abstractmethod
    def cp(self, p:float, T:float) -> float:
        """
        Constant pressure heat capacity contribution [J/kg/K]
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.cp, err)
    
    #########################################################################
    @abstractmethod
    def h(self, p:float, T:float) -> float:
        """
        Enthalpy contribution [J/kg]
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.h, err)
            
    #########################################################################
    @abstractmethod
    def u(self, p:float, T:float) -> float:
        """
        Internal energy contribution [J/kg]
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.u, err)
    
    #########################################################################
    @abstractmethod
    def rho(self, p:float , T:float) -> float:
        """
        Density [kg/m^3]
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.rho, err)
    
    #########################################################################
    @abstractmethod
    def T(self, p:float, rho:float) -> float:
        """
        Temperature [K]
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(rho, float, "rho")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.T, err)
            
    #########################################################################
    @abstractmethod
    def p(self, T:float, rho:float) -> float:
        """
        pressure [Pa]
        """
        try:
            self.checkType(T, float, "T")
            self.checkType(rho, float, "rho")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.p, err)
    
    #########################################################################
    @abstractmethod
    def Z(self, p:float, T:float) -> float:
        """
        Compression factor [-]
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.Z, err)
    
    #########################################################################
    @abstractmethod
    def cpMcv(self, p:float, T:float) -> float:
        """
        Difference cp - cv.
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.cpMcv, err)
            
    #########################################################################
    @abstractmethod
    def dcpdT(self, p, T):
        """
        dcp/dT [J/kg/K^2]
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.dcpdT, err)
    
    #########################################################################
    @abstractmethod
    def dpdT(self, p, T):
        """
        dp/dT [Pa/K]
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.dpdT, err)
    
    #########################################################################
    @abstractmethod
    def dTdp(self, p, T):
        """
        dT/dp [K/Pa]
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.dTdp, err)
    
    #########################################################################
    @abstractmethod
    def drhodp(self, p, T):
        """
        drho/dp [kg/(m^3 Pa)]
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.drhodp, err)
    
    #########################################################################
    @abstractmethod
    def dpdrho(self, p, T):
        """
        dp/drho [Pa * m^3 / kg]
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.dpdrho, err)
    
    #########################################################################
    @abstractmethod
    def drhodT(self, p, T):
        """
        drho/dT [kg/(m^3 K)]
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.drhodT, err)
    
    #########################################################################
    @abstractmethod
    def dTdrho(self, p, T):
        """
        dT/drho [K * m^3 / kg]
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.drhodT, err)

#############################################################################
#Generate selection table
EquationOfState.createRuntimeSelectionTable()