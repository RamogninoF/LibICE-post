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
from typing import Iterable, Any

import yaml

from libICEpost.src.base.Functions.typeChecking import checkType

from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture, mixtureBlend
from libICEpost.src.thermophysicalModels.specie.specie.Molecule import Molecule
from libICEpost.src.thermophysicalModels.specie.reactions.Reaction.StoichiometricReaction import StoichiometricReaction
from libICEpost.src.thermophysicalModels.specie.reactions.ReactionModel.Stoichiometry import Stoichiometry
from libICEpost.src.thermophysicalModels.thermoModels.thermoMixture.ThermoMixture import ThermoMixture

from io import StringIO
import cantera as ct

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
    # Create mechanism with thermophysical from database of janaf7
    with StringIO() as tempf:
        makeEquilibriumMechanism(tempf, set([s.specie.name for s in air] + [s.specie.name for s in fuel] + [oxidizer.name]), overwrite=True)

        mix = ct.Solution(yaml=tempf.getvalue())
        mix.X = {s.specie.name: s.X for s in air}
        
        stoich_air_fuel_ratio = mix.stoich_air_fuel_ratio({s.specie.name: s.X for s in fuel}, {s.specie.name: s.X for s in air}, basis="mole")
        
        return stoich_air_fuel_ratio
    
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
def makeEquilibriumMechanism(path_or_stream:str|Any, species:Iterable[str], *, overwrite:bool=False) -> None:
    """
    Create a mechanism (in yaml format) for computation of chemical equilibrium 
    (with cantera) with the desired specie. The thermophysical properties are 
    based on NASA polynomials, which are looked-up in the corresponding database.
    
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
        path_or_stream (str or stream): The path where to save the mechanism in .yaml format or a writable stream.
        species (Iterable[Molecule]): The list of specie to use in the mechanism.
        overwrite (bool, optional): Overwrite if found?  Defaults to False.
    """
    # Check for the path_or_stream
    checkType(species, Iterable, "species")
    [checkType(s, str, f"species[{ii}]") for ii, s in enumerate(species)]
    
    # Make species a set (remove duplicate)
    species = set(species)
    species_list = list(species)
    
    # Determine if path_or_stream is a string (file path) or a stream
    is_path = isinstance(path_or_stream, str)
    if is_path:
        path = path_or_stream
        if not path.endswith(".yaml"):
            path += ".yaml"
        
        # Check path
        if not overwrite and os.path.isfile(path):
            raise IOError(f"Path '{path}' exists. Set 'overwrite' to True to overwrite.")
    
    # Load the databases
    from libICEpost.Database.chemistry.thermo.Thermo.janaf7 import janaf7_db, janaf7
    from libICEpost.Database.chemistry.specie.Molecules import Molecules
    
    # Find the atoms
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
                "composition":{a.atom.name:float(a.n) for a in Molecules[s]},
                "thermo":
                {
                    "model":"NASA7",
                    "temperature-ranges":[float(janaf7_db[s].Tlow), float(janaf7_db[s].Tth), float(janaf7_db[s].Thigh)],
                    "data":[[float(v) for v in janaf7_db[s].cpLow], [float(v) for v in janaf7_db[s].cpHigh]]
                }
            } for s in species_list
        ]
    
    output["reactions"] = []
    if is_path:
        with open(path, 'w') as yaml_file:
            yaml.dump(output, yaml_file, default_flow_style=False)
    else:
        yaml.dump(output, path_or_stream, default_flow_style=False)
    
#############################################################################
@lru_cache(maxsize=__CACHE_SIZE__)
def computeLHV(fuel:Molecule|str|Mixture, *, fatal=True) -> float:
    """
    Compute the lower heating value (LHV) of a molecule. This must be stored in 
    the database of fuels (database.chemistry.specie.Fuels), so that it has an 
    oxidation reaction in the corresponding database (database.chemistry.reactions.StoichiometricReaction).
    
    Args:
        fuel (Molecule|str|Mixture): Either the molecule, the name of the molecule, or a Mixture in case of multi-component fuel.
        fatal (bool, optional): Raise error if fuel not found in database? Defaults to True.
        
    Returns:
        float: The LHV [J/kg]
    """
    from libICEpost.Database.chemistry.reactions.StoichiometricReaction import StoichiometricReaction_db, StoichiometricReaction
    from libICEpost.src.thermophysicalModels.thermoModels.thermoMixture.ThermoMixture import ThermoMixture
    from libICEpost.Database.chemistry.specie.Molecules import Fuels
    
    checkType(fuel, (str, Molecule, Mixture), "fuel")
    
    #From Molecule or str
    if isinstance(fuel, Molecule):
        if isinstance(fuel, str):
            fuel = Fuels[fuel]

        #If fuel is not in the database, return 0 and raise warning
        if not fuel.name + "-ox" in StoichiometricReaction_db:
            if fatal:
                raise ValueError(f"Fuel '{fuel.name}' not found in database. Cannot compute LHV.")
            return 0.0
        oxReact:StoichiometricReaction = StoichiometricReaction_db[fuel.name + "-ox"]
        
        reactants = ThermoMixture(oxReact.reactants,thermoType={"Thermo":"janaf7", "EquationOfState":"PerfectGas"})
        products = ThermoMixture(oxReact.products,thermoType={"Thermo":"janaf7", "EquationOfState":"PerfectGas"})
        
        return (reactants.Thermo.hf() - products.Thermo.hf())/oxReact.reactants.Y[oxReact.reactants.index(fuel)]

    #From Mixture
    elif isinstance(fuel, Mixture):
        # LHV = sum(Yi*LHVi)
        return sum([computeLHV(f.specie, fatal=fatal)*f.Y for f in fuel])
    
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