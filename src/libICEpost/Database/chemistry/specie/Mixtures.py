#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023

Mixtures
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from libICEpost.src.base.Functions.runtimeWarning import runtimeWarning

from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture

import json

import libICEpost.Database as Database
from libICEpost.Database import database
Molecules = database.chemistry.specie.Molecules

Mixtures = database.chemistry.specie.addFolder("Mixtures")

#############################################################################
#                                   DATA                                    #
#############################################################################

def fromJson(fileName):
    """
    Add mixtures to the database from a json file.
    """
    try:
        with open(fileName) as f:
            data = json.load(f)
            for mix in data:
                Mixtures[mix] = \
                    Mixture\
                        (
                            [Molecules[mol] for mol in data[mix]["specie"]],
                            data[mix]["composition"],
                            data[mix]["fracType"] if "fracType" in data[mix] else "mole",
                            mix
                        )
            
    except BaseException as err:
        runtimeWarning(f"Failed to load the mixtures database '{fileName}':\n{err}.")
    
fileName = Database.location + "/data/Mixtures.json"
fromJson(fileName)

del fileName
