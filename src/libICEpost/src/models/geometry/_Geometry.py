#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
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
class Geometry(BaseClass):
    """
    Base class for handling the geometrical parameters of a domain and the evolution
    of its shape (surface, volume, etc.) over time.
    """
    
    @property
    @abstractmethod
    def patches(self) -> list[str]:
        """The list of patches"""
        return []
    
    #########################################################################
    def __str__(self):
        STR =  "{:15s} {:15s}".format("TypeName", self.TypeName)
        return STR
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"
    
    #########################################################################
    @abstractmethod
    def V(self,t:float|Iterable[float]) -> float|np.ndarray:
        """
        Returns the instantaneous volume at time t.

        Args:
            t (float | Iterable[float]): Time

        Returns:
            float|np.ndarray: Domain volume [m^3]
        """
    
    ###################################
    @abstractmethod
    def A(self,t:float|Iterable[float]) -> float|np.ndarray:
        """
        Returns the chamber area at time t.
        Args:
            t (float | Iterable[float]): Time

        Returns:
            float|np.ndarray: Total surface area [m^2]
        """
    
    ###################################
    @abstractmethod
    def areas(self,t:float|Iterable[float]) -> pd.DataFrame:
        """
        Get pandas.Dataframe with area of all patches at time t.
        
        Args:
            t (float | Iterable[float]): Time in t

        Returns:
            pandas.Dataframe: DataFrame of areas [m^2] at time t. Columns are patch names, while index is the time.
        """
    
    ###################################
    @abstractmethod
    def dVdt(self,CA:float|Iterable[float]) -> float|np.ndarray:
        """
        Returns the time derivative of instantaneous in-cylinder volume at time t.
        Args:
            t (float | Iterable[float]): Time

        Returns:
            float|np.ndarray: dV/dt [m^3/[time unit]]
        """
    
#########################################################################
#Create selection table
Geometry.createRuntimeSelectionTable()