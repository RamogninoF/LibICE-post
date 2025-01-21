#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: <N. Surname>       <e-mail>
Last update:        DD/MM/YYYY
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from __future__ import annotations

#load the base class
from .EgrModel import EgrModel

from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture
from libICEpost.src.thermophysicalModels.specie.reactions.ReactionModel.Stoichiometry import Stoichiometry
from libICEpost.src.thermophysicalModels.specie.reactions.functions import computeAlphaSt
from libICEpost.src.thermophysicalModels.specie.specie.Mixture import mixtureBlend

from libICEpost.src.base.dataStructures.Dictionary import Dictionary

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class StoichiometricMixtureEGR(EgrModel):
    """
    Egr composition from stoichiometric combustion.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    
    #########################################################################
    #Properties:

    #########################################################################
    #Class methods and static methods:
    @classmethod
    def fromDictionary(cls, dictionary:dict|Dictionary):
        """
        Create from dictionary
        {
            air (Mixture): The air mixture.
            fuel (Mixture): The fuel mixture.
            egr (float): The egr mass fraction.
            combustionEfficiency (float, optional): Combustion efficiency. Defaults to 1.0.
        }
        """
        cls.checkType(dictionary,(dict, Dictionary),"dictionary")
        #Cast to Dictionary
        if isinstance(dictionary, dict):
            dictionary = Dictionary(**dictionary)
        
        return cls(**dictionary)
    
    #########################################################################
    #Constructor
    def __init__(self, /, *, air:Mixture, fuel:Mixture, egr:float, combustionEfficiency=1.0, **kwargs):
        """
        Initialize from egr mass fraction and combustion efficiency

        Args:
            air (Mixture): The air mixture.
            fuel (Mixture): The fuel mixture.
            egr (float): The egr mass fraction.
            combustionEfficiency (float, optional): Combustion efficiency. Defaults to 1.0.
        """

        #Argument checking:
        # Check that the arguments satisfy what is expected from the init method

        #Type checking
        self.checkType(air, Mixture, "air")
        self.checkType(fuel, Mixture, "fuel")
        self.checkType(egr, float, "egr")
        self.checkType(combustionEfficiency, float, "combustionEfficiency")
        
        #Initialize the object
        self._air = air.copy()
        self._fuel = fuel.copy()
        
        self._egr = egr
        self._combustionEfficiency = combustionEfficiency
        
        #Compute stoichiometric combustion products
        alphaSt = computeAlphaSt(air, fuel) #TODO pass oxidizer
        yf = 1./(alphaSt + 1.)
        react = air.copy()
        react.dilute(fuel, yf, "mass")
        prods = Stoichiometry(react).products
        
        #Impose combustion efficiency
        self._egrMixture = prods
        self._egrMixture = mixtureBlend([react, prods], [1. - combustionEfficiency, combustionEfficiency], "mass")
    
    #########################################################################
    #Dunder methods:
    
    #########################################################################
    #Methods:

#########################################################################
#Add to selection table of Base
EgrModel.addToRuntimeSelectionTable(StoichiometricMixtureEGR)
