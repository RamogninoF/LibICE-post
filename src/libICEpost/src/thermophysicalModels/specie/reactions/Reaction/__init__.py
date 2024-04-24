"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        01/02/2024

Classes and packages for handling reactions in gaseous mixtures

Content of the package:
    Reaction (class)
        Defines classes to model reactions
    
    StoichiometricReaction (class)
        Class handling chemical reactions (transformation of 
        reactants into products) through balancing of stoichiometry.
    
"""
from .Reaction import Reaction
from .StoichiometricReaction import StoichiometricReaction

import libICEpost.Database.chemistry.reactions