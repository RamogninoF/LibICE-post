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

from libICEpost.src.base.Utilities import Utilities
from dataclasses import dataclass

from .Atom import Atom

import libICEpost.Database.chemistry.constants
from libICEpost.Database import database

constants = database.chemistry.constants

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
@dataclass
class MoleculeItem:
    """
    Dataclass used as return value by Molecule.__getitem__ method
    """
    atom:Atom
    n:float

#Chemical specie:
class Molecule(Utilities):
    
    #########################################################################
    """
    Class containing information of a chemical specie.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        name:           str
            Name of the chemical specie
            
        atoms:          list<Atom>
            Atomic composition of the chemical specie
        numberOfAtoms:  list<float>
            Number of atoms of each specie
        
    """
    
    name:str
    atoms:list[Atom]
    numberOfAtoms:list[float]
    

    #Compute Rgas:
    @property
    def Rgas(self):
        """
        Compute the mass-specific gas constant of the molecule:
            Rgas = R / MM
        """
        specGasConst = constants.Rgas / self.MM
        return specGasConst

    #########################################################################
    @classmethod
    def empty(cls):
        """
        Overload empty initializer.
        """
        item = super().empty()
        item.atoms = []
        item.numberOfAtoms = []
        return item
    
    #########################################################################
    @classmethod
    def fromDictionary(cls, dictionary):
        """
        Construct from dictionary:
        {
            name:           str
                Name of the chemical specie
            atoms:          list<Atom>
                Atomic composition of the chemical specie
            numberOfAtoms:  list<float>
                Number of atoms of each specie
        }
        """
        try:
            cls.checkType(dictionary, dict, "dictionary")
            
            entryList = ["name", "atoms", "numberOfAtoms"]
            for entry in entryList:
                if not entry in dictionary:
                    raise ValueError(f"Mandatory entry '{entry}' not found in dictionary.")
            
            out = cls\
                (
                    dictionary["name"], 
                    dictionary["atoms"], 
                    dictionary["numberOfAtoms"]
                )
            return out
            
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed construction from dictionary", err)
    
    #########################################################################
    #Constructor:
    def __init__(self, specieName, atomicSpecie, numberOfAtoms):
        """
        atomicSpecie:   list<Atom>
            List of the atomic specie in the chemical specie
        numberOfAtoms:  list<float>
            Number of atoms for each atomic specie contained in the
            chemical specie
        """
        
        #Check arguments:
        try:
            self.checkType(specieName, str, entryName="specieName")
            self.checkInstanceTemplate(atomicSpecie, [Atom.empty()], entryName="atomicSpecie")
            self.checkInstanceTemplate(numberOfAtoms, [1.], entryName="numberOfAtoms")
            
            if not(len(atomicSpecie) == len(numberOfAtoms)):
                raise ValueError("Lists 'atomicSpecie' and 'numberOfAtoms' are not consistent.")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        #Initialization:
        self.name = specieName
        self.atoms = []
        self.numberOfAtoms = []
        
        #Fill atoms:
        for ii, atom in enumerate(atomicSpecie):
            if not atom.name in self:
                self.atoms.append(atom.copy())
                self.numberOfAtoms.append(numberOfAtoms[ii])
            else:
                index = self.index(atom)
                self.numberOfAtoms[index] += numberOfAtoms[ii]
    
    #########################################################################
    #Operators:
    
    ##############################
    #Equality:
    def __eq__(self, otherSpecie):
        """
        Two chemical specie are equal if they have same name, 
        the same atomic specie (with same names), and the same 
        thermodynamic properties.
        """
        if isinstance(otherSpecie, self.__class__):
            if (self.name != otherSpecie.name) or not(self.atoms == otherSpecie.atoms):
                return False
            else:
                return True
        else:
            raise ValueError("Cannot to compare elements of type '{}' and '{}'.".format(otherSpecie.__class__.__name__, self.__class__.__name__))
    
    ##############################
    #Disequality:
    def __ne__(self,other):
        """
        Negation of __eq__ operator
        """
        return not(self.__eq__(other))
    
    ##############################
    #Lower then:
    def __lt__(self,otherSpecie):
        """
        Ordering by molecular weight
        """
        if isinstance(otherSpecie, self.__class__):
            return self.MM < otherSpecie.MM
        else:
            raise ValueError("Cannot to compare elements of type '{}' and '{}'.".format(otherSpecie.__class__.__name__, self.__class__.__name__))
    
    ##############################
    #Higher then:
    def __gt__(self,otherSpecie):
        """
        Ordering by molecular weight
        """
        if isinstance(otherSpecie, self.__class__):
            return self.MM > otherSpecie.MM
        else:
            raise ValueError("Cannot to compare elements of type '{}' and '{}'.".format(otherSpecie.__class__.__name__, self.__class__.__name__))
    
    ##############################
    #Higher/equal then:
    def __ge__(self,otherSpecie):
        """
        Ordering by molecular weight
        """
        return ((self == otherSpecie) or (self > otherSpecie))
    

    ##############################
    #Lower/equal then:
    def __le__(self,otherSpecie):
        """
        Ordering by molecular weight
        """
        return ((self == otherSpecie) or (self < otherSpecie))
    
    ##############################
    #Sum:
    def __iadd__(self,otherSpecie):
        """
        In place addition. Possible additions:
            Molecule + Molecule = Molecule
            Molecule + Atom = Molecule
        """
        #Argument checking:
        try:
            Utilities.checkTypes(otherSpecie, [self.__class__, Atom], entryName="otherSpecie")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__add__, err)
        
        if isinstance(otherSpecie, Atom):
            otherSpecie = Molecule(otherSpecie.name, [otherSpecie], [1])
        
        try:
            #Add atoms of second specie
            for atom in otherSpecie:
                #Check if already present
                if atom.atom.name in self:
                    #Check if with different properties:
                    if not(atom.atom in self):
                        raise ValueError("Atomic specie named '{}' already present in molecule with different properties, cannot add atomic specie to molecule.".format(atom.atom.name))
                    #Add number of atoms of second specie
                    indexSelf = self.index(atom.atom)
                    self.numberOfAtoms[indexSelf] += atom.n
                else:
                    #Add new atomic specie
                    self.atoms.append(atom.atom.copy())
                    self.numberOfAtoms.append(atom.n)
            
            #Set name from brute formula
            self.name = self.bruteFormula()
        
        except BaseException as err:
            self.fatalErrorInClass(self.__iadd__, "Failed addition '{} += {}'".format(self.__class__.__name__, otherSpecie.__class__.__name__), err)
        
        return self
    
    ##############################
    #Sum:
    def __add__(self,otherSpecie):
        """
        Possible additions:
            Molecule + Molecule = Molecule
            Molecule + Atom = Molecule
        """
        try:
            newSpecie = self.copy()
            newSpecie += otherSpecie
        except BaseException as err:
            self.fatalErrorInClass(self.__add__, "Failed addition '{} + {}'".format(self.__class__.__name__, otherSpecie.__class__.__name__), err)
        return newSpecie
    
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
                "atoms": self.atoms,
                "numbers":self.numberOfAtoms
            }
        
        return R.__repr__()
    
    ###############################
    def __contains__(self, entry):
        """
        Checks if a Atom is part of the Molecule.
        """
        #Argument checking:
        try:
            self.checkTypes(entry, [str, Atom], "entry")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__contains__, err)
        
        if isinstance(entry, Atom):
            return (entry in self.atoms)
        else:
            return (entry in [s.name for s in self.atoms])
    
    ###############################
    def __index__(self, entry):
        """
        Return the idex position of the Atom in the Molecule.
        """
        #Argument checking:
        try:
            self.checkType(entry, Atom, "entry")
            if not entry in self:
                raise ValueError("Atom {} not found in molecule".format(entry.name))
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__index__, err)
        
        return self.atoms.index(entry)
    
    ###############################
    def index(self, entry):
        """
        Return the idex position of the Atom in the Molecule.
        """
        return self.__index__(entry)
    
    ###############################
    def __len__(self):
        """
        Return the number of Atomic specie in the molecule.
        """
        return len(self.atoms)
    
    ###############################
    #Access:
    def __getitem__(self, atom):
        """
        atom:     str / Atom / int
        
        Get the data relative to Atom in the Molecule
            -> If str: checking for atom matching the name
            -> If Atom: checking for atomic specie
            -> If int:  checing for entry following the order
        
        Return: MoleculeItem
        """
        #Argument checking:
        try:
            self.checkTypes(atom, [str, Atom, int], entryName="atom")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__getitem__, err)
        
        try:
            if isinstance(atom, str):
                if not atom in [a.name for a in self.atoms]:
                    raise ValueError("Atom {} not found in molecule".format(atom))
                index = [a.name for a in self.atoms].index(atom)
            
            elif isinstance(atom, Atom):
                if not atom in self:
                    raise ValueError("Atom {} not found in molecule".format(atom.name))
                index = self.index(atom)
            
            elif isinstance(atom, int):
                if atom < 0 or atom >= len(self):
                    raise ValueError("Index {} out of range".format(atom))
                index = atom
        except BaseException as err:
            self.fatalErrorInClass(self.__getitem__, "failure retrieving atom in molecule", err)
        
        data = MoleculeItem(self.atoms[index].copy(), self.numberOfAtoms[index])
            # {
            #     "atom":self.atoms[index].copy(),
            #     "numberOfAtoms":self.numberOfAtoms[index]
            # }
        
        return data
    
    ###############################
    #Iteration:
    def __iter__(self):
        """
        Iteration over the atoms in the molecule.
        """
        return MoleculeIter(self)
    
    #########################################################################
    #Molecular mass:
    @property
    def MM(self):
        """
        Compute the molecular mass of the chemical specie.
        """
        MM = 0.0
        for atom in self:
            MM += atom.atom.mass * atom.n
        return MM
    
    ##############################
    #Compute the brute formula of the chemical specie:
    def bruteFormula(self):
        """
        Returns the brute formula of the specie
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
    
    ##############################
    #List of atomic specie:
    def atomList(self):
        """
        Returns a list<Atom> containing a list of the atomic specie
        contained in the chemical specie.
        """
        atomList = []
        for atom in self.atoms:
            atomList.append(atom.copy())
        
        return atomList
    
    ###############################
    def atomicCompositionMatrix(self):
        """
        Return a 1xN numpy.ndarray with the atomic composition 
        matrix of the molecule, where N is the number of atoms 
        in the molecule. Each element of the matrix is the number 
        of atoms of the atomic specie in the mixture, sorted 
        according to their order in 'atoms' array.
        """
        return self.__class__.np.array([a.n for a in self])
    
    def setName(self, value):
        """
        Set the name of the specie.
        """
        self.name = str(value)
        return self
    
#############################################################################
#                               FRIEND CLASSES                              #
#############################################################################
#Iterator:
class MoleculeIter:
    """
    Iterator for Molecule class.
    """
    def __init__(self, molecule:Molecule):
        self.molecule = molecule
        self.atoms = [a.name for a in molecule.atoms]
        
        self.current_index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current_index < len(self.atoms):
            out = self.molecule[self.atoms[self.current_index]]
            self.current_index += 1
            return out
        else:
            raise StopIteration

#############################################################################
#Load database
import libICEpost.Database.chemistry.specie.Molecules