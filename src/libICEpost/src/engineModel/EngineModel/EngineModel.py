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
from types import FunctionType
from operator import attrgetter
import os

import numpy as np

from libICEpost.src.base.BaseClass import BaseClass, abstractmethod
from libICEpost.src.base.dataStructures.EngineData.EngineData import EngineData
from libICEpost.src.base.Filter.Filter import Filter

from libICEpost.src.base.dataStructures.Dictionary import Dictionary

from ..EngineTime.EngineTime import EngineTime
from ..EngineGeometry.EngineGeometry import EngineGeometry

from libICEpost.src.thermophysicalModels.thermoModels.thermoMixture.ThermoMixture import ThermoMixture
from libICEpost.src.thermophysicalModels.thermoModels.ThermoModel import ThermoModel

from libICEpost.src.thermophysicalModels.thermoModels.CombustionModel.CombustionModel import CombustionModel
from libICEpost.src.thermophysicalModels.thermoModels.EgrModel.EgrModel import EgrModel
from libICEpost.src.engineModel.HeatTransferModel.HeatTransferModel import HeatTransferModel

from libICEpost.src.thermophysicalModels.thermoModels.CombustionModel.NoCombustion import NoCombustion
from libICEpost.src.engineModel.HeatTransferModel.Woschni import Woschni

from libICEpost.Database.chemistry.specie.Mixtures import Mixtures, Mixture

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
# TODO:
#   Handle direct injection (injectionModel?)
#   Handle interaction with other zones (creviceModel? prechamberModel?)

# NOTE: to handle diesel combustion, need to compute the phi from the injected mass 
# (probably the main parameter for the combustion model)

# NOTE: This model handles a single-zone model of the cylinder. Sub-classes may be 
# defined to introduce additional zones, like in case of pre-chamber engines, crevice 
# modeling, or maybe gas-exchange analysis (ducts)

class EngineModel(BaseClass):
    """
    Base class for modeling of an engine and processing experimental/numerical data
    
    NOTE:
    For naming of variables:
        -> By default they refer to the "cylinder" zone
        -> Variables referred to a specific zone are allocated as "<variableName>_<zoneName>"
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    TODO: documentation and user info
    
    """
    #Attibutes:
    _cylinder:ThermoModel
    """Cylinder thermodynamic region"""
    
    Types:dict[str:type] = \
        {
            "EngineGeometry":           EngineGeometry,
            "EngineTime":               EngineTime,
            "EgrModel":                 EgrModel,
            "CombustionModel":          CombustionModel,
            "HeatTransferModel":        HeatTransferModel,
        }
    """Types for each main model"""
    
    Submodels:dict[str:type] = \
        {
            "EgrModel":             EgrModel(),
            "CombustionModel":      NoCombustion(reactants=Mixture.empty()),
            "HeatTransferModel":    Woschni(),
        }
    """The available sub-models and their default initializers"""
    
    Zones:list[str] = \
        [
            "cylinder"
        ]
    """The zones avaliable in the model"""
    
    thermophysicalProperties:Dictionary
    """Dictionary with thermophysical properties for mixtures"""
    
    combustionProperties:Dictionary
    """Dictionary with properties for combustion modeling and chemical composition of mixtures"""
    
    CombustionModel:CombustionModel
    """The combustion model"""
    
    EgrModel:EgrModel
    """The EGR model"""
    
    HeatTransferModel:HeatTransferModel
    """The wall heat transfer model"""
    
    _air:Mixture
    """Air mixture"""
    
    info:Dictionary
    """General information for pre-post processing"""
    
    #########################################################################
    # Properties
    @property
    def raw(self)-> EngineData:
        """
        The raw data

        Returns:
            EngineData
        """
        return self._raw
    
    #################################
    @property
    def data(self)-> EngineData:
        """
        The processed/filtered data

        Returns:
            EngineData
        """
        return self._data
    
    #########################################################################
    # Class methods
    @classmethod
    def fromDictionary(cls, dictionary:Dictionary) -> EngineModel:
        """
        Construct from dictionary like:
        {
            EngineTime:         str
                Name of the EngineTime model to use
            <EngineTime>Dict:   dict
                Dictionary containing the data specific of the selected 
                SngineTime model (e.g., if engineTime is 'SparkIgnitionTime',
                then this dictionary must be named 'SparkIgnitionTimeDict'). 
                See at the helper for function 'fromDictionary' of the specific 
                EngineTime model selected.
                
            EngineGeometry:         str
                Name of the EngineGeometry model to use
            <EngineGeometry>Dict:   dict
                Dictionary with data required from engineGeometry.
                See at the helper for function 'fromDictionary' of the specific 
                EngineGeometry model selected.
            
            thermoPhysicalProperties:   dict
                Dictionary with types and data for thermophysical modeling of mixtures
            {
                ThermoType: dict
                {
                    Thermo: str
                    EquationOfState:    str
                }
                <Thermo>Dict: dict
                <EquationOfState>Dict: dict
            }
            
            combustionProperties:   dict
                Dictionaries for data required for mixture preparation and combustion modeling.
            {
                injectionModels: dict
                {
                    TODO
                },
                
                air:    Mixture (default: database.chemistry.specie.Mixtures.dryAir)
                    The air mixture composition
                
                initialMixture: dict
                    Dictionary with data for initialization of the mixture 
                    in the thermodynamic zones
                {
                    <zoneName>:
                    {
                        [depends on specific engine model]
                    }
                },
                
                CombustionModel:         str
                    Name of the CombustionModel to use
                <CombustionModel>Dict:   dict
                    Dictionary with data required from CombustionModel
                    See at the helper for function 'fromDictionary' of the specific 
                    CombustionModel model selected.
            }
            
            dataDict (dictionary): Dictionary with info for loading data, pre-processing and setting initial conditions.
            {
                TODO
            }
        }
        """
        try:
            cls.checkTypes(dictionary, [dict, Dictionary], "dictionary")
            if isinstance(dictionary, dict):
                dictionary = Dictionary(dictionary)
            
            print("Constructing engine model from dictionary\n")
            
            #Engine time:
            print("Construct EngineTime")
            etModel = dictionary.lookup("EngineTime")
            ET = EngineTime.selector(etModel, dictionary.lookup(etModel + "Dict"))
            print(ET,"\n")
            
            #EngineGeometry:
            print("Construct EngineGeometry")
            egModel = dictionary.lookup("EngineGeometry")
            EG = EngineGeometry.selector(egModel, dictionary.lookup(egModel + "Dict"))
            print(EG,"\n")

            #combustionProperties
            combustionProperties = dictionary.lookup("combustionProperties")
            
            #thermophysical properties
            thermophysicalProperties = dictionary.lookup("thermophysicalProperties")
            
            #Data for pre-processing
            dataDict = dictionary.lookup("dataDict")
            
            #Submodels
            subModels = {}
            smDict = dictionary.lookupOrDefault("submodels", Dictionary())
            for sm in cls.Submodels:
                if sm in smDict:
                    print(f"Construct {sm} sub-model")
                    smTypeName = dictionary.lookup(sm)
                    subModels[sm] = cls.Submodels[sm].selector(smTypeName, smDict.lookup(sm + "Dict"))
            
            out = cls(time=ET, geometry=EG, thermophysicalProperties=thermophysicalProperties, combustionProperties=combustionProperties, dataDict=dataDict, **subModels)
            return out
            
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed contruction from dictionary", err)
    
    #########################################################################
    #Constructor:
    def __init__(self, *,
                 time:EngineTime,
                 geometry:EngineGeometry,
                 thermophysicalProperties:dict|Dictionary,
                 combustionProperties:dict|Dictionary,
                 dataDict:dict|Dictionary=None,
                 **submodels,
                 ):
        """
        Base class for engine model, used for type-checking and loading the sub-models.

        Args:
            time (EngineTime): The engine time
            geometry (EngineGeometry): The engine geometry
            thermophysicalProperties (dict|Dictionary): Dictionary with thermophysical properties of mixtures
            combustionProperties (dict|Dictionary): Dictionary with combustion data and chemical composition
            dataDict (dict|Dictionary, optional): Dictionary for loading data. If not given, data are not loaded 
                and thermodynamic regions not initialized. Defaults to None.
            **submodels (dict, optional): Optional sub-models to load. Defaults to {}.
        """
        try:
            #Main models
            self.checkType(geometry, self.Types["EngineGeometry"], "geometry")
            self.checkType(time, self.Types["EngineTime"], "engineTime")
            self.geometry = geometry
            self.time = time
            
            #Data structures
            self._raw = EngineData()     #Raw data
            self._data = EngineData()    #Filtered data
            
            #Submodels
            for model in self.Submodels:
                if model in submodels:
                    #Get from input
                    sm = submodels[model]
                    self.checkType(sm, self.Types[model], f"{submodels}[{model}]")
                else:
                    #Take default
                    sm = self.Submodels[model].copy()
                #Set sub-model
                self.__setattr__(model, sm)
            
            #Thermos
            self.checkType(thermophysicalProperties, dict, "thermophysicalProperties")
            if isinstance(thermophysicalProperties, dict):
                thermophysicalProperties = Dictionary(**thermophysicalProperties)
            self.thermophysicalProperties = thermophysicalProperties.copy()
            
            #Combustion properties
            self.checkType(combustionProperties, dict, "combustionProperties")
            if isinstance(combustionProperties, dict):
                combustionProperties = Dictionary(**combustionProperties)
            self.combustionProperties = combustionProperties.copy()
            
            #Contruct the thermodynamic models
            self._constructThemodynamicModels(combustionProperties)
            
            #TODO: construct injection models
            
            #Construct the Egr model
            self._constructEgrModel(combustionProperties)
            
            #Construct the combustion model
            self._constructCombustionModel(combustionProperties)
            
            #Misc parameters
            self.info = Dictionary()
            self.info["path"] = None
            self.info["dataDict"] = None
            self.info["filter"] = None
            self.info["initialConditions"] = None
            
            #Pre-processing
            if not dataDict is None:
                self.preProcess(**dataDict)
            
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, f"Failed constructing instance of class {self.__class__.__name__}", err)
    
    #########################################################################
    #Construction methods:
    def _constructThemodynamicModels(self, combustionProperties:dict|Dictionary) -> EngineModel:
        """
        Construct the thermodynamic models of the system, setting their initial 
        mixture composition. Here setting everything to air, might be overwritten
        in sub-classes to handle specific initializations (SI engine will use 
        the premixedFuel entry)
        
        Args:
            combustionProperties (dict|Dictionary): the combustion properties
        
        Returns:
            EngineModel: self
        """
        self.checkType(combustionProperties, dict, "combustionProperties")
        if not isinstance(combustionProperties, Dictionary):
            combustionProperties = Dictionary(**combustionProperties)
            
        #Air composition
        air = combustionProperties.lookupOrDefault("air", Mixtures.dryAir)
        self._air = air.copy()
        
        #Here set everything to air, in sub-classes update
        for zone in self.Zones:
            self.__setattr__("_" + zone, ThermoModel(ThermoMixture(self._air.copy(), **self.thermophysicalProperties)))
        return self
    
    ####################################
    def _constructEgrModel(self, combustionProperties:dict|Dictionary):
        """
        Construct the EGR model and apply it to the cylinder region.
        Might be overwritten in child for applying EGR also to sub-regions of cylinder.
        
        Args:
            combustionProperties (dict|Dictionary): the combustion properties
        
        Returns:
            EngineModel: self
        """
        print("Constructing EGR model")
        
        self.checkType(combustionProperties, dict, "combustionProperties")
        if not isinstance(combustionProperties, Dictionary):
            combustionProperties = Dictionary(**combustionProperties)
        
        if "EgrModel" in combustionProperties:
            #Construct egr model from combustion properties
            egrModelType:str = combustionProperties.lookup("EgrModel")
            egrModelDict = combustionProperties.lookupOrDefault(egrModelType + "Dict", Dictionary())
            egrModelDict.update(reactants=self._cylinder.mixture.mix) #Append to dictionary the cylinder properties
        else:
            #Use default
            self.EgrModel = self.Submodels["EgrModel"].copy().update(reactants=self._cylinder.mixture.mix)
        
        #NOTE: When introducing the injection models, need to compute EVO composition instead
        
        #Construct the EGR model
        self.EgrModel = EgrModel.selector(egrModelType, egrModelDict)
        
        print(f"\tType: {self.EgrModel.__class__.__name__}")
        
        #Apply EGR to reactants
        self._cylinder.mixture.mix.dilute(self.EgrModel.EgrMixture, self.EgrModel.egr)
    
    ####################################
    def _constructCombustionModel(self, combustionProperties:dict|Dictionary):
        """
        Construct the combustion model.
        Might be overwritten in child to set additional parameters to combustionModelDict 
        (fuel for PremixedCombustion model is updated in SparkIgnitionEngine)
        
        Args:
            combustionProperties (dict|Dictionary): the combustion properties
        
        Returns:
            EngineModel: self
        """
        print("Constructing combustion model")
        
        self.checkType(combustionProperties, dict, "combustionProperties")
        if not isinstance(combustionProperties, Dictionary):
            combustionProperties = Dictionary(**combustionProperties)
        
        combustionModelType = combustionProperties.lookupOrDefault("CombustionModel", None, fatal=False)
        if not combustionModelType is None:
            #Get dictionary
            combustionModelDict = combustionProperties.lookupOrDefault(combustionModelType + "Dict", Dictionary())
            combustionModelDict.update( #Append reactants to combustion model dictionary
                reactants=self._cylinder.mixture.mix    #Initial in-cylinder mixture
            )
            
            #Construct
            self.CombustionModel = CombustionModel.selector(combustionModelType, combustionModelDict)
        else:
            #Use default
            self.CombustionModel = self.Submodels["CombustionModel"].copy().update(reactants=self._cylinder.mixture.mix)
        
        print(f"\tType: {self.CombustionModel.__class__.__name__}")
        
        #Check consistency
        if not isinstance(self.CombustionModel, self.Types["CombustionModel"]):
            raise TypeError(f"Combustion model type {combustionModelType} in combustionProperties dictionaries not compatible with allowed type for engine model {self.__class__.__name__} ({self.Types['CombustionModel']})")
        
    #########################################################################
    #Updating methods:
    def _updateMixtures(self) -> None:
        """
        Update mixture compositions (might be overwritten in child classes)
        """
        #TODO: Update the in-cylinder mixture based on injection models (may have already injected some mass)
        
        #Update the combustion model at current time
        self._updateCombustionModel()
        
        #Update in-cylinder mixture based on combustion model current mixture
        self._cylinder.mixture.update(self.CombustionModel.mixture)
        
    ####################################
    def _updateCombustionModel(self):
        """
        Update combustion model
        """
        #TODO: Update the reactants mixture based on injection models (may have already injected some mass)
        
        index = self.data.data.index[self.data['CA'] == self.time.time].tolist()[0]
        data = self.data.data.loc()[index].to_dict()
        self.CombustionModel.update(**data) #NOTE: update also fuel when implementing injection models
    
    #########################################################################
    #Dunder methods:
    def __str__(self):
        STR = ""
        STR += "Engine model instance:\n"
        STR += "Engine time\n\t" + self.time.__str__().replace("\n", "\n\t")
        STR += "\n"
        STR += "Engine geometry:\n\t" + self.geometry.__str__().replace("\n", "\n\t")
        STR += "\n"
        STR += "EGR model:\n\t" + self.EgrModel.__str__().replace("\n", "\n\t")
        STR += "\n"
        STR += "Combustion model:\n\t" + self.CombustionModel.__str__().replace("\n", "\n\t")
        return STR
        
    #########################################################################
    #Pre-processing methods:
    def _loadFile(self,*args,**argv) -> EngineModel:
        """
        Loads a file with raw data to self.raw. See EngineData.loadFile 
        documentation for arguments:
        """
        self.raw.loadFile(*args,**argv)
        return self
    
    ####################################
    def _loadArray(self,*args,**argv):
        """
        Loads an array with raw data to self.raw. See EngineData.loadArray 
        documentation for arguments:
        """
        self._raw.loadArray(*args,**argv)
        return self
    
    ####################################
    def loadData(self, dataPath:str=None, *, data:dict|Dictionary) -> EngineModel:
        """
        Load raw data.
        
        TODO: Info
        
        Args:
            data (dict | Dictionary): Dictionary containing the data to load for each region.
            dataPath (str, optional): Global path where to load/write data. Defaults to None.

        Returns:
            EngineModel: self
        """
        print("Loading data")
        print(f"Data path: {dataPath}")
        
        #Seth path info
        self.info["dataPath"] = dataPath
        
        #Cast to Dictionary
        data = Dictionary(**data)
        self.info["data"] = data
        
        #Load data:
        for zone in self.Zones:
            zoneDict = data.lookup(zone)
            
            #Check that pressure is found (mandatory)
            if (not "p" in zoneDict) and (not "p" in self.raw.columns):
                raise ValueError(f"Mandatory entry 'p' in data dictionary for zone {zone} not found. Pressure trace must be loaded for each thermodynamic region.")
            
            #Loop over data to be loaded:
            for entry in zoneDict:
                dataDict = zoneDict.lookup(entry)
                self.checkType(dataDict, Dictionary, f"{zone}[{entry}]")
                
                #If the region is not cylinder, append its name to the field
                entryName:str = entry + (f"_{zone}" if zone != "cylinder" else "")
                currData:Dictionary = dataDict.lookup("data")
                opts:Dictionary = currData.lookupOrDefault("opts", Dictionary())
                
                #Get format
                dataFormat:str = dataDict.lookup("format")
                if (dataFormat == "file"):
                    #File
                    fileName = currData.lookup("fileName")
                    
                    #relative to dataPath if given
                    fileName = (dataPath + os.path.sep if dataPath else "") + fileName
                    
                    #Load
                    self._loadFile(fileName, entryName, **opts)
                    
                elif (dataFormat == "array"):
                    #(CA,val) array
                    dataArray = currData.lookup("array")
                    self._loadArray(dataArray, entryName, **opts)
                
                elif (dataFormat == "function"):
                    #Function f(CA)
                    function:FunctionType = currData.lookup("function")
                    self.checkType(function, FunctionType, f"{zone}[{entry}][function]")
                    
                    CA = self.raw["CA"]
                    f = CA.apply(function)
                    
                    self._loadArray(np.array((CA,f)).T, entryName, **opts)
                    
                elif (dataFormat == "uniform"):
                    #Uniform value
                    value:float = currData.lookup("value")
                    self.checkType(value, float, f"{zone}[{entry}][value]")
                    self.raw[entryName] = value
                
                elif (dataFormat == "calc"):
                    #Apply operation between alredy loaded data
                    function:FunctionType = currData.lookup("function")
                    self.checkType(function, FunctionType, f"{zone}[{entry}][function]")
                    
                    #Function arguments
                    argNames:list[str] = function.__code__.co_varnames
                    
                    #Check if are present:
                    for arg in argNames:
                        if not arg in self.raw.columns:
                            raise ValueError(f"Field '{arg}' was not loaded.")
                    
                    #Extract corresponding columns from data-frame:
                    cols = {c:self.raw[c] for c in argNames}
                    
                    CA = self.raw["CA"]
                    f = function(**cols)
                    
                    self._loadArray(np.array((CA,f)).T, entryName, **opts)
                
                else:
                    raise ValueError(f"Unknown data format '{dataFormat}' for entry {zone}[{entry}]")
                    
        return self
    
    ####################################
    def filterData(self, filter:"Filter|FunctionType|None"=None) -> EngineModel:
        """
        filter: Filter|FunctionType|None (optional)
            Filter to apply to raw data (e.g. resampling, low-pass filter, etc.). Required
            a method __call__(xp, yp)->(x,y) that resamples the dataset (xp,yp) to the
            datapoints (x,y).
        
        Filter the data in self.raw. Save the corresponding 
        filtered data to self.data.
        If filter is None, data are cloned from self.raw
        """
        try:
            #Save filter
            self.info["filter"] = filter
            
            #Clone if no filter is given
            if filter is None:
                for field in self._raw.columns:
                    self._data.loadArray(np.array((self._raw.data["CA"],self._raw.data[field])).T, field)
                return self
            
            #Apply filter
            print(f"Applying filter {filter if isinstance(filter,Filter) else filter.__name__}")
            for var in self._raw.columns:
                #Filter data
                if var != "CA":
                    self._data.loadArray(np.array(filter(self._raw.data["CA"], self._raw.data[var])).T, var)
            
        except BaseException as err:
            self.fatalErrorInClass(self.filterData, f"Failed filtering data", err)
        
        return self
    
    ####################################
    def initializeThemodynamicModels(self, **initialConditions) -> EngineModel:
        """
        Set the initial conditions of all thermodynamic regions of the EngineModel.
        For region to be initialized, a dict is given for the inital conditions,
        according to the following convention:
        
        ->  If a float is given, the value is used
        ->  If a str is given, it refers to the name of the vabiables stored in the EngineModel,
            in which case the corresponding initial condition is sampled from the the corresponding
            data-set at self.time.startTime.
        ->  If string starting with @ is given, it applies that method with input (self.time.startTime)

        Ex:
        {
            "pressure": "p",            #This interpolates self.data.p at self.time.startTime
            "mass": 1.2e-3,             #Value
            "volume": "@geometry.V"     #Evaluates self.geometry.V(self.time.startTime)
        }
        
        Args:
            **initialConditions:  data initialization of each zone in the model.
        """
        try:
            #Update start-time of engine time so that it is bounded to first avaliable time-step
            
            if not "CA" in self.data.columns:
                raise ValueError("No data loaded yet.")
            
            #Set start-time
            self.time.updateStartTime(self.data["CA"])
            self.info["time"] = self.time.time
            
            #Update the mixtures at start-time (combustion models, injection models, etc.)
            self._updateMixtures()
            
            initialConditions = Dictionary(**initialConditions)
            #Store initial conditions
            self.info["initialConditions"] = initialConditions
            
            for zone in self.Zones:
                zoneDict = initialConditions.lookup(zone)
                self.checkType(zoneDict, dict, "zoneDict")
                
                attrgetter("_" + zone)(self).initializeState(**self._preprocessThermoModelInput(zoneDict, zone=zone))

        except BaseException as err:
            self.fatalErrorInClass(self.filterData, f"Failed initializing thermodynamic regions", err)
        
        return self
    
    ####################################
    def _preprocessThermoModelInput(self, inputDict:dict, zone:str) -> dict:
        """
        Auxiliary function to pre-process input dictionary 
        to initialization of a thermodynamic region

        NOTE:
            Might be overwritten in child class to also initialize 
            the mixture composition, for example based on the combustion model.
            In such case, do so:
                def _preprocessThermoModelInput(self, inputDict:dict, zone:str) -> dict:
                    tempDict = super()._preprocessThermoModelInput(inputDict, zone)
                    
                    ... #Manipulate mixture based on output dictionary
                    
                    nameList = ["mass", "temperature", "pressure", "volume", "density"]
                    outputDict = {v:[tempDict[v]] for v in tempDict if v in nameList}   #Set state variables
                    outputDict["mixture"] = mix #Set mixture
                    
                    return outputDict
                    
        
        Args:
            inputDict (dict): dictionary for thermodynamic inputs
            zone (str): the zone name
        
        Returns:
            dict: processed dictionary
        """
        #TODO error handling
        
        outputDict = {}
        for key in inputDict:
            val = inputDict[key]
            
            if isinstance(val,float):
                #Float -> use value
                outputDict[key] = val
            elif isinstance(val,str):
                #str
                startTime:float = self.time.startTime
                
                if val.startswith("@"):
                    #str with @ -> apply method
                    code = f"outputDict[key] = self.{val[1:]}(startTime)"
                    exec(code)
                else:
                    #str -> interpolate
                    outputDict[key] = attrgetter(val + (f"_{zone}" if not (zone == "cylinder") else ""))(self.data)(startTime)
            else:
                #Error
                raise TypeError(f"Type '{val.__class__.__name__}' not supported ({key}).")
        
        return outputDict
    
    ####################################
    def preProcess(self, dataPath:str=None, *, data:dict|Dictionary, preProcessing:dict|Dictionary=None, initialConditions:dict|Dictionary) -> EngineModel:
        """
        Pre-processing:
            1) Loading data (from files or arrays)
            2) Pre-process the data (filtering, optional)
            3) Initialize thermodynamic regions
        
        NOTE:
        Naming of variables when loading data as follows:
            -> By default they refer to the "cylinder" zone
            -> Variables referred to a specific zone are allocated as "<variableName>_<zoneName>"

        TODO: example
        
        Args:
            data (dict | Dictionary): Dictionary with info for loading data.
            preProcessing (dict | Dictionary, optional): Dictionary with pre-processing information. Defaults to None.
            dataPath (str, optional): Master path of the tree. Defaults to None.
            initialConditions (dict | Dictionary): Dictionary with initial condition for thermodynamic models

        Returns:
            EngineModel: self
        """
        
        print("Pre-processing")
        
        #Loading data:
        self.loadData(dataPath, data=data)
        
        # Filtering data
        self.info["preProcessing"] = preProcessing
        filter = None
        if not preProcessing is None:
            preProcessing = Dictionary(**preProcessing)
            filterType = preProcessing.lookupOrDefault("Filter", None, fatal=False)
            if isinstance(filterType, str):
                #Got type name for run-time construction
                filter:Filter = Filter.selector(filterType, preProcessing.lookup(f"{filterType}Dict"))
            elif isinstance(filterType, Filter):
                #Got filter item
                filter = filterType
            else:
                #No filtering
                pass
            
        self.filterData(filter)
        
        #Initial conditions for thermodinamic models:
        self.initializeThemodynamicModels(**initialConditions)
        
        return self
        
    #########################################################################
    #Processing methods:
    def process(self) -> EngineModel:
        """
        Process the data, main time-loop.
        
        This is split into two function calls, which may be overwritten in child classes to tailored processings:
        1) _process__pre__: Create the columns in self.data for the fields generted by post-processing
        2) _update: The state-updating procedure in the main time-loop
        
        Returns:
            EngineModel: self
        """
        try:
            print("")
            print("Processing")
            print("startTime:",self.time.startTime)
            print("endTime:",self.time.endTime)
            print("current time:",self.info["time"])
            
            #Create fields
            self._process__pre__()
            
            #Process cylinder data
            for t in self.time(self.data["CA"]):
                #Restart from last time
                if t > self.info["time"]:
                    self.info["time"] = t
                    self._update()

            return self
        except BaseException as err:
            self.fatalErrorInClass(self.process, f"Failed processing data for engine model {self.__class__.__name__}", err)
    
    ####################################
    def _process__pre__(self) -> None:
        """
        Creation of the post-processed fields.
        
        NOTE:
            When overwriting, first call this method:
            def _process__pre__(self) -> None:
                super()._process__pre__()
                ...
        """
        #Add fields to data:
        fields = ["dpdCA", "V", "T", "gamma", "ahrr", "cumAhrr", "A"]
        for f in fields:
            if not f in self.data.columns:
                self.data[f] = float("nan")
        
        #Areas
        areas = self.geometry.areas(self.time.time)
        for patch in areas.columns:
            name = patch + "Area"
            if not name in self.data.columns:
                self.data[name] = float("nan")
        
        #Specie
        for specie in self._cylinder.mixture.mix:
            self.data[specie.specie.name + "_x"] = 0.0
            self.data[specie.specie.name + "_y"] = 0.0
        
        #Set initial values as start-time:
        CA = self.time.time
        if CA == self.time.startTime:
            index = self.data.data.index[self.data['CA'] == CA].tolist()
            
            #In-cylinder data
            V = self.geometry.V(CA)
            p = self.data.p(CA)
            T = self._cylinder.state.T
            gamma = self._cylinder.mixture.gamma(p,T)
            self.data["V"][index] = V
            self.data["T"][index] = T
            self.data["gamma"][index] = gamma
            
            #Ahrr
            self.data["ahrr"][index] = 0.0
            self.data["cumAhrr"][index] = 0.0
            
            #Specie
            for specie in self._cylinder.mixture.mix:
                self.data[specie.specie.name + "_x"][index] = specie.X
                self.data[specie.specie.name + "_y"][index] = specie.Y
            
            #Patch areas
            for patch in areas.columns:
                name = patch + "Area"
                if not name in self.data.columns:
                    self.data[name][index] = areas[patch]
            
            #Total area
            self.data["A"][index] = self.geometry.A(CA)
    
    
    ####################################
    def _update(self) -> None:
        """
        Method for updating the state during the time-loop. Here updating 
        cylinder as single-zone model without interaction with other regions.
        Could be overwritten for more detailed models (e.g., two-zone SI model, TJI, etc.)
        
        NOTE:
            When overwriting, afterwards call this method:
            def _update(self) -> None:
                ...
                super()._update()
        """
        #TODO injection models for mass end energy souce terms
        #TODO heat transfer models for temperature (open systems only!)
        
        #Current time
        CA = self.time.time
        
        #Update state
        p = self.data.p(CA)
        V = self.geometry.V(CA)
        dpdCA = (self.data.p(CA) - self.data.p(self.time.oldTime))/self.time.deltaT
        self._cylinder.update(pressure=p, volume=V)
        
        #Gamma
        T = self._cylinder.state.T
        gamma = self._cylinder.mixture.gamma(p,T)
        
        #Apparent heat release rate [J/CA]
        t1 = gamma/(gamma - 1.0)*p*self.geometry.dVdCA(CA) 
        t2 = 1.0/(gamma - 1.0)*self.geometry.V(CA)*dpdCA
        ahrr = t1 + t2
        
        self._updateMixtures()
        
        #Store
        index = self.data.data.index[self.data['CA'] == CA].tolist()[0]
        
        #Main parameters
        self.data["dpdCA"][index] = dpdCA
        self.data["V"][index] = V
        self.data["T"][index] = T
        self.data["gamma"][index] = gamma
        self.data["ahrr"][index] = ahrr
        
        #Integrate
        self.data["cumAhrr"][index] = self.data["cumAhrr"][index-1] + 0.5*(self.data["ahrr"][index-1] + ahrr)*self.time.deltaT
        
        #Mixture composition
        for specie in self._cylinder.mixture.mix:
            if not specie.specie.name + "_x" in self.data.columns:
                self.data[specie.specie.name + "_x"] = 0.0
                self.data[specie.specie.name + "_y"] = 0.0
            else:
                self.data[specie.specie.name + "_x"][index] = specie.X
                self.data[specie.specie.name + "_y"][index] = specie.Y
                
        #Patch areas
        areas = self.geometry.areas(CA)
        for patch in areas.columns:
            name = patch + "Area"
            if not name in self.data.columns:
                self.data[name][index] = areas[patch]
        
        #Total area
        self.data["A"][index] = self.geometry.A(CA)
    
    ####################################
    def refresh(self, reset:bool=False) -> EngineModel:
        """
        Refresh data and restart processing:
            1) loadData
            2) filterData
            3) process

        Args:
            reset (bool, optional): If need to restart from scratch. Defaults to False.
        
        Returns:
            EngineModel: self
        """
        #TODO: refactoring of initialization of thermodynamic models
        if reset:
            self._data = EngineData()
            self._raw = EngineData()
            self.preProcess(
                dataPath=self.info["dataPath"],
                data=self.info["data"],
                preProcessing=self.info["preProcessing"],
                initialConditions=self.info["initialConditions"])
        
        else:
            self.loadData(self.info["dataPath"], data=self.info["data"])
            self.filterData(self.info["filter"])
            
        self.process()
        
    ####################################
    def integrateVariable(self, y:str, *, x:str="CA", start:float=None, end:float=None) -> EngineModel:
        """
        Integrate a variable over another. If inital or final CA are not given, are set to first/last in CA range.

        Args:
            y (str): name of y variable.
            x (str, optional): Name of x variable. Defaults to "CA".
            start (float, optional): Initial CA. Defaults to None.
            end (float, optional): Final CA. Defaults to None.
        
        Returns:
            EngineModel: self
        """
        if not x in self.data.columns:
            raise ValueError(f"Variable '{x}' not present among data.")
        if not y in self.data.columns:
            raise ValueError(f"Variable '{y}' not present among data.")
        
        from scipy import integrate
        
        start = self.data["CA"][0] if start is None else start
        end = self.data["CA"][len(self.data)-1] if end is None else end
        
        self.checkType(start,float,"start")
        self.checkType(end,float,"end")
        
        index = self.data.data.index[np.array(self.data.data["CA"] >= start) & np.array(self.data.data["CA"] <= end)]
        data = self.data.data.iloc[index]
        
        return integrate.trapz(data[y], x=data[x])
    
    ####################################
    def IMEP(self, start:float=None, end:float=None) -> EngineModel:
        """
        Compute indicated mean effective pressure. If inital or final CA are not given, are set to first/last in CA range.

        Args:
            start (float, optional): Initial CA. Defaults to None.
            end (float, optional): Final CA. Defaults to None.
        
        Returns:
            EngineModel: self
        """
        from scipy import integrate
        
        start = self.data["CA"][0] if start is None else start
        end = self.data["CA"][len(self.data)-1] if end is None else end
        
        self.checkType(start,float,"start")
        self.checkType(end,float,"end")
        
        index = self.data.data.index[np.array(self.data.data["CA"] >= start) & np.array(self.data.data["CA"] <= end)]
        data = self.data.data.iloc[index]
        data["V"] = self.geometry.V(data["CA"])
        
        return integrate.trapz(data["p"], x=data["V"])/(max(data["V"]) - min(data["V"]))
    
#########################################################################
#Create selection table
EngineModel.createRuntimeSelectionTable()
    