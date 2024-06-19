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

from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture, mixtureBlend
from libICEpost.src.thermophysicalModels.specie.specie.Molecule import Molecule
from libICEpost.src.thermophysicalModels.specie.reactions.Reaction.StoichiometricReaction import StoichiometricReaction

from libICEpost.Database import database

#TODO caching (memoization package handles also unhashable types)

#############################################################################
#                              MAIN FUNCTIONS                               #
#############################################################################

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
    fuels = []
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
            raise ValueError(f"Oxidation reaction not found in database 'rections.{ReactionType}' for the couple (fuel, oxidizer) = ({f.name, oxidizer.name})")
    
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
    
    