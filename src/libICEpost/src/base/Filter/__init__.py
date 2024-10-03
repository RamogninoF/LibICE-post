"""
@author: <N. Surname>       <e-mail>
Last update:        DD/MM/YYYY

Fliters for data pre-processing

Content of the package:
    Filter (class)
        Base class
    
    Resample (class)
        Resampling with constant discretization
        
    LowPass (class)
        Low-pass filter
    
"""

#Load the classes
from .Filter import Filter
from .Resample import Resample
from .LowPass import LowPass
from .LowPassAndResample import LowPassAndResample
from .UserDefinedFilter import UserDefinedFilter