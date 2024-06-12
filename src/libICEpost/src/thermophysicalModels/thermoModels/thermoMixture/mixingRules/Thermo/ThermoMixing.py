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

from __future__ import annotations

from libICEpost.src.base.BaseClass import BaseClass, abstractmethod

from .....specie.thermo.Thermo import Thermo
from .....specie.specie.Mixture import Mixture

from libICEpost.Database import database

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class ThermoMixing(BaseClass):
    """
    Class handling mixing rule to combine thermodynamic data of specie into a multi-component mixture.
    
    Defines a moethod to generate the thermodynamic data of a mixture of gasses.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        ThermoType: str
            Type of thermodynamic data for which it is implemented
        
        Thermo: EquationOfState
            The thermodynamic data of the mixture

        thermos: _Database
            Link to database of equations of state (database.chemistry.thermo.EquationOfState)

    """

    ThermoType:str
    thermos = database.chemistry.thermo.Thermo
    
    #########################################################################
    #Properties
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
            Thermo.selectionTable().check(self.ThermoType)
            self.update(mix)
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, f"Failed construction of {self.__class__.__name__} class",err)
    #########################################################################
    #Properties:
    @property
    def Thermo(self) -> Thermo:
        """
        The thermodynamic data of the mixture.
        """
        self.update()
        return self._Thermo

    #########################################################################
    def update(self, mix:Mixture=None) -> ThermoMixing:
        """
        Method to update the thermodynamic data based on the mixture composition (interface).
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
        Method to update the thermodynamic data based on the mixture composition (implementation).
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
ThermoMixing.createRuntimeSelectionTable()