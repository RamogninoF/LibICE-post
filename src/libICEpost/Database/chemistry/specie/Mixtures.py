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

from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture

import json

import libICEpost.Database as Database
from libICEpost.Database import database

from  libICEpost.Database.chemistry.specie.Molecules import Molecules

Mixtures = database.chemistry.specie.addFolder("Mixtures")

#############################################################################
#                                   DATA                                    #
#############################################################################

#Define method for loading from json dictionary
def fromJson(fileName:str) -> None:
    """
    Add mixtures to the database from a json file.
    """
    from libICEpost.Database import database

    from  libICEpost.Database.chemistry.specie.Molecules import Molecules
    Mixtures = database.chemistry.specie.Mixtures

    with open(fileName) as f:
        data = json.load(f)
        for mix in data:
            Mixtures[mix] = \
                Mixture\
                    (
                        [Molecules[mol] for mol in data[mix]["specie"]],
                        data[mix]["composition"],
                        data[mix]["fracType"] if "fracType" in data[mix] else "mole"
                    )

#Load database
fileName = Database.location + "/data/Mixtures.json"
fromJson(fileName)
del fileName

#Add method to database
Mixtures.fromJson = fromJson
