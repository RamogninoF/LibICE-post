#The type of engine model
engineModelType = "SparkIgnitionEngine"

#Properties of the specific EngineModel sub-class
SparkIgnitionEngineDict = \
{
    #The sub-class handling time
    "EngineTime": "SparkIgnitionTime",
    "SparkIgnitionTimeDict": \
    {
        "IVC": -143, #[CAD]
        "EVO": 125,  #[CAD]
        "speed": "to_overload", #[rpm] THIS WILL BE OVERWRITTEN (TEMPLATE)
        "SA": "to_overload", #[CAD] THIS WILL BE OVERWRITTEN (TEMPLATE)
    },

    #The sub-class handling the engine geometrical parameters
    "EngineGeometry": "ConRodGeometry",
    "ConRodGeometryDict": \
    {
        "bore": 0.128,       #[m]
        "stroke": 0.144,     #[m]
        "conRodLen": 0.2415,  #[m]
        "CR":20.3,            #[-]
    },
    
    #Dictionary for thermophysical properties
    "thermophysicalProperties":\
        Dictionary.fromFile(f"{this.path}/thermophysicalProperties.py"),
    
    #Dictionary for combustion properties
    "combustionProperties":\
        Dictionary.fromFile(f"{this.path}/combustionProperties.py"),
    
    #Dictionary for data loading
    "dataDict":Dictionary.fromFile(f"{this.path}/dataDict.py"),
    
    #Dictionary for specific sub-models
    "submodels":\
        {
            #Heat transfer model
            "HeatTransferModelType":"Woschni",
            "WoschniDict":{} #Default coefficients
        }
}