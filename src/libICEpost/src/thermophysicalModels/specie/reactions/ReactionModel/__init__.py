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
    
    Inhert (module)
        Non-reacting mixture
    
    DissociationModel (module)
        Defines classes to handel dissociation of specie in a mixture. Used in the 
        Stoichiometry reaction model to impose dissociation of molecules.
"""

from .ReactionModel import ReactionModel
from .Stoichiometry import Stoichiometry
from .Equilibrium import Equilibrium
from .Inhert import Inhert

from . import DissociationModel