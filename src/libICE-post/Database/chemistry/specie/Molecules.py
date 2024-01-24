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

from src.base.Functions.runtimeWarning import runtimeWarning

from src.thermophysicalModels.specie.specie.Molecule import Molecule

import json

import Database
import Database.chemistry.specie.periodicTable

#############################################################################
#                                   DATA                                    #
#############################################################################

Molecules = {}
Fuels = {}

_theseLocals = locals()

def fromJson(fileName, typeName="Molecules"):
    """
    Add molecules to the database from a json file.
    """
    try:
        with open(fileName) as f:
            data = json.load(f)
            for mol in data:
                _theseLocals[mol] = \
                    Molecule\
                        (
                            data[mol]["name"],
                            [Database.chemistry.specie.periodicTable.__dict__[atom] for atom in data[mol]["specie"]],
                            data[mol]["atoms"]
                        )
                    
                if typeName == "Molecules":
                    Molecules[mol] = _theseLocals[mol]
                elif typeName == "Fuels":
                    Fuels[mol] = _theseLocals[mol]
                else:
                    raise ValueError(f"Invalid typeName {typeName}. Available are:\t Molecules, Fuels.")
            
    except BaseException as err:
        runtimeWarning(f"Failed to load the molecule database '{fileName}':\n{err}.")

fileName = Database.location + "/data/Molecules.json"
fromJson(fileName, "Molecules")

fileName = Database.location + "/data/Fuels.json"
fromJson(fileName, "Fuels")

del fileName
