#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        17/10/2023
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from libICEpost.src.base.BaseClass import BaseClass, abstractmethod

from .....specie.thermo.EquationOfState.EquationOfState import EquationOfState
from .....specie.specie.Mixture import Mixture

from libICEpost.Database import database
EoS_db = database.chemistry.thermo.EquationOfState

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class EquationOfStateMixing(BaseClass):
    """
    Class handling mixing rule to combine equation of states of specie into a multi-component mixture.
    
    Defines a moethod to generate the equation of state of a mixture of gasses.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        EoSType: str
            Type of equation of state for which it is implemented
        
        EoS: EquationOfState
            The eqation of state of the mixture

        mix: The mixture

        thermos: _Database
            Link to database of equations of state (database.chemistry.thermo.EquationOfState)

    """

    _EoS:EquationOfState
    _mix:Mixture
    EoSType:str
    thermos = EoS_db
    
    #########################################################################
    #Properties:
    @property
    def EoS(self) -> EquationOfState:
        """
        The equation of state of the mixture.
        """
        self._update()
        return self._EoS
    
    ##############################
    @property
    def mix(self) -> Mixture:
        """The mixture"""
        return self._mix

    ##############################
    @property
    def Rgas(self) -> float:
        """The mass-specific gas constant of the mixture"""
        return self._mix.Rgas

    #########################################################################
    #Constructor:
    def __init__(self, mix:Mixture):
        """
        mix: Mixture
            Mixture to which generate the equation of state.

        Base (virtual) class: does not support instantiation.
        """
        EquationOfState.selectionTable().check(self.EoSType)
        self._mix = mix.copy()
        self.update(mix)

    #########################################################################
    def update(self, mix:Mixture=None) -> bool:
        """
        Method to update the equation of state based on the mixture composition (interface).

        Args:
            mix (Mixture, optional): Change the mixture. Defaults to None.

        Returns:
            bool: If something changed
        """
        return self._update(mix)
    
    #####################################
    @abstractmethod
    def _update(self, mix:Mixture=None) -> bool:
        """
        Method to update the equation of state based on the mixture composition (implementation).
        
        Args:
            mix (Mixture, optional): Change the mixture. Defaults to None.

        Returns:
            bool: If something changed
        """
        if not mix is None:
            if mix != self._mix:
                self._mix.update(mix.species, mix.Y, fracType="mass")
                return True
        
        #Already updated
        return False

#########################################################################
#Create selection table
EquationOfStateMixing.createRuntimeSelectionTable()