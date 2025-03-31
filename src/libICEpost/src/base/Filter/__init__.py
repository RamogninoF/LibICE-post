"""
Module for definition of filter objects, which can be used to pre-process data before the analysis
(resampling, low-pass filtering, etc.). The filters are defined as classes, which can be used to
create filter objects. The filter objects can be used to filter the data throught the `__call__(x, y)`
method, which returns the filtered (x, y) data.

**WARNING**: deprecated module. Use libICEpost.src.base.filters instead.
"""

#Load the classes
from . import Filter
from . import Resample
from . import LowPass
from . import LowPassAndResample
from . import UserDefinedFilter

# Deprecated import system
import warnings
warnings.warn("deprecated module libICEpost.src.base.Filter. Use the following instead:\n\tfrom libICEpost.src.base.filters import ...", DeprecationWarning, stacklevel=2)
