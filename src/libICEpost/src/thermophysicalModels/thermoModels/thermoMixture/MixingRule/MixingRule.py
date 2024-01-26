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

from libICEpost.src.base.BaseClass import BaseClass

from ....specie.thermo.EquationOfState import EquationOfState
from ....specie.specie.Molecule import Molecule
from ....specie.specie.Mixture import Mixture

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class MixingRule(BaseClass):
    """
    Class handling mixing rule to combine equation of states of specie into a multi-component mixture
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
    """
    
    #########################################################################
    #Constructor:
    def __init__(self, chem):
        """
            
        Base (virtual) class: does not support instantiation.
        """
        pass
    #########################################################################
    #Operators:

     #########################################################################
