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
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        Rgas: float
            The mass specific gas constant
    """
    
    #########################################################################
    #Constructor:
    def __init__(self, Rgas:float):
        try:
            self.checkType(Rgas, float, "Rgas")
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, "Argument checking failed", err)
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
    
    ##############################
    #Representation:
    def __repr__(self):
        R = \
            {
                "type": self.TypeName,
                "Rgas": self.Rgas
            }
        return R.__repr__()

     #########################################################################
    @abstractmethod
    def cp(self, p, T):
        """
        Constant pressure heat capacity [J/kg/K]
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.cp, err)
            
    ################################
    @abstractmethod
    def hf(self):
        """
        Enthalpy of formation [J/kg]
        """
        pass
    
    ################################
    @abstractmethod
    def ha(self, p, T):
        """
        Absolute enthalpy [J/kg]
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.ha, err)
    
    ################################
    def hs(self, p, T):
        """
        Sensible enthalpy [J/kg]
        
        hs = ha - hf
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.hs, err)
        
        return self.ha(p,T) - self.hf()
    
    ################################
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
        
#############################################################################
Thermo.createRuntimeSelectionTable()
