"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        25/06/2024
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from libICEpost.src.engineModel  import EngineGeometry, EngineTime

from libICEpost.src.base.Functions.typeChecking import checkType
from libICEpost.src.base.Functions.runtimeWarning import fatalErrorInFunction

#TODO caching (memoization package handles also unhashable types)

#############################################################################
#                              MAIN FUNCTIONS                               #
#############################################################################
def upMean(*, geometry:EngineGeometry.ConRod.ConRodGeometry, time:EngineTime.EngineTime.EngineTime) -> float:
    """
    Compute the mean piston speed of a piston engine.

    Args:
        geometry (EngineGeometry.ConRod.ConRodGeometry): The engine geometry
        time (EngineTime.EngineTime.EngineTime): The engine time

    Returns:
        float: mean piston speed
    """
    try:
        checkType(geometry, EngineGeometry.ConRod.ConRodGeometry, "geometry")
        checkType(time, EngineTime.EngineTime.EngineTime, "time")
        
        return 2.*time.omega*geometry.S
    except BaseException as err:
        fatalErrorInFunction(upMean, "Failed computing mean piston speed", err)