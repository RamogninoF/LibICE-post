import numpy as np
from libICEpost.Database.chemistry.specie.Mixtures import Mixtures

#Sampling points
p = np.array( #Pressure
    [
        1, 
        # 5, 
        10, 
        # 20, 
        50, 
        100, 
        150, 
        # 200, 
        # 300,
        ]
    )*1e5
Tu = np.array( #Unburnt gas temperature
    [
        300, 
        # 400, 
        500, 
        # 600, 
        700, 
        # 800, 
        900, 
        # 1000, 
        1100, 
        # 1200, 
        1300, 
        # 1400,
        ]
    )
phi = np.array( #equivalence ratio
    [
        # 0.2,
        # 0.3,
        # 0.4,
        # 0.5,
        # 0.6,
        0.7,
        # 0.8,
        0.9,
        1.0,
        1.1,
        # 1.2,
        1.3,
        # 1.4,
        # 1.5,
        # 1.6,
        # 1.7,
        # 1.8,
        # 1.9,
        # 2.0,
        ]
    )
# egr = np.array( #exhaust gas recirculation
#     [
#         0.0,
#         0.05,
#         0.1,
#         0.15,
#         0.2,
#         0.25,
#         0.3,
#         0.35,
#         0.4,
#         0.45,
#         0.5,
#         0.55,
#         0.6
#         ]
#     )

#Initial point where to start computation. This can be either a single point (dictionary) or a list of points (list[dictionary])
# initialConditions = \
#     {
#         "p": 1e5,
#         "Tu":300,
#         "phi":1.,
#         "egr":0.
#     }
initialConditions = \
    {
        "p": p[0],
        "Tu":Tu[0],
        "phi":1.,
        "egr":0.
    }

#Initial mesh parameters
meshType = "constantWidth" #"pressureTemperatureAdaptive"
pressureAdaptiveDict = \
    {
        "refLength": 0.014,     #Lenght at standard conditions
        "expCoeff":1.5
    }
pressureTemperatureAdaptiveDict = \
    {
        "refLength": 0.0138,     #Lenght at standard conditions
        "pressCoeff":1.45,
        "tempCoeff":-1.6,
        "maxGridPoints":3000,   #Allow up to 3000 grid-points (default is 1000 in cantera)
    }
    
userDefinedDict = \
    {
        "grid": np.linspace(0, 0.025, 20)
    }
constantWidthDict = \
    {
        "width": 0.001,
        "maxGridPoints":3000,   #Allow up to 3000 grid-points (default is 1000 in cantera)
    }

#Grid refinement parameters
gridRefinementParams = \
    {
        "ratio": 2, 
        "slope":0.005, 
        "curve":0.005, 
        "prune":0.000,
    }

#Mixture properties
mechanism = "./h2_li_2004.yaml"
fuel = {"H2": 1.0}  #Fuel mixture
air = {s.specie.name: s.Y for s in Mixtures.dryAir}  #Air

#Miscellaneous
loglevel = 0 #Verbosity level of solution
numberOfProcessors = 36 #Number of cores for parallelization

#Outputs
tableName = "outputTable"           #The name of the table to create
debugFile = "./tempTable.csv"     #Debug csv file used for restart
restartFile = "./tempTable.csv"     #File for reloading

