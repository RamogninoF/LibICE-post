"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        25/06/2024

Generic functions useful for internal combustion engines.
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from libICEpost.src.base.Functions.typeChecking import checkType

from functools import lru_cache
from libICEpost.GLOBALS import __CACHE_SIZE__

#############################################################################
#                              MAIN FUNCTIONS                               #
#############################################################################
@lru_cache(__CACHE_SIZE__)
def upMean(*, n:float, S:float) -> float:
    """
    Compute the mean piston speed of a piston engine [m/s].

    Args:
        n (float): Engine speed [rpm]
        S (float): Engine stroke [m]

    Returns:
        float: mean piston speed [m/s]
    """
    checkType(n, float, "n")
    checkType(S, float, "S")
    
    return 2.*n/60.*S