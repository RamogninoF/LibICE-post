#####################################################################
#                               IMPORT                              #
#####################################################################

from src.base.Utilities import Utilities

from src.thermophysicalModels.specie.specie.Molecule import Molecule

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Laminar flame speed (base class):
class Thermo(Utilities):
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
            
        Raising a 'NotImplementedError' if attempting to construct an object of
        this class. Used only as base class (overwritten from derived classes).
        """
        try:
            if (self.__class__ == Thermo):
                raise NotImplementedError("Trying to construct base (virtual) class.")
            
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
