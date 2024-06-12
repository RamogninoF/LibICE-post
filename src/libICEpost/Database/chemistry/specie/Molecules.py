#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023

Chemical specie
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from libICEpost.src.base.Functions.runtimeWarning import fatalErrorInFunction

from libICEpost.src.thermophysicalModels.specie.specie.Molecule import Molecule

import json

import libICEpost.Database as Database
from libICEpost.Database import database

Molecules = database.chemistry.specie.addFolder("Molecules")
Fuels = database.chemistry.specie.addFolder("Fuels")

#############################################################################
#                                   DATA                                    #
#############################################################################

#Define method to load from dictionary
def fromJson(fileName, typeName="Molecules"):
    """
    Add molecules to the database from a json file.
    """

    from libICEpost.Database import database
    from libICEpost.Database.chemistry.specie.periodicTable import periodicTable
    Molecules = database.chemistry.specie.Molecules
    Fuels = database.chemistry.specie.Fuels

    try:
        with open(fileName) as f:
            data = json.load(f)
            for mol in data:
                Molecules[mol] = \
                    Molecule\
                        (
                            data[mol]["name"],
                            [periodicTable[atom] for atom in data[mol]["specie"]],
                            data[mol]["atoms"]
                        )
                    
                if typeName == "Fuels":
                    Fuels[mol] = Molecules[mol]
                elif not (typeName == "Molecules"):
                    raise ValueError(f"Invalid typeName {typeName}. Available are:\t Molecules, Fuels.")
            
    except BaseException as err:
        fatalErrorInFunction(fromJson, f"Failed to load the molecule database '{fileName}':\n{err}.")

#Load database
fileName = Database.location + "/data/Molecules.json"
fromJson(fileName, "Molecules")

fileName = Database.location + "/data/Fuels.json"
fromJson(fileName, "Fuels")

del fileName

#Add method to database
Molecules.fromJson = fromJson
