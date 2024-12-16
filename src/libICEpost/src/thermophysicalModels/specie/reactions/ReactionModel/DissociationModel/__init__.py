"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        01/02/2024

Defines classes to handel dissociation of specie in a mixture. Used in the Stoichiometry reaction model to impose dissociation of molecules.

Content of the package:
    DissociationModel (module)
        Base class
        
    ConstantDissociationFraction (module)
        Dissociation of a molacule with constant dissociation fraction
"""

from .DissociationModel import DissociationModel
from .ConstantDissociationFraction import ConstantDissociationFraction