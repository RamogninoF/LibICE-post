"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        16/12/25

Function objects to perform additional computations in an EngineModel 
class at each iteration of the processing loop. A function-object should 
be a function taking only the EngineModel as an argument and is called 
at the end of each time loop to perform additional operations (tipically 
to store some variables which are updated at every time-step).
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from typing import Literal
from types import FunctionType

from libICEpost.src.engineModel.EngineModel.EngineModel import EngineModel, get_postfix

from libICEpost.src.base.Functions.typeChecking import checkType

from libICEpost.src.base.BaseClass import BaseClass, abstractmethod
from libICEpost import Dictionary

from libICEpost.src.thermophysicalModels.thermoModels.ThermoModel import ThermoModel

#############################################################################
#                                MAIN CLASSES                               #
#############################################################################

#Base function object class
class FunctionObject(BaseClass):
    """
    Base class for implementing function objects.
    """
    
    #############################################################################
    @abstractmethod
    def __call__(self, model:EngineModel) -> tuple[float,int]:
        """
        A function object must implement a __call__ method taking an EngineModel as input and returning None.
        
        Args:
            model (EngineModel): The input model to apply the FO.
            
        Returns:
            tuple[float,index]: current CA and corresponding index in the database of the engineModel instance.
        """
        self.checkType(model, EngineModel, "model")
        
        #Current time
        CA = model.time.time
        index = model.data['CA'].to_list().index(CA)
        
        return CA, index

#############################################################################
class CodedFunctionObject(FunctionObject):
    """
    A user-defined function object. The used must define the function f(model:EngineModel) 
    that is executed at every call of __call__ method.
    
    The user can refer to some other sub-classes of FunctionObject class for reference.
    """
    
    function:FunctionType
    """The function to execute at every __call__."""
    
    def __init__(self, *, function:FunctionType):
        """
        Construct the function object associated to a zone an a kind of composition fraction.
        
        Args:
            function (FunctionType): The function f(model:engineModel) that is called at every time-step.
            zone (str, optional): The zone for which saving the composition. Defaults to "cylinder".
        """
        checkType(function, FunctionType, "function")
        
        self.function = function
        
    #############################################################################
    @classmethod
    def fromDictionary(cls, dictionary:dict):
        """
        Construct from dictionary.

        Args:
            dictionary (dict): Dictionary containing:
                function (FunctionType): the function to call at every __call__

        Returns:
            CodedFunctionObject: Instance of this class
        """
        dictionary = Dictionary(**dictionary)
        return cls(function=dictionary.lookup("function"))
    
    #############################################################################
    def __call__(self, model:EngineModel):
        """
        Evaluate the function object.

        Args:
            model (EngineModel): Input model
        """
        return self.function(model)

#############################################################################
class ZoneFunctionObject(FunctionObject):
    """
    Function objects constructed for a specific zone. 
    Variables saved for a zone are saved as:
        <var>_<zone>
        
    Where:
        var: The variable to save
        zone: The zone name. By convention, properties of the cylinder zone have no '_<zone>' postfix.
    """
    
    zone:str
    """The zone for which saving the composition"""
    postfix:str
    """The postfix corresponding to the zone"""
    
    #############################################################################
    @classmethod
    @abstractmethod
    def fromDictionary(cls, dictionary:dict) -> Dictionary:
        """
        Construct from dictionary.

        Args:
            dictionary (dict): Dictionary containing:
                zone (str, optional): zone for which saving. Defaults to 'cylinder'.

        Returns:
            Dictionary: Update the dictionary with the zone in case not found.
        """
        dictionary = Dictionary(**dictionary)
        dictionary["zone"] = dictionary.lookupOrDefault("zone", default="cylinder")
        return dictionary
    
    #############################################################################
    def __init__(self, *, zone:str="cylinder"):
        """
        Construct the function object associated to a zone.

        Args:
            zone (str, optional): The zone. Defaults to "cylinder".
        """
        checkType(zone, str, "zone")
        
        self.zone = zone
        self.postfix = get_postfix(zone)
        
    #############################################################################
    @abstractmethod
    def __call__(self, model:EngineModel) -> tuple[float, int, ThermoModel]:
        """Check that zone exists
        
        Returns:
            tuple[float, int, ThermoModel]: current CA and corresponding index in the database of the engineModel instance, and the ThermoModel associated to the zone."""
        if not self.zone in model.Zones:
            raise ValueError(f"Model does not contain zone {self.zone}. Avaliable zones are:\n\t" + "\n\t".join(model.Zones))

        return *super().__call__(model), getattr(model, f"_{self.zone}")  #The zone
        
#############################################################################
class SaveMixtureComposition(ZoneFunctionObject):
    """
    Store the mixture composition in terms of either mole and/or 
    mass fractionsfor a zone at each time-step. Mixture 
    composition is saved as:
        <specie>_<x/y>_<zone>
        
    Where:
        specie: The specie name
        x/y: Wether mole or mass fraction
        zone: The zone name. By convention, properties of the cylinder zone have no '_<zone>' postfix.
        
    Args:
        model (EngineModel): The model to which apply the functionObject.
    """
    fracType:str
    """Which kind of fraction to save"""
    
    #############################################################################
    def __init__(self, *, fracType:Literal["mass", "mole", "both"], **kwargs):
        """
        Construct the function object associated to a zone an a kind of composition fraction.

        Args:
            fracType (Literal[&quot;mass&quot;, &quot;mole&quot;, &quot;both&quot;]): Which kind of fraction to save (mass, mole, or both).
            zone (str, optional): The zone for which saving the composition. Defaults to "cylinder".
        """
        super().__init__(**kwargs)
        checkType(fracType, str, "fracType")
        if not fracType in ["mass", "mole", "both"]: raise ValueError(f"Unknown fracType {fracType}. Avaliable are (mass, mole, both).")
        
        self.fracType = fracType
        
    #############################################################################
    @classmethod
    def fromDictionary(cls, dictionary:dict):
        """
        Construct from dictionary.

        Args:
            dictionary (dict): Dictionary containing:
                zone (str): zone for which saving
                fracType(str): type of composition fraction (mass, mole, both)

        Returns:
            SaveMixtureComposition: Instance of this class
        """
        #Update with zone
        dictionary = super().fromDictionary(dictionary)
        return cls(zone=dictionary.lookup("zone"), fracType=dictionary.lookup("fracType"))
    
    #############################################################################
    def __call__(self, model:EngineModel):
        """
        Evaluate the function object for a model.

        Args:
            model (EngineModel): Input model
        """
        
        #Type checking
        _, index, Z = super().__call__(model)
        
        for specie in Z.mixture.mix:
            if self.fracType in ["mole", "both"]:
                model.data.loc[index, specie.specie.name + "_x" + self.postfix] = specie.X
            if self.fracType in ["mass", "both"]:
                model.data.loc[index, specie.specie.name + "_y" + self.postfix] = specie.Y

#############################################################################
class SaveMixtureProperties(ZoneFunctionObject):
    """
    Store the mixture thermophysical properties for a zone at each time-step as:
        <property>_<zone>
        
    Where:
        property: The property
        zone: The zone name. By convention, properties of the cylinder zone have no '_<zone>' postfix.
        
    Args:
        model (EngineModel): The model to which apply the functionObject.
    """
    cp:bool
    """save cp?"""
    cv:bool
    """save cv?"""
    gamma:bool
    """save gamma?"""
    ha:bool
    """save ha?"""
    ua:bool
    """save ua?"""
    hs:bool
    """save hs?"""
    us:bool
    """save us?"""
    hf:bool
    """save hf?"""
    Z:bool
    """save Z?"""
    MM:bool
    """save MM?"""
    
    #############################################################################
    def __init__(self, *, cp:bool=True, cv:bool=True, gamma:bool=True, MM:bool=False, ha:bool=False, ua:bool=False, hs:bool=False, us:bool=False, hf:bool=False, Z:bool=False, **kwargs):
        """
        Construct the function object associated to a zone an which properties to save.

        Args:
            cp (bool, optional): Save cp?. Defaults to True.
            cv (bool, optional): Save cv?. Defaults to True.
            gamma (bool, optional): Save gamma?. Defaults to True.
            ha (bool, optional): Save ha?. Defaults to False.
            ua (bool, optional): Save ua?. Defaults to False.
            hs (bool, optional): Save hs?. Defaults to False.
            us (bool, optional): Save us?. Defaults to False.
            hf (bool, optional): Save hf?. Defaults to False.
            Z (bool, optional): Save Z?. Defaults to False.
            MM(bool, optional): Save MM?. Defaults to False.
            zone (str, optional): The zone for which saving the properties. Defaults to "cylinder".
        """
        #Type checking
        super().__init__(**kwargs)
        self.checkType(cp, bool, "cp")
        self.checkType(cv, bool, "cv")
        self.checkType(gamma, bool, "gamma")
        self.checkType(ha, bool, "ha")
        self.checkType(ua, bool, "ua")
        self.checkType(hs, bool, "hs")
        self.checkType(us, bool, "us")
        self.checkType(hf, bool, "hf")
        self.checkType(Z, bool, "Z")
        self.checkType(MM, bool, "MM")
        
        self.cp     = cp
        self.cv     = cv
        self.gamma  = gamma
        self.ha     = ha
        self.ua     = ua
        self.hs     = hs
        self.us     = us
        self.hf     = hf
        self.Z     = Z
        self.MM     = MM
        
    #############################################################################
    @classmethod
    def fromDictionary(cls, dictionary:dict):
        """
        Construct from dictionary.

        Args:
            dictionary (dict): Dictionary containing:
                zone (str): zone for which saving
                cp (bool): Save cp?
                cv (bool): Save cv?
                gamma (bool): Save gamma?
                ha (bool): Save ha?
                ua (bool): Save ua?
                hs (bool): Save hs?
                us (bool): Save us?
                hf (bool): Save hf?
                Z (bool): Save Z?
                MM (bool): Save MM?
        Returns:
            SaveMixtureProperties: Instance of this class
        """
        dictionary = Dictionary(**dictionary)
        return cls(**dictionary)
    
    #############################################################################
    def __call__(self, model:EngineModel):
        """
        Evaluate the function object for a model.

        Args:
            model (EngineModel): Input model
        """
        
        #Type checking
        _, index, Z = super().__call__(model)
        
        p = model.data.loc[index, "p" + self.postfix]
        T = model.data.loc[index, "T" + self.postfix]
        
        if self.cp:
            model.data.loc[index, "cp" + self.postfix] = Z.mixture.cp(p,T)
        if self.cv:
            model.data.loc[index, "cv" + self.postfix] = Z.mixture.cv(p,T)
        if self.gamma:
            model.data.loc[index, "gamma" + self.postfix] = Z.mixture.gamma(p,T)
        if self.ha:
            model.data.loc[index, "ha" + self.postfix] = Z.mixture.ha(p,T)
        if self.ua:
            model.data.loc[index, "ua" + self.postfix] = Z.mixture.ua(p,T)
        if self.hf:
            model.data.loc[index, "hf" + self.postfix] = Z.mixture.Thermo.hf()
        if self.Z:
            model.data.loc[index, "Z" + self.postfix] = Z.mixture.EoS.Z()
        if self.hs:
            model.data.loc[index, "hs" + self.postfix] = Z.mixture.hs(p,T)
        if self.us:
            model.data.loc[index, "us" + self.postfix] = Z.mixture.us(p,T)
        if self.MM:
            model.data.loc[index, "MM" + self.postfix] = Z.mixture.mix.MM


#############################################################################
FunctionObject.createRuntimeSelectionTable()
FunctionObject.addToRuntimeSelectionTable(SaveMixtureComposition)
FunctionObject.addToRuntimeSelectionTable(SaveMixtureProperties)
FunctionObject.addToRuntimeSelectionTable(CodedFunctionObject)