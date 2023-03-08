#####################################################################
#                               IMPORT                              #
#####################################################################

from src.base.Utilities import Utilities

from src.thermophysicalModels.specie.specie.Atom import Atom
from src.thermophysicalModels.specie.specie.Molecule import Molecule
from src.thermophysicalModels.specie.reaction.Reaction import Reaction

from src.thermophysicalModels.specie.thermo.Thermo import Thermo

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Table with thermodynamic properties:
class thermoTable(Utilities):
    """
    Class handling a thermodynamic table (data of atomic specie, chemical specie
    and reactions).
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Arguments:
        atoms:          dict<str:Atom>
            Atomic specie
            
        molecules:      dict<str:Molecule>
            Chemical specie
        
        reactions:      dict<str:Reaction>  #TODO
            Reactions
        
        thermo:         dict<str:Thermo>
            Thermodynamic properties of chemical specie
    """
    
    atoms = {}
    molecules = {}
    reactions = {}
    thermos = {}
    
    #########################################################################
    #Constructor:
    def __init__(self, molecules=None, reactions=None, thermos=None, **argv):
        """
        molecules:  list<Molecule>
            List of chemical specie
        reactions:  list<Reaction>
            List of reactions
        thermos:    list<Thermo>
            List of thermodynamic properties to add to the table
        [keyword arguments]
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
        try:
            if not(molecules is None):
                self.__class__.checkInstanceTemplate(molecules, [Molecule.empty()], entryName="molecules")
            if not(reactions is None):
                self.__class__.checkInstanceTemplate(reactions, [Reaction.empty()], entryName="reactions")
            if not(thermos is None):
                self.__class__.checkInstanceTemplate(thermos, [Thermo.empty()], entryName="thermos")
            
            opts = self.__class__.updateKeywordArguments(argv, {"verbose":True})
        except BaseException as err:
            self.fatalErrorInArgumentChecking(__init__, err)
        
        #Initialize lists
        self.atoms = {}
        self.molecules = {}
        self.reactions = {}
        self.thermos = {}
        
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
                self.addThermo(thermos)
        
        if opts["verbose"]:
            print(self)
        
    #########################################################################
    #Operators:
    #Print:
    def __str__(self):
        string = "~~~~~~~~~~~~~~~~~~ THERMOTABLE ~~~~~~~~~~~~~~~~~~\n"
        string += "\n"
        
        hLine = lambda a: (("-"*(len(a)-1)) + "\n")
        
        #Atomic specie:
        template = "| {:10}| {:10}|\n"
        
        string += "ATOMS:\n"
        title = template1.format("", "m [g/mol]")
        
        string += hLine(title)
        string += title
        string += hLine(title)
        
        for atom in self.atoms:
            string += template.format(atom.name, atom.mass)
        
        string +=hLine(title)
        string += "\n"
        
        #Chem specie:
        template = "| {:10}| {:20}| {:10}|\n"
        
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
        template = "| {:20}| {:20}|\n"
        
        string += "REACTIONS:\n"
        title = template.format("Reactants", "Products")
        
        string += hLine(title)
        string += title
        string += hLine(title)
        
        for reaction in self.reactions:
            formula = reaction.formula()
            reactants, products = tuple(formula.split("=>"))
            string += template.format(reactants, products)
        
        string +=hLine(title)
        string += "\n"
        
        #Thermos:
        template = "| {:20}| {:20}|\n"
        
        string += "REACTIONS:\n"
        title = template.format("Reactants", "Products")
        
        string += hLine(title)
        string += title
        string += hLine(title)
        
        for reaction in self.reactions:
            formula = reaction.formula()
            reactants, products = tuple(formula.split("=>"))
            string += template.format(reactants, products)
        
        string +=hLine(title)
        string += "\n"
        
        string += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        
        return string
    
    #################################
    #Inplace addition:
    def __iadd__(self, other):
        """
        Possible additions:
            thermoTable + Atom
            thermoTable + Molecule
            thermoTable + Reaction
            thermoTable + Thermo
            thermoTable + Reaction
            thermoTable + thermoTable
        """
        #Argument checking:
        try:
            self.checkTypes(other, [Atom, Molecule, Reaction, Thermo, thermoTable])
        except BaseException as err:
            self.fatalErrorInArgumentChecking(__iadd__, err)
        
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
        elif isinstance(other Thermo):
            self.addThermo(other)
            
        #ThermoTable
        elif isinstance(other, thermoTable):
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
        
        return self
    
    #################################
    #Addition:
    def __add__(self, other):
        """
        Possible additions:
            thermoTable + Atom
            thermoTable + Molecule
            thermoTable + Reaction
            thermoTable + Thermo
            thermoTable + Reaction
            thermoTable + thermoTable
        """
        #Argument checking:
        try:
            self.checkTypes(other, [Atom, Molecule, Reaction, Thermo, thermoTable])
        except BaseException as err:
            self.fatalErrorInArgumentChecking(__add__, err)
        
        newTab = thermoTable(verbose=False)
        newTab += other
        
        return newTab
    
    #################################
    def __contains__(self, entry):
        """
        Checks if a Atom, Molecule, Reaction or Thermo is stored in the table.
        """
        #Argument checking:
        try:
            self.checkTypes(entry, [Atom, Molecule, Reaction, Thermo], entryName="entry")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(__contains__, err)
            
            if isinstance(entry, Atom):
                groupClass = "atoms"
                
            elif isinstance(entry, Molecule):
                groupClass = "molecules"
            
            elif isinstance(entry, Reaction):
                groupClass = "reactions"
            
            elif isinstance(entry, Thermo):
                groupClass = "thermos"
            
            group = self.__dict__[groupClass]
            return (entry in map(group.__getitem__, list(group.keys())))
    
    #########################################################################
    #Add atomic specie to the table:
    def addAtom(self, atom):
        """
        atom:   Atom
        
        Add an atomic specie to the thermodynamic table.
        """
        #Argument checking:
        try:
            self.__class__.checkTypes(atom, Atom, "atom")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(addAtom, err)
        
        try:
            if not(atom in self):
                #Check if present with different properties:
                if atom.name in self.atoms:
                    raise ValueError("Error when adding atomic specie '{}' to the table: specie already present in the table but with different properties.".format(atom.name))
                
                else:
                    self.atoms[atom.name] = atom.copy()
        except BaseException as err:
            self.fatalErrorIn(__contains__, "Failed adding atom to table", err)
        
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
            self.__class__.checkTypes(molecule, Molecule, "molecule")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(addMolecule, err)
        
        try:
            if not(molecule in self):
                #Check if present with different properties:
                if molecule.name in self.molecules:
                    raise ValueError("Error when adding chemical specie '{}' to the table: specie already present in the table but with different properties.".format(molecule.name))
                
                else:
                    self.molecules[molecule.name] = molecule.copy()
                    
                    #Add atomic specie:
                    for atom in molecule.atoms:
                        self.addAtom(atom)
                        
                    #Add default reaction:
                    self.addDefaultReaction(molecule)
        except BaseException as err:
            self.fatalErrorIn(__contains__, "Failed adding molecule to table", err)
        
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
            self.__class__.checkTypes(thermo, Thermo, "thermo")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(addThermo, err)
        
        try:
            if not(thermo in self):
                #Check if present with different properties:
                if thermo.specie.name in self.thermos:
                    raise ValueError("Error when adding thermodynamic properties of chemical specie '{}' to the table: already present in the table but with different properties.".format(thermo.specie.name))
                
                else:
                    self.thermos[thermo.specie.name] = thermos.copy()
                    
                    #Add chem specie:
                    self.addMolecule(thermo.specie)
        except BaseException as err:
            self.fatalErrorIn(__contains__, "Failed adding thermophysical data to table", err)
        
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
            self.__class__.checkTypes(reaction, Reaction, "thermo")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(addReaction, err)
        
        raise NotImplementedError("Reactions not implemented.")
    
#############################################################################
#                             FRIEND FUNCTIONS                              #
#############################################################################
#Merge a list of tables:
def mergeTables(tables):
    #Argument checking:
    try:
        thermoTable.checkInstanceTemplate([thermoTable.empty()])
    except BaseException as err:
        Utilities.fatalErrorInArgumentChecking(None, mergeTables, err)
    return sum(tables)
