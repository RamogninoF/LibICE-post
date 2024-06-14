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

try:
    from dataclasses import dataclass
    #Test python version
    @dataclass(kw_only=True)
    class __test_Dataclass:
        pass
    del __test_Dataclass
    
except:
    #Python < 3.10
    from pydantic.dataclasses import dataclass

from collections.abc import Mapping

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#DataClass for thermodynamic state of the system
@dataclass(kw_only=True)
class ThermoState(Mapping, Utilities):
    """
    DataClass storing the thermodynamic state of the system:
        pressure (p) [Pa]
        temperature (T) [T]
        Volume (V) [m^3]
        density (rho) [kg/m^3]
        mass (m) [kg]
    """
    p:float = float("nan")
    T:float = float("nan")
    m:float = float("nan")
    V:float = float("nan")
    rho:float = float("nan")
    
    #Allow unpacking with ** operator
    def __len__(self):
        return 5
    
    def __getitem__(self, ii):
        return {"p":self.p,"T":self.T,"m":self.m,"V":self.V,"rho":self.rho}[ii]
    
    def __iter__(self):
        return iter(["p", "T", "m", "V", "rho"])
