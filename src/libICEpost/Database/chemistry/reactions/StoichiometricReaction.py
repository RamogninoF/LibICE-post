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

from libICEpost.src.base.Functions.runtimeWarning import fatalErrorInFunction

from libICEpost.src.thermophysicalModels.specie.reactions.Reaction.StoichiometricReaction import StoichiometricReaction

import json

import libICEpost.Database as Database
from libICEpost.Database import database
periodicTable = database.chemistry.specie.periodicTable
Molecules = database.chemistry.specie.Molecules

StoichiometricReaction_db = database.chemistry.reactions.addFolder("StoichiometricReaction")

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
    StoichiometricReaction_db = database.chemistry.reactions.StoichiometricReaction
    try:
        with open(fileName) as f:
            data = json.load(f)
            for react in data:
                StoichiometricReaction_db[react] = \
                    StoichiometricReaction\
                        (
                            [Molecules[mol] for mol in data[react]["reactants"]],
                            [Molecules[mol] for mol in data[react]["products"]]
                        )
                    
    except BaseException as err:
        fatalErrorInFunction(fromJson,f"Failed to load the reactions database '{fileName}':\n{err}.")

#Create oxidation reactions from Fuels database
def fromFuels():
    """
    Create oxidation reactions for fuels in Database.chemistry.specie.Molecules.Fuels dictionary
    """
    from libICEpost.Database import database
    periodicTable = database.chemistry.specie.periodicTable
    Molecules = database.chemistry.specie.Molecules
    Fuels = database.chemistry.specie.Fuels
    StoichiometricReaction_db = database.chemistry.reactions.StoichiometricReaction

    #print("Creating oxidation reactions for fuels:")
    try:
        for fuelName in Fuels:
            fuel = Fuels[fuelName]
            reactName = fuelName + "-ox"
            if not reactName in StoichiometricReaction_db:
                prod = []
                if periodicTable.N in fuel.atoms:
                    prod.append(Molecules.N2)
                if periodicTable.H in fuel.atoms:
                    prod.append(Molecules.H2O)
                if periodicTable.C in fuel.atoms:
                    prod.append(Molecules.CO2)
                if periodicTable.S in fuel.atoms:
                    prod.append(Molecules.SO2)
                
                StoichiometricReaction_db[reactName] = \
                    StoichiometricReaction\
                        (
                            [fuel, Molecules.O2],
                            prod
                        )
                #print(f"\t",reactName + ":",Reactions[reactName])

    except BaseException as err:
        fatalErrorInFunction(fromJson,f"Failed to create oxidation reactions for fuels", err)

#Load database
fileName = Database.location + "/data/StoichiometricReaction.json"
fromJson(fileName)
del fileName

fromFuels()

#Add methods to database
StoichiometricReaction_db.fromJson = fromJson
StoichiometricReaction_db.fromFuels = fromFuels