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
from libICEpost.src.thermophysicalModels.specie.reactions.functions import computeAlphaSt, computeAlpha
from libICEpost.src.base.dataStructures.Dictionary import Dictionary

from ..ThermoState import ThermoState

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class PremixedCombustion(CombustionModel):
    """
    Premixted combustion model
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
    """
    _xb:float
    
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
                xb (float, optional): The initial progress variable. Defaults to 0.0.
                reactionModel (str, optional): Model handling reactions. defaults to "Stoichiometry".
                <reactionModel>Dict (dict, optional): the dictionary for construction of the specific ReactionModel.
                state (ThermoState, optional): Giving current state to manage state-dependend 
                    reaction models(e.g. equilibrium). Defaults to empty state ThermoState().
        """
        #Cast to Dictionary
        cls.checkType(dictionary, dict, "dictionary")
        dictionary = Dictionary(**dictionary)
            
        #Constructing this class with the specific entries
        out = cls\
            (
                **dictionary,
            )
        return out
    
    #########################################################################
    def __init__(self, /, *,
                 xb:float=0.0,
                 **kwargs):
        """
        Construct combustion model from fuel and reactants. 
        Other keyword arguments passed to base class CombustionModel.
        
        Args:
            air (Mixture): The fuel composition
            fuel (Mixture): The fuel composition
        """
        #Argument checking:
        self.checkType(xb, float, "xb")

        #Initialize base class
        super().__init__(**kwargs)
        
        #Initialize unburnt mixture
        self._xb = -1   #Enforce first update
        self.update(xb=xb)
    
    #########################################################################
    #Dunder methods:
    
    #########################################################################
    #Methods:
    def update(self, xb:float=None, *args, **kwargs) -> bool:
        """
        Update mixture composition based on progress variable, fuel, and reactants composition.
        
        Args:
            xb (float, None): the burned mass fraction. Defaults to None (no update).
            reactants (Mixture, optional): update reactants composition. Defaults to None.
            state (ThermoState, optional): Giving current state to manage state-dependend 
                reaction models(e.g. equilibrium). Defaults to None.

        Returns:
            bool: if something changed
        """
        update = False
        
        #Xb
        if not xb is None:
            if xb != self._xb:
                self._xb = min(max(xb, 0.), 1.) #Clamp between 0 and 1
                update = True
            
        #Update the state and air composition
        update = update or super().update(*args, **kwargs)
        
        if update:
            #Update combustion products
            prod = self._reactionModel.products
            self._combustionProducts.update(prod.species, prod.Y, fracType="mass")
            
            #Update current state based on combustion progress variable
            newMix = self.freshMixture.copy()
            newMix.dilute(self.combustionProducts, self._xb, "mass")
            self._mixture.update(newMix.species, newMix.Y, fracType="mass")
            
        return update

#########################################################################
#Add to selection table of Base
CombustionModel.addToRuntimeSelectionTable(PremixedCombustion)
