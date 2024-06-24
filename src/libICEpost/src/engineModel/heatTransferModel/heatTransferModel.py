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

from abc import ABCMeta, abstractmethod

from libICEpost.src.base.BaseClass import BaseClass

from ..EngineModel.EngineModel import EngineModel

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
    #Constructor:
    
    #########################################################################
    #Compute heat transfer coefficient:
    @abstractmethod
    def h(self, engine:EngineModel, *, CA:float|None=None) -> float:
        """
        Compute wall heat transfer coefficient at cylinder walls.
        
        Args:
            engine (EngineModel): The engine model from which taking data.
            CA (float | None, optional): Time for which computing heat transfer. If None, uses engine.time.time. Defaults to None.

        Returns:
            float: convective wall heat transfer coefficient
        """
        self.checkType(engine,EngineModel,"engine")
        if not CA is None:
            self.checkType(CA,float,"CA")
    
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