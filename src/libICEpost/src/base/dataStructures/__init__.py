"""
Useful data structures for the libICEpost library.

## Modules

### EngineData
Data structure for engine data. It is a TimeSeries with a specific name for time (CA).
**WARNING**: this class is deprecated and will be removed in future versions to use the
TimeSeries class directly with the specific name for time (CA).

### Tabulation
Module for definition of tabulation objects, which can be used to store data in a tabular format.

### Dictionary
This module provides a Dictionary class with some OpenFOAM-like methods.

### loading
Interface functions to easily load fields into `libICEpost` `TimeSeries` objects.

## Classes and functions
- `TimeSeries` (class): data structure for time series data
- `TimeSeriesWarning` (class): warning for `TimeSeries`
- `loadField` (function): load a field into a `TimeSeries` object

@author: F. Ramognino       <federico.ramognino@polimi.it>
"""

# TimeSeries
from ._TimeSeries import TimeSeries, TimeSeriesWarning
from ._loading import loadField
from . import _loading as loading