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
from typing import Iterable
import numpy as np

from libICEpost.src.base.Utilities import Utilities
from dataclasses import dataclass

from .Atom import Atom

import libICEpost.Database.chemistry.constants
from libICEpost.Database import database

constants = database.chemistry.constants

from functools import lru_cache
from libICEpost.GLOBALS import __CACHE_SIZE__

#############################################################################
#                               FUNCTIONS                                   #
#############################################################################

#Allow caching of molecular mass:
@lru_cache(maxsize=__CACHE_SIZE__)
def molecularMass(molecule:Molecule) -> float:
    """
    Compute the molecular mass of a molecule.
    """
    return sum([a.atom.mass * a.n for a in molecule])

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
@dataclass
class MoleculeItem:
    """
    Dataclass used as return value by Molecule.__getitem__ method
    """
    atom:Atom
    """The atomic specie."""
    n:float
    """The number of atoms of the atomic specie."""

#Chemical specie:
class Molecule(Utilities):
    
    #########################################################################
    """
    Class containing information of a chemical specie.

    Attributes:
        name (str): Name of the chemical specie.
        atoms (list[Atom]): Atomic composition of the chemical specie.
        numberOfAtoms (list[float]): Number of atoms of each specie.
    """
    
    name:str
    """The name of the chemical specie."""
    
    _atoms:list[Atom]
    """The atomic composition of the chemical specie."""
    
    _numberOfAtoms:list[float]
    """The number of atoms of each specie."""
    
    #########################################################################
    #Properties:
    @property
    def Rgas(self) -> float:
        """
        Compute the mass-specific gas constant of the molecule:
            Rgas = R / MM [J/(kg K)]
        """
        specGasConst = constants.Rgas / (self.MM * 1e-3)
        return specGasConst

    @property
    def atoms(self) -> list[Atom]:
        """
        Get the atomic composition of the chemical specie.
        """
        return self._atoms[:]

    @property
    def numberOfAtoms(self) -> list[float]:
        """
        Get the number of atoms of each specie.
        """
        return self._numberOfAtoms[:]
    
    #########################################################################
    @classmethod
    def empty(cls):
        """
        Disable empty initializer.
        """
        raise NotImplementedError("Cannot create an empty Molecule instance.")
    
    #########################################################################
    #Constructor:
    def __init__(self, specieName:str, atomicSpecie:Iterable[Atom], numberOfAtoms:Iterable[float]):
        """
        Construct giving the name of the molecule, the list of atomic specie and number of atoms for each element.
        Args:
            specieName (str): Name of the molecule
            atomicSpecie (Iterable[Atom]): List of the atomic specie in the chemical specie
            numberOfAtoms (Iterable[float]): Number of atoms for each atomic specie contained in the
                chemical specie
        """
        
        #Check arguments:
        self.checkType(specieName, str, entryName="specieName")
        self.checkArray(atomicSpecie, Atom, "atomicSpecie")
        self.checkArray(numberOfAtoms, float, "numberOfAtoms")
        
        if not(len(atomicSpecie) == len(numberOfAtoms)):
            raise ValueError("Lists 'atomicSpecie' and 'numberOfAtoms' are not consistent.")
        
        if len(atomicSpecie) == 0:
            raise ValueError("Cannot create a Molecule instance without atomic species.")
        
        #Initialization:
        self.name = specieName
        self._atoms = []
        self._numberOfAtoms = []
        
        #Fill atoms:
        for ii, atom in enumerate(atomicSpecie):
            if not atom.name in self:
                self._atoms.append(atom.copy())
                self._numberOfAtoms.append(numberOfAtoms[ii])
            else:
                index = self.index(atom)
                self._numberOfAtoms[index] += numberOfAtoms[ii]
    
    #########################################################################
    #Operators:
    
    ##############################
    #Equality:
    def __eq__(self, otherSpecie:Molecule):
        """Determine if two chemical species are equal.

        Two chemical species are considered equal if they have the same name,
        the same atomic species (with the same names), and the same thermodynamic
        properties.

        Args:
            otherSpecie (Molecule): The other chemical species to compare against.

        Returns:
            bool: True if the chemical species are equal, False otherwise.

        Raises:
            ValueError: If the otherSpecie is not an instance of the same class.
        """
        if isinstance(otherSpecie, self.__class__):
            if (self.name != otherSpecie.name) or not(self.atoms == otherSpecie.atoms):
                return False
            else:
                return True
        else:
            raise ValueError("Cannot to compare elements of type '{}' and '{}'.".format(otherSpecie.__class__.__name__, self.__class__.__name__))
    
    ##############################
    #Hashing:
    def __hash__(self):
        """
        Hashing of the representation.
        """
        return hash(tuple((a,n) for a,n in zip(self.atoms, self.numberOfAtoms)))
    
    ##############################
    #Disequality:
    def __ne__(self,other:Molecule):
        """Check if two Molecule objects are not equal.

        This method negates the result of the __eq__ method to determine
        if two Molecule objects are not equal.

        Args:
            other (Molecule): The other Molecule object to compare with.

        Returns:
            bool: True if the Molecule objects are not equal, False otherwise.
        """
        return not(self.__eq__(other))
    
    ##############################
    #Lower then:
    def __lt__(self,otherSpecie:Molecule):
        """
        Compare the molecular mass (MM) of this specie with another specie.
        
        Args:
            otherSpecie (Molecule): The other Molecule instance to compare with.
        
        Returns:
            bool: True if this Molecule's molecular mass (MM) is less than the otherSpecie's molecular weight, False otherwise.
        
        Raises:
            ValueError: If the otherSpecie is not an instance of the same class.
        """
        if isinstance(otherSpecie, Molecule):
            return self.MM < otherSpecie.MM
        else:
            raise ValueError("Cannot to compare elements of type '{}' and '{}'.".format(otherSpecie.__class__.__name__, self.__class__.__name__))
    
    ##############################
    #Higher then:
    def __gt__(self,otherSpecie):
        """
        Compare the molecular mass (MM) of this specie with another specie.

        Args:
            otherSpecie (Molecule): The other specie to compare with.

        Returns:
            bool: True if the molecular mass (MM) of this specie is greater than the molecular mass of the other specie, False otherwise.

        Raises:
            ValueError: If the otherSpecie is not an instance of the same class.
        """

        if isinstance(otherSpecie, Molecule):
            return self.MM > otherSpecie.MM
        else:
            raise ValueError("Cannot to compare elements of type '{}' and '{}'.".format(otherSpecie.__class__.__name__, self.__class__.__name__))
    
    ##############################
    #Higher/equal then:
    def __ge__(self,otherSpecie):
        """
        Check if this specie is greater than or equal to another specie (by molecular mass).
        
        Args:
            otherSpecie (Molecule): The other specie to compare against.
            
        Returns:
            bool: True if this specie is greater than or equal to the other specie, False otherwise.
        """
        
        return ((self == otherSpecie) or (self > otherSpecie))
    

    ##############################
    #Lower/equal then:
    def __le__(self,otherSpecie:Molecule):
        """
        Check if this Molecule instance is less than or equal to another Molecule instance (by molecular mass).
        Args:
            otherSpecie (Molecule): The other Molecule instance to compare with.
        Returns:
            bool: True if this Molecule instance is less than or equal to the other Molecule instance, False otherwise.
        """
        
        
        return ((self == otherSpecie) or (self < otherSpecie))
    
    ##############################
    #Sum:
    def __add__(self,otherSpecie:Molecule|Atom) -> Molecule:
        """
        Adding a Molecule or Atom to the current Molecule.
        The resulting Molecule will have the combined atoms of both 
        the original and the added Molecule or Atom. The name is 
        set with the brute formula.
        
        Args:
            otherSpecie (Molecule | Atom): The Molecule or Atom to be added to the 
            current Molecule.
            
        Returns:
            Molecule: The new Molecule instance with the added atoms.
            
        Raises:
            ValueError: If an atomic specie with the same name but different 
            properties is already present in the Molecule.
        """
        #Argument checking:
        self.checkType(otherSpecie, [Molecule, Atom], entryName="otherSpecie")
        
        if isinstance(otherSpecie, Atom):
            otherSpecie = Molecule(otherSpecie.name, [otherSpecie], [1])
        
        atoms = self.atoms
        numberOfAtoms = self.numberOfAtoms
        #Add atoms of second specie
        for atom in otherSpecie:
            #Check if already present
            if atom.atom.name in self:
                #Check if with different properties:
                if not(atom.atom in self):
                    raise ValueError("Atomic specie named '{}' already present in molecule with different properties, cannot add atomic specie to molecule.".format(atom.atom.name))
                #Add number of atoms of second specie
                indexSelf = self.index(atom.atom)
                numberOfAtoms[indexSelf] += atom.n
            else:
                #Add new atomic specie
                atoms.append(atom.atom.copy())
                numberOfAtoms.append(atom.n)
        
        #Create the Molecule instance
        mol = Molecule("", atoms, numberOfAtoms)
        
        #Set the name of the Molecule to brute formula
        mol.name = mol.bruteFormula()
        
        #Return the Molecule
        return mol
    
    ##############################
    #Print function:
    def __str__(self):
        StrToPrint = ("Chemical specie: " + self.name + "\n")
        
        template = "| {:15s}| {:15s}   {:15s}|\n"
        title = template.format("Atom", "m [g/mol]", "# atoms [-]")
        
        hLine = lambda a: (("-"*(len(a)-1)) + "\n")
        
        StrToPrint += hLine(title)
        StrToPrint += title
        StrToPrint += hLine(title)
        
        for atom in self:
            StrToPrint += template.format(atom.atom.name, str(atom.atom.mass), str(atom.n))
        
        StrToPrint += hLine(title)
        StrToPrint += template.format("tot.", str(self.MM), "")
        
        StrToPrint += hLine(title)
        
        StrToPrint += "\n"
        
        return StrToPrint
    
    ##############################
    #Representation:
    def __repr__(self):
        R = \
            {
                "name": self.name,
                "mass": self.MM,
                "bruteFormula": self.bruteFormula()
            }
        
        return R.__repr__()
    
    ###############################
    def __contains__(self, entry:str|Atom):
        """Checks if an Atom or a string representing an Atom's name is part of the Molecule.
        
        Args:
            entry (str | Atom): The Atom or the name of the Atom to check for membership in the Molecule.
        
        Returns:
            bool: True if the Atom or the Atom's name is part of the Molecule, False otherwise.
        
        Raises:
            TypeError: If the entry is not of type str or Atom.
        """
        #Argument checking:
        self.checkType(entry, [str, Atom], "entry")
        
        if isinstance(entry, Atom):
            return (entry in self.atoms)
        else:
            return (entry in [s.name for s in self.atoms])
    
    ###############################
    def __index__(self, entry:Atom):
        """
        Return the index position of the Atom in the Molecule.
        
        Parameters:
            entry (Atom|str): The Atom object or its name index position is to be found in the Molecule.
        
        Returns:
            int: The index position of the Atom in the Molecule.
        
        Raises:
            ValueError: If the Atom is not found in the Molecule.
        """
        #Argument checking:
        self.checkType(entry, (Atom, str), "entry")
        if not entry in self:
            raise ValueError("Atom {} not found in molecule".format(entry.name if isinstance(entry, Atom) else entry))
        
        if isinstance(entry, str):
            return [a.name for a in self.atoms].index(entry)
        else:
            return self.atoms.index(entry)
    
    ###############################
    #Alias:
    index = __index__
    
    ###############################
    def __len__(self) -> int:
        """
        Return the number of atomic species in the molecule.
        Returns:
            int: The number of atoms in the molecule.
        """
        return len(self.atoms)
    
    ###############################
    #Access:
    def __getitem__(self, atom:str|Atom|int) -> MoleculeItem:
        """
        Retrieve data relative to an Atom in the Molecule.
        Parameters:
            atom (str | Atom | int): The atom to retrieve data for.
                - If str: Checks for an atom matching the name.
                - If Atom: Checks for the atomic species.
                - If int: Checks for the entry following the order.
        Returns:
            MoleculeItem: The data associated with the specified atom.
        Raises:
            ValueError: If the atom is not found in the molecule
            IndexError: If the index is out of range.
        """
        #Argument checking:
        self.checkType(atom, [str, Atom, int], entryName="atom")
        
        #If str, check for atom name:
        if isinstance(atom, str):
            if not atom in [a.name for a in self.atoms]:
                raise ValueError("Atom {} not found in molecule".format(atom))
            index = [a.name for a in self.atoms].index(atom)
        
        #If Atom, check for atom:
        elif isinstance(atom, Atom):
            if not atom in self:
                raise ValueError("Atom {} not found in molecule".format(atom.name))
            index = self.index(atom)
        
        #If int, check for index:
        elif isinstance(atom, int):
            if atom < 0 or atom >= len(self):
                raise IndexError("Index {} out of range".format(atom))
            index = atom
                
        data = MoleculeItem(self.atoms[index], self.numberOfAtoms[index])
        
        return data
    
    ###############################
    #Iteration:
    def __iter__(self):
        """
        Returns an iterator that yields MoleculeItem instances for each atom and its corresponding count in the molecule.
        Yields:
            MoleculeItem: An instance containing an atom and its count.
        """
        return (MoleculeItem(a, n) for a, n in zip(self.atoms, self.numberOfAtoms))
    
    #########################################################################
    #Molecular mass:
    @property
    def MM(self) -> float:
        """
        Compute the molecular mass of the chemical specie [g/mol].
        """
        return molecularMass(self)
    
    ##############################
    #Compute the brute formula of the chemical specie:
    def bruteFormula(self) -> str:
        """
        Returns the brute formula of the specie.
        """
        BF = ""
        
        for atom in self:
            if (atom.n == 1):
                BF += atom.atom.name
            elif atom.n == int(atom.n):
                BF += atom.atom.name + str(int(atom.n))
            else:
                BF += atom.atom.name + "{:.3f}".format(atom.n)
        
        return BF
    
    ###############################
    def atomicCompositionMatrix(self):
        """
        Return a 1xN numpy.ndarray with the atomic composition 
        matrix of the molecule, where N is the number of atoms 
        in the molecule. Each element of the matrix is the number 
        of atoms of the atomic specie in the mixture, sorted 
        according to their order in 'atoms' array.

        Returns:
            numpy.ndarray: A 1xN array representing the atomic composition matrix.
        """
        return np.array([a.n for a in self])

#############################################################################
#Load database
import libICEpost.Database.chemistry.specie.Molecules