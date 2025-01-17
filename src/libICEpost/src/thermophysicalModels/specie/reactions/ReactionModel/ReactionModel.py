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

from __future__ import annotations


from libICEpost.src.base.BaseClass import BaseClass, abstractmethod

from ..Reaction.Reaction import Reaction
from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture
from libICEpost.Database import database

from libICEpost.src.thermophysicalModels.thermoModels.ThermoState import ThermoState

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class ReactionModel(BaseClass):
    """
    Defines classes to handel reaction of mixtures involving multiple simple reactions
    
    Attributes:
        reactants (Mixture):    The mixture of the reactants
        products (Mixture):     The mixture of products of the reaction
        reactions (_Database):  Database of oxidation reactions. Reference to database.chemistry.reactions[ReactionType]
    
    """
    _ReactionType:str
    """The type for reactions to lookup for in the database"""
    
    _reactants:Mixture
    """The mixture of reactants"""
    
    _products:Mixture
    """The mixture of products"""
    
    _state:ThermoState|None
    """The last thermodynamic state used to update the reaction model"""
    
    #########################################################################
    #Properties:
    @property
    def reactants(self) -> Mixture:
        """The mixture of reactants"""
        return self._reactants
    
    @reactants.setter
    def reactants(self, mix:Mixture):
        self.checkType(mix,Mixture,"mix")
        self.update(mix)

    @property
    def products(self):
        """The mixture of products"""
        return self._products
        
    @property
    def reactions(self):
        """The database with the avaliabe reactions"""
        return self._reactions[self.ReactionType]
    
    @property
    def ReactionType(self):
        """Name of the reactions used"""
        return self._ReactionType
    
    @property
    def state(self):
        """The last thermodynamic state used to update the reaction model"""
        return self._state
    
    #########################################################################
    #Constructor:
    def __init__(self, reactants:Mixture, *, state:ThermoState=None):
        """
        Construct from reactants and initial state.

        Args:
            reactants (Mixture): The composition of the reactants
            state (ThermoState): Thermodynamic state to update the reaction model.
        """
        self.checkType(reactants, Mixture, "reactants")
        self._reactions = database.chemistry.reactions
        
        self._reactants = Mixture.empty()
        self._products = Mixture.empty()
        
        self._state = None
        
        self.update(reactants=reactants, state=state)

    #########################################################################
    #Operators:

    #########################################################################
    def update(self, reactants:Mixture=None, *, state:ThermoState=None) -> bool:
        """
        Method to update the reactants data based on the mixture composition (interface).

        Args:
            reactants (Mixture, optional): Mixture of reactants if to be changed. Defaults to None.
            state (ThermoState, optional): Thermodynamic state to update the reaction model.

        Returns:
            bool: if something changed
        """
        if not reactants is None:
            self.checkType(reactants, Mixture, "reactants")
        
        if not state is None:
            self.checkType(state, ThermoState, "state")
        
        return self._update(reactants, state=state)
    
    #####################################
    @abstractmethod
    def _update(self, reactants:Mixture=None, *, state:ThermoState=None) -> bool:
        """
        Method to update the reactants based on the mixture composition (implementation).
        
        Args:
            reactants (Mixture, optional): Mixture of reactants if to be changed. Defaults to None.
            state (ThermoState): Thermodynamic state to update the reaction model.
            
        Returns:
            bool: if something changed
        """
        update = False
        
        #Update reactants
        if not reactants is None:
            self.checkType(reactants, Mixture, "reactants")
            if self._reactants != reactants:
                self._reactants.update(reactants.species, reactants.Y, fracType="mass")
                update = True
        
        #Update state variables
        if not state is None:
            self.checkType(state, ThermoState, "state")
            if self._state != state:
                self._state = state.copy()
                update = True
        
        return update
    
#########################################################################
#Create selection table
ReactionModel.createRuntimeSelectionTable()