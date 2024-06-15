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

from libICEpost.src.base.BaseClass import BaseClass, abstractmethod
from libICEpost.src.base.dataStructures.EngineData.EngineData import EngineData
from libICEpost.src.base.Filter.Filter import Filter

from libICEpost.src.base.dataStructures.Dictionary import Dictionary

from ..EngineTime.EngineTime import EngineTime
from ..EngineGeometry.EngineGeometry import EngineGeometry

from libICEpost.src.thermophysicalModels.thermoModels.CombustionModel.CombustionModel import CombustionModel
from libICEpost.src.thermophysicalModels.thermoModels.ThermoModel import ThermoModel

from libICEpost.Database.chemistry.specie.Mixtures import Mixtures, Mixture

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
# TODO:
#   Handle direct injection (injectionModel?)
#   Handle interaction with other zones (creviceModel? prechamberModel?)

# NOTE: to handle diesel combustion, need to compute the phi from the injected mass 
# (probably the main parameter for the combustion model, and pass it to the EGR model)

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
    
    Attibutes:
    """
    
    """Types for each main model"""
    Types:dict[str:type] = \
        {
            "EngineGeometry":           EngineGeometry,
            "EngineTime":               EngineTime,
            "CombustionModel":          CombustionModel,
        }
    
    """The available sub-models"""
    Submodels:dict[str:type] = \
        {
            # "heatTransferModel":        None,
        }
    
    """The zones avaliable in the model"""
    Zones:list[str] = \
        [
            "cylinder"
        ]
    
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

                initialMixture: dict
                {
                    <zoneName>:
                    {
                        air:    Mixture (default: database.chemistry.specie.Mixtures.dryAir),
                        premixedFuel: dict (optional)
                        {
                            mixture: Mixture,
                            phi:     float,
                        }
                    }
                },
                
                CombustionModel:         str
                    Name of the CombustionModel to use
                <CombustionModel>Dict:   dict
                    Dictionary with data required from CombustionModel
                    See at the helper for function 'fromDictionary' of the specific 
                    CombustionModel model selected.
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

            #CombustionModel:
            print("Construct CombustionModel")
            
            #Manipulating the combustionProperties
            combustionModelDict = dictionary.lookupOrDefault(cls.Types["CombustionModel"].__name__ + "Dict", Dictionary())
            
            #Give premixed composition entries to combustion model. They will updated in constructor.
            
            
            combustionModel = dictionary.lookup("CombustionModel")
            CM = CombustionModel.selector(combustionModel, dictionary.lookupOrDefault(combustionModel + "Dict", Dictionary()))
            print(CM,"\n")
            
            #TODO: Injection models
            
            #Submodels
            subModels = {}
            smDict = dictionary.lookupOrDefault("submodels", Dictionary())
            for sm in cls.Submodels:
                if sm in smDict:
                    print(f"Construct {sm} sub-model")
                    smTypeName = dictionary.lookup(sm)
                    subModels[sm] = cls.Submodels[sm].selector(smTypeName, smDict.lookup(sm + "Dict"))
            
            out = cls(ET, EG, subModels)
            
            #Initialize mixtures
            out.initializeMixtures(**dictionary.lookup("initialMixture"))
            
            return out
            
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed contruction from dictionary", err)
    
    #########################################################################
    #Constructor:
    def __init__(self, *, 
                 time:EngineTime, 
                 geometry:EngineGeometry, 
                 combustionModel:CombustionModel,
                 submodels:dict={}, 
                 injectionModels:dict={},
                 ):
        """
        Base class for engine model, used for type-checking and loading the sub-models.

        Args:
            time (EngineTime): The engine time
            geometry (EngineGeometry): The engine geometry
            combustionModel (CombustionModel): Combustion model to use
            submodels (dict, optional): Dictionary containing the optional sub-models to load. Defaults to {}.
            injectionModels (dict, optional): Dictionary containing the optional injection models to load. Defaults to {}.
        """
        try:
            #Main models
            self.checkType(geometry, self.Types["EngineGeometry"], "geometry")
            self.checkType(time, self.Types["EngineTime"], "engineTime")
            self.checkType(combustionModel, self.Types["CombustionModel"], "combustionModel")
            self.geometry = geometry
            self.time = time
            self.combustionModel = combustionModel
            
            #Submodels
            self.checkType(submodels, dict, "submodels")
            for model in self.Submodels:
                if model in submodels:
                    self.checkType(submodels[model], self.Types[model], f"{submodels}[{model}]")
            
            #Data structures
            self._raw = EngineData()     #Raw data
            self._data = EngineData()    #Filtered data
            
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, f"Failed constructing instance of class {self.__class__.__name__}", err)
    
    #########################################################################
    def __str__(self):
        STR = ""
        STR += "Engine model instance:\n"
        STR += "Engine time\n\t" + self.time.__str__().replace("\n", "\n\t")
        STR += "\n"
        STR += "Engine geometry:\n\t" + self.geometry.__str__().replace("\n", "\n\t")
        
        return STR
        
    #########################################################################
    def loadFile(self,*args,**argv) -> EngineModel:
        """
        Loads a file with raw data to self.raw. See EngineData.loadFile 
        documentation for arguments:
        """
        self.raw.loadFile(*args,**argv)
        return self
    
    loadFile.__doc__ += EngineData.loadFile.__doc__
    
    ####################################
    def loadArray(self,*args,**argv):
        """
        Loads an array with raw data to self.raw. See EngineData.loadArray 
        documentation for arguments:
        """
        self._raw.loadArray(*args,**argv)
        return self
    
    loadArray.__doc__ += EngineData.loadArray.__doc__
    
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
            # Clear filtered data
            self._data = EngineData()
            if filter is None:
                self._data = self._raw
                return self
            
            #Apply filter
            print(f"Applying filter {filter if isinstance(filter,Filter) else filter.__name__}")
            for var in self._raw.columns:
                #Filter data
                if var != "CA":
                    _, self._data.data[var] = filter(self._raw.data["CA"], self._raw.data[var])
                else:
                    self._data.data[var], _ = filter(self._raw.data["CA"], self._raw.data[var])
                    
                #Create interpolator
                self._data.createInterpolator(var)
            
        except BaseException as err:
            self.fatalErrorInClass(self.filterData, f"Failed filtering data", err)
        
        return self
    
    ####################################
    #TODO:
    # Initializing the mixture composition on each thermodynamic zone. The be overwritten in subclasses 
    # to handle specific initializations (SI engine will use the premixed-fuel entry, which will be 
    # sent to the the combustion model)
    @abstractmethod
    def initializeMixtures(self, /, *, cylinder:dict, **zones) -> EngineModel:
        #Here set the air, in sub-classes update
        pass
    
    ####################################
    def initializeThemodynamicModels(self, /, *, cylinder:dict, **zones) -> EngineModel:
        """
        Set the initial conditions of all thermodynamic regions of the EngineModel.
        For region to be initialized, a dict is given for the inital conditions,
        according to the following convention:
        
        ->  If a float is given, the value is used
        ->  If a str is given, it refers to the name of the vabiables stored in the EngineModel,
            in which case the corresponding initial condition is sampled from the the corresponding
            data-set at self.engineTime.startTime (if None, to first instant of pressure trace)
        ->  If string starting with @ is given, it applies that method with input (self.engineTime.startTime)

        Ex:
        {
            "pressure": "p",            #This interpolates self.data.p at self.time.startTime
            "mass": 1.2e-3,             #Value
            "volume": "@geometry.V"     #Evaluates self.geometry.V(self.time.startTime)
        }
        
        Args:
            cylinder (dict): data for initialization of in-cylinder state.
            **zones:  data initialization of each zone in the model.
        """
        try:
            self.checkType(cylinder, dict, "cylinder")
            self._cilinder = ThermoModel(**self._preprocessThermoModelInput(cylinder))
            
            for zone in zones:
                if not zone in self.Zones:
                    raise ValueError(f"Unknown zone {zone}. Available zones in engine model are: {self.Zones}")
                
                self.checkType(zones[zone], dict, zone)
                self.__setattr__("_" + zone, ThermoModel(**self._preprocessThermoModelInput(zones[zone])))
            
        except BaseException as err:
            self.fatalErrorInClass(self.filterData, f"Failed initializing thermodynamic regions", err)
        
        return self
    
    ####################################
    def _preprocessThermoModelInput(self, inputDict:dict) -> dict:
        """
        Auxiliary function to pre-process input dictionary 
        to initialization of a thermodynamic region

        Args:
            inputDict (dict): dictionary for thermodynamic inputs

        #TODO error handling
        
        Returns:
            dict: processed dictionary
        """
        outputDict = {}
        for key in inputDict:
            val = inputDict[key]
            if isinstance(val,float):
                #Float -> use value
                outputDict[key] = val
                
            elif isinstance(val,str):
                #str -> interpolate
                if self.time.startTime is None:
                    startTime:float = self.data["CA"][0]
                else:
                    startTime:float = self.time.startTime
                
                #str with @ -> apply method
                if val.startswith("@"):
                    code = f"outputDict[key] = self.{val[1:]}(startTime)"
                    exec(code)
                else:
                    outputDict[key] = attrgetter(val)(self.data)(startTime)
                  
        return outputDict
    
    ####################################
    # TODO:Boundary conditions: heat transfer at walls
    # def setBoundaryConditions(self, /, *, cylinder:dict):
    #     """
    #     Set the boundary conditions of all thermodynamic regions of the EngineModel
    #     """
    #     pass
    
    ####################################
    @abstractmethod
    def process(self):
        """
        Process the data (to be overwritten)
        """
        pass
    
#########################################################################
#Create selection table
EngineModel.createRuntimeSelectionTable()
    