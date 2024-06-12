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

from libICEpost.src.thermophysicalModels.thermoModels.ThermoModel import ThermoModel

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class EngineModel(BaseClass):
    """
    Base class for modeling of an engine and processing experimental/numerical data
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
    """
    Types:dict[str:type] = \
        {
            "EngineGeometry":           EngineGeometry,
            "EngineTime":               EngineTime,
            #"thermo":                   thermoModel,
        }
    
    Submodels:dict[str:type] = \
        {
            # "heatTransferModel":        None,
        }
    
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
    @classmethod
    def fromDictionary(cls, dictionary:Dictionary) -> EngineModel:
        """
        Construct from dictionary like:
        {
            EngineTime:         str
                Name of the engineTime model to use
            <EngineTime>Dict:   dict
                Dictionary containing the data specific of the selected 
                engineTime model (e.g., if engineTime is 'sparkIgnitionTime',
                then this dictionary must be named 'sparkIgnitionTimeDict'). 
                See at the helper for function 'fromDictionary' of the specific 
                engineTime model selected.
                
            EngineGeometry:         str
                Name of the engineTime model to use
            <EngineGeometry>Dict:   dict
                Dictionary with data required from engineGeometry (see help for 
                engineGeometry.fromDictionary for input data)
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
            print("Construct engineGeometry")
            egModel = dictionary.lookup("EngineGeometry")
            EG = EngineGeometry.selector(egModel, dictionary.lookup(egModel + "Dict"))
            print(EG,"\n")

            #Submodels
            subModels = {}
            smDict = dictionary.lookupOrDefault("submodels", Dictionary())
            for sm in cls.Submodels:
                if sm in smDict:
                    smTypeName = dictionary.lookup(sm)
                    subModels[sm] = cls.Submodels[sm].selector(smTypeName, smDict.lookup(sm + "Dict"))
            
            return cls(ET, EG, subModels)
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed contruction from dictionary", err)
    
    #########################################################################
    #Constructor:
    def __init__(self, time:EngineTime, geometry:EngineGeometry, submodels:dict={}):
        """
        time:       EngineTime
        geometry:   EngineGeometry
        submodels:  dict
            Dictionary containing the optional sub-models to load
        
        Base class for engine model, used for type-checking and loading the 
        sub-models.
        """
        try:
            #Main models
            self.checkType(geometry, self.Types["EngineGeometry"], "geometry")
            self.checkType(time, self.Types["EngineTime"], "engineTime")
            self.geometry = geometry
            self.time = time
            
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
    def initializeThemodynamicModels(self, /, *, cylinder:dict) -> EngineModel:
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
        """
        try:
            self.checkType(cylinder, dict, "cylinder")
            self._cilinder = ThermoModel(**self._preprocessThermoModelInput(cylinder))
                    
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
    