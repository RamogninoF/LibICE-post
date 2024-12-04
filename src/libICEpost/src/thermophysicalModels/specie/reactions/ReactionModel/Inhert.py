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

from libICEpost import Dictionary

from .ReactionModel import ReactionModel
from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture
from libICEpost.src.thermophysicalModels.thermoModels.ThermoState import ThermoState

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class Inhert(ReactionModel):
    """
    Inhert mixture (no reactions)
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Attributes:
        reactants:  (Mixture)
            The mixture of the reactants
        
        products:  (Mixture)
            The mixture of products of the reaction
    
    """
    _ReactionType:str = None
    """The type for reactions to lookup for in the database"""
    
    #########################################################################
    @classmethod
    def fromDictionary(cls, dictionary):
        """
        Constuct from dictionary.
        
        Args:
            dictionary (dict): The dictionary from which constructing, containing:
                reactants (Mixture): the mixture of reactants
        """
        cls.checkType(dictionary, dict, "dictionary")
        dictionary = Dictionary(**dictionary)
        out = cls\
            (
                dictionary.lookup("reactants")
            )
        return out
    
    #########################################################################
    #Properties:
    
    #########################################################################
    #Constructor:
    def __init__(self, reactants:Mixture):
        """
        Args:
            reactants (Mixture): the mixture of reactants.
        """
        super().__init__(reactants)
        
        #Point products to reactants
        self._products = self._reactants
        
    #########################################################################
    #Operators:
    
    ################################
    
    #########################################################################
    #Methods:
    def _update(self, reactants:Mixture=None, *, state:ThermoState=None) -> bool:
        """
        Method to update the products.

        Args:
            reactants (Mixture, optional): Update mixture of reactants. Defaults to None.
            state (ThermoState, optional): Thermodynamic state to update the reaction model. (NOT USED)

        Returns:
            bool: if something changed
        """
        #Just update reactants
        return super()._update(reactants)
        
    ################################
    
    
#########################################################################
#Add to selection table
ReactionModel.addToRuntimeSelectionTable(Inhert)