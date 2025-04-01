"""
Module for definition of filter objects, which can be used to pre-process data before the analysis
(resampling, low-pass filtering, etc.). The filters are defined as classes, which can be used to
create filter objects. The filter objects can be used to filter the data throught the `__call__(x, y)`
method, which returns the filtered (x, y) data.

Content of the module:
    - `Filter` (class): abstract base class for the filters
    - `Resample` (class): resampling filter
    - `LowPass` (class): low-pass filter (Butterworth)
    - `LowPassAndResample` (class): low-pass filter and resampling
    - `UserDefinedFilter` (class): user-defined filter (custom function for `__call__`)
    - `filter` (function): function to apply the filter to a `libICEpost` `TimeSeries` object
    - `Clone` (class): filter that does nothing (used to clone the data without any modification)

@author: F. Ramognino (federico.ramognino@polimi.it)
"""

#Load the classes
from ._Filter import Filter
from ._Resample import Resample
from ._LowPass import LowPass
from ._LowPassAndResample import LowPassAndResample
from ._UserDefinedFilter import UserDefinedFilter
from ._Clone import Clone

from ._functions import filter