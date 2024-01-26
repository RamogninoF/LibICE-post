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

from ....base.BaseClass import BaseClass

from ..thermoMixture.ThermoMixture import ThermoMixture
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
        EoSType:    str
            TypeName of the equation of state (EquationOfState)
        ThermoType: str
            TypeName of the thermodynamic properties model (Thermo)
    """
    
    #########################################################################
    #Constructor:
    def __init__(self, EoSType : str, ThermoType : str):
        """
        EoSType:    str
            TypeName of the equation of state (EquationOfState)
        ThermoType: str
            TypeName of the thermodynamic properties model (Thermo)

        Construct new instance of thermodynamic model (virtual) with optional thermoTable.
        """
        try:
            EquationOfState.selectionTable().check(EoSType)
            Thermo.selectionTable().check(ThermoType)

        except BaseException as err:
            self.fatalErrorInClass(self.__init__, f"Failed construction of {self.__class__.__name__}<{EoSType},{ThermoType}> class",err)
    
    #########################################################################
    #Operators:
    
    ################################
    
    #########################################################################
        
    ################################
    
    
