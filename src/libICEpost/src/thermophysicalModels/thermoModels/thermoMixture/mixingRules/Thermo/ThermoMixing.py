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

from libICEpost.Database import database, _DatabaseClass

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class ThermoMixing(BaseClass):
    """
    Class handling mixing rule to combine thermodynamic data of specie into a multi-component mixture.
    
    Defines a moethod to generate the thermodynamic data of a mixture of gasses.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        ThermoType (str): Type of thermodynamic data for which it is implemented
        Thermo (Thermo): The Thermo of the mixture
        thermos (_DatabaseClass): Link to database of thermodynamic properties (database.chemistry.thermo.Thermo)
        ThermoType: str

    """

    #Type of thermodynamic data for which it is implemented. To 
    # be overriden by derived classes with the proper type (str).
    @staticmethod
    @abstractmethod
    def ThermoType() -> str:
        """The type of thermodynamic data to lookup for in the database"""
    
    thermos:_DatabaseClass = database.chemistry.thermo.Thermo
    """Link to database of thermodynamic data"""
    
    #########################################################################
    #Properties
    @property
    def mix(self) -> Mixture:
        """The mixture composition"""
        return self._mix

    #########################################################################
    #Constructor:
    def __init__(self, mix:Mixture):
        """
        Base (virtual) class: does not support instantiation.
        
        Args:
            mix (Mixture): Mixture to which generate the thermodynamic data.
        """
        Thermo.selectionTable().check(self.ThermoType)
        self._mix = mix.copy()
        self.update(mix)
        
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
ThermoMixing.createRuntimeSelectionTable()