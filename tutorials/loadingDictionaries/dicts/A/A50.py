#Properties of the specific EngineModel sub-class
SparkIgnitionEngineDict = \
{
    # Operating condition "A50" is characterized by a spark-advance of -4.73 CAD
    "SparkIgnitionTimeDict": \
    {
        "SA": -4.73, #[CAD]
    },
    
    "dataDict":\
    {
        "data":\
        {
            "cylinder":\
            {
                #Load the pressure data from the file "pExpA50"
                "p":\
                {
                    "data":
                    {
                        "fileName": "pExpA50"
                    }
                },
                
                #Set the in-cylinder mass to 0.00413863 kg
                "m_exp":\
                {
                    #The parameters to use
                    "data":
                    {
                        "value": 0.00413863, # [kg]
                    }
                },
            }
        }
    }
}