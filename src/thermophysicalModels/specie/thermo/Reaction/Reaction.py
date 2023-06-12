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

from src.base.Utilities import Utilities
from src.base.Functions.runtimeWarning import runtimeWarning

from ...specie.Mixture import Mixture
from ...specie.Molecule import Molecule

from operator import attrgetter
import sympy

import json
import Database
from Database import database

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
        
        string += " -> "
        
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
    
    ##############################
    #Representation:
    def __repr__(self):
        R = \
            {
                "name": self.__str__(),
                "reactants": self.reactants,
                "products": self.products
            }
        
        return R.__repr__()
    
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
            
            #Check if all specie are involved in the reaction:
            for ii, specie in enumerate(molecules):
                if (specie in self.reactants) and (specie in self.products) and not(specie in self.inherts):
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
            
            self.reactants = Mixture([s["specie"] for s in self.reactants], list(xReact), "mole")
            self.products = Mixture([s["specie"] for s in self.products], list(xProd), "mole")
            
        except BaseException as err:
            self.fatalErrorIn(self.update, "Failed balancing the reaction", err)
            

#############################################################################
#                                   DATA                                    #
#############################################################################
database["chemistry"]["thermo"]["Reactions"] = {}

fileName = Database.location + "Reactions.json"
try:
    with open(fileName) as f:
        data = json.load(f)
        for react in data:
            database["chemistry"]["thermo"]["Reactions"][react] = \
                Reaction\
                    (
                        [database["chemistry"]["specie"]["Molecules"][mol] for mol in data[react]["reactants"]],
                        [database["chemistry"]["specie"]["Molecules"][mol] for mol in data[react]["products"]]
                    )

    for fuel in database["chemistry"]["specie"]["Fuels"]:
        prod = []
        if database["chemistry"]["specie"]["PeriodicTable"]["N"] in database["chemistry"]["specie"]["Molecules"][fuel].atoms:
            prod.append(database["chemistry"]["specie"]["Molecules"]["N2"])
        if database["chemistry"]["specie"]["PeriodicTable"]["H"] in database["chemistry"]["specie"]["Molecules"][fuel].atoms:
            prod.append(database["chemistry"]["specie"]["Molecules"]["H2O"])
        if database["chemistry"]["specie"]["PeriodicTable"]["C"] in database["chemistry"]["specie"]["Molecules"][fuel].atoms:
            prod.append(database["chemistry"]["specie"]["Molecules"]["CO2"])
        if database["chemistry"]["specie"]["PeriodicTable"]["S"] in database["chemistry"]["specie"]["Molecules"][fuel].atoms:
            prod.append(database["chemistry"]["specie"]["Molecules"]["SO2"])
        
        database["chemistry"]["thermo"]["Reactions"][fuel + "-ox"] = \
            Reaction\
                (
                    [database["chemistry"]["specie"]["Molecules"][fuel], database["chemistry"]["specie"]["Molecules"]["O2"]],
                    prod
                )

except BaseException as err:
    runtimeWarning(f"Failed to load the reactions database '{fileName}':\n{err}.")
