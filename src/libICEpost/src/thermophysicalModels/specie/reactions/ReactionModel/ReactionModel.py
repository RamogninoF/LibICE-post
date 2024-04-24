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

from ..Reaction.Reaction import Reaction
from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture
from libICEpost.Database import database


#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class ReactionModel(BaseClass):
    """
    Defines classes to handel reaction of mixtures involving multiple simple reactions
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Attributes:
        reactants:  (Mixture)
            The mixture of the reactants
        
        products:  (Mixture)
            The mixture of products of the reaction
            
        reactions:  (_Database)
           Database of oxidation reactions. Reference to database.chemistry.reactions
    
    """
    _ReactionType:str
    
    #########################################################################
    #Properties:
    @property
    def reactants(self):
        return self._reactants
    
    @reactants.setter
    def reactants(self, mix:Mixture):
        self.checkType(mix,Mixture,"mix")
        self.update(mix)

    @property
    def products(self):
        self.update()
        return self._products
        
    @property
    def reactions(self):
        return self._reactions
    
    @property
    def ReactionType(self):
        return self._ReactionType
    
    #########################################################################
    #Constructor:
    def __init__(self, reactants:Mixture):
        """
        reactants: Mixture
            The composition of the reactants
        Construct from reactants
        """
        try:
            self.checkType(reactants, Mixture, "reactants")
            self._reactions = database.chemistry.reactions
            
            self.update(reactants)
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, "Failed construction", err)

    #########################################################################
    #Operators:
    
    ################################
    

    #########################################################################
    def update(self, reactants:Mixture=None):
        """
        Method to update the reactants data based on the mixture composition (interface).
        """
        try:
            if not reactants is None:
                self.checkType(reactants, Mixture, "reactants")
        except BaseException as err:
            self.fatalErrorInClass(self.__init__,"Argument checking failed", err)
        
        self._update(reactants)
        
        return self
    
    #####################################
    @abstractmethod
    def _update(self, reactants:Mixture=None):
        """
        Method to update the reactants based on the mixture composition (implementation).
        """
        if not reactants is None:
            self._reactants = reactants
        
        # Store current mixture composition. Used to update the class 
        # data in case the mixutre has changed
        if not hasattr(self,"_reactantsOld"):
            #First initialization
            self._reactantsOld = self._reactants.copy()
            return False
        else:
            #Updating
            if not (self._reactants == self._reactantsOld):
                #Change detected
                self._reactantsOld = self._reactants
                return False
        
        #Already updated (True)
        return True
    
#########################################################################
#Create selection table
ReactionModel.createRuntimeSelectionTable()