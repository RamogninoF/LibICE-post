#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023

Chemical reactions
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from src.base.Functions.runtimeWarning import runtimeWarning

from src.thermophysicalModels.specie.thermo.Reaction import Reaction

import json

import Database
from Database.chemistry.specie import periodicTable, Molecules

#############################################################################
#                                   DATA                                    #
#############################################################################

_theseLocals = locals()

def fromJson(fileName, typeName="Molecules"):
    """
    Add reactions to the database from a json file.
    """
    try:
        with open(fileName) as f:
            data = json.load(f)
            for react in data:
                _theseLocals = \
                    Reaction\
                        (
                            [Molecules.__dict__[mol] for mol in data[react]["reactants"]],
                            [Molecules.__dict__[mol] for mol in data[react]["products"]]
                        )
                    
    except BaseException as err:
        runtimeWarning(f"Failed to load the reactions database '{fileName}':\n{err}.")

def fromFuels():
    """
    Create oxidation reactions for fuels in Database.chemistry.specie.Molecules.Fuels dictionary
    """
    print("Creating oxidation reactions for fuels:")
    try:
        for fuelName in Molecules.Fuels:
            fuel = Molecules.Fuels[fuelName]
            reactName = fuelName + "-ox"
            print (reactName)
            if not reactName in _theseLocals:
                prod = []
                if periodicTable.N in fuel.atoms:
                    prod.append(Molecules.N2)
                if periodicTable.H in fuel.atoms:
                    prod.append(Molecules.H2O)
                if periodicTable.C in fuel.atoms:
                    prod.append(Molecules.CO2)
                if periodicTable.S in fuel.atoms:
                    prod.append(Molecules.SO2)
                
                print(prod)
                
                _theseLocals[reactName] = \
                    Reaction\
                        (
                            [fuel, Molecules.O2],
                            prod
                        )

    except BaseException as err:
        runtimeWarning(f"Failed to create oxidation reactions for fuels")
        
fileName = Database.location + "/data/Reactions.json"
fromJson(fileName)

del fileName

fromFuels()
