#Properties of the specific EngineModel sub-class
SparkIgnitionEngineDict = \
{
    # Operating condition "A75" is characterized by a spark-advance of -4.75 CAD
    "SparkIgnitionTimeDict": \
    {
        "SA": -4.75, #[CAD]
    },
    
    "dataDict":\
    {
        "data":\
        {
            "cylinder":\
            {
                #Load the pressure data from the file "pExpA75"
                "p":\
                {
                    "data":
                    {
                        "fileName": "pExpA75"
                    }
                },
                
                #Set the in-cylinder mass to 0.00539428 kg
                "m_exp":\
                {
                    #The parameters to use
                    "data":
                    {
                        "value": 0.00539428, # [kg]
                    }
                },
            }
        }
    }
}