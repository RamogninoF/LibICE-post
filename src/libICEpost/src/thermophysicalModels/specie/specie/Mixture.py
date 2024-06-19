#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023

TODO:
    Optimize the dilute method
    The 'for item in self' could be non optimal with current implementation
    Define a update(mix:Mixture) method to change the mixture composition. Then use it whenever a Mixture is changed in a class, so that its pointer is preserved.
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from __future__ import annotations

from libICEpost.src.base.Utilities import Utilities
from dataclasses import dataclass

import math
from .Atom import Atom
from .Molecule import Molecule

from libICEpost.Database import database
from libICEpost.Database import chemistry

constants = database.chemistry.constants

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
@dataclass
class MixtureItem:
    """
    Dataclass used as return value by Mixture.__getitem__ method
    """
    specie:Molecule
    X:float
    Y:float

#Mixture class:
class Mixture(Utilities):
    #########################################################################
    """
    Class handling a the mixture of a homogeneous mixture.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        _specie:     list<Molecule>
            Specie in the mixture
        
        _X:          list<float>
            Mole fractions of specie in the mixture
        
        _Y:          list<float>
            Mass fractions of specie in the mixture
    """
    
    _decimalPlaces = 10
    _X:list[float]
    _Y:list[float]
    _specie:list[Molecule]
    
    #########################################################################
    @property
    def Rgas(self):
        """
        The mass-specific gas constant of the mixture.
        """
        specGasConst = constants.Rgas / self.MM
        return specGasConst

    #########################################################################
    @property
    def Y(self):
        """
        The mass fractions.
        """
        return [self.np.round(y, Mixture._decimalPlaces) for y in self._Y]
    
    #################################
    @Y.setter
    def Y(self, y:list):
        self.checkTypes(y, [list, self.np.ndarray], "y")
        if not len(y) == len(self):
            raise ValueError("Inconsistent size of y with mixture composition.")
        self._Y = list(y[:])
        self.updateMoleFracts()
        
    #################################
    @property
    def X(self):
        """
        The mole fractions.
        """
        return [self.np.round(x, Mixture._decimalPlaces) for x in self._X]
    
    #################################
    @X.setter
    def X(self, x:list):
        self.checkTypes(x, [list, self.np.ndarray], "x")
        if not len(x) == len(self):
            raise ValueError("Inconsistent size of x with mixture composition.")
        self._X = list(x[:])
        self.updateMassFracts()
    
    #################################
    @property
    def specie(self):
        """
        The specie in the mixture.
        """
        return self._specie[:]
    
    #########################################################################
    @classmethod
    def empty(cls):
        """
        Overload empty initializer.
        """
        item = super().empty()
        item._X = []
        item._Y = []
        item._specie = []
        return item
    
    #########################################################################
    #Constructor:
    def __init__(self, specieList:list[Molecule], composition:list[float], fracType ="mass"):
        """
        specieList:         list<Molecule>
            Names of the chemical specie in the mixture (must be in
            ThermoTable)
        composition:    list<float>
            Names of the atomic specie contained in the chemical specie
        fracType:       str ("mass" or "mole")
            Type of dilution, if mass fraction or mole fraction based.
        
        Create a mixture composition from molecules and composition.
        """
        #Argument checking:
        try:
            self.checkInstanceTemplate(specieList, [Molecule.empty()], entryName="specieList")
            self.checkInstanceTemplate(composition, [1.0], entryName="composition")
            self.checkType(fracType, str, entryName="fracType")
            
            if not((fracType == "mass") or (fracType == "mole")):
                raise TypeError("'fracType' accepted are: 'mass', 'mole'. Cannot create the mixture.")
        
            if not(len(composition) == len(specieList)):
                raise ValueError("Entries 'composition' and 'specieList' must be of same length.")
            
            if len(composition):
                if not math.isclose(sum(composition), 1.):
                    raise TypeError("Elements of entry 'composition' must add to 1." )
                
                if not((min(composition) >= 0.0) and (max(composition) <= 1.0)):
                    raise ValueError("All "+ fracType+ " fractions must be in range [0,1].")
            
            if not(specieList == [i for n, i in enumerate(specieList) if i not in specieList[:n]]):
                raise ValueError("Found duplicate entries in 'specieList' list.")
        
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        #Initialize data:
        self._specie = [s.copy() for s in specieList]
        
        #Store data:
        if (fracType == "mass"):
            self._Y = composition[:]
            self._X = [0.0] * len(composition)
            self.updateMolFracts()
        elif (fracType == "mole"):
            self._X = composition[:]
            self._Y = [0.0] * len(composition)
            self.updateMassFracts()
        
        #Data for iteration:
        self._current_index = 0
    
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
                "specie": self.specie,
                "X": self.X,
                "Y": self.Y,
                "MM": self.MM
            }
        
        return R.__repr__()
    
    ###############################
    #Access:
    def __getitem__(self, specie) -> MixtureItem:
        """
        specie:     str / Molecule / int
        
        Get the data relative to molecule in the mixture
            -> If str: checking for molecule matching the name
            -> If Molecule: checking for specie
            -> If int:  checing for entry following the order
        
        Returns:
            MixtureItem: dataclass for data of specie in mixture.
        """
        #Argument checking:
        try:
            self.checkTypes(specie, [str, Molecule, int], entryName="specie")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__getitem__, err)
        
        try:
            if isinstance(specie, str):
                if not specie in [s.name for s in self.specie]:
                    raise ValueError("Specie {} not found in mixture composition".format(specie))
                index = [s.name for s in self.specie].index(specie)
            
            elif isinstance(specie, Molecule):
                index = self.specie.index(specie)
            
            elif isinstance(specie, int):
                if specie < 0 or specie >= len(self):
                    raise ValueError("Index {} out of range".format(specie))
                index = specie
        except BaseException as err:
            self.fatalErrorInClass(self.__getitem__, "failure retrieving molecule in mixture", err)
        
        data = MixtureItem(specie=self.specie[index].copy(), X=self.X[index], Y=self.Y[index])
            # {
            #     "specie":self.specie[index].copy(),
            #     "X":self.X[index],
            #     "Y":self.Y[index]
            # }
        
        return data
    
    ###############################
    #Delete item:
    def __delitem__(self, specie):
        """
        specie:     str / Molecule / int
        
        Remove molecule from mixture
            -> If str: checking for molecule matching the name
            -> If Molecule: checking for specie
            -> If int:  checing for entry following the order
        
        Returns:
            MixtureItem: dataclass for data of specie in mixture.
        """
        #Argument checking:
        try:
            self.checkTypes(specie, [str, Molecule, int], entryName="specie")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__getitem__, err)
        
        try:
            if isinstance(specie, str):
                if not specie in [s.name for s in self.specie]:
                    raise ValueError("Specie {} not found in mixture composition".format(specie))
                index = [s.name for s in self.specie].index(specie)
            
            elif isinstance(specie, Molecule):
                index = self.specie.index(specie)
            
            elif isinstance(specie, int):
                if specie < 0 or specie >= len(self):
                    raise ValueError("Index {} out of range".format(specie))
                index = specie
        except BaseException as err:
            self.fatalErrorInClass(self.__getitem__, "failure retrieving molecule in mixture", err)
        
        #Rescale mole fractions
        for ii in range(len(self)):
            self._X[ii] /= (1 - self._X[index])
        
        #Delete item:
        del self._specie[index]
        del self._X[index]
        del self._Y[index]
        
        #Update mass fractions
        self.updateMassFracts()
    
    ###############################
    #Iteration:
    def __iter__(self):
        """
        Iteration over the specie in the mixture.
        """
        return MixtureIter(self)
    
    ###############################
    def __contains__(self, entry):
        """
        Checks if a Molecule is part of the mixture.
        """
        #Argument checking:
        try:
            self.checkTypes(entry, [str, Molecule], "entry")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__contains__, err)
        
        if isinstance(entry, Molecule):
            return (entry in self.specie)
        else:
            return (entry in [s.name for s in self.specie])
    
    ###############################
    def __index__(self, entry):
        """
        Return the idex position of the Molecule in the Mixture.
        """
        #Argument checking:
        try:
            self.checkType(entry, Molecule, "entry")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__index__, err)
        
        return self.specie.index(entry)
    
    ###############################
    def index(self, entry):
        """
        Return the idex position of the Molecule in the Mixture.
        """
        try:
            self.checkType(entry, Molecule, "entry")
            if not entry in self:
                raise ValueError("Molecule {} not found in mixture".format(entry.name))
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__index__, err)
        return self.__index__(entry)
    
    ###############################
    def __len__(self):
        """
        Return the number of chemical specie in the Mixture.
        """
        return len(self.specie)
    
    ###############################
    def __eq__(self, mix):
        self.checkType(mix, Mixture, "mix")
        specieList1 = sorted([s for s in self],key=(lambda x: x.specie))
        specieList2 = sorted([s for s in mix],key=(lambda x: x.specie))

        return specieList1 == specieList2
    
    #########################################################################
    #Member functions:
    
    ###############################
    #Compute Molar fractions:
    def updateMolFracts(self):
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
    def MM(self):
        """
        Return the average molecular mass of the mixture.
        """
        MMmixture = 0.0
        for specj in self:
            MMmixture += specj.X * specj.specie.MM
        return MMmixture
    
    ###############################
    #Return the sum of mass fractions of species:
    def Ysum(self):
        """
        Return the sum of mass fractions of specie in the composition (should add to 1).
        """
        Ysum = 0.0
        for speci in self:
            Ysum += speci.X
        return Ysum
    
    ###############################
    #Return the sum of mole fractions of species:
    def Xsum(self):
        """
        Return the sum of mole fractions of specie in the composition (should add to 1).
        """
        Xsum = 0.0
        for speci in self:
            Xsum += speci.X
        return Xsum
    
    ###############################
    #Dilute the mixture with a second mixture, given the mass fraction of dilutant with respect to overall mixture (for example EGR):
    def dilute(self, dilutingMix:Mixture, dilutionFract:float, fracType:str="mass"):
        """
        dilutingMix:        Mixture/Molecule
            Diluting mixture
        dilutionFract:      float
            mass/mole fraction of the dilutant mixture with respect 
            to the overall mixture.
        fracType:       str ("mass" or "mole")
            Type of dilution, if mass fraction or mole fraction based.
        
        Dilute the mixture with a second mixture, given the 
        mass/mole fraction of the dilutant mixture with respect 
        to the overall mixture.
        """
        #Argument checking:
        try:
            self.checkTypes(dilutingMix, [self.__class__, Molecule], "dilutingMix")
            self.checkType(dilutionFract, float, "dilutionFract")
            self.checkType(fracType, str, "fracType")
            if not((fracType == "mass") or (fracType == "mole")):
                raise ValueError("'fracType' accepted are: 'mass', 'mole'. Cannot perform dilution.")
            
            if (dilutionFract < 0.0 or dilutionFract > 1.0):
                raise ValueError("DilutionFract must be in range [0,1].")
        
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.dilute, err)
        
        #If dilution fraction is too low, skip
        if dilutionFract < 10.**(-1.*self._decimalPlaces):
            return self
        
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
            self._specie = [s for s in dilutingMix.specie]
        
        #Dilute
        try:
            for speci in dilutingMix:
                #Check if it was already present:
                if not(speci.specie in self):
                    #Add the new specie
                    self._specie.append(speci.specie)
                    if (fracType == "mass"):
                        self._Y.append(speci.Y * dilutionFract)
                        self._X.append(float('nan'))
                        # self.updateMolFracts()
                    elif (fracType == "mole"):
                        self._X.append(speci.X * dilutionFract)
                        self._Y.append(float('nan'))
                        # self.updateMassFracts()
                else:
                    #Dilute the already present specie
                    index = self.index(speci.specie)
                    if (fracType == "mass"):
                        self._Y[index] = (self.Y[index] * (1.0 - dilutionFract)) + (speci.Y * dilutionFract)
                    elif (fracType == "mole"):
                        self._X[index] = (self.X[index] * (1.0 - dilutionFract)) + (speci.X * dilutionFract)
            
            #Update mass/mole fractions of other specie:
            for speci in self:
                if not(speci.specie in dilutingMix):
                    index = self.index(speci.specie)
                    if (fracType == "mass"):
                        self._Y[index] *= (1.0 - dilutionFract)
                    elif (fracType == "mole"):
                        self._X[index] *= (1.0 - dilutionFract)
            
            if (fracType == "mass"):
                self.updateMolFracts()
            elif (fracType == "mole"):
                self.updateMassFracts()
        except BaseException as err:
            self.fatalErrorInClass(self.dilute, "Failed diluting the mixture", err)
        return self
    
    ###############################
    #Extract submixture given specie list
    def extract(self, specieList):
        """
        specieList:        list<Molecule>
            List of specie to extract
        
        Extract a submixture from a list of specie. Raises ValueError if a Molecule
        is not found in mixture
        """
        try:
            self.checkContainer(specieList, list, Molecule, "specieList")
            
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
        except BaseException as err:
            self.fatalErrorInClass(self.extract, "Error extracting sub-mixture", err)

    ###############################
    def removeZeros(self) -> Mixture:
        """
        Remove Molecules with too low mass and mole fraction (Mixture._decimalPlaces).

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
        """
        #Full mixture:
        if mix == self:
            return (1.0, Mixture.empty())
        
        #Mass fraction of mix in self
        yMix = sum([self[s.specie].Y for s in mix if s.specie in self])
        
        #Find limiting element:
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
        
        #Remove near-zero remainders
        newY = [(y if y > 10.**(-1.*self._decimalPlaces) else 0.0) for y in newY]
        
        #Normalize
        sumY = sum(newY)
        newY = [y/sumY for y in newY]
        
        #Build mixture
        remainder = Mixture([s.specie for s in self], newY, "mass").removeZeros()
        
        return yMixNew,remainder
        
        
#############################################################################
#                               FRIEND CLASSES                              #
#############################################################################
#Iterator:
class MixtureIter:
    """
    Iterator for Mixture class.
    """
    def __init__(self, composition:Mixture):
        self.composition:Mixture = composition
        self.specieList:list[Molecule] = [s.name for s in composition.specie]
        self.current_index:int = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current_index < len(self.specieList) and not(len(self.specieList) == 0):
            out = self.composition[self.specieList[self.current_index]]
            self.current_index += 1
            return out
        else:
            raise StopIteration

#############################################################################
#                             FRIEND FUNCTIONS                              #
#############################################################################
#Mixture blend:
def mixtureBlend(mixtures:list[Mixture], composition:list[float], fracType:str="mass") -> Mixture:
    """
    mixture:    list<mixture>
            List of mixtures to be blended
    composition:          list<float>
        List of mass/mole fractions for the blending
    fracType:   str
        Type of blending (mass/mole fraction-based)
    
    Blends together a group of mixtures.
    """
    #Argument checking:
    try:
        Utilities.checkContainer(mixtures, list, Mixture, entryName="mixtures")
        Utilities.checkContainer(composition, list, float, entryName="composition")
        
        if not((fracType == "mass") or (fracType == "mole")):
            raise TypeError("'fracType' accepted are: 'mass', 'mole'. Cannot create the mixture.")
        
        if not(len(composition) == len(mixtures)):
            raise ValueError("Entries 'composition' and 'mixtures' must be of same length.")
        
        if len(composition) < 1:
            raise TypeError("'composition' cannot be empty." )
        
        if not math.isclose(sum(composition), 1.):
            raise TypeError("Elements of entry 'composition' must add to 1." )
        
        if not((min(composition) >= 0.0) and (max(composition) <= 1.0)):
            raise ValueError("All "+ fracType+ " fractions must be in range [0,1].")
        
        if not(mixtures == [i for n, i in enumerate(mixtures) if i not in mixtures[:n]]):
            raise ValueError("Found duplicate entries in 'mixtures' list.")
        
    except BaseException as err:
        Utilities.fatalErrorInArgumentChecking(None,mixtureBlend, err)
    
    mixBlend:Mixture = None
    for ii, mix in enumerate(mixtures):
        if composition[ii] <= 0.:
            continue
        
        if mixBlend is None:
            mixBlend = mix.copy()
            Yblen = composition[ii]
            continue
            
        Ydil = composition[ii]/(Yblen + composition[ii])
        mixBlend.dilute(mix, Ydil, fracType)
        Yblen += composition[ii]
    
    return mixBlend

#############################################################################
#Load database
import libICEpost.Database.chemistry.specie.Mixtures