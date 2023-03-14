#####################################################################
#                               IMPORT                              #
#####################################################################

from ..specie.Mixture import Mixture
from .ThermoTable import ThermoTable

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Table with thermodynamic properties:
class ThermoMixture(Mixture):
    """
    Class handling a mixture with thermodynamic properties (through a ThermoTable instance).

    Attributes:
        thermo:          ThermoTable
            Thermodynamic table
    """
    
    __doc__ += \
        "\n    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n" + \
        "    Documentation of base classes\n"
    
    __doc__ += "\n    " + Mixture.__name__ + ":\n" + Mixture.__doc__
    
    thermo = ThermoTable()
    
    #########################################################################
    #Constructor:
    def __init__(self, mixture, thermo, **argv):
        """
        
        """
        raise NotImplementedError("Not implemented")
