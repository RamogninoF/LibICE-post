from libICEpost.Database.chemistry.specie.Mixtures import Mixtures, Mixture
from libICEpost.Database.chemistry.specie.Molecules import Fuels

#Used by the egine model to handle injection of fuel, so with change of mixture composition
injectionModels = \
{
    #TODO
},

#Used by the engine model to compute the initial mixture composition (without EGR)
initialMixture = \
{
    "cylinder":
        {
        "air":Mixtures.dryAir,
        "premixedFuel": \
            {
                "mixture": Mixture([Fuels.IC8H18], [1.0]),
                "phi":1.0,
            },
        }
},

PremixedCombustionDict = \
{
    #These entries are overwrittend at construction of the engine 
    # model, hence not needed. They are used only if constructing 
    # just the combustion model
    #-->
    "air":Mixtures.dryAir,
    "fuel": Mixture([Fuels.IC8H18], [1.0]),
    "phi":1.0,
    #<--
    
    #Entries of for CombustionModel
    "egrModel":"StoichiometricMixtureEGR",#"ExternalInterEGR",
    "StoichiometricMixtureEGRDict":\
    {
        "egr":0.115,
        "combustionEfficiency":0.9
    },
    "ExternalInterEGRDict":\
    {
        "externalEGR":0.0,
        "internalEGR":0.0,
        "combustionEfficiency":0.9
    },
    
    "reactionModel":"Stoichiometry", #TODO: equilibrium
}