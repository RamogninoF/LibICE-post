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

from ...specie.Molecule import Molecule

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class EquationOfState(BaseClass):
    """
    Class handling thermodynamic equation of state of a chemical specie
    
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
            
        Base (virtual) class: does not support instantiation.
        """
        try:
            self.checkType(chem, Molecule, entryName="chem")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__,err)
        
        self.chem = chem.copy()
    #########################################################################
    #Operators:
    
    ################################
    #Print:
    def __str__(self):
        stringToPrint = ""
        stringToPrint += f"Equation of state for {chem.__class__.__name__}:\t{chem.name}\n"
        stringToPrint += "Type:\t" + self.TypeName + "\n"
        
        return stringToPrint
    
    ##############################
    #Representation:
    def __repr__(self):
        R = \
            {
                "type": self.TypeName,
                "chem": self.chem
            }
                       
        return R.__repr__()

     #########################################################################
    @abstractmethod
    def cp(self, p, T):
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
    def cv(self, p, T):
        """
        Constant volume heat capacity contribution [J/kg/K]
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.cv, err)
    
    #########################################################################
    @abstractmethod
    def h(self, p, T):
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
    def rho(self, p, T):
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
    def T(self, p, rho):
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
    def p(self, T, rho):
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
    def Z(self, p, T):
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
EquationOfState.createRuntimeSelectionTable()
