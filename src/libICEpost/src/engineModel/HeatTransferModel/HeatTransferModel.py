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

from __future__ import annotations

from typing import Self
from collections.abc import Iterable

from libICEpost.src.engineModel.EngineModel import EngineModel

from libICEpost.src.base.BaseClass import BaseClass, abstractmethod

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Heat transfer model (base class):
class HeatTransferModel(BaseClass):
    """
    Base class for modeling of wall heat transfer.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    """
    
    #########################################################################
    #Class methods:
    @classmethod
    def fromDictionary(cls, dictionary:dict) -> Self:
        """
        Construct from dictionary with heat transfer model parameters (to be overloaded for docstring)

        Returns:
            Self: instance of selected heatTransferModel
        """
        return cls(**dictionary)
    
    #########################################################################
    #Compute heat transfer coefficient:
    @abstractmethod
    def h(self, *, engine:EngineModel.EngineModel, CA:float|Iterable|None=None, **kwargs) -> float:
        """
        Compute wall heat transfer coefficient at walls. To be overwritten.

        Args:
            engine (EngineModel): The engine model from which taking data.
            CA (float | Iterable | None, optional): Time for which computing heat transfer. If None, uses engine.time.time. Defaults to None.

        Returns:
            float: convective wall heat transfer coefficient [W/(m^2 K)]
        """
        pass
    
    ##############################
    #Change coefficients (or some of them):
    def update(self, /, **args) -> None:
        """
        Update coefficients of the model
        """
        for arg in args:
            if arg in self.coeffs:
                self.coeffs[arg] = args[arg]
            else:
                raise ValueError(f"Coefficient '{arg}' not found. Available coefficients of heat transfer model {self.__class__.__name__} are:\n\t" + "\n\t".join(list(self.coeffs.keys)))
        
        
#########################################################################
#Create selection table
HeatTransferModel.createRuntimeSelectionTable()