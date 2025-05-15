#Properties of the specific EngineModel sub-class
SparkIgnitionEngineDict = \
{
    # Operating condition "A100" is characterized by a spark-advance of -2 CAD
    "SparkIgnitionTimeDict": \
    {
        "SA": -2., #[CAD]
    },
    
    "dataDict":\
    {
        "data":\
        {
            "cylinder":\
            {
                #Load the pressure data from the file "pExpA100"
                "p":\
                {
                    "data":
                    {
                        "fileName": "pExpA100"
                    }
                },
                
                #Set the in-cylinder mass to 0.006193 kg
                "m_exp":\
                {
                    #The parameters to use
                    "data":
                    {
                        "value": 0.006193, # [kg]
                    }
                },
            }
        }
    }
}