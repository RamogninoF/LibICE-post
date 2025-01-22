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

from libICEpost.src.base.Functions.typeChecking import checkType
from libICEpost.src.base.Utilities import Utilities
from dataclasses import dataclass

from typing import Literal, Iterable, Self
from enum import Enum

import numpy as np
import math
from .Atom import Atom
from .Molecule import Molecule

from libICEpost.Database import database
from libICEpost.Database import chemistry

constants = database.chemistry.constants

#############################################################################
class _fracType(Enum):
    mass = "mass"
    mole = "mole"

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
@dataclass
class MixtureItem:
    """
    Dataclass used as return value by Mixture.__getitem__ method
    """
    specie:Molecule
    """The specie in the mixture"""
    X:float
    """The mole fraction of the specie"""
    Y:float
    """The mass fraction of the specie"""

#Mixture class:
class Mixture(Utilities):
    #########################################################################
    """
    Class handling a the mixture of a homogeneous mixture.
    
    Attributes:
        specie (Iterable[Molecule]): The specie in the mixture.
        X (Iterable[float]): The mole fractions of the specie in the mixture.
        Y (Iterable[float]): The mass fractions of the specie in the mixture.
    """
    
    _decimalPlaces = 10
    """Decimal places for rounding mass and mole fractions."""
    _X:list[float]
    """The mole fractions of the specie in the mixture."""
    _Y:list[float]
    """The mass fractions of the specie in the mixture."""
    _species:list[Molecule]
    """The species in the mixture."""
    
    #########################################################################
    @property
    def Rgas(self) -> float:
        """
        The mass-specific gas constant of the mixture [J/(kg K)].
        """
        specGasConst = constants.Rgas / (self.MM * 1e-3)
        return specGasConst

    #########################################################################
    @property
    def Y(self) -> list[float]:
        """
        The mass fractions.
        """
        return [np.round(y, Mixture._decimalPlaces) for y in self._Y]
    
    #################################
    @Y.setter
    def Y(self, y:Iterable[float]):
        self.checkArray(y, float, "y")
        if not len(y) == len(self):
            raise ValueError("Inconsistent size of y with mixture composition.")
        self._Y = list(y[:])
        self.updateMoleFracts()
        
    #################################
    @property
    def X(self) -> list[float]:
        """
        The mole fractions.
        """
        return [np.round(x, Mixture._decimalPlaces) for x in self._X]
    
    #################################
    @X.setter
    def X(self, x:Iterable[float]):
        self.checkArray(x, float, "x")
        if not len(x) == len(self):
            raise ValueError("Inconsistent size of x with mixture composition.")
        self._X = list(x[:])
        self.updateMassFracts()
    
    #################################
    @property
    def species(self) -> list[Molecule]:
        """
        The species in the mixture.
        """
        return self._species[:]
    
    #################################
    @property
    def specieNames(self) -> list[str]:
        """
        The names of the specie in the mixture.
        """
        return [s.name for s in self._species]
    
    #################################
    @property
    def specieWeights(self) -> list[float]:
        """
        The molecular weights of the chemical specie in the mixture [g/mol].
        """
        return [s.MM for s in self._species]
    
    #########################################################################
    @classmethod
    def empty(cls):
        """
        Overload empty initializer.
        """
        return cls([], [], "mass")
    
    #########################################################################
    #Constructor:
    def __init__(self, specieList:Iterable[Molecule], composition:Iterable[float], fracType:Literal["mass","mole"]="mass"):
        """
        Create a mixture composition from molecules and composition.

        Args:
            specieList (Iterable[Molecule]): The molecules in the mixture.
            composition (Iterable[float]): The composition of the mixture.
            fracType (Literal[&quot;mass&quot;,&quot;mole&quot;], optional): Type of fractions used in the composition. Defaults to "mass".
        """
        self._species = []
        self._Y = []
        self._X = []
        self.update(species=specieList, composition=composition, fracType=fracType)
    
    #########################################################################
    #Operators:
    
    ###############################
    #Print:
    def __str__(self):
        StrToPrint = ""
        template = "| {:14s}| {:12s} | {:12s} | {:12s}|\n"
        template1 = "{:.6f}"
        
        hLine = lambda a: (("-"*(len(a)-1)) + "\n")
        
        title = template.format("Mixture", "MM [g/mol]", "X [-]", "Y [-]")
        
        StrToPrint += hLine(title)
        StrToPrint += title
        StrToPrint += hLine(title)
        
        for data in self:
            StrToPrint += template.format(data.specie.name, template1.format(data.specie.MM), template1.format(data.X), template1.format(data.Y))
        
        StrToPrint += hLine(title)
        StrToPrint += template.format("tot", template1.format(self.MM), template1.format(self.Xsum()), template1.format(self.Ysum()))
        
        StrToPrint += hLine(title)
        
        return StrToPrint
    
    ##############################
    #Representation:
    def __repr__(self):
        R = \
            {
                "specie": self.specieNames,
                "X": self.X,
                "Y": self.Y,
                "MM": self.MM
            }
        
        return R.__repr__()
    
    ###############################
    #Access:
    def __getitem__(self, specie) -> MixtureItem:
        """
        Get the data relative to molecule in the mixture.
        
        Attributes:
            specie (str|Molecule|int): The specie to retrieve.
                - If str: checking for molecule matching the name
                - If Molecule: checking for specie
                - If int:  checing for entry following the order
        
        Returns:
            MixtureItem: dataclass for data of specie in mixture.
        """
        #Argument checking:
        self.checkType(specie, (str, Molecule, int), entryName="specie")
        
        #If str, check if a specie with that name is in the mixture
        if isinstance(specie, str):
            if not specie in [s.name for s in self.species]:
                raise ValueError("Specie {} not found in mixture composition".format(specie))
            index = self.specieNames.index(specie)
        
        #If Molecule, check if the specie is in the mixture
        elif isinstance(specie, Molecule):
            index = self.species.index(specie)
        
        #If int, check if the index is in the range
        elif isinstance(specie, int):
            if specie < 0 or specie >= len(self):
                raise ValueError("Index {} out of range".format(specie))
            index = specie
        
        #Return the data as a dataclass
        data = MixtureItem(specie=self.species[index], X=self.X[index], Y=self.Y[index])
        return data
    
    ###############################
    #Delete item:
    def __delitem__(self, specie:str|Molecule|int):
        """
        Remove a molecule from the mixture.
        
        Attributes:
            specie (str|Molecule|int): The specie to remove.
                - If str: checking for molecule matching the name
                - If Molecule: checking for specie
                - If int:  checing for entry following the order
        """
        #Argument checking:
        self.checkType(specie, [str, Molecule, int], entryName="specie")
        
        #If str, check if a specie with that name is in the mixture
        if isinstance(specie, str):
            if not specie in [s.name for s in self.species]:
                raise ValueError("Specie {} not found in mixture composition".format(specie))
            index = [s.name for s in self.species].index(specie)
        
        #If Molecule, check if the specie is in the mixture
        elif isinstance(specie, Molecule):
            index = self.species.index(specie)
        
        #If int, check if the index is in the range
        elif isinstance(specie, int):
            if specie < 0 or specie >= len(self):
                raise ValueError("Index {} out of range".format(specie))
            index = specie
        
        #Delete item:
        x = self._X[index]
        del self._species[index]
        del self._X[index]
        del self._Y[index]
        
        #Rescale mole fractions
        for ii in range(len(self)):
            self._X[ii] /= (1. - x)
        
        #Update mass fractions
        self.updateMassFracts()
    
    ###############################
    #Iteration:
    def __iter__(self):
        """
        Iterate over the specie in the mixture.
        
        Returns:
            MixtureItem: dataclass for data of specie in mixture.
        """
        return (MixtureItem(specie=s, X=x, Y=y) for s,x,y in zip(self.species, self.X, self.Y))
    
    ###############################
    def __contains__(self, entry:Molecule|str) -> bool:
        """
        Checks if a Molecule is part of the mixture.
        
        Args:
            entry (Molecule|str): The molecule to check.
                - If Molecule: checking for specie
                - If str: checking for molecule matching the name
        
        Returns:
            bool: True if the molecule is in the mixture, False otherwise.
        """
        #Argument checking:
        self.checkType(entry, [str, Molecule], "entry")
        
        if isinstance(entry, Molecule):
            return (entry in self.species)
        else:
            return (entry in [s.name for s in self.species])
    
    ###############################
    def __index__(self, entry:Molecule|str) -> int:
        """
        Return the idex position of a molecule in the Mixture.
        
        Args:
            entry (Molecule|str): The molecule to check.
                - If Molecule: checking for specie
                - If str: checking for molecule matching the name
        """
        self.checkType(entry, (Molecule,str), "entry")
        if not entry in self:
            raise ValueError("Molecule {} not found in mixture".format(entry.name if isinstance(entry, Molecule) else entry))
        
        #If Molecule, return the index of the specie in the mixture
        if isinstance(entry, Molecule):
            return self.species.index(entry)
        
        #If str, return the index of the specie with that name
        else:
            return self.specieNames.index(entry)
    
    ###############################
    #Alias for __index__:
    index = __index__
    
    ###############################
    def __len__(self) -> int:
        """
        Return the number of chemical specie in the Mixture.
        """
        return len(self._species)
    
    ###############################
    def __eq__(self, mix:Mixture) -> bool:
        """
        Check if two mixtures are equal, so if they have the same species and the same composition.
        """
        self.checkType(mix, Mixture, "mix")
        specieList1 = sorted([s for s in self],key=(lambda x: x.specie))
        specieList2 = sorted([s for s in mix],key=(lambda x: x.specie))

        return specieList1 == specieList2
    
    ###############################
    def __ne__(self, mix:Mixture) -> bool:
        """
        Check if two mixtures are different, so if they have different species or different composition.
        """
        return not(self == mix)
    
    ##############################
    #Hashing:
    def __hash__(self):
        """
        Hashing of the representation.
        """
        return hash(self.__repr__()) 
    
    #########################################################################
    #Member functions:
    
    #Overwrite the copy method:
    def copy(self) -> Mixture:
        """
        Return a copy of the mixture.
        """
        #Since molecules are immutable, we can just copy the list
        return Mixture(self.species, self.Y, "mass")
    
    ###############################
    #Update the composition with a new one
    def update(self, species:Iterable[Molecule], composition:Iterable[float], *, fracType:Literal["mass","mole"]="mass"):
        """
        Reset the mixture composition.

        Args:
            species (Iterable[Molecule]): The species in the mixture
            composition (Iterable[float]): The composition to impose
            fracType (Literal[&quot;mass&quot;,&quot;mole&quot;], optional): Type for composition fractions. Defaults to "mass".
        """
        #Argument checking:
        self.checkArray(species, Molecule, "species")
        self.checkArray(composition, float, "composition")
        
        fracType = _fracType(fracType)
        
        if not(len(composition) == len(species)):
            raise ValueError("Length mismatch between species and composition.")
        
        if len(composition):
            if not math.isclose(sum(composition), 1.):
                raise ValueError(f"Elements of entry 'composition' must add to 1 (sum = {sum(composition)})" )
            
            if not((min(composition) >= 0.0) and (max(composition) <= 1.0)):
                raise ValueError(f"All {fracType} fractions must be in range [0,1] ({composition}).")
        
        if not(len(species) == len(set(species))):
            raise ValueError("Found duplicate entries in 'specieList' list.")
        
        #Skip if the composition is the same:
        if set((s,y) for s, y in zip(species, composition)) == set((s, y) for s, y in zip(self.species, (self.Y if fracType == _fracType.mass else self.X))):
            return
        
        #Initialize data:
        self._species = [s for s in species]
        
        #Store data:
        if (fracType == _fracType.mass):
            self._Y = composition[:]
            self._X = [0.0] * len(composition)
            self.updateMoleFracts()
        elif (fracType == _fracType.mole):
            self._X = composition[:]
            self._Y = [0.0] * len(composition)
            self.updateMassFracts()
    
    ###############################
    #Compute Molar fractions:
    def updateMoleFracts(self):
        """
        Update mole fractions of the specie from mass fractions.
        """
        aux = 0.0
        for speci in self:
            aux += speci.Y / speci.specie.MM
            
        for ii, speci in enumerate(self):
            self._X[ii] = (speci.Y / speci.specie.MM) / aux
    
    ###############################
    #Compute Mass fractions:
    def updateMassFracts(self):
        """
        Update mass fractions of the specie from mole fractions.
        """
        aux = 0.0
        for speci in self:
            aux += speci.X * speci.specie.MM
        
        for ii, speci in enumerate(self):
            self._Y[ii] = (speci.X * speci.specie.MM) / aux
            
    ###############################
    #Compute MMmix:
    @property
    def MM(self) -> MM:
        """
        Return the average molecular mass of the mixture [g/mol].
        """
        MMmixture = 0.0
        for specj in self:
            MMmixture += specj.X * specj.specie.MM
        return MMmixture
    
    ###############################
    #Return the sum of mass fractions of species:
    def Ysum(self) -> float:
        """
        Return the sum of mass fractions of specie in the composition (should add to 1).
        """
        return sum(self._Y)
    
    ###############################
    #Return the sum of mole fractions of species:
    def Xsum(self) -> float:
        """
        Return the sum of mole fractions of specie in the composition (should add to 1).
        """
        return sum(self._X)
    
    ###############################
    #Dilute the mixture with a second mixture, given the mass fraction of dilutant with respect to overall mixture (for example EGR):
    def dilute(self, dilutingMix:Mixture|Molecule, dilutionFract:float, fracType:Literal["mass","mole"]="mass") -> Self:
        """
        Dilute the mixture with a second mixture, given the 
        mass/mole fraction of the dilutant mixture with respect 
        to the overall mixture.

        Args:
            dilutingMix (Mixture|Molecule): The mixture/molecule to use for dilution
            dilutionFract (float): The mass/mole fraction of the diluting mixture in the final mixture.
            fracType (Literal[&quot;mass&quot;,&quot;mole&quot;], optional): The type of fraction for dilution. Defaults to "mass".
            
        Returns:
            Self: self
        """
        #Argument checking:
        self.checkType(dilutingMix, [Mixture, Molecule], "dilutingMix")
        self.checkType(dilutionFract, float, "dilutionFract")
        fracType = _fracType(fracType)
        
        if (dilutionFract < 0.0 or dilutionFract > 1.0):
            raise ValueError(f"DilutionFract must be in range [0,1] ({dilutionFract} was found).")
        
        #Cast molecule to mixture
        if isinstance(dilutingMix, Molecule):
            dilutingMix = Mixture([dilutingMix], [1.0])
        
        #If diluting with empty mixture, skip
        if len(dilutingMix) < 1:
            return self
        
        #If the mixture is empty:
        if len(self) == 0:
            self._X = dilutingMix.X[:]
            self._Y = dilutingMix.Y[:]
            self._species = [s for s in dilutingMix.species]
        
        #If dilution fraction is too low, add the new species with zero X and Y
        if dilutionFract < 10.**(-1.*self._decimalPlaces):
            for s in dilutingMix:
                if not s.specie in self.species:
                    self._species.append(s.specie)
                    self._X.append(0.0)
                    self._Y.append(0.0)
            return self
        
        #Dilute
        for speci in dilutingMix:
            #Check if it was already present:
            if not(speci.specie in self):
                #Add the new specie
                self._species.append(speci.specie)
                if (fracType == _fracType.mass):
                    self._Y.append(speci.Y * dilutionFract)
                    self._X.append(float('nan'))
                elif (fracType ==  _fracType.mole):
                    self._X.append(speci.X * dilutionFract)
                    self._Y.append(float('nan'))
            else:
                #Dilute the already present specie
                index = self.index(speci.specie)
                if (fracType ==  _fracType.mass):
                    self._Y[index] = (self.Y[index] * (1.0 - dilutionFract)) + (speci.Y * dilutionFract)
                elif (fracType ==  _fracType.mole):
                    self._X[index] = (self.X[index] * (1.0 - dilutionFract)) + (speci.X * dilutionFract)
        
        #Update mass/mole fractions of other specie:
        for speci in self:
            if not(speci.specie in dilutingMix):
                index = self.index(speci.specie)
                if (fracType ==  _fracType.mass):
                    self._Y[index] *= (1.0 - dilutionFract)
                elif (fracType ==  _fracType.mole):
                    self._X[index] *= (1.0 - dilutionFract)
        
        if (fracType ==  _fracType.mass):
            self.updateMoleFracts()
        elif (fracType ==  _fracType.mole):
            self.updateMassFracts()
            
        return self
    
    ###############################
    #Extract submixture given specie list
    def extract(self, specieList:Iterable[Molecule]) -> Mixture:
        """
        Extract a submixture from a list of specie.
        
        Args:
            specieList (Iterable[Molecule]): List of specie to extract
        
        Raises:
            ValueError: If a specie is not found in the mixture
            
        Returns:
            Mixture: The extracted submixture
        """
        self.checkArray(specieList, Molecule, "specieList")
        
        output = None
        xOutput = 0.0
        for specie in specieList:
            if specie in self:
                if output is None:
                    output = Mixture([specie], [1])
                else:
                    output.dilute(specie, self[specie].X/(xOutput + self[specie].X), "mole")
                xOutput += self[specie].X
            else:
                raise ValueError(f"Specie {specie.name} not found in mixture.")
        
        if output is None:
            raise ValueError("Cannot extract empty mixture.")
        
        return output

    ###############################
    def removeZeros(self) -> Mixture:
        """
        Remove Molecules with too low mass and mole fraction (X or Y lower than 10**(-Mixture._decimalPlaces)).

        Returns:
            Mixture: self
        """
        toDel = []
        for item in self:
            if (item.X <= 10.**(-1.0*(Mixture._decimalPlaces))) or (item.Y <= 10.**(-1.0*(Mixture._decimalPlaces))):
                toDel.append(item.specie)

        for item in toDel:
            del self[item]
        
        return self
        
    ###############################
    #Substract a mixture from this:
    def subtractMixture(self, mix:Mixture) -> tuple[float,Mixture]:
        """
        Finds the maximum sub-mixture with composition 'mix' in this. Then returns a tuple with (yMix, remainder)
        which are the mass-fraction of mixture 'mix' in this and the remaining mixture once 'mix' is removed.

        Args:
            mix (Mixture): Mixture to subtract from this

        Returns:
            tuple[float,Mixture]: couple (yMix, remainder)
        
        Example:
            - Create a mixture of H2, O2 and CO2 and substract a mixture of H2 and O2
                >>> from libICEpost.src.thermophysicalModels.specie.specie.Atom import Atom
                >>> from libICEpost.src.thermophysicalModels.specie.specie.Molecule import Molecule
                >>> from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture
                # Atoms and molecules
                >>> O = Atom("O", 16.00)
                >>> H = Atom("H", 1.008)
                >>> C = Atom("C", 12.01)
                >>> H2 = Molecule("H2", [H], [2.0])
                >>> O2 = Molecule("O2", [O], [2.0])
                >>> CO2 = Molecule("CO2", [C,O], [1.0, 2.0])
                #Mixture of H2, O2 and CO2
                >>> Mix1 = Mixture([H2, O2, CO2], [0.1, 0.2, 0.7])
                >>> print(Mix1)
                -------------------------------------------------------------
                | Mixture       | MM [g/mol]   | X [-]        | Y [-]       |
                -------------------------------------------------------------
                | H2            | 2.016000     | 0.691250     | 0.100000    |
                | O2            | 32.000000    | 0.087098     | 0.200000    |
                | CO2           | 44.010000    | 0.221652     | 0.700000    |
                -------------------------------------------------------------
                | tot           | 13.935602    | 1.000000     | 1.000000    |
                -------------------------------------------------------------
                #Mixture of only H2 and O2
                >>> Mix2 = Mixture([H2, O2], [0.5, 0.5])
                >>> print(Mix2)
                -------------------------------------------------------------
                | Mixture       | MM [g/mol]   | X [-]        | Y [-]       |
                -------------------------------------------------------------
                | H2            | 2.016000     | 0.940734     | 0.500000    |
                | O2            | 32.000000    | 0.059266     | 0.500000    |
                -------------------------------------------------------------
                | tot           | 3.793039     | 1.000000     | 1.000000    |
                -------------------------------------------------------------
                #Substract Mix2 from Mix1
                >>> yMix, remainder = Mix1.subtractMixture(Mix2)
                >>> yMix
                0.2
                >>> print(remainder)
                -------------------------------------------------------------
                | Mixture       | MM [g/mol]   | X [-]        | Y [-]       |
                -------------------------------------------------------------
                | O2            | 32.000000    | 0.164210     | 0.125000    |
                | CO2           | 44.010000    | 0.835790     | 0.875000    |
                -------------------------------------------------------------
                | tot           | 42.037834    | 1.000000     | 1.000000    |
                -------------------------------------------------------------
        """
        #Full mixture:
        if mix == self:
            return (1.0, Mixture.empty())
        
        #Mass fraction of mix in self
        yMix = sum([self[s.specie].Y for s in mix if s.specie in self])
        
        #Find limiting specie:
        yLimRatio = float("inf")
        for specie in mix:
            if not specie.specie in self:
                yLimRatio = 0.0
                break
            
            currY = self[specie.specie].Y
            #Check if this specie is limiting and if it is the most limiting
            if (currY <= specie.Y*yMix) and (currY/(specie.Y*yMix) <= yLimRatio):
                limSpecie = specie.specie
                yLimRatio = currY/(specie.Y*yMix)
        
        #Some element is not found
        if yLimRatio == 0.0:
            return (0.0, self.copy().removeZeros())
        
        #Compute difference
        yMixNew = yMix*yLimRatio
        newY = [s.Y - (mix[s.specie].Y*yMixNew if s.specie in mix else 0.0) for s in self]
        
        #Truncate near-zero Y species to zero
        newY = [(y if (y > 10.**(-1.*self._decimalPlaces)) else 0.0) for y in newY]
        
        #Normalize
        sumY = sum(newY)
        newY = [y/sumY for y in newY]
        
        #Build mixture
        remainder = Mixture(self.species, newY, "mass").removeZeros()
        
        return yMixNew,remainder
        

#############################################################################
#                             FRIEND FUNCTIONS                              #
#############################################################################
#Mixture blend:
def mixtureBlend(mixtures:Iterable[Mixture], composition:Iterable[float], fracType:Literal["mass","mole"]="mass") -> Mixture:
    """
    Blends together a group of mixtures.
    
    Args:
        mixtures (Iterable[Mixture]): List of mixtures to be blended
        composition (Iterable[float]): List of mass/mole fractions for the blending
        fracType (Literal[&quot;mass&quot;,&quot;mole&quot;], optional): Type of blending (mass/mole fraction-based). Defaults to "mass".
    
    Returns:
        Mixture: The blended mixture
    """
    #Argument checking:
    checkType(mixtures, Iterable, entryName="mixtures")
    [checkType(s, Mixture, entryName=f"mixtures[{ii}]") for ii,s in enumerate(mixtures)]
    checkType(composition, Iterable, entryName="composition")
    [checkType(s, float, entryName=f"composition[{ii}]") for ii,s in enumerate(composition)]
    
    if not(len(composition) == len(mixtures)):
        raise ValueError("Entries 'composition' and 'mixtures' must be of same length.")
    
    if len(composition) < 1:
        raise ValueError("'composition' cannot be empty." )
    
    if not math.isclose(sum(composition), 1., abs_tol=10.**(-1.*Mixture._decimalPlaces)):
        raise ValueError(f"Elements of entry 'composition' must add to 1 ({sum(composition)})." )
    
    if not((min(composition) >= 0.0) and (max(composition) <= 1.0)):
        raise ValueError(f"All {fracType} fractions must be in range [0,1] ({composition}).")
    
    mixBlend:Mixture = None
    for ii, mix in enumerate(mixtures):
        if composition[ii] <= 10.**(-1.*Mixture._decimalPlaces):
            continue
        
        #If first mixture, initialize as copy
        if mixBlend is None:
            mixBlend = mix.copy()
            Yblen = composition[ii]
            continue
        
        #Dilute the mixture 
        Ydil = composition[ii]/(Yblen + composition[ii])
        mixBlend.dilute(mix, Ydil, fracType)
        Yblen += composition[ii]
    
    return mixBlend

#############################################################################
#Load database
import libICEpost.Database.chemistry.specie.Mixtures