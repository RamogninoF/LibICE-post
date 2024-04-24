#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023

janaf7 thermodynamic propeties
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from libICEpost.src.base.Functions.runtimeWarning import fatalErrorInFunction
import json

import libICEpost.Database as Database
from libICEpost.Database import database

from libICEpost.src.thermophysicalModels.specie.specie import Molecule
Molecules = database.chemistry.specie.Molecules

janaf7_db = database.chemistry.thermo.Thermo.addFolder("janaf7")

#############################################################################
#                                   DATA                                    #
#############################################################################

#Define method to load from json dictionay
def fromJson(fileName, typeName="Molecules"):
    """
    Add janaf7 type Thermo to the database from a json file.
    """
    from libICEpost.src.thermophysicalModels.specie.thermo.Thermo.janaf7 import janaf7

    from libICEpost.Database import database
    from libICEpost.src.thermophysicalModels.specie.specie import Molecule
    Molecules = database.chemistry.specie.Molecules
    janaf7_db = database.chemistry.thermo.Thermo.janaf7
    
    try:
        with open(fileName) as f:
            data = json.load(f)
            for mol in data:
                janaf7_db[mol] = \
                    janaf7\
                        (
                            Molecules[mol].Rgas,
                            data[mol]["lowCpCoeffs"],
                            data[mol]["highCpCoeffs"],
                            data[mol]["Tcommon"],
                            data[mol]["Tlow"],
                            data[mol]["Thigh"]
                        )
                
    except BaseException as err:
        fatalErrorInFunction(fromJson,f"Failed to load the janaf7 database '{fileName}'", err)

#Load database
fileName = Database.location + "/data/janaf7.json"
fromJson(fileName)
del fileName

#Add method to database
janaf7_db.fromJson = fromJson
