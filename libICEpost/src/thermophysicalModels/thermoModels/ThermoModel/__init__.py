"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        31/01/2024

Classes for thermodynamic modeling of a system.

Content of the package
    ThermoModel (class)
        Base class for a thermodynamic model.
        
    TwoZoneModel (class)
        Two zone model with infinitely thin flame separating 
        reactants and products
"""

from .ThermoModel import ThermoModel

# TODO: Subclasses to handle combustion:
#   - twoZone (assumption of infinitely-thin reaction zone separating reactants and products)
#   - something for diffusive flames (?)