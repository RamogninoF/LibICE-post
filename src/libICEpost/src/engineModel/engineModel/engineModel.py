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

from src.base.BaseClass import BaseClass, abstractmethod
from src.base.dataStructures.EngineData.EngineData import EngineData

#TODO:
from src.base.dataStructures.Dictionary import Dictionary

from ..engineTime import engineTime
from ..engineGeometry import engineGeometry

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class engineModel(BaseClass):
    """
    Base class for modeling of an engine and processing experimental/numerical data
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
    """
    Types:dict[str:type] = \
        {
            "engineGeometry":           engineGeometry,
            "engineTime":               engineTime,
            #"thermo":                   thermoModel,
        }
    
    Submodels:dict[str:type] = \
        {
            # "heatTransferModel":        None,
            # "laminarFlameSpeedModel":   None,
        }
    
    #########################################################################
    @classmethod
    def fromDictionary(cls, dictionary:Dictionary) -> engineModel:
        """
        Construct from dictionary like:
        {
            engineTime:         str
                Name of the engineTime model to use
            <engineTime>Dict:   dict
                Dictionary containing the data specific of the selected 
                engineTime model (e.g., if engineTime is 'sparkIgnitionTime',
                then this dictionary must be named 'sparkIgnitionTimeDict'). 
                See at the helper for function 'fromDictionary' of the specific 
                engineTime model selected.
                
            engineGeometry:         str
                Name of the engineTime model to use
            <engineGeometry>Dict:   dict
                Dictionary with data required from engineGeometry (see help for 
                engineGeometry.fromDictionary for input data)
        }
        """
        try:
            cls.checkTypes(dictionary, [dict, Dictionary], "dictionary")
            if isinstance(dictionary, dict):
                dictionary = Dictionary(dictionary)
            
            print("Constructing engine model from dictionary")
            
            #Engine time:
            print("Construct engineTime")
            etModel = dictionary.lookup("engineTime")
            ET = engineTime.selector(etModel, dictionary.lookup(etModel + "Dict"))
            
            #EngineGeometry:
            print("Construct engineGeometry")
            egModel = dictionary.lookup("engineGeometry")
            EG = engineGeometry.selector(egModel, dictionary.lookup(egModel + "Dict"))

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
    def __init__(self, time:engineTime, geometry:engineGeometry, submodels:dict={}):
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
            self.checkType(geometry, self.Types["engineGeometry"], "geometry")
            self.checkType(time, self.Types["engineTime"], "engineTime")
            self.geometry = geometry
            self.time = time
            
            #Submodels
            self.checkType(submodels, dict, "submodels")
            for model in self.Submodels:
                if model in submodels:
                    self.checkType(submodels[model], self.Types[model], f"{submodels}[{model}]")
            
            #Data structures
            self.raw = EngineData()     #Raw data
            self.data = EngineData()    #Filtered data
            
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
    def loadFile(self,*args,**argv) -> engineModel:
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
        self.raw.loadArray(*args,**argv)
        return self
    
    loadArray.__doc__ += EngineData.loadArray.__doc__
    
    ####################################
    def filterData(self, dt:float, /, *,Filter=None):
        """
        dt:     float
            New time-step to use for resampling the raw data
        Filter: Filter (None)
            Filter to apply to raw data before performing the 
            resampling (e.g. low-pass filter)
        
        Filter the data in self.raw applying a filer (optional) 
        and resampling with given time-step. Save the corresponding 
        filtered data to self.data
        
        TODO: Filer
        """
        try:
            self.checkType(dt, float, "dt")
            
            if len(self.data) == 0:
                self.data.data["CA"] = self.np.arange(self.raw.data["CA"][0],self.raw.data["CA"][len(self.raw)-1], dt)
            
            for var in self.raw.columns:
                if var != "CA":
                    self.data.data[var] = self.data.data["CA"].apply(getattr(self.raw, var))
        except BaseException as err:
            self.fatalErrorInClass(self.filterData, f"Failed filtering data", err)
        
        return self
    ####################################
    @abstractmethod
    def process(self):
        """
        Process the data (to be overwritten)
        """
        pass