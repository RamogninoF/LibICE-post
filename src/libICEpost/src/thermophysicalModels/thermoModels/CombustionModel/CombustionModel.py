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
    _combustionProducts:Mixture
    _mixture:Mixture
    _state:ThermoState
    _reactionModel:ReactionModel
    
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
    
    ################################
    @property
    def state(self) -> ThermoState:
        """
        The current state (read only access)

        Returns:
            ThermoState
        """
        return self._state.copy()
        
    #########################################################################
    #Class methods and static methods:
    
    #########################################################################
    #Constructor
    def __init__(self, /, *,
                 reactants:Mixture,
                 reactionModel:str="Stoichiometry",
                 state:ThermoState|dict[str:type]=ThermoState(),
                 **kwargs
                 ):
        """
        Initialization of main parameters of combustion model.
        
        Args:
            reactants (Mixture): Air
            reactionModel (str, optional): Model handling reactions. defaults to "Stoichiometry".
            state (ThermoState, optional): Giving current state to manage state-dependend 
                combustion models(e.g. equilibrium). Defaults to empty state ThermoState().
        """

        #Argument checking:
        try:
            #Type checking
            self.checkType(reactants, Mixture, "reactants")
            self.checkTypes(state, [ThermoState, dict], "state")
            
            kwargs = Dictionary(**kwargs)
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        try:
            #Initialize the object
            if isinstance(state, dict):
                state = ThermoState(**state)
            self._state = state
            
            #To be updated by specific combustion model
            self._mixture = reactants.copy()
            self._freshMixture = reactants.copy()
            self._combustionProducts = reactants.copy()
            
            self._reactionModel = ReactionModel.selector(
                reactionModel, 
                kwargs.lookupOrDefault(reactionModel + "Dict", Dictionary()).update(reactants=self._freshMixture)
                )
            
            #In child classes need to initialize the state (fresh mixture, combustion products, etc.)
            
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, f"Failed construction of {self.__class__.__name__}", err)
    
    #########################################################################
    #Dunder methods:
    
    #########################################################################
    #Methods:
    @abstractmethod
    def update(self, *, reactants:Mixture=None, state:ThermoState|dict[str:type]=None, **kwargs) -> bool:
        """
        Update the state of the system. To be overwritten in child classes.
        
        Args:
            reactants (Mixture, optional): update reactants composition. Defaults to None.
            state (ThermoState|dict[str:type], optional): the state variables of the system (needed to 
                update the combustion model - e.g. equilibrium)
                
        Returns:
            bool: if something changed
        """
        update = False
        
        #Update reactants
        if not reactants is None:
            self.checkType(reactants, Mixture, "air")
            
            old = self._freshMixture
            self._freshMixture = reactants
            # self._combustionProducts = reactants
            # self._mixture = reactants
            if old != self.freshMixture:
                update = True
            
        #Update state variables
        if not state is None:
            self.checkTypes(state, (dict, ThermoState), "state")
            if isinstance(state, dict):
                state = ThermoState(**state)
            
            oldState = self.state
            self._state = state
            if oldState != self.state:
                update = True
            
        return update
    
#########################################################################
#Create selection table for the class used for run-time selection of type
CombustionModel.createRuntimeSelectionTable()