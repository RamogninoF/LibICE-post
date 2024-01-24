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

from src.base.BaseClass import BaseClass

from src.thermophysicalModels.specie.specie.Molecule import Molecule

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class Thermo(BaseClass):
    """
    Base class for computation of thermodynamic properties of chemical specie (cp, cv, ...)
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        specie: Molecule
            Chemical specie for which the thermodynamic properties are defined
    """
    
    #########################################################################
    #Constructor:
    def __init__(self, specie):
        """
        specie: Molecule
            Chemical specie for which the thermodynamic properties are defined
            
        Base (virtual) class: does not support instantiation.
        """
        try:
            self.checkType(specie, Molecule, entryName="specie")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__,err)
        
        self.specie = specie.copy()
    
    #########################################################################
    #Operators:
    
    ################################
    #Print:
    def __str__(self):
        stringToPrint = ""
        stringToPrint += "Thermodynamic data associated to molecule:\t" + self.specie.name + "\n"
        stringToPrint += "Type:\t" + self.TypeName + "\n"
        
        return stringToPrint
    
    ##############################
    #Representation:
    def __repr__(self):
        R = \
            {
                "type": self.TypeName,
                "specie": self.specie
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
    def cv(self, p, T):
        """
        Constant volume heat capacity [J/kg/K]
        """
        try:
            self.checkType(p, float, "p")
            self.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.cp, err)
    
    ################################
    @abstractmethod
    def gamma(self, p, T):
        """
        Heat capacity ratio cp/cv [-]
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
Thermo.createRuntimeSelectionTable("Thermo")
