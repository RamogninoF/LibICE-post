"""
@author: F. Ramognino (federico.ramognino@polimi.it)

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
