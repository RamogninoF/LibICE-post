from libICEpost.Database.chemistry.specie.Mixtures import Mixtures, Mixture
from libICEpost.Database.chemistry.specie.Molecules import Fuels

#Used by the engine model to compute the initial mixture composition (without EGR)
air = Mixtures.dryAir   #Standard air composition
initialMixture = \
{
    "cylinder":
        {
        "premixedFuel": \
            {
                "mixture": Mixture([Fuels.IC8H18], [1.0]),
                "phi":1.0,
            },
        }
}

#EGR model
EgrModel = "StoichiometricMixtureEGR"#"ExternalInterEGR"

StoichiometricMixtureEGRDict = \
{
    "air":Mixtures.dryAir,
    "fuel":Mixture([Fuels.IC8H18], [1.0]),
    "egr":0.115,
    "combustionEfficiency":0.9
}

ExternalInterEGRDict = \
{
    "externalEGR":0.0,
    "internalEGR":0.0,
    "combustionEfficiency":0.9
}
    
#Used by the egine model to handle injection of fuel, so with change of mixture composition
injectionModels = \
{
    #TODO
}

PremixedCombustionDict = \
{
    "reactionModel":"Stoichiometry", #TODO: equilibrium
}