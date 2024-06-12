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

from dataclasses import dataclass

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#DataClass for thermodynamic state of the system
@dataclass
class ThermoState:
    """
    DataClass storing the thermodynamic state of the system:
        pressure (p) [Pa]
        temperature (T) [T]
        Volume (V) [m^3]
        density (rho) [kg/m^3]
        mass (m) [kg]
    """
    p:float
    T:float
    m:float
    V:float
    rho:float