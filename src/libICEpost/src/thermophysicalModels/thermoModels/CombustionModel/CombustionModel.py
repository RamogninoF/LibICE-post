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

#Import BaseClass class (interface for base classes)
from libICEpost.src.base.BaseClass import BaseClass, abstractmethod

from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture
from libICEpost.src.thermophysicalModels.specie.reactions.ReactionModel.ReactionModel import ReactionModel

from ..ThermoState import ThermoState

from libICEpost.src.base.dataStructures.Dictionary import Dictionary

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################

class CombustionModel(BaseClass):
    """
    Class handling combustion
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        air:    ThermoMixture
            The thermodynamic mixture of air
        
    """
    _freshMixture:Mixture
    """The mixture of reactants"""
    
    _combustionProducts:Mixture
    """The mixture of combustion products"""
    
    _mixture:Mixture
    """The current mixture"""
    
    _reactionModel:ReactionModel
    """The reaction model"""
    
    #########################################################################
    #Properties:
    
    ################################
    @property
    def freshMixture(self) -> Mixture:
        """
        The current fresh (unburnt) mixture
        
        Returns:
            Mixture
        """
        return self._freshMixture
    
    ################################
    @property
    def combustionProducts(self) -> Mixture:
        """
        The combustion products
        
        Returns:
            Mixture
        """
        return self._combustionProducts
    
    ################################
    @property
    def mixture(self) -> Mixture:
        """
        The mixture at current state
        
        Returns:
            Mixture
        """
        return self._mixture
    
    ################################
    @property
    def reactionModel(self) -> ReactionModel:
        """
        The reaction model

        Returns:
            ReactionModel
        """
        return self._reactionModel
        
    #########################################################################
    #Class methods and static methods:
    
    #########################################################################
    #Constructor
    def __init__(self, /, *,
                 reactants:Mixture,
                 reactionModel:str="Stoichiometry",
                 state:ThermoState=ThermoState(),
                 **kwargs
                 ):
        """
        Initialization of main parameters of combustion model.
        
        Args:
            reactants (Mixture): Air
            reactionModel (str, optional): Model handling reactions. defaults to "Stoichiometry".
            state (ThermoState, optional): Giving current state to manage state-dependend 
                reaction models (e.g. equilibrium). Defaults to empty state ThermoState().
        """

        #Argument checking:
        #Type checking
        self.checkType(reactants, Mixture, "reactants")
        self.checkType(state, [ThermoState, dict], "state")
        
        kwargs = Dictionary(**kwargs)
        
        #To be updated by specific combustion model
        self._mixture = reactants.copy()
        self._freshMixture = reactants.copy()
        self._combustionProducts = reactants.copy()
        
        self._reactionModel = ReactionModel.selector(
            reactionModel, 
            kwargs.lookupOrDefault(reactionModel + "Dict", Dictionary()).update(reactants=self._freshMixture, state=state)
            )
        
        #In child classes need to initialize the state (fresh mixture, combustion products, etc.)
    
    #########################################################################
    #Dunder methods:
    
    #########################################################################
    #Methods:
    @abstractmethod
    def update(self, *, reactants:Mixture=None, state:ThermoState=None, **kwargs) -> bool:
        """
        Update the state of the system. To be overwritten in child classes.
        
        Args:
            reactants (Mixture, optional): update reactants composition. Defaults to None.
            state (ThermoState, optional): the state variables of the system (needed to 
                update the combustion model - e.g. equilibrium)
                
        Returns:
            bool: if something changed
        """
        update = False
        
        #Update reactants
        if not reactants is None:
            self.checkType(reactants, Mixture, "reactants")
            if self._freshMixture != reactants:
                self._freshMixture.update(reactants.species, reactants.Y, fracType="mass")
                update = True
        
        #Update the reaction model
        update = update or self._reactionModel.update(state=state, reactants=reactants)
            
        return update
    
#########################################################################
#Create selection table for the class used for run-time selection of type
CombustionModel.createRuntimeSelectionTable()