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
    def __init__(self, reactants, products):
        """
        reactants:  list<Molecule>
            List of molecules in the reactants
        products:   list<Molecule>
            List of molecules in the products
        """
        #Argument checking:
        try:
            self.checkContainer(reactants, list, Molecule, "reactants")
            self.checkContainer(products, list, Molecule, "products")
            
            self._reactants = Mixture(reactants, [1.0/len(reactants)]*len(reactants))
            self._products = Mixture(products, [1.0/len(products)]*len(products))
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        try:
            self.update()
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, "Failed constructing the reaction", err)
    
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
        try:
            if not mix is None:
                self.checkType(mix, Mixture, "Mixture")
        except BaseException as err:
            self.fatalErrorInClass(self.__init__,"Argument checking failed", err)
        
        try:
            self._update(mix)
        except BaseException as err:
            self.fatalErrorInClass(self.update, "Failed balancing the reaction", err)

        return self
    
    #####################################
    @abstractmethod
    def _update(self, mix:Mixture=None):
        """
        Method to update the composition of reactants and products (implementation).
        """
        if not mix is None:
            self._reactants = mix
            # Store current mixture composition. Used to update the class 
            # data in case the mixutre has changed
            self._reactantsOld = self._reactants.copy()
    
#########################################################################
#Create selection table
Reaction.createRuntimeSelectionTable()