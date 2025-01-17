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

from libICEpost.src.thermophysicalModels.specie.specie.Molecule import Molecule

import json

import libICEpost.Database as Database
from libICEpost.Database import database

Molecules:dict[str,Molecule] = database.chemistry.specie.addFolder("Molecules")
Fuels:dict[str,Molecule] = database.chemistry.specie.addFolder("Fuels")
Oxidizers:dict[str,Molecule] = database.chemistry.specie.addFolder("Oxidizers")

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
                
            if typeName != "Molecules":
                moleculeClass = database.chemistry.specie[typeName] if typeName in database.chemistry.specie else database.chemistry.specie.addFolder(typeName)
                moleculeClass[mol] = Molecules[mol]

#Load database
fileName = Database.location + "/data/Molecules.json"
fromJson(fileName, "Molecules")

fileName = Database.location + "/data/Fuels.json"
fromJson(fileName, "Fuels")

fileName = Database.location + "/data/Oxidizers.json"
fromJson(fileName, "Oxidizers")

del fileName

#Add method to database
Molecules.fromJson = fromJson
