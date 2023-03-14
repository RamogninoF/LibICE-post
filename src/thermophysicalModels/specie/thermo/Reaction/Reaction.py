#####################################################################
#                               IMPORT                              #
#####################################################################

from src.base.Utilities import Utilities

from ...specie.Mixture import Mixture
from ...specie.Molecule import Molecule

from operator import attrgetter
import sympy

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Chemical reaction:
class Reaction(Utilities):
    """
    Class handling chemical reactions (transformation of reactants into products).
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        reactants:  Mixture
            The reactants
        products:   Mixture
            The products
        atoms:      list<Atom>
            List of atomic specie involved in the reaction
    """
    
    reactants = Mixture.empty()
    products = Mixture.empty()
    inherts = []
    
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
            self.__class__.checkContainer(reactants, list, Molecule, "reactants")
            self.__class__.checkContainer(products, list, Molecule, "products")
            
            self.reactants = Mixture(reactants, [1.0/len(reactants)]*len(reactants))
            self.products = Mixture(products, [1.0/len(products)]*len(products))
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        try:
            self.update()
        except BaseException as err:
            self.fatalErrorIn(self.__init__, "Failed constructing the reaction", err)
    
    #########################################################################
    def __str__(self):
        """
        Print the formula of the reaction (coefficient in mole fractions):
            reactants => products
        """
        string = ""
        for r in self.reactants:
            if (r["X"] == 1):
                string += r["specie"].name
            elif r["X"] == int(r["X"]):
                string += str(int(r["X"])) + " " + r["specie"].name
            else:
                string += "{:.3f}".format(r["X"]) + " " + r["specie"].name
            
            string += " + "
        string = string[:-3]
        
        string += " => "
        
        for p in self.products:
            if (p["X"] == 1):
                string += p["specie"].name
            elif p["X"] == int(p["X"]):
                string += str(int(p["X"])) + " " + p["specie"].name
            else:
                string += "{:.3f}".format(p["X"]) + " " + p["specie"].name
            
            string += " + "
        string = string[:-3]
        
        return string
    
    #########################################################################
    def checkAtomicSpecie(self):
        """
        Checks that the atomic composition of the specie are consistent
        """
        atomsR = []
        for r in self.reactants:
            for a in r["specie"]:
                if not a["atom"] in atomsR:
                    atomsR.append(a["atom"].copy())
        
        atomsP = []
        for p in self.products:
            for a in p["specie"]:
                if not a["atom"] in atomsP:
                    atomsP.append(a["atom"].copy())
        
        if not ( sorted(atomsR, key=attrgetter('name')) == sorted(atomsP, key=attrgetter('name')) ):
            raise ValueError("Incompatible atomic compositions of reactants and products.")
        
        return self
    
    ##################################
    def update(self):
        """
        Computes the composition of reactants and products through mass
        balance of each atomic specie.
        
        If system is not solvable, raises ValueError.
        
        If there are molecules that remain inhert across the reaction
        they are removed (indetermined problem) and a warning message
        is printed.
        """
        try:
            #Check consistency between reactants and products in terms of atomic specie
            self.checkAtomicSpecie()
            
            #Determine all chemical specie involved in the reaction
            molecules = []
            for specie in self.reactants:
                molecules.append(specie["specie"])
            for specie in self.products:
                molecules.append(specie["specie"])
            
            #Determine all atomic specie involved in the reaction
            atoms = []
            for specie in molecules:
                for atom in specie:
                    if not atom["atom"] in atoms:
                        atoms.append(atom["atom"])
            
            #Build the matrix of coefficients, associated to the balances of each atomic specie
            coeffs = self.__class__.np.zeros((len(atoms), len(molecules)))
            
            for specie in self.reactants:
                atomIndices = [atoms.index(a["atom"]) for a in specie["specie"]]
                specieIndex = self.reactants.index(specie["specie"])
                coeffs[atomIndices,specieIndex] += specie["specie"].atomicCompositionMatrix().T
            
            for specie in self.products:
                atomIndices = [atoms.index(a["atom"]) for a in specie["specie"]]
                specieIndex = self.products.index(specie["specie"]) + len(self.reactants)
                coeffs[atomIndices,specieIndex] -= specie["specie"].atomicCompositionMatrix().T
            
            #Look for inhert specie, i.e. those present both in reactants and products:
            self.inherts = []
            for ii, specie in enumerate(molecules):
                if (specie in self.reactants) and (specie in self.products) and not(specie in self.inherts):
                    self.inherts.append(specie)
            
            #Remove inhert from matrix:
            indexInhert = []
            for specie in self.inherts:
                index = self.reactants.index(specie)
                indexInhert.append(index)
                index = self.products.index(specie) + len(self.reactants)
                indexInhert.append(index)
            coeffs = self.np.delete(coeffs, indexInhert, axis=1)
            
            #Create the mixture with only the inhert specie, with equal mole fractions. Then dilute the overall mixture with the inhert specie, with 50:50 mole fractions.
            if len(self.inherts) > 0:
                inhertMix = Mixture(self.inherts, [1./len(self.inherts)]*len(self.inherts), "mole")
            else:
                inhertMix = Mixture.empty()
                
            if (coeffs.size > 0):
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
                    if not specie in self.inherts:
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
                
                self.reactants = Mixture([s["specie"] for s in self.reactants], list(xReact), "mole")
                self.products = Mixture([s["specie"] for s in self.products], list(xProd), "mole")
            else:
                self.reactants = Mixture.empty()
                self.products = Mixture.empty()
            
            #Dilute with inhert:
            self.reactants.dilute(inhertMix, 0.5, "mole")
            self.products.dilute(inhertMix, 0.5, "mole")
            
        except BaseException as err:
            self.fatalErrorIn(self.update, "Failed balancing the reaction", err)
            
