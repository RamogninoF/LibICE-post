"""
@author: F. Ramognino       <federico.ramognino@polimi.it>

Useful data structures.

## Content of the package:
    `Tabulation` (`module`): data structure for tabulated data (e.g. from OpenFOAM)
    `EngineData` (`module`): data structure for engine data. It is a `TimeSeries` with a specific name for time (CA).
        **WARNING**: this class is deprecated and will be removed in future versions to use the `TimeSeries` class 
        directly with the specific name for time (CA).
    `Dictionary` (`module`): Ordered dictionary embedding some useful OpenFOAM-like methods
    
    `TimeSeries` (`class`): data structure for time series data
    `TimeSeriesWarning` (`class`): warning for `TimeSeries`
    
"""

# TimeSeries
from ._TimeSeries import TimeSeries, TimeSeriesWarning