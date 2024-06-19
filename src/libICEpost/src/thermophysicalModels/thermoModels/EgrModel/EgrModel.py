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

#Import BaseClass class (interface for base classes)
from libICEpost.src.base.BaseClass import BaseClass, abstractmethod

from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################

class EgrModel(BaseClass):
    """
    Class for computation of EGR mixture. Instantiation of this class imposes no EGR.
    
    NOTE: egr mass fraction is referred to the full mixture!
        y_egr = m_egr/(m_egr + m_air + m_fuel)
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        
    """
    
    #########################################################################
    #Properties:
    @property
    def EgrMixture(self) -> Mixture:
        """
        The EGR mixture composition

        Returns:
            Mixture
        """
        return self._egrMixture
    
    ################################
    @property
    def egr(self) -> float:
        """
        The egr mass fraction
        
        Returns:
            float
        """
        return self._egr
    
    #########################################################################
    #Class methods and static methods:
    @classmethod
    def fromDictionary(cls, dictionary:dict):
        """
        Create from dictionary
        {
        }
        """
        try:
            return cls()
            
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed construction from dictionary", err)
    
    #########################################################################
    #Constructor
    def __init__(self, **kwargs):
        """
        No egr to be applied.
        """
        try:
            #Initialize the object
            self._egrMixture = Mixture.empty()
            self._egr = 0.0
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, f"Failed construction of {self.__class__.__name__}", err)
    
    #########################################################################
    #Dunder methods:
    
    #########################################################################
    #Methods:
    
#########################################################################
#Create selection table for the class used for run-time selection of type
EgrModel.createRuntimeSelectionTable()