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

from ...specie.Mixture import Mixture

from .Reaction import Reaction

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Chemical reaction:
class StoichiometricReaction(Reaction):
    """
    Class handling chemical reactions (transformation of reactants into products) through
    balancing of stoichiometry. Reaction happens infinitely fast with instantaneous
    conversion of reactants into products.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        reactants:  Mixture
            The reactants
            
        products:   Mixture
            The products
    """
    
    #########################################################################
    def __init__(self, reactants, products):
        """
        reactants:  list<Molecule>
            List of molecules in the reactants. The composition is 
            automatically computed based on mass balances of atomic 
            species
        products:   list<Molecule>
            List of molecules in the products. The composition is 
            automatically computed based on mass balances of atomic 
            species
        """
        #Argument checking:
        try:
            super().__init__(reactants, products)
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, "Failed constructing the reaction", err)
    
    #########################################################################
    @classmethod
    def fromDictionary(cls, dictionary):
        """
        Create from dictionary.
        {
            "reactants": list<Molecules>
                The molecules in the reactants
            "products": list<Molecules>
                The molecules in the products
        }
        """
        try:
            entryList = ["reactants", "products"]
            for entry in entryList:
                if not entry in dictionary:
                    raise ValueError(f"Mandatory entry '{entry}' not found in dictionary.")
            
            out = cls\
                (
                    dictionary["reactants"],
                    dictionary["products"]
                )
            return out
        
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed construction from dictionary", err)
    
    #########################################################################
    def __str__(self):
        """
        Print the formula of the reaction (coefficient in mole fractions):
            reactants => products
        """
        string = ""
        for r in self.reactants:
            if (r.X == 1):
                string += r.specie.name
            elif r.X == int(r.X):
                string += str(int(r.X)) + " " + r.specie.name
            else:
                string += "{:.3f}".format(r.X) + " " + r.specie.name
            
            string += " + "
        string = string[:-3]
        
        string += " -> "
        
        for p in self.products:
            if (p.X == 1):
                string += p.specie.name
            elif p.X == int(p.X):
                string += str(int(p.X)) + " " + p.specie.name
            else:
                string += "{:.3f}".format(p.X) + " " + p.specie.name
            
            string += " + "
        string = string[:-3]
        
        return string
    
    ##################################
    def _update(self, mix:Mixture=None):
        """
        mix: Mixture (None)
            The new mixture of reactants (if needs to be changed)
        
        Computes the composition of reactants and products through mass
        balance of each atomic specie.
        
        If system is not solvable, raises ValueError.
        
        If there are molecules that remain inhert across the reaction
        raises a ValueError.
        """
        super()._update(mix)
        
        #Check consistency between reactants and products in terms of atomic specie
        self.checkAtomicSpecie()
        
        #Determine all chemical specie involved in the reaction
        molecules = []
        for specie in self.reactants:
            molecules.append(specie.specie)
        for specie in self.products:
            molecules.append(specie.specie)
        
        #Determine all atomic specie involved in the reaction
        atoms = []
        for specie in molecules:
            for atom in specie:
                if not atom.atom in atoms:
                    atoms.append(atom.atom)
        
        #Build the matrix of coefficients, associated to the balances of each atomic specie
        coeffs = self.np.zeros((len(atoms), len(molecules)))
        
        for specie in self.reactants:
            atomIndices = [atoms.index(a.atom) for a in specie.specie]
            specieIndex = self.reactants.index(specie.specie)
            coeffs[atomIndices,specieIndex] += specie.specie.atomicCompositionMatrix().T
        
        for specie in self.products:
            atomIndices = [atoms.index(a.atom) for a in specie.specie]
            specieIndex = self.products.index(specie.specie) + len(self.reactants)
            coeffs[atomIndices,specieIndex] -= specie.specie.atomicCompositionMatrix().T
        
        #Check if all specie are involved in the reaction:
        for ii, specie in enumerate(molecules):
            if (specie in self.reactants) and (specie in self.products):
                raise ValueError("Some chemical specie are not active in the reaction.")
        
        #Remove empty atom balances:
        for ii, atom in enumerate(atoms):
            if (coeffs[ii,:] == 0).all():
                coeffs = self.np.delete(coeffs, ii, axis=0)
        
        #Solve homogenoeus linear system coeffs*X = 0
        from scipy import linalg
        X = linalg.null_space(coeffs).T
        
        #Reconstruct the map
        indexes = []
        for ii, specie in enumerate(molecules):
            indexes.append(ii)
        
        #Compute reactants and products compositions:
        xGlob = [0.0]*(len(self.reactants)+len(self.products))
        for x in X:
            x *= self.np.sign(x[0])
            for ii, x_ii in enumerate(x):
                xGlob[indexes[ii]] += x_ii
        
        xReact = xGlob[:len(self.reactants)]
        xProd = xGlob[len(self.reactants):]
        
        xReact /= sum(xReact)
        xProd /= sum(xProd)
        
        self._reactants.X = xReact
        self._products.X = xProd

#########################################################################
#Add to selection table
Reaction.addToRuntimeSelectionTable(StoichiometricReaction)

#Load database
import libICEpost.Database.chemistry.reactions.StoichiometricReaction
