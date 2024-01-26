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

from libICEpost.src.base.Utilities import Utilities

from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture
from ..ThermoTable import ThermoTable
from .MixingRule.MixingRule import MixingRule

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class ThermoMixture(Utilities):
    """
    Base class for computing thermodynamic data of a mixture.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        mix:    Mixture
            The chemical composition of the mixture.

        db:     ThermoTable
            Database of thermodynamic data.
        
        mr: MixingRule
            The mixing rule used for computation of the equation of state of the mixture.
    """
    
    #########################################################################
    #Constructor:
    def __init__(self, mixture, mixingRule, thermoTable):
        """
        thermoTable:    ThermoTable
            Table with thermodynamic data (atomic specie, molecules, reactions, thermos, etc...)
        Construct new instance of thermodynamic model (virtual) with optional thermoTable.
        """
        try:
            self.checkType(thermoTable, ThermoTable, "thermoTable")
            self.checkType(mixture, Mixture, "mixture")
            self.checkType(mixingRule, MixingRule, "mixingRule")

            self.db = thermoTable.copy()
            self.mix = mix.copy()
            self.mr = mixingRule.copy()
                
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, "Failed construction", err)
        
    #########################################################################
    #Operators:
    
    ################################
    
    #########################################################################
    
    
