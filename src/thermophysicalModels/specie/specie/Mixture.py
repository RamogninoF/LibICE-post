#####################################################################
#                               IMPORT                              #
#####################################################################

from src.base.Utilities import Utilities

from src.thermophysicalModels.specie.specie.Atom import Atom
from src.thermophysicalModels.specie.specie.Molecule import Molecule

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Mixture class:
class Mixture(Utilities):
    #########################################################################
    """
    Class handling a the mixture of a homogeneous mixture.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        specie:     list<Molecule>
            Specie in the mixture
        
        X:          list<float>
            Mole fractions of specie in the mixture
        
        Y:          list<float>
            Mass fractions of specie in the mixture
    """
    
    specie = [Molecule.empty()]
    X = [float("nan")]
    Y = [float("nan")]
    
    #########################################################################
    #Constructor:
    def __init__(self, specieList, composition, fracType ="mass"):
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
            self.__class__.checkInstanceTemplate(specieList, [Molecule.empty()], entryName="specieList")
            self.__class__.checkInstanceTemplate(composition, [1.0], entryName="composition")
            self.__class__.checkType(fracType, str, entryName="fracType")
            
            if not((fracType == "mass") or (fracType == "mole")):
                raise TypeError("'fracType' accepted are: 'mass', 'mole'. Cannot create the mixture.")
        
            if not(len(composition) == len(specieList)):
                raise ValueError("Entries 'composition' and 'specieList' must be of same length.")
            
            if len(composition):
                if (not(sum(composition)) == 1):
                    raise TypeError("Elements of entry 'composition' must add to 1." )
                
                if not((min(composition) >= 0.0) and (max(composition) <= 1.0)):
                    raise ValueError("All "+ fracType+ " fractions must be in range [0,1].")
            
            if not(specieList == [i for n, i in enumerate(specieList) if i not in specieList[:n]]):
                raise ValueError("Found duplicate entries in 'specieList' list.")
        
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        #Initialize data:
        self.specie = [s.copy() for s in specieList]
        self.X = []
        self.Y = []
        
        #Store data:
        if (fracType == "mass"):
            self.Y = composition[:]
            self.X = [0.0] * len(composition)
            self.updateMolFracts()
        elif (fracType == "mole"):
            self.X = composition[:]
            self.Y = [0.0] * len(composition)
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
            StrToPrint += template.format(data["specie"].name, template1.format(data["specie"].MM()), template1.format(data["X"]), template1.format(data["Y"]))
        
        StrToPrint += hLine(title)
        StrToPrint += template.format("tot", template1.format(self.MM()), template1.format(self.Xsum()), template1.format(self.Ysum()))
        
        StrToPrint += hLine(title)
        
        StrToPrint += "\n"
        
        return StrToPrint
    
    ###############################
    #Access:
    def __getitem__(self, specie):
        """
        specie:     str / Molecule / int
        
        Get the data relative to molecule in the mixture
            -> If str: checking for molecule matching the name
            -> If Molecule: checking for specie
            -> If int:  checing for entry following the order
        
        {
            specie:     Molecule
                The molecule
            X:          float
                Mole fraction in mixture
            Y:          float
                Mass fraction in mixture
        }
        """
        #Argument checking:
        try:
            self.__class__.checkTypes(specie, [str, Molecule, int], entryName="specie")
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
            self.fatalErrorIn(self.__getitem__, "failure retrieving molecule in mixture", err)
        
        data = \
            {
                "specie":self.specie[index].copy(),
                "X":self.X[index],
                "Y":self.Y[index]
            }
        
        return data
    
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
            self.__class__.checkTypes(entry, [str, Molecule], "entry")
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
            self.__class__.checkType(entry, Molecule, "entry")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__index__, err)
        
        return self.specie.index(entry)
    
    ###############################
    def index(self, entry):
        """
        Return the idex position of the Molecule in the Mixture.
        """
        try:
            self.__class__.checkType(entry, Molecule, "entry")
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
    
    #########################################################################
    #Member functions:
    
    ###############################
    #Compute Molar fractions:
    def updateMolFracts(self):
        aux = 0.0
        for speci in self:
            aux += speci["Y"] / speci["specie"].MM()
            
        for ii, speci in enumerate(self):
            self.X[ii] = (speci["Y"] / speci["specie"].MM()) / aux
    
    ###############################
    #Compute Mass fractions:
    def updateMassFracts(self):
        aux = 0.0
        for speci in self:
            aux += speci["X"] * speci["specie"].MM()
        
        for ii, speci in enumerate(self):
            self.Y[ii] = (speci["X"] * speci["specie"].MM()) / aux
            
    ###############################
    #Compute MMmix:
    def MM(self):
        """
        Return the average molecular mass of the mixture.
        """
        MMmixture = 0.0
        for specj in self:
            MMmixture += specj["X"] * specj["specie"].MM()
        return MMmixture
    
    ###############################
    #Compute Rgas:
    def Rgas(self):
        """
        Return the mass-specific gas constant of the mixture.
        """
        RUniv = 8314.0
        specGasConst = RUniv / self.MM()
        return specGasConst
    
    ###############################
    #Return the sum of mass fractions of species:
    def Ysum(self):
        """
        Return the sum of mass fractions of specie in the composition (should add to 1).
        """
        Ysum = 0.0
        for speci in self:
            Ysum += speci["Y"]
        return Ysum
    
    ###############################
    #Return the sum of mole fractions of species:
    def Xsum(self):
        """
        Return the sum of mole fractions of specie in the composition (should add to 1).
        """
        Xsum = 0.0
        for speci in self:
            Xsum += speci["X"]
        return Xsum
    
    ###############################
    #Dilute the mixture with a second mixture, given the mass fraction of dilutant with respect to overall mixture (for example EGR):
    def dilute(self, dilutingMix, dilutionFract, fracType ="mass"):
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
            self.__class__.checkTypes(dilutingMix, [self.__class__, Molecule], "dilutingMix")
            self.__class__.checkType(dilutionFract, float, "dilutionFract")
            self.__class__.checkType(fracType, str, "fracType")
            if not((fracType == "mass") or (fracType == "mole")):
                raise ValueError("'fracType' accepted are: 'mass', 'mole'. Cannot perform dilution.")
            
            if (dilutionFract < 0.0 or dilutionFract > 1.0):
                raise ValueError("DilutionFract must be in range [0,1].")
        
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.dilute, err)
        
        if isinstance(dilutingMix, Molecule):
            dilutingMix = Mixture([dilutingMix], [1.0])
        
        for speci in dilutingMix:
            #Check if it was already present:
            if not(speci["specie"] in self):
                #Add the new specie
                self.specie.append(speci["specie"].copy())
                if (fracType == "mass"):
                    self.Y.append(speci["Y"] * dilutionFract)
                elif (fracType == "mole"):
                    self.X.append(speci["X"] * dilutionFract)
            else:
                #Dilute the already present specie
                index = self.index(speci["specie"])
                if (fracType == "mass"):
                    self.Y[index] = (self.Y[index] * (1.0 - dilutionFract)) + (speci["Y"] * dilutionFract)
                elif (fracType == "mole"):
                    self.X[index] = (self.X[index] * (1.0 - dilutionFract)) + (speci["X"] * dilutionFract)
        
        #Update mass/mole fractions of other specie:
        for speci in self:
            if not(speci["specie"] in dilutingMix):
                index = self.index(speci["specie"])
                if (fracType == "mass"):
                    self.Y[index] *= (1.0 - dilutionFract)
                elif (fracType == "mole"):
                    self.X[index] *= (1.0 - dilutionFract)
        
        if (fracType == "mass"):
            self.updateMolFracts()
        elif (fracType == "mole"):
            self.updateMassFracts()
    
        return self

#############################################################################
#                               FRIEND CLASSES                              #
#############################################################################
#Iterator:
class MixtureIter:
    def __init__(self, composition):
        self.composition = composition
        self.specieList = [s.name for s in composition.specie]
        
        self.current_index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current_index < len(self.specieList):
            out = self.composition[self.specieList[self.current_index]]
            self.current_index += 1
            return out
        else:
            raise StopIteration

#############################################################################
#                             FRIEND FUNCTIONS                              #
#############################################################################
#Mixture blend:
def mixtureBlend(mixtures, composition, fracType ="mass"):
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
        Utilities.checkInstanceTemplate(mixtures, [Mixture.empty()], entryName="mixtures")
        Utilities.checkInstanceTemplate(composition, [1.0], entryName="composition")
        Utilities.checkType(fracType, str, entryName="fracType")
        
        if not((fracType == "mass") or (fracType == "mole")):
            raise TypeError("'fracType' accepted are: 'mass', 'mole'. Cannot create the mixture.")
        
        if not(len(composition) == len(mixtures)):
            raise ValueError("Entries 'composition' and 'mixtures' must be of same length.")
        
        if len(composition) < 1:
            raise TypeError("'composition' cannot be empty." )
        
        if (not(sum(composition)) == 1):
            raise TypeError("Elements of entry 'composition' must add to 1." )
        
        if not((min(composition) >= 0.0) and (max(composition) <= 1.0)):
            raise ValueError("All "+ fracType+ " fractions must be in range [0,1].")
        
        if not(specie == [i for n, i in enumerate(specie) if i not in specie[:n]]):
            raise ValueError("Found duplicate entries in 'specie' list.")
        
    except BaseException as err:
        Utilities.fatalErrorInArgumentChecking(None,mixtureBlend, err)
    
    mixBlend = mixtures[0].copy()
    Yblen = Y[0]
    for ii in range(len(mixtures) - 1):
        Ydil = Y[ii+1]/(Yblen + Y[ii+1])
        mixBlend.dilute(mixtures[ii+1], Ydil, fracType)
        Yblen += Y[ii+1]
    
    return mixBlend
