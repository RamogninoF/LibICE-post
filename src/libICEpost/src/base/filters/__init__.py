"""
@author: F. Ramognino (federico.ramognino@polimi.it)

Module for definition of filter objects, which can be used to pre-process data before the analysis
(resampling, low-pass filtering, etc.). The filters are defined as classes, which can be used to
create filter objects. The filter objects can be used to filter the data throught the __call__(x, y)
method, which returns the filtered (x, y) data.

The filters are defined in the following classes:
    - Filter: base class for the filters
    - Resample: resampling over a regular grid
    - LowPass: low-pass filter (Butterworth)
    - LowPassAndResample: low-pass filter and resampling
    - UserDefinedFilter: user-defined filter (custom function for __call__)
"""

#Load the classes
from ._Filter import Filter
from ._Resample import Resample
from ._LowPass import LowPass
from ._LowPassAndResample import LowPassAndResample
from ._UserDefinedFilter import UserDefinedFilter