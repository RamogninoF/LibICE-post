#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from ._Geometry import Geometry

from collections.abc import Iterable
import numpy as np
import pandas as pd

from libICEpost.src.base.Functions.typeChecking import checkType, checkArray, checkMap

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class ConstantVolume(Geometry):
    """
    Base class for handling the geometrical parameters of a domain and the evolution
    of its shape (surface, volume, etc.) over time.
    """
    
    _patches:dict[str,float]
    """The list of patches and their areas"""
    
    _volume:float
    """The volume of the domain"""
    
    #########################################################################
    #Properties:
    @property
    def patches(self) -> list[str]:
        """The list of patches"""
        return self._patches
    
    #########################################################################
    def __init__(self, patches:dict[str,float], volume:float):
        """
        Construct from the patch areas and the volume of the domain.
        
        Args:
            patches (dict[str,float]): Dictionary of patch names and their areas [m^2]
            volume (float): The volume of the domain [m^3]
        """
        checkMap(patches, str, float, "patches")
        checkType(volume, float, "volume")
        
        self._patches = patches
        self._volume = volume
        
        #Check if the areas are positive
        if len(patches) == 0:
            raise ValueError("Patches dictionary is empty")
        for name, area in self._patches.items():
            if area <= 0.0:
                raise ValueError(f"Area of patch {name} must be positive")
        
        #Check if the volume is positive
        checkType(volume, float, "Volume")
        if volume <= 0.0:
            raise ValueError("Volume must be positive")
    
    #########################################################################
    def __str__(self):
        STR =  "{:15s} {:15s}\n".format("TypeName", self.TypeName)
        STR += "Patches:\n"
        for name, area in self._patches.items():
            STR += "    {:15s} {:15s}\n".format(name, str(area))
        STR += "{:15s} {:15s}\n".format("Volume", str(self._volume))
        return STR
    
    def __repr__(self):
        return f"{self.__class__.__name__}(patches={self._patches}, volume={self._volume})"
    
    #########################################################################
    def V(self,t:float|Iterable[float]) -> float|np.ndarray:
        """
        Returns the instantaneous volume at time t.

        Args:
            t (float | Iterable[float]): Time

        Returns:
            float|np.ndarray: Domain volume [m^3]
        """
        checkType(t, (float, Iterable), "t")
        if isinstance(t, Iterable):
            checkArray(t, float, "t")
            return np.full_like(np.array(t), self._volume)
        else:
            return self._volume
    
    ###################################
    def A(self,t:float|Iterable[float]) -> float|np.ndarray:
        """
        Returns the chamber area at time t.
        Args:
            t (float | Iterable[float]): Time

        Returns:
            float|np.ndarray: Total surface area [m^2]
        """
        areas = self.areas(t)
        if isinstance(t, Iterable):
            return np.sum(areas.values(), axis=1)
        else:
            return np.sum(areas.values())
    
    ###################################
    def areas(self,t:float|Iterable[float]) -> pd.DataFrame:
        """
        Get pandas.Dataframe with area of all patches at time t.
        
        Args:
            t (float | Iterable[float]): Time in t

        Returns:
            pandas.Dataframe: DataFrame of areas [m^2] at time t. Columns are patch names, while index is the time.
        """
        checkType(t, (float, Iterable), "t")
        if isinstance(t, Iterable):
            checkArray(t, float, "t")
            return pd.DataFrame({name: np.full_like(np.array(t), area) for name, area in self._patches.items()}, index=t)
        else:
            return pd.DataFrame({name: area for name, area in self._patches.items()}, index=[t])
    
    ###################################
    def dVdt(self,t:float|Iterable[float]) -> float|np.ndarray:
        """
        Returns the time derivative of instantaneous in-cylinder volume at time t.
        Args:
            t (float | Iterable[float]): Time

        Returns:
            float|np.ndarray: dV/dt [m^3/[time unit]]
        """
        checkType(t, (float, Iterable), "t")
        if isinstance(t, Iterable):
            checkArray(t, float, "t")
            return np.zeros_like(np.array(t))
        else:
            return 0.0
    
#########################################################################
#Create selection table
Geometry.createRuntimeSelectionTable()