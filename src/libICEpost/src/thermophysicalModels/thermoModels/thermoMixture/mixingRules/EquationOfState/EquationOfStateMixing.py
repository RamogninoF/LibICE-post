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
    EoSType:str
    thermos = EoS_db
    
    #########################################################################
    #Properties:
    @property
    def EoS(self) -> EquationOfState:
        """
        The equation of state of the mixture.
        """
        #In case mixture has changed, update the class data
        if self.mix != self._mixOld:
            self.update(self.mix)
        return self._EoS
    
    ##############################
    @property
    def mix(self) -> Mixture:
        return self._mix

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
            self.fatalErrorInClass(self.__init__, f"Failed construction of {self.__class__.__name__} class",err)

    #########################################################################
    def update(self, mix:Mixture=None):
        """
        Method to update the equation of state based on the mixture composition (interface).
        """
        try:
            if not mix is None:
                self.checkType(mix, Mixture, "Mixture")
        except BaseException as err:
            self.fatalErrorInClass(self.__init__,"Argument checking failed", err)
        
        self._update(mix)

        return self
    
    #####################################
    @abstractmethod
    def _update(self, mix:Mixture=None):
        """
        Method to update the equation of state based on the mixture composition (implementation).
        """
        if not mix is None:
            self._mix = mix
        
        # Store current mixture composition. Used to update the class 
        # data in case the mixutre has changed
        if not hasattr(self,"_mixOld"):
            #First initialization
            self._mixOld = self._mix.copy()
            return False
        else:
            #Updating
            if not (self._mix == self._mixOld):
                #Change detected
                self._mixOld = self._mix
                return False
        
        #Already updated (True)
        return True

#########################################################################
#Create selection table
EquationOfStateMixing.createRuntimeSelectionTable()