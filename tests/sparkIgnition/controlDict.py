from libICEpost.src.base.dataStructures.Dictionary import Dictionary

engineModelType = "SparkIgnitionEngine"
SparkIgnitionEngineDict = \
{
    "EngineTime": "SparkIgnitionTime",
    "SparkIgnitionTimeDict": \
    {
        "IVC": -130,
        "EVO": 100,
        "speed": 800,
        "SA": -14.2
    },

    "EngineGeometry": "ConRodGeometry",
    "ConRodGeometryDict": \
    {
        "bore": 86e-3,
        "stroke": 86e-3,
        "conRodLen": 148e-3,
        "CR":8.7,
    },
    
    "thermophysicalProperties":Dictionary.fromFile(f"{this.path}/thermophysicalProperties.py"),
    "combustionProperties":Dictionary.fromFile(f"{this.path}/combustionProperties.py"),
    
    "dataDict":Dictionary.fromFile(f"{this.path}/dataDict.py")
}