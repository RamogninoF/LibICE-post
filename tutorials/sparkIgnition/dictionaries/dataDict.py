#Global path where data are stored
dataPath = f"{this.path}/../data"

#The fields to load for each region
data = \
{
    #Data for the cylinder region
    "cylinder":\
    {
        #Pressure (mandatory)
        "p":\
        {
            #The format of the data to load
            "format":"file",    #Retreive from file
            
            #The parameters to use
            "data":
            {
                #Name of the file
                "fileName":"p.Cyl",
                
                #Options to apply (scaling, shifting, etc.)
                "opts":\
                    {
                        # "varScale":1.0,   #Scaling variable
                        # "varOff":0.0,     #Offset to variable
                        # "CAscale":1.0,    #Scaling CA
                        # "CAoff":0.0,      #Offset to CA
                    }
            }
        },
        
        #Evolution of burnt mass fraction (for combustion model)
        "xb":\
        {
            "format":"function", #function of CA
            "data":
            {
                #Lambda function to apply on CA
                #example: step-function at spark-advance (-14.2 CAD)
                "function": lambda CA: (0.0 if CA < -14.2 else 1.0)
            }
        },
        
        #Pressure in bar (handy for plotting)
        "pBar":\
        {
            "format":"calc", #Calculated from loaded fields
            "data":
            {
                #Function to apply on loaded fields to compute the new one
                "function": lambda p: p*1e-5,
            }
        },
        
        #Wall temperatures (for heat-transfer model)
        "Twalls":\
        {
           "format":"uniform", #Uniform value over time
            "data":
            {
                #Value to set
                "value": 330.0,
            }
        },

        #Mass from the CFD symulation
        "m_CFD":\
        {
            "format":"file",
            "data":
            {
                "fileName":"massBal.Cyl",
                "opts":{}
            }
        },
        
        #Turbulent velocity fluctuation
        "uPrime":\
        {
            "format":"file",
            "data":
            {
                "fileName":"uprime.Cyl",
                "opts":{}
            }
        },
    }
}

#Parameters for pre-processing of data
preProcessing = \
{
    #Filter to apply on the data-set
    "Filter":"Resample", # Resampling over uniform grid
    "ResampleDict":\
        {
            "delta":1.0 #Delta-t [CA]
        },
        
    #User-defined filter through function/lambda such as:
    #f(Iterable,Iterable) -> tuple[Iterable,Iterable]
    "UserDefinedFilterDict":\
        {
            "function": lambda x,y : (x,y) #Dummy no-filter function
        },
    
    #Low-pass filter
    "LowPassDict":\
        {
            "cutoff":1, #Cut-off frequency
            "order":5,  #Order of the filter
            "delta":1.0 #Delta-t over which resampling after filtering
        }
}

#Initial conditions each thermodynamic region
initialConditions = \
{
    #In-cylinder region (at closed-valves)
    "cylinder": \
    {
        "pressure":"p",         #Interpolation from field 'p'
        "mass":"m_CFD",         #Interpolation from field 'm_CFD'
        "volume":"@geometry.V", #Computation from the method self.geometry.V(CA)
        "xb":0.0,               #Value
    }
}