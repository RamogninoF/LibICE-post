#####################################################################
#                               IMPORT                              #
#####################################################################

from abc import ABCMeta, abstractmethod

from src.base.Utilities import Utilities

from src.thermophysicalModels.specie.specie.Molecule import Molecule

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Laminar flame speed (base class):
class Thermo(Utilities, metaclass=ABCMeta):
    """
    Base class for computation of thermodynamic properties of chemical specie (cp, cv, ...)
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        specie: Molecule
            Chemical specie for which the thermodynamic properties are defined
    """
    #########################################################################
    
    #Name:
    typeName = "Thermo"
    
    specie = Molecule.empty()
    
    #########################################################################
    #Constructor:
    def __init__(self, specie):
        """
        specie: Molecule
            Chemical specie for which the thermodynamic properties are defined
            
        Base (virtual) class: does not support instantiation.
        """
        try:
            self.__class__.checkType(specie, Molecule, entryName="specie")
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
        stringToPrint += "Type:\t" + self.typeName + "\n"
        
        return stringToPrint

    
    ################################
    @abstractmethod
    def cp(self,T):
        """
        Returns the constant pressure heat capacity at temperature T of the 
        chemical specie.
        """
        try:
            self.__class__.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.cp, err)
    
    ################################
    @abstractmethod
    def cv(self,T):
        """
        Returns the constant volume heat capacity at temperature T of the 
        chemical specie.
        """
        try:
            self.__class__.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.cp, err)
    
    ################################
    @abstractmethod
    def gamma(self,T):
        """
        Returns the ratio cp/cv at temperature T of the chemical specie.
        """
        try:
            self.__class__.checkType(T, float, "T")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.cp, err)
