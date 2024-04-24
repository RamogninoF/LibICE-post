#####################################################################
#                               IMPORT                              #
#####################################################################

from libICEpost.src.base.Utilities import Utilities

from ..specie.specie.Atom import Atom
from ..specie.specie.Molecule import Molecule

from ..specie.thermo.Reaction.Reaction import Reaction
from ..specie.thermo.Thermo.Thermo import Thermo

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Table with thermodynamic properties:
class ThermoTable(Utilities):
    """
    Class handling a thermodynamic table (data of atomic specie, chemical specie
    and reactions).
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        atoms:          list<Atom>
            Atomic specie
            
        molecules:      list<Molecule>
            Chemical specie
        
        reactions:      list<Reaction>
            Reactions
        
        thermo:         list<Thermo>
            Thermodynamic properties of chemical specie
    """
    
    atoms = []
    molecules = []
    reactions = []
    thermos = []
    
    #########################################################################
    #Constructor:
    def __init__(self, **argv):
        """
        [keyword arguments]
        molecules:  list<Molecule>
            List of chemical specie
        reactions:  list<Reaction>
            List of reactions
        thermos:    list<Thermo>
            List of thermodynamic properties to add to the table
        verbose:    bool (True)
            Show info when constructing the table
            
            The chemical specie in the table are initialized from:
            ->  those in 'chemSpecieList'
            ->  reactants and products of the reactions
            ->  those associated to each Thermo
            
            The ractions in the table are initialized from:
            ->  those in 'reactionsList'
            ->  Default reactions (transition of a single specie from
                reactants to products without reaction)
                
            The atomic specie in the table are initialized from:
            ->  Atoms in all molecules
            
            In case there are multiple atomic/chemical specie or reactions
            with same name but different properties, a ValueError is raised.
        """
        print("CONSTRUCTING THERMODYNAMIC TABLE")
        
        #Argument checking:
        defArgv = \
            {
                "molecules":[],
                "reactions":[],
                "thermos":[],
                "verbose":True
            }
        
        try:
            opts = self.updateKeywordArguments(argv, defArgv, allowEmptyContainer=True)
            
            molecules = opts["molecules"]
            reactions = opts["reactions"]
            thermos = opts["thermos"]
            
            self.checkContainer\
                (
                    molecules,
                    list,
                    Molecule,
                    entryName="molecules",
                    allowEmptyContainer=True
                )
            self.checkContainer\
                (
                    reactions,
                    list,
                    Reaction,
                    entryName="reactions",
                    allowEmptyContainer=True
                )
            self.checkContainer\
                (
                    thermos,
                    list,
                    Thermo,
                    entryName="thermos", 
                    allowEmptyContainer=True
                )
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        #Initialize lists
        self.atoms = self.__class__.atoms
        self.molecules = self.__class__.molecules
        self.reactions = self.__class__.reactions
        self.thermos = self.__class__.thermos
        
        try:
            #Add molecules:
            if not(molecules is None):
                for molecule in molecules:
                    self.addMolecule(molecule)
                    
            #Add reactions:
            if not(reactions is None):
                for reaction in reactions:
                    self.addReaction(reaction)
            
            #Add thermo pros:
            if not(thermos is None):
                for thermo in thermos:
                    self.addThermo(thermo)
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, "Failed constructing the thermodynamic table", err)
        
        if opts["verbose"]:
            print(self)
        
    #########################################################################
    #Operators:
    #Print:
    def __str__(self):
        string = ""
        hLine = lambda a: (("-"*(len(a)-1)) + "\n")
        
        #Atomic specie:
        template = "| {:20}| {:20}|\n"
        
        string += "ATOMS:\n"
        title = template.format("", "m [g/mol]")
        
        string += hLine(title)
        string += title
        string += hLine(title)
        
        for atom in self.atoms:
            string += template.format(atom.name, atom.mass)
        
        string +=hLine(title)
        string += "\n"
        
        #Chem specie:
        template = "| {:20}| {:30}| {:20}|\n"
        
        string += "CHEMICAL SPECIE:\n"
        title = template.format("", "Brute formula", "m [g/mol]")
        
        string += hLine(title)
        string += title
        string += hLine(title)
        
        for chem in self.molecules:
            string += template.format(chem.name, chem.bruteFormula(), chem.MM())
        
        string +=hLine(title)
        string += "\n"
        
        #Reactions:
        template = "| {:40}| {:40}|\n"
        
        string += "REACTIONS:\n"
        title = template.format("Reactants", "Products")
        
        string += hLine(title)
        string += title
        string += hLine(title)
        
        for reaction in self.reactions:
            formula = str(reaction)
            reactants, products = tuple(formula.split("=>"))
            string += template.format(reactants, products)
        
        string +=hLine(title)
        string += "\n"
        
        #Thermos:
        template = "| {:20}| {:20}|\n"
        
        string += "Thermo:\n"
        title = template.format("Specie", "Type")
        
        string += hLine(title)
        string += title
        string += hLine(title)
        
        for thermo in self.thermos:
            string += template.format(thermo.specie.name, thermo.typeName)
        
        string +=hLine(title)
        string += "\n"
        
        #Add decorations
        name = "THERMOTABLE"
        width = max([len(l) for l in string.split("\n")])
        
        topDecor =" [" + name + "] "
        topDecor = "~"*((width - len(topDecor))//2) + topDecor + "~"*((width - len(topDecor))//2)
        bottomDecor = "~"*len(topDecor)
        string = topDecor + "\n" + string + bottomDecor + "\n"
        
        return string
    
    #################################
    #Inplace addition:
    def __iadd__(self, other):
        """
        Possible additions:
            ThermoTable + Atom
            ThermoTable + Molecule
            ThermoTable + Reaction
            ThermoTable + Thermo
            ThermoTable + Reaction
            ThermoTable + ThermoTable
        """
        #Argument checking:
        try:
            self.checkTypes(other, [Atom, Molecule, Reaction, Thermo, ThermoTable], "other")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__iadd__, err)
        
        try:
            #Atom
            if isinstance(other, Atom):
                self.addAtom(other)
                
            #Molecule
            elif isinstance(other, Molecule):
                self.addMolecule(other)
                
            #Reaction
            elif isinstance(other, Reaction):
                self.addReaction(other)
                
            #Thermo
            elif isinstance(other, Thermo):
                self.addThermo(other)
                
            #ThermoTable
            elif isinstance(other, ThermoTable):
                #Atoms:
                for a in other.atoms:
                    self.addAtom(a)
                
                #Molecule:
                for m in other.molecules:
                    self.addMolecule(m)
                
                #Reactions:
                for r in other.reactions:
                    self.addReaction(r)
                
                #Thermos:
                for t in other.thermos:
                    self.addThermo(t)
        except BaseException as err:
            self.fatalErrorInClass(self.__iadd__, "Failed addition '{} += {}'".format(self.__class__.__name__, other.__class__.__name__), err)
        
        return self
    
    #################################
    #Addition:
    def __add__(self, other):
        """
        Possible additions:
            ThermoTable + Atom
            ThermoTable + Molecule
            ThermoTable + Reaction
            ThermoTable + Thermo
            ThermoTable + Reaction
            ThermoTable + ThermoTable
        """
        #Argument checking:
        try:
            self.checkTypes(other, [Atom, Molecule, Reaction, Thermo, ThermoTable], "other")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__add__, err)
        
        try:
            newTab = ThermoTable(verbose=False)
            newTab += other
        except BaseException as err:
            self.fatalErrorInClass(self.__add__, "Failed addition '{} + {}'".format(self.__class__.__name__, other.__class__.__name__), err)
        
        return newTab
    
    #################################
    def __contains__(self, entry):
        """
        Checks if a Atom, Molecule, Reaction or Thermo is stored in the table.
        """
        #Argument checking:
        try:
            self.checkTypes(entry, [Atom, Molecule, Reaction, Thermo], "entry")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__contains__, err)
            
        if isinstance(entry, Atom):
            groupClass = "atoms"
            
        elif isinstance(entry, Molecule):
            groupClass = "molecules"
        
        elif isinstance(entry, Reaction):
            groupClass = "reactions"
        
        elif isinstance(entry, Thermo):
            groupClass = "thermos"
        
        group = self.__dict__[groupClass]
        return (entry in group)
    
    #########################################################################
    #Add atomic specie to the table:
    def addAtom(self, atom):
        """
        atom:   Atom
        
        Add an atomic specie to the thermodynamic table.
        """
        #Argument checking:
        try:
            self.checkType(atom, Atom, "atom")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(addAtom, err)
        
        try:
            if not(atom in self):
                #Check if present with different properties:
                if atom.name in [a.name for a in self.atoms]:
                    raise ValueError("Error when adding atomic specie '{}' to the table: specie already present in the table but with different properties.".format(atom.name))
                
                else:
                    self.atoms.append(atom.copy())
        except BaseException as err:
            self.fatalErrorInClass(self.addAtom, "Failed adding atom to table", err)
        
        return self
    
    #################################
    #Add a chemical specie to the table:
    def addMolecule(self, molecule):
        """
        molecule:         Molecule
        
        Add a chemical specie to the thermodynamic table. The
        atomic specie that are part of the specie will be 
        automatically added.
        """
        #Argument checking:
        try:
            self.checkType(molecule, Molecule, "molecule")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.addMolecule, err)
        
        try:
            if not(molecule in self):
                #Check if present with different properties:
                if molecule.name in [m.name for m in self.molecules]:
                    raise ValueError("Error when adding chemical specie '{}' to the table: specie already present in the table but with different properties.".format(molecule.name))
                
                else:
                    self.molecules.append(molecule.copy())
                    
                    #Add atomic specie:
                    for atom in molecule:
                        self.addAtom(atom["atom"])
                        
                    #Add default reaction:
                    defaultReaction = Reaction([molecule],[molecule])
                    self.addReaction(defaultReaction)
        except BaseException as err:
            self.fatalErrorInClass(self.addMolecule, "Failed adding molecule to table", err)
        
        return self
    
    #################################
    #Add a thermo props of chemical specie to the table:
    def addThermo(self, thermo):
        """
        thermo:         Thermo
        
        Add thermodynamic properties of a chemical specie
        to the thermodynamic table. The associated chemical 
        specie that will be automatically added.
        """
        #Argument checking:
        try:
            self.checkType(thermo, Thermo, "thermo")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.addThermo, err)
        
        try:
            if not(thermo in self):
                #Check if there was a thermo already associated to this specie:
                if thermo.specie in [t.specie for t in self.thermos]:
                    raise ValueError("A Thermo was already associated to specie '{}' in the thermodynamic table".format(thermo.specie.name))
                
                #Add thermo
                self.thermos.append(thermo.copy())
                
                #Add chem specie:
                self.addMolecule(thermo.specie)
        except BaseException as err:
            self.fatalErrorInClass(self.addThermo, "Failed adding thermophysical data to table", err)
        
        return self
    
    #################################
    #Add reations:
    def addReaction(self, reaction):
        """
        reaction:         Reaction
        
        Add a reaction to the thermodynamic table. The
        chemical specie that are part of the specie will be 
        automatically added.
        """
        #Argument checking:
        try:
            self.checkType(reaction, Reaction, "reaction")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.addReaction, err)
        
        try:
            if not(reaction in self):
                #Add molecules in reactants and products:
                for r in reaction.reactants:
                    self.addMolecule(r["specie"])
                for p in reaction.products:
                    self.addMolecule(p["specie"])
                
                self.reactions.append(reaction)
                
        except BaseException as err:
            self.fatalErrorInClass(self.addReaction, "Failed adding reaction to table", err)
        
        return self
    
    #################################
    def thermoFromSpecie(self, specie):
        """
            specie:     Molecule
        Get the thermodynamic data associated to a specific specie.
        """
        #Type checking:
        try:
            self.checkType(specie, Molecule, "specie")
        except BaseException as err:
            self.__class__.fatalErrorInArgumentChecking(self.thermoFromSpecie, err)
        
        try:
            if not(specie in [t.specie for t in self.thermos]):
                raise ValueError("No Thermo found associated to specie '{}'".format(specie.name))
            index = [t.specie for t in self.thermos].index(specie)
            return self.thermos[index].copy()
        except BaseException as err:
            self.fatalErrorInClass(self.thermoFromSpecie, "Failed retrieving Thermo for specie {}", err)
    
    #################################
    def reactionsFromReactants(self, molecules):
        """
            molecules: list<Molecules>
                List of molecules that can be in reactants
            
            Retrieve all reactions stored in the table that have
            at least one specie in 'molecules' among reactants.
            The reactions are sorted in order from the reaction
            with the most number of specie present to the least.
        """
        try:
            self.checkContainer(molecules, list, Molecule, "molecules")
        except BaseException as err:
            self.__class__.fatalErrorInArgumentChecking(self.reactionsFromReactants, err)
        
        outList = []
        for specie in molecules:
            #Check if specie in table
            self.index(specie)
            
            #Get reactions containing the specie
            reacts = [r for r in self.reactions if specie in r.reactants]
            
            #Merge with outList:
            for r in reacts:
                if not r in outList:
                    outList.append(r.copy())
            
        #Sort:
        numOfSpec = [len([s for s in r.reactants if s["specie"] in molecules]) for r in outList]
        _, index = sorted(numOfSpec)
        
        return outList[index]
