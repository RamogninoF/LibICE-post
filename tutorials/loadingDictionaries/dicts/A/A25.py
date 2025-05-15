#Properties of the specific EngineModel sub-class
SparkIgnitionEngineDict = \
{
    # Operating condition "A25" is characterized by a spark-advance of -5.06 CAD
    "SparkIgnitionTimeDict": \
    {
        "SA": -5.06, #[CAD]
    },
    
    "dataDict":\
    {
        "data":\
        {
            "cylinder":\
            {
                #Load the pressure data from the file "pExpA25"
                "p":\
                {
                    "data":
                    {
                        "fileName": "pExpA25"
                    }
                },
                
                #Set the in-cylinder mass to 0.0030858 kg
                "m_exp":\
                {
                    #The parameters to use
                    "data":
                    {
                        "value": 0.0030858, # [kg]
                    }
                },
            }
        }
    }
}