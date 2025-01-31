#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        10/06/2024
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

import os
from typing import Iterable

import yaml

from libICEpost.src.base.Functions.typeChecking import checkType

from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture, mixtureBlend
from libICEpost.src.thermophysicalModels.specie.specie.Molecule import Molecule
from libICEpost.src.thermophysicalModels.specie.reactions.Reaction.StoichiometricReaction import StoichiometricReaction
from libICEpost.src.thermophysicalModels.specie.reactions.ReactionModel.Stoichiometry import Stoichiometry
from libICEpost.src.thermophysicalModels.thermoModels.thermoMixture.ThermoMixture import ThermoMixture

from libICEpost.Database import database

#TODO caching (memoization package handles also unhashable types)
from functools import lru_cache
from libICEpost.GLOBALS import __CACHE_SIZE__

#############################################################################
#                              MAIN FUNCTIONS                               #
#############################################################################
@lru_cache(maxsize=__CACHE_SIZE__)
def computeAlphaSt(air:Mixture, fuel:Mixture, *, oxidizer:Molecule=database.chemistry.specie.Molecules.O2) -> float:
    """
    Compute the stoichiometric air-fuel ratio given air and fuel mixture compositions.

    Args:
        air (Mixture): The air mixture composition
        fuel (Mixture): The fuel mixture composition
        oxidizer (Molecule, optional): The oxidizing molecule. Defaults to database.chemistry.specie.Molecules.O2.
        
    Returns:
        float
    """
    
    #Splitting the computation into three steps:
    #1) Removing the non-reacting compounds
    #   ->  Identified as those not found in the reactants 
    #       of any reactions
    #2) Identification of the active reactions
    #   ->  Active reactions are those where all reactants are present
    #       in the mixture and at least one fuel and the oxidizer
    #3) Solve the balance
    
    #Identification of active fuels in fuel mixture
    fuels:list[Molecule] = []
    for s in fuel:
        if s.specie.name in database.chemistry.specie.Fuels:
            fuels.append(s.specie)
    
    #Get reactions from database
    reactions = database.chemistry.reactions
    ReactionType = "StoichiometricReaction"
    
    #Look for the oxidation reactions for all fuels
    oxReactions:dict[str:StoichiometricReaction] = {}    #List of oxidation reactions
    for f in fuels:
        found = False
        for r in reactions[ReactionType]:
            react = reactions[ReactionType][r]
            if (f in react.reactants) and (oxidizer in react.reactants):
                found = True
                oxReactions[f.name] = react
                break
        if not found:
            #Create oxidation reaction
            oxReactions[f.name] = StoichiometricReaction.fromFuelOxidation(fuel=f, oxidizer=oxidizer)
            #Add to the database for later use
            reactions[ReactionType][oxReactions[f.name].name] = oxReactions[f.name]
            # raise ValueError(f"Oxidation reaction not found in database 'rections.{ReactionType}' for the couple (fuel, oxidizer) = {f.name, oxidizer.name}")
    
    #If oxidizing agent is not in air, raise value error:
    if not oxidizer in air:
        raise ValueError(f"Oxidizing molecule {oxidizer.name} not found in air mixture.")
    
    #If air contains any fuel, value error:
    if any([True for f in fuels if f in air]):
        raise ValueError("Air mixture must not contain any fuel.")
    
    #Compute mixture of stoichiometric reactants in following steps:
    #   1) Blend reactants of active reaction based on proportion of molecules in fuel mixture
    #   2) Detect fuel/oxidiser masses without inert species
    #   3) Add the non-active compounts in fuel to preserve their ratio
    #   4) Add non-active compounds in air to preserve their ratio
    #   5) Compute alpha
    
    #1)
    X = [fuel[f].X for f in fuels]
    sumX = sum(X)
    X = [x/sumX for x in X]
    reactants = mixtureBlend([oxReactions[f.name].reactants for f in fuels], X, "mole")
    
    #2)
    Y_fuel = sum(s.Y for s in reactants if s.specie in fuel)
    Y_air = sum(s.Y for s in reactants if s.specie in air)
    
    #3)
    if len([m for m in fuel if not (m.specie in fuels)]) > 0:
        reactingFracInFuel = sum([m.Y for m in fuel if m.specie in fuels])
        reactingFracInReactants = sum([m.Y for m in reactants if m.specie in fuels])
        Y_fuel += (1. - reactingFracInFuel)/reactingFracInFuel*reactingFracInReactants
    
    #4)
    if len([m for m in air if not (m.specie == oxidizer)]) > 0:
        oxidizerFracInAir = sum([m.Y for m in air if (m.specie == oxidizer)])
        oxidizerFracInReactants = sum([m.Y for m in reactants if (m.specie == oxidizer)])
        Y_air += (1. - oxidizerFracInAir)/oxidizerFracInAir*oxidizerFracInReactants
        
    #5)
    alphaSt = Y_air/Y_fuel
    
    return alphaSt

#############################################################################
@lru_cache(maxsize=__CACHE_SIZE__)
def computeAlpha(air:Mixture, fuel:Mixture, reactants:Mixture, *, oxidizer:Molecule=database.chemistry.specie.Molecules.O2) -> float:
    """
    Compute the air-fuel ratio given air, fuel, and reactants mixture compositions.

    Args:
        air (Mixture): The air mixture composition
        fuel (Mixture): The fuel mixture composition
        reactants (Mixture): The reactants mixture composition
        oxidizer (Molecule, optional): The oxidizing molecule. Defaults to database.chemistry.specie.Molecules.O2.
        
    Returns:
        float
    """
    #Procedure:
    #   1) Isolate air based on its composition (preserve proportion of mass/mole fractions)
    #   2) Isolate fuel based on its composition (preserve proportion of mass/mole fractions)
    #   3) Compute ratio of their mass fractions in full mixture
    
    # 1)
    yAir, remainder = reactants.subtractMixture(air)
    
    # 2)
    yFuel, remainder = remainder.subtractMixture(fuel)
    yFuel *= (1. - yAir)
    
    # 3)
    return yAir/yFuel
    
#############################################################################
def makeEquilibriumMechanism(path:str, species:Iterable[str], *, overwrite:bool=False) -> None:
    """
    Create a mechanism (in yaml format) for computation of chemical equilibrium 
    (with cantera) with the desired specie. The thermophysical properties are 
    based on NASA polinomials, which are looked-up in the corresponding database.
    
        File structure:
            phases:
            - name: gas
              thermo: ideal-gas
              elements: [C, H, N, ...]
              species: [AR, N2, HE, H2, ...]
              kinetics: gas
              state: {T: 300.0, P: 1 atm}
            
            species:
            - name: CO2
              composition: {C: 1, O:2}
              thermo:
                  model: NASA7
                  temperature-ranges: [200.0, 1000.0, 6000.0]
                  data:
                  - [...] #Low coefficients
                  - [...] #High coefficients
            - ...
    
    Args:
        path (str): The path where to save the mechanism in .yaml format.
        species (Iterable[Molecule]): The list of specie to use in the mechanism.
        overwrite (bool, optional): Overwrite if found?  Defaults to False.
    """
    #Check for the path
    checkType(path, str, "path")
    checkType(species, Iterable, "species")
    [checkType(s, str, f"species[{ii}]") for ii,s in enumerate(species)]
    
    #Make species a set (remove duplicate)
    species = set(species)
    species_list = list(species)
    
    if not path.endswith(".yaml"):
        path += ".yaml"
    
    #Check path
    if not overwrite and os.path.isfile(path):
        raise IOError("Path '{}' exists. Set 'overwrite' to True to overwrite.")
    
    #Load the databases
    from libICEpost.Database.chemistry.thermo.Thermo.janaf7 import janaf7_db, janaf7
    from libICEpost.Database.chemistry.specie.Molecules import Molecules
    
    #Find the atoms
    atoms:list[str] = []
    for s in species_list:
        specie = Molecules[s]
        for a in specie:
            if not a.atom.name in atoms:
                atoms.append(a.atom.name)
    
    output = {}
    output["phases"] = \
        [
            {
                "name":"gas",
                "thermo":"ideal-gas",
                "elements":atoms,
                "species":species_list,
                "kinetics":"gas",
                "state":{"T": 300.0, "P": 101325.0}
            }
        ]
    output["species"] = \
        [
            {
                "name":s,
                "composition":{a.atom.name:a.n for a in Molecules[s]},
                "thermo":
                {
                    "model":"NASA7",
                    "temperature-ranges":[janaf7_db[s].Tlow, janaf7_db[s].Tth, janaf7_db[s].Thigh],
                    "data":[janaf7_db[s].cpLow, janaf7_db[s].cpHigh]
                }
            } for s in species_list
        ]
    
    output["reactions"] = []
    
    print(f"Writing mechanism for computation of chemical equilibrium to file '{path}'")
    print(f"Molecules: {species}")
    print(f"Elements: {atoms}")
    with open(path, 'w') as yaml_file:
        yaml.dump(output, yaml_file)
    
#############################################################################
@lru_cache(maxsize=__CACHE_SIZE__)
def computeLHV(fuel:Molecule|str) -> float:
    """
    Compute the lower heating value (LHV) of a molecule. This must be stored in 
    the database of fuels (database.chemistry.specie.Fuels), so that it has an 
    oxidation reaction in the corresponding database (database.chemistry.reactions.StoichiometricReaction).
    
    Attributes:
        fuel (Molecule|str): A fuel molecule or its name. This will be looked-up 
        in the database of oxidation reactions.
    
    Returns:
        float: The LHV [J/kg]
    """
    checkType(fuel, (str, Molecule), "fuel")
    if isinstance(fuel, str):
        from libICEpost.Database.chemistry.specie.Molecules import Fuels
        fuel = Fuels[fuel]
    
    from libICEpost.Database.chemistry.reactions.StoichiometricReaction import StoichiometricReaction_db
    from libICEpost.src.thermophysicalModels.thermoModels.thermoMixture.ThermoMixture import ThermoMixture
    
    oxReact = StoichiometricReaction_db[fuel.name + "-ox"]
    
    reactants = ThermoMixture(oxReact.reactants,thermoType={"Thermo":"janaf7", "EquationOfState":"PerfectGas"})
    products = ThermoMixture(oxReact.products,thermoType={"Thermo":"janaf7", "EquationOfState":"PerfectGas"})
    
    return (reactants.Thermo.hf() - products.Thermo.hf())/oxReact.reactants.Y[oxReact.reactants.specie.index(fuel)]

#############################################################################
@lru_cache(maxsize=__CACHE_SIZE__)
def computeMixtureEnergy(mixture:Mixture, oxidizer:Molecule=database.chemistry.specie.Molecules.O2) -> float:
    """
    Compute the energy of a mixture based on the LHV of fuels contained. Computes stoichiometric 
    combustion based on the fuels in the database (database.chemistry.specie.Fuels).
    
    Attributes:
        mixture (Mixture): The mixture.
        oxidizer (Molecule, optional): The oxidizing agend. Defaults to database.chemistry.specie.Molecules.O2.
    
    Returns:
        float: The avaliable chemical energy of the mixture [J/kg]
    """
    reactionModel = Stoichiometry(mixture)
    
    #Build thermodynamic models of mixture based on janaf and perfect gas
    thermoType = \
        {
            "EquationOfState":"PerfectGas",
            "Thermo":"janaf7"
        }
    reactants = ThermoMixture(reactionModel.reactants, thermoType=thermoType)
    products = ThermoMixture(reactionModel.products, thermoType=thermoType)
    
    return (reactants.Thermo.hf() - products.Thermo.hf())