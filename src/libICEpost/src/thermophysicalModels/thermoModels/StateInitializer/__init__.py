"""
@author: <N. Surname>       <e-mail>
Last update:        DD/MM/YYYY

Classes for initialization of the a ThermoState from given properties

Content of the package:
    StateInitializer (class)
        Base class  for initialization of ThermoState (used for selection)
    
    mpV (class)
        Initialize from (mass,pressure,volume)
    
"""

#Load the classes
from . import StateInitializer
from . import mpV