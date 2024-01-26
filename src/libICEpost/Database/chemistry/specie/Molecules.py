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

from libICEpost.src.base.Functions.runtimeWarning import runtimeWarning

from libICEpost.src.thermophysicalModels.specie.specie.Molecule import Molecule

import json

import libICEpost.Database as Database

from libICEpost.Database import database
periodicTable = database.chemistry.specie.periodicTable

Molecules = database.chemistry.specie.addFolder("Molecules")
Fuels = database.chemistry.specie.addFolder("Fuels")

#############################################################################
#                                   DATA                                    #
#############################################################################
def fromJson(fileName, typeName="Molecules"):
    """
    Add molecules to the database from a json file.
    """
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
        runtimeWarning(f"Failed to load the molecule database '{fileName}':\n{err}.")

fileName = Database.location + "/data/Molecules.json"
fromJson(fileName, "Molecules")

fileName = Database.location + "/data/Fuels.json"
fromJson(fileName, "Fuels")

del fileName
