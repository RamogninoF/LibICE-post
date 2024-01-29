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

from libICEpost.src.base.Functions.runtimeWarning import runtimeWarning

from libICEpost.src.thermophysicalModels.specie.thermo.Reaction import Reaction

import json

import libICEpost.Database as Database
from libICEpost.Database import database
periodicTable = database.chemistry.specie.periodicTable
Molecules = database.chemistry.specie.Molecules

Reactions = database.chemistry.thermo.addFolder("Reactions")

#############################################################################
#                                   DATA                                    #
#############################################################################

#Define loading from dictionary in json format
def fromJson(fileName):
    """
    Add reactions to the database from a json file.
    """
    from libICEpost.Database import database
    Molecules = database.chemistry.specie.Molecules
    Reactions = database.chemistry.thermo.Reactions

    try:
        with open(fileName) as f:
            data = json.load(f)
            for react in data:
                Reactions[react] = \
                    Reaction\
                        (
                            [Molecules[mol] for mol in data[react]["reactants"]],
                            [Molecules[mol] for mol in data[react]["products"]]
                        )
                    
    except BaseException as err:
        runtimeWarning(f"Failed to load the reactions database '{fileName}':\n{err}.")

#Create oxidation reactions from Fuels database
def fromFuels():
    """
    Create oxidation reactions for fuels in Database.chemistry.specie.Molecules.Fuels dictionary
    """
    from libICEpost.Database import database
    periodicTable = database.chemistry.specie.periodicTable
    Molecules = database.chemistry.specie.Molecules
    Fuels = database.chemistry.specie.Fuels
    Reactions = database.chemistry.thermo.Reactions

    print("Creating oxidation reactions for fuels:")
    try:
        for fuelName in Fuels:
            fuel = Fuels[fuelName]
            reactName = fuelName + "-ox"
            print (reactName)
            if not reactName in Reactions:
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
                
                Reactions[reactName] = \
                    Reaction\
                        (
                            [fuel, Molecules.O2],
                            prod
                        )

    except BaseException as err:
        runtimeWarning(f"Failed to create oxidation reactions for fuels")

#Load database
fileName = Database.location + "/data/Reactions.json"
fromJson(fileName)
del fileName

fromFuels()

#Add methods to database
Reactions.fromJson = fromJson
Reactions.fromFuels = fromFuels