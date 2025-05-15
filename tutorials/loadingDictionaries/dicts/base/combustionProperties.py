#Loading mixtures and molecules from database
from libICEpost.Database.chemistry.specie.Mixtures import Mixtures, Mixture
from libICEpost.Database.chemistry.specie.Molecules import Fuels
air = Mixtures.dryAir   #Standard air composition

#Dictionary for computation of initial mixture composition in each region
initialMixture = \
{
    #In-cylinder region
    "cylinder":
        {
        #Information for the premixed fuel
        "premixedFuel": \
            {
                #The mixture of the fuel (pure iso-octane)
                "mixture": Mixture([Fuels.IC8H18], [1.0]),
                
                #The equivalence ratio of the mixture
                "phi":0.0,
            },
        }
}

# The model to account for exhaust-gas recirculation 
# on in-cylinder mixture composition
EgrModel = "StoichiometricMixtureEGR" #EGR composition computed at lambda = 1
StoichiometricMixtureEGRDict = \
{
    "air":Mixtures.dryAir,                  #Air mixture
    "fuel":Mixture([Fuels.IC8H18], [1.0]),  #Fuel mixture
    "egr":0.0,                              #EGR mass fraction
}

#The combustion model used (spark-ignition)
CombustionModel = "PremixedCombustion" #Premixed combustion
PremixedCombustionDict = \
{
    #The reaction model used to compute the mixture composition
    "reactionModel":"Stoichiometry", # Stoichiometric-reaction 
                                     # combustion products
                                     # [Reactants] -> [Products]
}