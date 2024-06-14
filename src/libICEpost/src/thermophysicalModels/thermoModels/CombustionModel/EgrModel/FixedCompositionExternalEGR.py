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

from libICEpost.src.base.dataStructures.Dictionary import Dictionary

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class FixedCompositionExternalEGR(EgrModel):
    """
    Imposed external EGR composition.
    
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
            egrComposition (Mixture): The EGR mixture.
            egr (float): The egr mass fraction.
        }
        """
        try:
            cls.checkTypes(dictionary,(dict, Dictionary),"dictionary")
            #Cast to Dictionary
            if isinstance(dictionary, dict):
                dictionary = Dictionary(**dictionary)
            
            return cls(**dictionary)
            
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed construction from dictionary", err)
    
    #########################################################################
    #Constructor
    def __init__(self, *, egrMixture:Mixture, egr:float, **kwargs):
        """
        Initialize from egr mixture and mass fraction.

        Args:
            egrComposition (Mixture): The EGR mixture.
            egr (float): The egr mass fraction.
        """

        #Argument checking:
        try:
            #Type checking
            self.checkType(egr, float, "egr")
            self.checkType(egrMixture, Mixture, "egrMixture")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        try:
            #Initialize the object
            self._egr = egr
            self._egrMixture = egrMixture.copy()
            
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, f"Failed construction of {self.__class__.__name__}", err)
    
    #########################################################################
    #Dunder methods:
    
    #########################################################################
    #Methods:

#########################################################################
#Add to selection table of Base
EgrModel.addToRuntimeSelectionTable(FixedCompositionExternalEGR)
