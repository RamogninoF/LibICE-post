#####################################################################
#                               IMPORT                              #
#####################################################################

from src.base.Utilities import Utilities

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Atomic specie:
class Atom(Utilities):
    """
    Class handling an atomic specie.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        name:   str
            Name of the atomic specie
            
        mass:   float
            Atomic mass
    
    """
    
    name = ""
    mass = float("nan")
    
    #############################################################################
    #Constructor:
    def __init__(self, name, mass):
        """
        name:   str
                Name of the atomic specie
        mass:   float
            Atomic mass
        """
        #Check arguments:
        try:
            Utilities.checkType(name, str, entryName="name")
            Utilities.checkType(mass, float, entryName="mass")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        self.name = name
        self.mass = mass
        
    #############################################################################
    #Operators:
    
    ##############################
    #Equality:
    def __eq__(self, otherSpecie):
        """
        Two species are equal if have the same value for all attributes.
        """
        if isinstance(otherSpecie, self.__class__):
            for field in otherSpecie.__dict__:
                if self.__dict__[field] != otherSpecie.__dict__[field]:
                    return False
            return True
        else:
            warning("Trying to compare elements of type '{}' and '{}'.".format(otherSpecie.__class__.__name__, self.__class__.__name__))
            return False
    
    ##############################
    #Disequality:
    def __ne__(self,other):
        """
        Negation of __eq__ operator
        """
        return not(self.__eq__(other))
    
    ##############################
    #Sum:
    def __add__(self, otherSpecie):
        """
        Possible additions:
            atomSpecie + atomSpecie = chemSpecie
            atomSpecie + chemSpecie = chemSpecie
        """
        from src.thermophysicalModels.specie.specie.Molecule import Molecule
        
        #Argument checking:
        try:
            Utilities.checkTypes(otherSpecie, [self.__class__, Molecule], entryName="otherSpecie")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__add__, err)
        
        if isinstance(otherSpecie, self.__class__):
            atomicSpecie = [self.copy()]
            numberOfAtoms = [1]
                
            if (self == otherSpecie):
                numberOfAtoms[0] += 1
                
            elif (self.name == otherSpecie.name):
                raise TypeError("Cannot add two atomic specie with same name but different properties.")
            
            else:
                atomicSpecie.append(otherSpecie)
                numberOfAtoms.append(1)
            
            #Create specie from atoms and initialize name from brute formula
            returnSpecie = Molecule("", atomicSpecie, numberOfAtoms)
            returnSpecie.name = returnSpecie.bruteFormula()
        
        else:
            returnSpecie = otherSpecie + self
        
        return returnSpecie
