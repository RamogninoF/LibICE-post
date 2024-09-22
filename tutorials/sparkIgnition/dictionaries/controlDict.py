
#The type of engine model
engineModelType = "SparkIgnitionEngine"

#Properties of the specific EngineModel sub-class
SparkIgnitionEngineDict = \
{
    #The sub-class handling time
    "EngineTime": "SparkIgnitionTime",
    "SparkIgnitionTimeDict": \
    {
        "IVC": -130, #[CAD]
        "EVO": 100,  #[CAD]
        "speed": 800,#[rpm]
        "SA": -14.2  #[CAD]
    },

    #The sub-class handling the engine geometrical parameters
    "EngineGeometry": "ConRodGeometry",
    "ConRodGeometryDict": \
    {
        "bore": 86e-3,       #[m]
        "stroke": 86e-3,     #[m]
        "conRodLen": 148e-3, #[m]
        "CR":8.7,            #[-]
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