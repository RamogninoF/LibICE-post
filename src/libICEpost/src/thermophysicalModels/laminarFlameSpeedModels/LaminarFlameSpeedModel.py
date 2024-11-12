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

from libICEpost.src.base.Utilities import Utilities
from libICEpost.src.base.BaseClass import BaseClass, abstractmethod

import numpy as np

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Laminar flame speed (base class):
class LaminarFlameSpeedModel(BaseClass, Utilities):
    """
    Base class for computation of laminar flame speed.
    """
    #########################################################################
    
    
    #########################################################################
    #Constructor:
    def __init__(self):
        """
        Base (virtual) class: does not support instantiation.
        """
        pass
        
    #########################################################################
    #Cumpute laminar flame speed:
    @abstractmethod
    def Su(self,p:float,T:float,phi:float,EGR:float=None) -> float|np.ndarray:
        """
        Used to compute laminar flame speed in derived class. Here in the base class
        it is used only for argument checking.

        Args:
            p (float): Pressure [Pa].
            T (float): Unburnt gas temperature [K]
            phi (float): Equivalence ratio [-].
            EGR (float, optional): (optional) mass fraction of recirculated exhaust gasses. Defaults to None.

        Returns:
            float|np.ndarray: The computed laminar flame speed [m/s].
        """
        self.checkType(p, float, entryName="p")
        self.checkType(T, float, entryName="T")
        self.checkType(phi, float, entryName="phi")
        if not(EGR is None):
            self.checkType(EGR, float, entryName="EGR")
    
    ##############################
    #Cumpute laminar flame thickness:
    @abstractmethod
    def deltaL(self,p:float,T:float,phi:float,EGR:float=None) -> float|np.ndarray:
        """
        Used to compute laminar flame thickness in derived class. Here in the base class
        it is used only for argument checking.

        Args:
            p (float): Pressure [Pa].
            T (float): Unburnt gas temperature [K]
            phi (float): Equivalence ratio [-].
            EGR (float, optional): (optional) mass fraction of recirculated exhaust gasses. Defaults to None.

        Returns:
            float|np.ndarray: The computed laminar flame thickness [m].
        """
        self.checkType(p, float, entryName="p")
        self.checkType(T, float, entryName="T")
        self.checkType(phi, float, entryName="phi")
        if not(EGR is None):
            self.checkType(EGR, float, entryName="EGR")
        
#############################################################################
LaminarFlameSpeedModel.createRuntimeSelectionTable()
