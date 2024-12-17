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

#load the base class
from .EngineModel import EngineModel

#Other imports
from operator import attrgetter

from libICEpost.src.base.dataStructures.Dictionary import Dictionary

from ..EngineTime.EngineTime import EngineTime
from ..EngineGeometry.EngineGeometry import EngineGeometry

from libICEpost.src.thermophysicalModels.thermoModels.CombustionModel.PremixedCombustion import PremixedCombustion
from libICEpost.src.engineModel.EngineTime.SparkIgnitionTime import SparkIgnitionTime

from libICEpost.src.thermophysicalModels.thermoModels.ThermoModel import ThermoModel
from libICEpost.src.thermophysicalModels.specie.reactions.functions import computeAlphaSt
from libICEpost.Database.chemistry.specie.Mixtures import Mixture

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class SparkIgnitionEngine(EngineModel):
    """
    Simple spark-ignition engine model with single-zone modeling.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        
    """
    Types = {t:EngineModel.Types[t] for t in EngineModel.Types}
    Types["CombustionModel"] = PremixedCombustion
    
    CombustionModel:PremixedCombustion
    
    _fuel:Mixture
    """The current in-cylinder fuel mixture composition"""
    
    #########################################################################
    #Properties:

    #########################################################################
    #Class methods and static methods:
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
                {
                    <zoneName>:
                    {
                        premixedFuel: dict (optional)
                        {
                            mixture: Mixture,
                            phi:     float,
                        }
                    }
                },
                
                PremixedCombustionDict:   dict
                    Dictionary with data required from PremixedCombustion combustion model
                    See at the helper for function 'fromDictionary' of the specific 
                    CombustionModel model selected.
            }
            
        }
        """
        return super().fromDictionary(dictionary)
    
    #########################################################################
    # Constructor
    #Not overwrite
    
    #########################################################################
    #Construction methods:
    def _constructThemodynamicModels(self, combustionProperties:dict|Dictionary) -> EngineModel:
        """
        Construct the thermodynamic models of the system, setting their initial 
        mixture composition. Here setting everything to air, to be overwritten in sub-classes.
        
        Args:
            combustionProperties (dict|Dictionary): the combustion properties

        Returns:
            EngineModel: self
        """
        #Construct zones and set to air
        super()._constructThemodynamicModels(combustionProperties)
        
        #Zone dictionaries
        zones = combustionProperties.lookup("initialMixture")
        
        #NOTE: Cylinder zone must always be supplied, to get an initial fuel mixture. This will be updated by injection models.
        if not "cylinder" in zones:
            raise ValueError("cylinder zone initialization must be supplied.")
        
        for zone in self.Zones:
            if not zone in zones:
                continue
            
            #Get data for zone
            zoneDict = zones[zone]
            self.checkType(zoneDict, dict, f"zones[{zone}]")
            zoneDict = Dictionary(**zoneDict)
            
            if not "premixedFuel" in zoneDict:
                continue
            
            zoneDict = zoneDict.lookup("premixedFuel")
            
            #This zone:
            currZone:ThermoModel = attrgetter("_" + zone)(self)
            
            #Fuel
            fuel:Mixture = zoneDict.lookup("mixture")
            
            #Alpha
            if ("phi" in zoneDict) and not ("alpha" in zoneDict):
                air = self._air
                phi:float = zoneDict.lookup("phi")
                alphaSt = computeAlphaSt(air=air, fuel=fuel)
                alpha = alphaSt/phi
            elif ("alpha" in zoneDict) and not ("phi" in zoneDict):
                alpha = zoneDict.lookup("alpha")
            else:
                print(zoneDict)
                raise ValueError("Either phi or alpha must be supplied to set the premixed fuel.")
            
            #Mass fraction of fuel:
            yf = 1./(alpha + 1.)
            
            #Dilute with fuel
            currZone.mixture.mix.dilute(fuel, yf, "mass")
        return self
    
    ####################################
    def _constructCombustionModel(self, combustionProperties:dict|Dictionary):
        """
        Appending fuel and air to combustionModelDict
        
        Args:
            combustionProperties (dict|Dictionary): the combustion properties
        
        Returns:
            EngineModel: self
        """
        self.checkType(combustionProperties, dict, "combustionProperties")
        if not isinstance(combustionProperties, Dictionary):
            combustionProperties = Dictionary(**combustionProperties)
        
        #Get fuel
        fuel = combustionProperties.lookup("initialMixture").lookup("cylinder").lookup("premixedFuel").lookup("mixture")
        
        #Get air 
        air = combustionProperties.lookup("air")
        
        #Update combustion model dictionary
        combustionModelType = self.Types['CombustionModel'].__name__
        combustionModelDict = combustionProperties.lookupOrDefault(combustionModelType + "Dict", Dictionary())
        combustionModelDict.update(air=air.copy(), fuel=fuel.copy()) #Set fuel and air
        combustionProperties.update(**{combustionModelType+"Dict":combustionModelDict, "CombustionModel":combustionModelType})
        
        super()._constructCombustionModel(combustionProperties)
        
        #Check consistency
        if not isinstance(self.CombustionModel, self.Types["CombustionModel"]):
            raise TypeError(f"Combustion model type {combustionModelType} in combustionProperties dictionaries not compatible with allowed type for engine model {self.__class__.__name__} ({self.Types['CombustionModel']})")
        
    #########################################################################
    #Pre-processing methods:
    def _preprocessThermoModelInput(self, inputDict:dict, zone:str) -> dict:
        """
        Set also mixture composition based on xb.
        
        NOTE: xb field must be already loaded.

        Args:
            inputDict (dict): The input dictionary
            zone (str): zone name

        Returns:
            dict: processed input parameters for ThermoModel constructor
        """
        tempDict = super()._preprocessThermoModelInput(inputDict, zone)
        
        if zone == "cylinder":
            if (not "xb" in tempDict):
                raise ValueError("Field xb was not supplied to the initial conditions of cylinder zone.")
            
            #Update combustion model:
            self.CombustionModel.update(xb=tempDict["xb"])
            
            #Update mixture: 
            mix = self.CombustionModel.mixture
        
        nameList = ["mass", "temperature", "pressure", "volume", "density"]
        outputDict = {v:tempDict[v] for v in tempDict if v in nameList}   #Set state variables
        
        if zone == "cylinder":
            outputDict["mixture"] = mix #Set mixture
        
        return outputDict
    
    #########################################################################
    #Processing methods:
    # _update not overloaded
        
    #####################################
    # _process__pre__ not to be overloaded
    
    
#########################################################################
#Add to selection table of Base
EngineModel.addToRuntimeSelectionTable(SparkIgnitionEngine)
