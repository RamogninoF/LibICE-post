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
}


def f(x,y):
    return x,y

data = \
    {
        "path":"./data",
        "pressure":\
        {
            "format":"file", # TODO: array
            "data":
            {
                "fileName":"p.Cyl",
                "opts":{}
            }
        },
        "otherVariables":\
        {
        },
        "preProcessing":\
        {
            "FilterType":"Resample", # "Resample", "UserDefinedFilter", "LowPass"
            "ResampleDict":\
                {
                    "delta":1.0
                },
            "UserDefinedFilterDict":\
                {
                    "function":f
                },
            "LowPassDict":\
                {
                    "cutoff":1,
                    "order":5
                }
        }
    }