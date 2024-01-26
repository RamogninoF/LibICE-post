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

from ....specie.thermo.EquationOfState import EquationOfState

from ....specie.specie.Mixture import Mixture

from libICEpost.Database import database

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class MixingRule(BaseClass):
    """
    Class handling mixing rule to combine equation of states of specie into a multi-component mixture.
    
    Defines a moethod to generate the equation of state of a mixture of gasses.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        EoSType: str
            Type of equation of state for which it is implemented
        
        EoS: EquationOfState
            The eqation of state of the mixture

        thermos: _Database
            Link to database of equations of state (database.chemistry.thermo.EquationOfState)

    """

    EoSType:str
    thermos = database.chemistry.thermo.EquationOfState
    
    _EoS = None
    #########################################################################
    #Constructor:
    def __init__(self, mix:Mixture):
        """
        mix: Mixture
            Mixture to which generate the equation of state.

        Base (virtual) class: does not support instantiation.
        """
        try:
            EquationOfState.selectionTable().check(self.EoSType)
            self.update(mix)
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, f"Failed construction of {self.__class__.__name__}<{self.EoSType}> class",err)
    #########################################################################
    #Properties:
    @property
    def EoS(self):
        """
        The equation of state of the mixture.
        """
        if not (self._EoS is None):
            raise ValueError("Equation of state not initialized")
        else: 
            return self._EoS


    #########################################################################
    def update(self, mix:Mixture):
        """
        Method to update the equation of state based on the mixture composition (interface).
        """
        try:
            self.checkType(mix, Mixture, "Mixture")
        except BaseException as err:
            self.fatalErrorInClass(self.__init__,"Argument checking failed", err)
        
        self._update(mix)

        return self
    
    #####################################
    @abstractmethod
    def _update(self, mix:Mixture):
        """
        Method to update the equation of state based on the mixture composition (implementation).
        """
        pass

#########################################################################
#Create selection table
MixingRule.createRuntimeSelectionTable()