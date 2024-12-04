"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        01/02/2024

Defines classes to handel reaction of mixtures involving multiple simple reactions

Content of the package:
    ReactionModel (module)
        Base class
        
    Stoichiometry (module)
        Combustion with infinitely fast combustion through balancing of stoichiometry
        
    Equilibrium (module)
        Computation of combustion products based on equilibrium
"""

from .ReactionModel import ReactionModel
from .Stoichiometry import Stoichiometry
from .Equilibrium import Equilibrium
from .Inhert import Inhert