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
            self.__class__.runtimeWarning("Trying to compare elements of type '{}' and '{}'.".format(otherSpecie.__class__.__name__, self.__class__.__name__))
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
            Atom + Atom = Molecule
            atomSpecie + Molecule = Molecule
        """
        from .Molecule import Molecule
        
        #Argument checking:
        try:
            Utilities.checkTypes(otherSpecie, [self.__class__, Molecule], entryName="otherSpecie")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__add__, err)
        
        try:
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
            
        except BaseException as err:
            self.fatalErrorIn(self.__add__, "Failed addition '{} + {}'".format(self.__class__.__name__, otherSpecie.__class__.__name__), err)
        
        return returnSpecie
    
    ##############################
    #Multiplication:
    def __mul__(self, num):
        """
        Possible additions:
            Atom * float/int = Molecule
        """
        from .Molecule import Molecule
        
        #Argument checking:
        try:
            Utilities.checkType(num, float, entryName="num")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__mul__, err)
        
        try:
            returnSpecie = Molecule("",[self.copy()], [num])
            returnSpecie.name = returnSpecie.bruteFormula()
            
        except BaseException as err:
            self.fatalErrorIn(self.__mul__, "Failed multiplication '{}*{}'".format(self.__class__.__name__, num.__class__.__name__), err)
        
        return returnSpecie
    
    ##############################
    #Multiplication:
    def __rmul__(self, num):
        """
        Possible additions:
            Atom * float/int = Molecule
        """
        return self*num
