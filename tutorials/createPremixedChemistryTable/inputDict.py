import numpy as np
from libICEpost.Database.chemistry.specie.Mixtures import Mixtures

#Sampling points
p = np.array( #Pressure
    [
        1, 
        # 5, 
        # 10, 
        # 20, 
        # 50, 
        # 75, 
        100, 
        # 125, 
        # 150, 
        # 175, 
        # 200, 
        300,
        ]
    )*1e5
Tu = np.arange(300, 3500, 200) #Unburnt gas temperature
phi = np.concatenate(  #equivalence ratio
    [
        1./np.array(
        [
            100.,
            4.,
            3.,
            2.,
            # 1.9,
            # 1.8,
            # 1.7,
            # 1.6,
            1.5,
            # 1.4,
            # 1.3,
            # 1.2,
            # 1.1,
        ]),
        np.array(
        [
            1.0,
            # 1.1,
            # 1.2,
            # 1.3,
            # 1.4,
            1.5,
            # 1.6,
            # 1.7,
            # 1.8,
            # 1.9,
            2.,
            3.,
            4.,
            100.,
        ])
    ])
egr = np.array( #exhaust gas recirculation
    [
        0.0,
        # 0.1,
        # 0.2,
        # 0.3,
        # 0.4,
        # 0.5,
        # 0.6,
        # 0.7,
        # 0.8,
        # 0.9,
        1.0
        ]
    )

#Mixture properties
mechanism = "./h2_li_2004.yaml"
fuel = {"H2": 1.0}  #Fuel mixture
air = {s.specie.name: s.Y for s in Mixtures.dryAir}  #Air

#Miscellaneous
numberOfProcessors = 16     #Number of cores for parallelization
tableName = "outputTable"   #The name of the table to create

