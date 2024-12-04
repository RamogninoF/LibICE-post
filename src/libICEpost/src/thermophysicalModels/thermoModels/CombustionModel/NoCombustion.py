#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: <N. Surname>       <e-mail>
Last update:        DD/MM/YYYY
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from __future__ import annotations

#load the base class
from .CombustionModel import CombustionModel

#Other imports
from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture
from libICEpost.src.base.dataStructures.Dictionary import Dictionary

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class NoCombustion(CombustionModel):
    """
    No combustion (inhert)
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
    """
    
    #########################################################################
    #Properties:
    
    #########################################################################
    #Class methods and static methods:
    @classmethod
    def fromDictionary(cls, dictionary:dict|Dictionary):
        """
        Create from dictionary.
        
        Args:
            dictionary (dict): The dictionary from which constructing, containing:
                reactants (Mixture): The reactants composition
        """
        cls.checkType(dictionary,dict,"dictionary")
        dictionary = Dictionary(**dictionary)
            
        #Constructing this class with the specific entries
        out = cls\
            (
                **dictionary,
            )
        return out
    
    #########################################################################
    def __init__(self, /, *, reactants:Mixture, **kwargs):
        """
        Construct combustion model from reactants.
        Other keyword arguments passed to base class CombustionModel.
        
        Args:
            reactants (Mixture): The fresh mixture of reactants
        """
        super().__init__(reactants=reactants, reactionModel="Inhert")
    
    #########################################################################
    #Dunder methods:
    
    #########################################################################
    #Methods:
    def update(self,
               *args,
               **kwargs,
               ) -> bool:
        """
        Update mixture composition
        
        Args:
            reactants (Mixture, optional): update reactants composition. Defaults to None.

        Returns:
            bool: if something changed
        """
        update = super().update(*args, **kwargs)
        
        if update:
            self._combustionProducts = self._freshMixture
            self._mixture = self._freshMixture
        
        return update

#########################################################################
#Add to selection table of Base
CombustionModel.addToRuntimeSelectionTable(NoCombustion)
