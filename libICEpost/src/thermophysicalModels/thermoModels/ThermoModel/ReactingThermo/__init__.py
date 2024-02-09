"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        31/01/2024

Classes for thermodynamic modeling of reacting systems.

Content of the package:
    ReactingThermo (class)
        Base class for reacting thermodynamic systems
    
    SingleZoneModel (class)
        Single zone model with average-mixture properties between reactants and products
"""

from .ReactingThermo import ReactingThermo

# TODO: Subclasses to handle combustion:
#   - oneZone ()
#   - twoZone (assumption of infinitely-thin reaction zone separating reactants and products)
#   - something for diffusive flames (?)