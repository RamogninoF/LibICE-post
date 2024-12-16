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
from libICEpost.src.thermophysicalModels.thermoModels.ThermoState import ThermoState
from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class DissociationModel(BaseClass):
    """
    Defines classes to describe dissociation of some species in a mixture.
    """
    
    _state:ThermoState|None
    """The last thermodynamic state used to update the model"""
    
    #########################################################################
    #Properties:
    @property
    def state(self):
        """The last thermodynamic state used to update the reaction model"""
        return self._state
    
    #########################################################################
    #Constructor:
    def __init__(self, *, state:ThermoState=None):
        """
        Construct from initial state.

        Args:
            state (ThermoState, optional): Thermodynamic state to update the reaction model. Defaults to None.
        """
        self._state = None
        
        self.update(state=state)

    #########################################################################
    #Operators:

    #########################################################################
    def update(self, *, state:ThermoState=None) -> bool:
        """
        Method to update model (interface).

        Args:
            state (ThermoState, optional): Thermodynamic state to update the model.

        Returns:
            bool: if something changed
        """
        if not state is None:
            self.checkType(state, ThermoState, "state")
        
        return self._update(state=state)
    
    #####################################
    @abstractmethod
    def _update(self, *, state:ThermoState=None) -> bool:
        """
        Method to update the model (implementation).
        
        Args:
            state (ThermoState): Thermodynamic state to update the model.
            
        Returns:
            bool: if something changed
        """
        update = False
        
        #Update state variables
        if not state is None:
            self.checkType(state, ThermoState, "state")
            if self._state != state:
                self._state = state.copy()
                update = True
        
        return update
    
    #####################################
    def apply(self, mixture:Mixture, *, inplace:bool=True) -> Mixture|None:
        """
        Apply the dissociation model to the mixture. In-place update the mixture composition. If inplace=False, return the changed mixture.

        VIRTUAL METHOD
        
        Args:
            mixture (Mixture): The mixture to manipulate to impose the dissociation
            inplace (bool, optional): If inplace is True, change mixture and return None, else update mixture compositon. Defaults to True.
        """
        pass
    
#########################################################################
#Create selection table
DissociationModel.createRuntimeSelectionTable()