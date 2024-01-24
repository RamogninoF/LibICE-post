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

from abc import ABCMeta, abstractmethod

from src.base.Utilities import Utilities
from src.base.BaseClass import BaseClass

from ....specie.Mixture import Mixture
from .ThermoModel import ThermoModel

# NOTE: Basic requirements to build a thermodynamic model:
#   - Equation of state
#   - Thermodynamic properties model (Thermo)
# 
# TODO: Subclasses to handle combustion:
#   - twoZone (assumption of infinitely-thin reaction zone separating reactants and products)
#   - something for diffusive flames (?)

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class ThermoModel(BaseClass):
    """
    Base class for handling a thermodynamic model
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        db:     ThermoTable
            Database of thermodynamic data
    """
    
    #########################################################################
    #Constructor:
    def __init__(self, thermoTable=None):
        """
        thermoTable:    ThermoTable (None)
            Table with thermodynamic data (atomic specie, molecules, reactions, thermos, etc...)
        Construct new instance of thermodynamic model (virtual) with optional thermoTable.
        """
        try:
            if not thermoTable is None:
                self.checkType(thermoTable, ThermoTable, "thermoTable")
                self.db = thermoTable.copy()
            else:
                self.db = ThermoTable()
                
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, "Failed construction", err)
        
    #########################################################################
    #Operators:
    
    ################################
    
    #########################################################################
    
    
