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
from libICEpost.src.thermophysicalModels.thermoModels.thermoMixture.ThermoMixture import ThermoMixture
from libICEpost.src.thermophysicalModels.specie.reactions.ReactionModel.ReactionModel import ReactionModel

from .EgrModel.EgrModel import EgrModel

from libICEpost.src.base.dataStructures.Dictionary import Dictionary

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################

class CombustionModel(BaseClass):
    """
    Class handling combustion
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        air:    ThermoMixture
            The thermodynamic mixture of air
        
        thermo: Dictionary
            Data for the thermodynamic properteis
        
    """
    _freshMixture:ThermoMixture
    _fuel:ThermoMixture
    _air:ThermoMixture
    _combustionProducts:ThermoMixture
    _mixture:ThermoMixture
    _state:Dictionary
    _appliedEGR:bool
    _reactionModel:ReactionModel
    
    #########################################################################
    #Properties:
    @property
    def air(self) -> ThermoMixture:
        """
        The air mixture
        
        Returns:
            ThermoMixture
        """
        return self._air
    
    ################################
    @property
    def fuel(self) -> ThermoMixture:
        """
        The current fuel mixture
        
        Returns:
            ThermoMixture
        """
        return self._fuel
    
    ################################
    @property
    def freshMixture(self) -> ThermoMixture:
        """
        The current fresh (unburnt) mixture
        
        Returns:
            ThermoMixture
        """
        return self._freshMixture
    
    ################################
    @property
    def combustionProducts(self) -> ThermoMixture:
        """
        The combustion products
        
        Returns:
            ThermoMixture
        """
        return self._combustionProducts
    
    ################################
    @property
    def mixture(self) -> ThermoMixture:
        """
        The mixture at current state
        
        Returns:
            ThermoMixture
        """
        return self._mixture
    
    ################################
    @property
    def thermo(self) -> Dictionary:
        """
        Data for thermodynamic properties of mixtures

        Returns:
            Dictionary
        """
        return self._thermo.copy()
    
    ################################
    @property
    def egrModel(self) -> EgrModel:
        """
        The EGR model

        Returns:
            EgrModel
        """
        return self._EGRModel
    
    ################################
    @property
    def reactionModel(self) -> ReactionModel:
        """
        The reaction model

        Returns:
            ReactionModel
        """
        return self._reactionModel
    
    ################################
    @property
    def state(self) -> Dictionary:
        """
        The current state (read only access)

        Returns:
            Dictionary
        """
        return self._state.copy()
    
    #########################################################################
    #Class methods and static methods:
    
    #########################################################################
    #Constructor
    def __init__(self, /, *,
                 air:Mixture, 
                 thermo:Dictionary, 
                 combustionEfficiency:float=1.0,
                 egrModel:str="EgrModel",
                 reactionModel:str="Stoichiometry",
                 state:dict[str:float]={},
                 **kwargs
                 ):
        """
        Initialization of main parameters of combustion model.
        
        Args:
            air (Mixture): Air
            thermo (Dictionary): Information for thermodynamic properties of mixtures
            egrModel (str, optional): Model for computation of EGR. Defaults to "EgrModel", i.e., no EGR.
            reactionModel (str, optional): Model handling reactions. defaults to "Stoichiometry".
            state (dict[str:float], optional): Giving current state to manage state-dependend 
                combustion models(e.g. equilibrium). Defaults to {}.
        """

        #Argument checking:
        try:
            #Type checking
            self.checkType(air, Mixture, "air")
            self.checkTypes(thermo, [dict, Dictionary], "thermo")
            self.checkType(egrModel, str, "egrModel")
            
            if isinstance(thermo, dict):
                thermo = Dictionary(**thermo)
                
            kwargs = Dictionary(**kwargs)
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        try:
            #Initialize the object
            self._thermo = self.cp.deepcopy(thermo)
            self._air = ThermoMixture(air.copy(), **thermo)
            self._state = Dictionary(**state)
            
            #To be updated by specific combustion model
            self._mixture = ThermoMixture(air.copy(), **thermo)
            self._freshMixture = ThermoMixture(air.copy(), **thermo)
            self._combustionProducts = ThermoMixture(air.copy(), **thermo)
            
            self._EGRModel = EgrModel.selector(egrModel, kwargs.lookupOrDefault(egrModel + "Dict", {}))
            self._reactionModel = ReactionModel.selector(
                reactionModel, 
                kwargs.lookupOrDefault(reactionModel + "Dict", Dictionary()).update(reactants=self._freshMixture.mix)
                )
            
            #In child classes need to initialize the state (fresh mixture, combustion products, etc.)
            
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, f"Failed construction of {self.__class__.__name__}", err)
    
    #########################################################################
    #Dunder methods:
    
    #########################################################################
    #Methods:
    @abstractmethod
    def update(self, **state:dict[str:float]) -> CombustionModel:
        """
        Update the state of the system. To be overwritten in child classes.
        
        Args:
            **state (dict[str:float], optional): the state variables of the system (needed to 
                update the combustion model - e.g. equilibrium)
                
        Returns:
            CombustionModel: self
        """
        if not hasattr(self, "_appliedEGR"):
            #First time
            self._appliedEGR = False
        
        #Apply EGR to fresh mixture
        if not self._appliedEGR:
            fm:Mixture = self._freshMixture.mix
            fm.dilute(self._EGRModel.EgrMixture,self._EGRModel.egr, "mass")
            self._appliedEGR = True
        
        #Update state variables
        self._state.update(**state)
        
        return self
    
#########################################################################
#Create selection table for the class used for run-time selection of type
CombustionModel.createRuntimeSelectionTable()