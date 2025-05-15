#Global path where data are stored
dataPath = f"TO_OVERLOAD" # THIS WILL BE OVERWRITTEN (TEMPLATE)

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
            "format":"file",    #Retrieve from file
            
            #The parameters to use
            "data":
            {
                #Name of the file
                "fileName":"TO_OVERLOAD", # THIS WILL BE OVERWRITTEN (TEMPLATE)
                
                #Options to apply (scaling, shifting, etc.)
                "opts":\
                    {
                    }
            }
        },
        
        #Evolution of burnt mass fraction (for combustion model)
        "xb":\
        {
            "format":"uniform",
            "data":
            {
                "value":0.0, #Value to set
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
        
        #The experimental in-cylinder mass (will be overloaded in the specific operating condition)
        "m_exp":\
        {
            "format":"uniform",    #Retrieve from file
            "data":
            {
                "value":"TO_OVERLOAD" #The value will be overloaded in the specific operating condition
                #Here I set a non-valid value, so that the code will not run and this will fail
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
            "cutoff":0.4, #Cut-off frequency [1/CA]
            "delta":0.5 #Delta-t [CA]
        },
}

#Initial conditions each thermodynamic region
initialConditions = \
{
    #In-cylinder region (at closed-valves)
    "cylinder": \
    {
        "pressure":"p",         #Interpolation from field 'p'
        "mass":"m_exp",      #Mass of the cylinder [kg]
        "volume":"@geometry.V", #Computation from the method self.geometry.V(CA)
        "xb":"xb",              #Interpolation from field 'xb'
    }
}