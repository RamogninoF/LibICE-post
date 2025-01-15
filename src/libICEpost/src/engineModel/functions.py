"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        25/06/2024

Generic functions useful for internal combustion engines.
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from __future__ import annotations

from libICEpost.src.base.Functions.typeChecking import checkType

from .EngineModel.EngineModel import EngineModel

from functools import lru_cache
from libICEpost.GLOBALS import __CACHE_SIZE__

from scipy.interpolate import interp1d

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

#############################################################################
def MFB(engine:EngineModel, xb:float) -> float:
    """Compute the CA instant at which the engine
    model reaches a given fuel mass fraction (xb).
    Assuming that the xb array was already computed
    and stored in the engine model.

    Args:
        engine (EngineModel): The engine model
        xb (float): The value of xb to reach [0,1]
    Returns:
        float: CA(xb)
    """
    
    checkType(engine, EngineModel, "engine")
    checkType(xb,float,"xb")
    if not (xb > 0.0) and (xb <= 1.0):
         raise ValueError("xb must be in range [0,1]")
    
    return interp1d(engine.data["xb"], engine.data["CA"])(xb)

#############################################################################