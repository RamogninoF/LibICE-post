#Global path
dataPath = f"{this.path}/data"

#Data
data = \
{
    "cylinder":\
    {
        "p":\
        {
            "format":"file", # TODO: array, uniform
            "data":
            {
                "fileName":"p.Cyl",
                "opts":{}
            }
        },
        
        "xb":\
        {
            "format":"function", #function of CA
            "data":
            {
                "function": lambda CA: (0.0 if CA < -14.2 else 1.0)
            }
        },
        
        "xb":\
        {
            "format":"function", #function of CA
            "data":
            {
                "function": lambda CA: (0.0 if CA < -14.2 else 1.0)
            }
        },
    }
}

#Parameters for pre-processing
preProcessing = \
{
    "Filter":"Resample", # "Resample", "UserDefinedFilter", "LowPass"
    "ResampleDict":\
        {
            "delta":1.0
        },
    "UserDefinedFilterDict":\
        {
            "function": lambda x,y : (x,y)
        },
    "LowPassDict":\
        {
            "cutoff":1,
            "order":5,
            "delta":1.0
        }
}

#Initial conditions for thermo regions
initialConditions = \
{
    "cylinder": \
    {
        "pressure":"p",
        "mass":540e-6,
        "volume":"@geometry.V",
        "xb":0.0,
    }
}