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

from ....specie.ThermoMixture import ThermoMixture
from ...specie.thermo.EquationOfState.EquationOfState import EquationOfState
from ...specie.thermo.Thermo.Thermo import Thermo

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

    """
    
    #########################################################################
    #Constructor:
    def __init__(self, EoSType : str, ThermoType : str):
        """
        EoSType:    str
            TypeName of the equation of state
        Construct new instance of thermodynamic model (virtual) with optional thermoTable.
        """
                
        
        
    #########################################################################
    #Operators:
    
    ################################
    
    #########################################################################
    
    
