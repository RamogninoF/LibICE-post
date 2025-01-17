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

import json

import libICEpost.Database as Database
from libICEpost.Database import database

from libICEpost.src.thermophysicalModels.specie.specie import Molecule
Molecules = database.chemistry.specie.Molecules

constantCp_db = database.chemistry.thermo.Thermo.addFolder("constantCp")

#############################################################################
#                                   DATA                                    #
#############################################################################

#Define method to load from json dictionay
def fromJson(fileName, typeName="Molecules"):
    """
    Add constantCp type Thermo to the database from a json file. 
    Dictionaries containing either cp [J/kgK], cv [J/kgK], or 
    gamma of the mixture, and hf [J/kg] (optional).
    The specie must be already present in the molecule database
    (database.chemistry.specie.Molecules) and the name of its 
    dictionary consistent with it.

    Example:
    {
        "N2":
        {
            "cp":1036.8,
            "hf":0.0
        }
    }
    """
    from libICEpost.src.thermophysicalModels.specie.thermo.Thermo.constantCp import constantCp

    from libICEpost.Database import database
    from libICEpost.src.thermophysicalModels.specie.specie import Molecule
    Molecules = database.chemistry.specie.Molecules
    constantCp_db = database.chemistry.thermo.Thermo.constantCp
    
    with open(fileName) as f:
        data = json.load(f)
        for mol in data:
            Dict = {}
            for var in ["cp", "hf"]:
                if var in data[mol]:
                    Dict[var] = data[mol][var]
                else:
                    raise ValueError(f"Missing input key {var} for entry {mol}")

            constantCp_db[mol] = \
                constantCp\
                    (
                        Molecules[mol].Rgas,
                        Dict["cp"],
                        Dict["hf"]
                    )

#Load database
fileName = Database.location + "/data/constantCp.json"
fromJson(fileName)
del fileName

#Add method to database
constantCp_db.fromJson = fromJson
