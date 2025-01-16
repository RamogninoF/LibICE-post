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

from __future__ import annotations

from libICEpost.src.base.Utilities import Utilities
from libICEpost.src.base.Functions.runtimeWarning import runtimeWarning

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Atomic specie:
class Atom(Utilities):
    """
    Class handling an atomic specie.

    Attributes:
        name (str): Name of the atomic specie.
        mass (float): Atomic mass.
    """
    
    _name:str
    """The name of the atomic specie."""
    
    _mass:float
    """The atomic mass of the atomic specie [g/mol]."""
    
    
    #############################################################################
    #Properties:
    @property
    def name(self) -> str:
        """
        Get the name of the atomic specie.

        Returns:
            str: The name of the atomic specie.
        """
        return self._name

    @property
    def mass(self) -> float:
        """
        Get the atomic mass [g/mol].

        Returns:
            float: The atomic mass [g/mol].
        """
        return self._mass
    
    #############################################################################
    #Constructor:
    def __init__(self, name, mass):
        """
        Initialize an Atom instance.
        
        Args:
            name (str): Name of the element.
            mass (float): Atomic mass.
        """
        #Check arguments:
        Utilities.checkType(name, str, entryName="name")
        Utilities.checkType(mass, float, entryName="mass")
        
        self._name = name
        self._mass = mass
        
    #############################################################################
    #Operators:
    
    ##############################
    #Equality:
    def __eq__(self, otherSpecie):
        """
        Determine if two species are equal by comparing all their attributes.

        Args:
            otherSpecie (Atom): The other species to compare with.

        Returns:
            bool: True if all attributes of both species are equal, False otherwise.

        Raises:
            TypeError: If the other object is not of the same class.
        """
        if isinstance(otherSpecie, self.__class__):
            for field in set(self.__dict__.keys()).union(otherSpecie.__dict__.keys()):  # Union of the keys of the two dictionaries
                if self.__dict__.get(field) != otherSpecie.__dict__.get(field):
                    return False
            return True
        else:
            raise TypeError("Cannot compare elements of type '{}' and '{}'.".format(otherSpecie.__class__.__name__, self.__class__.__name__))
            return False
    
    ##############################
    #Hashing:
    def __hash__(self):
        """
        Hashing of the representation.
        """
        return hash(self.__repr__()) 
    
    ##############################
    #Disequality:
    def __ne__(self,otherSpecie:Atom):
        """
        Determine if two Atom objects are not equal.

        Args:
            otherSpecie (Atom): The other Atom object to compare against.

        Returns:
            bool: True if the Atom objects are not equal, False otherwise.
        """
        return not(self.__eq__(otherSpecie))
    
    ##############################
    #Lower then:
    def __lt__(self,otherSpecie):
        """
        Compare if the molecular weight of this Atom is lower than another Atom.

        Parameters:
            otherSpecie (Atom): The other Atom to compare with.

        Returns:
            bool: True if the molecular weight of this Atom is lower than the molecular weight of the other Atom, False otherwise.
        """
        
        if isinstance(otherSpecie, self.__class__):
            return self.mass < otherSpecie.mass
        else:
            raise ValueError("Cannot compare elements of type '{}' and '{}'.".format(otherSpecie.__class__.__name__, self.__class__.__name__))
    
    ##############################
    #Higher then:
    def __gt__(self,otherSpecie:Atom):
        """
        Compare if the molecular weight of this Atom is greater than another Atom.

        Parameters:
            otherSpecie (Atom): The other Atom to compare with.

        Returns:
            bool: True if the molecular weight of this Atom is greater than the molecular weight of the other Atom, False otherwise.
        """

        if isinstance(otherSpecie, self.__class__):
            return self.mass > otherSpecie.mass
        else:
            raise ValueError("Cannot to compare elements of type '{}' and '{}'.".format(otherSpecie.__class__.__name__, self.__class__.__name__))
    
    ##############################
    #Higher/equal then:
    def __ge__(self,otherSpecie:Atom):
        """
        Compare if the molecular weight of this Atom is greater than or equal to another Atom.

        Parameters:
            otherSpecie (Atom): The other Atom to compare with.

        Returns:
            bool: True if the molecular weight of this Atom is greater than or equal to the molecular weight of the other Atom, False otherwise.
        """
        return ((self == otherSpecie) or (self > otherSpecie))
    

    ##############################
    #Lower/equal then:
    def __le__(self,otherSpecie):
        """
        Compare if the molecular weight of this specie is less than or equal to another specie.

        Args:
            otherSpecie (Specie): The other specie to compare with.

        Returns:
            bool: True if the molecular weight of this specie is less than or equal to the molecular weight of the other specie, False otherwise.
        """
        return ((self == otherSpecie) or (self < otherSpecie))
    
    ##############################
    #Sum:
    def __add__(self, otherSpecie:Atom|"Molecule") -> "Molecule":
        """
        Add an Atom to another Atom or a Molecule to form a new Molecule.
            Atom + Molecule = Molecule
        Args:
            otherSpecie (Atom | Molecule): The other species to add, which can be either an Atom or a Molecule.
        Returns:
            Molecule: A new Molecule formed by the addition of the current Atom and the other species.
        Raises:
            TypeError: If two atomic species with the same name but different properties are added.
        """
        from .Molecule import Molecule
        
        #Argument checking:
        Utilities.checkType(otherSpecie, [Atom, Molecule], entryName="otherSpecie")
        
        if isinstance(otherSpecie, Atom):
            atomicSpecie = [self]
            numberOfAtoms = [1]
            
            #If same specie, increase number of atoms
            if (self == otherSpecie):
                numberOfAtoms[0] += 1
            
            #Check if the two atoms have different properties
            elif (self.name == otherSpecie.name):
                raise ValueError("Cannot add two atomic specie with same name but different properties.")
            
            #Add the other specie
            else:
                atomicSpecie.append(otherSpecie)
                numberOfAtoms.append(1)
            
            #Create specie from atoms and initialize name from brute formula
            returnSpecie = Molecule("", atomicSpecie, numberOfAtoms)
            returnSpecie.name = returnSpecie.bruteFormula()
            
        else:
            #Use the Molecule class to handle the addition
            returnSpecie = otherSpecie + self
        
        return returnSpecie
    
    ##############################
    #Multiplication:
    def __mul__(self, num) -> "Molecule":
        """
        Multiplies the current Atom instance by a given number to create a Molecule.
        Args:
            num (float): The number to multiply the Atom instance by.
        Returns:
            Molecule: A new Molecule instance created by multiplying the Atom instance by the given number.
        """
        
        from .Molecule import Molecule
        
        #Argument checking:
        Utilities.checkType(num, float, entryName="num")
        
        returnSpecie = Molecule("",[self.copy()], [num])
        returnSpecie.name = returnSpecie.bruteFormula()
        
        return returnSpecie
    
    ##############################
    #Multiplication:
    def __rmul__(self, num:float|int) -> "Molecule":
        """
        Implements the reflected multiplication operation for the Atom class.
        This method allows the Atom instance to be multiplied by a number using the
        reverse multiplication operator (num * Atom).
        Args:
            num (int or float): The number to multiply with the Atom instance.
        Returns:
            Molecule: A Molecule instance resulting from the multiplication.
        """
        return self*num
    
    ##############################
    #Representation:
    def __repr__(self):
        R = \
            {
                "name": self.name,
                "mass": self.mass,
            }
        
        return R.__repr__()

#############################################################################
#Load database
import libICEpost.Database.chemistry.specie.periodicTable