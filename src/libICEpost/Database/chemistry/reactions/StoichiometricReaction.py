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

from libICEpost.src.thermophysicalModels.specie.reactions.Reaction.StoichiometricReaction import StoichiometricReaction

import json

import libICEpost.Database as Database
from libICEpost.Database import database
periodicTable = database.chemistry.specie.periodicTable
Molecules = database.chemistry.specie.Molecules
Fuels = database.chemistry.specie.Fuels
Oxidizers = database.chemistry.specie.Oxidizers

StoichiometricReaction_db = database.chemistry.reactions.addFolder("StoichiometricReaction")

#############################################################################
#                                   DATA                                    #
#############################################################################

#Define loading from dictionary in json format
def fromJson(fileName):
    """
    Add reactions to the database from a json file.
    """
    with open(fileName) as f:
        data = json.load(f)
        for react in data:
            StoichiometricReaction_db[react] = \
                StoichiometricReaction\
                    (
                        [Molecules[mol] for mol in data[react]["reactants"]],
                        [Molecules[mol] for mol in data[react]["products"]]
                    )


#Load database
fileName = Database.location + "/data/StoichiometricReaction.json"
fromJson(fileName)
del fileName

#Oxidation reactions of fuels with O2
for fuelName in Fuels:
    fuel = Fuels[fuelName]
    reactName = fuel.name + "-ox"
    StoichiometricReaction_db[reactName] = StoichiometricReaction.fromFuelOxidation(fuel)

#Reduction reactions of reducers that are not O2
for oxidizerName in Oxidizers:
    oxidizer = Oxidizers[oxidizerName]
    reactName = oxidizer.name + "-red"
    StoichiometricReaction_db[reactName] = StoichiometricReaction.fromOxidizerReduction(oxidizer)

#Add methods to database
StoichiometricReaction_db.fromJson = fromJson