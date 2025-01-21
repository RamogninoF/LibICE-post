#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from libICEpost.src.base.BaseClass import BaseClass, abstractmethod


from collections.abc import Iterable
import numpy as np
import pandas as pd

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class EngineGeometry(BaseClass):
    """
    Base class for handling engine geometrical parameters during cycle.
    """
    
    @property
    @abstractmethod
    def patches(cls) -> list[str]:
        """The list of patches"""
    
    #########################################################################
    def __str__(self):
        STR =  "{:15s} {:15s}".format("TypeName", self.TypeName)
        return STR
    
    ###################################
    #Instant. chamber volume:
    @abstractmethod
    def V(self,CA:float|Iterable[float]) -> float|np.ndarray:
        """
        Returns the instantaneous in-cylinder volume at CA

        Args:
            CA (float | Iterable[float]): Time in CA

        Returns:
            float|np.ndarray: In-cylinder volume [m^3]
        """
    
    ###################################
    @abstractmethod
    def A(self,CA:float|Iterable[float]) -> float|np.ndarray:
        """
        Returns the chamber area at CA
        Args:
            CA (float | Iterable[float]): Time in CA

        Returns:
            float|np.ndarray: [m^2]
        """
    
    ###################################
    @abstractmethod
    def areas(self,CA:float|Iterable[float]) -> pd.DataFrame:
        """
        Get pandas.Dataframe with area of all patches at CA
        
        Args:
            CA (float | Iterable[float]): Time in CA

        Returns:
            pandas.Dataframe: DataFrame of areas [m^2] at CA. Columns are patch names and CA.
        """
    
    ###################################
    #Time (in CA) derivative of chamber volume:
    @abstractmethod
    def dVdCA(self,CA:float|Iterable[float]) -> float|np.ndarray:
        """
        Returns the time (in CA) derivative of instantaneous in-cylinder volume at CA
        Args:
            CA (float | Iterable[float]): Time in CA

        Returns:
            float|np.ndarray: dV/dCA [m^3/CA]
        """
    
    
#########################################################################
#Create selection table
EngineGeometry.createRuntimeSelectionTable()