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

from typing import Iterable

from libICEpost.src.base.BaseClass import BaseClass, abstractmethod

from ...specie.Mixture import Mixture
from ...specie.Molecule import Molecule

from operator import attrgetter

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Chemical reaction:
class Reaction(BaseClass):
    """
    Base class for handling chemical reactions (transformation of reactants into products).
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        reactants:  Mixture
            The reactants
            
        products:   Mixture
            The products
    """
    
    #########################################################################
    @property
    def reactants(self):
        return self._reactants
    
    ################################
    @reactants.setter
    def reactants(self, mix:Mixture):
        self.checkType(mix,Mixture,"mix")
        self.update(mix)
    
    ################################
    @property
    def products(self):
        return self._products
    
    #########################################################################
    def __init__(self, reactants:Iterable[Molecule], products:Iterable[Molecule]):
        """
        Construct from list of moleucles in reactants and products
        
        Args:
            reactants (Iterable[Molecule]): List of molecules in the reactants
            products (Iterable[Molecule]): List of molecules in the products
        """
        #Argument checking:
        self.checkType(reactants, Iterable, "reactants")
        self.checkType(products, Iterable, "products")
        [self.checkType(r, Molecule, f"reactants[{ii}]") for ii, r in enumerate(reactants)]
        [self.checkType(r, Molecule, f"products[{ii}]") for ii, r in enumerate(products)]
        
        self._reactants = Mixture(reactants, [1.0/len(reactants)]*len(reactants))
        self._products = Mixture(products, [1.0/len(products)]*len(products))
        
        self.update()
    
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
            for a in r.specie:
                if not a.atom in atomsR:
                    atomsR.append(a.atom)
        
        atomsP = []
        for p in self.products:
            for a in p.specie:
                if not a.atom in atomsP:
                    atomsP.append(a.atom)
        
        if not ( sorted(atomsR, key=attrgetter('name')) == sorted(atomsP, key=attrgetter('name')) ):
            raise ValueError("Incompatible atomic compositions of reactants and products.")
        
        return self
    
    #########################################################################
    def update(self, mix:Mixture=None):
        """
        Method to update the composition of reactants and products (interface).
        """
        if not mix is None:
            self.checkType(mix, Mixture, "Mixture")
        
        self._update(mix)
        return self
    
    #####################################
    @abstractmethod
    def _update(self, mix:Mixture=None):
        """
        Method to update the composition of reactants and products (implementation).
        """
        if not mix is None:
            if self._reactants != mix:
                self._reactants.update(mix)
    
#########################################################################
#Create selection table
Reaction.createRuntimeSelectionTable()