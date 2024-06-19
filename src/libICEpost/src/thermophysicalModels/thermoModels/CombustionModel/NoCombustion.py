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
        {
            reactants (Mixture): The reactants composition
        }
        """
        try:
            #Cast to Dictionary
            cls.checkTypes(dictionary,(dict, Dictionary),"dictionary")
            if isinstance(dictionary, dict):
                dictionary = Dictionary(**dictionary)
                
            #Constructing this class with the specific entries
            out = cls\
                (
                    **dictionary,
                )
            return out
            
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed construction from dictionary", err)
    
    #########################################################################
    def __init__(self, /, *, 
                 reactants:Mixture,
                 **kwargs):
        """
        Construct combustion model from reactants.
        Other keyword arguments passed to base class CombustionModel.
        
        Args:
            reactants (Mixture): The fresh mixture of reactants
        """
        super().__init__(reactants=reactants, **kwargs)
    
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
        return super().update(*args,**kwargs)

#########################################################################
#Add to selection table of Base
CombustionModel.addToRuntimeSelectionTable(NoCombustion)
