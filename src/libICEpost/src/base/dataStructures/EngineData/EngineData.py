#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>

Data structure for engine data. It is a TimeSeries with a specific name for time (CA).

**WARNING**: this class is deprecated and will be removed in future versions to use the
TimeSeries class directly with the specific name for time (CA).
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from libICEpost.src.base.dataStructures._TimeSeries import TimeSeries

class EngineData(TimeSeries):
    """
    Data structure for engine data. It is a `TimeSeries` with a specific name for time (CA).
    
    **WARNING**: this class is deprecated and will be removed in future versions to use the 
    `TimeSeries` class directly with the specific name for time (CA).
    """
    def __init__(self):
        """
        Construct an EngineData object.
        """
        super().__init__("CA")