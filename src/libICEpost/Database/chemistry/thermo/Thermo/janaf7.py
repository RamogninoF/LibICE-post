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

from src.base.Functions.runtimeWarning import runtimeWarning

from src.thermophysicalModels.specie.thermo.Thermo.janaf7 import janaf7

import json

import Database
import Database.chemistry.specie.Molecules

#############################################################################
#                                   DATA                                    #
#############################################################################

_theseLocals = locals()

def fromJson(fileName, typeName="Molecules"):
    """
    Add janaf7 type Thermo to the database from a json file.
    """
    try:
        with open(fileName) as f:
            data = json.load(f)
            for mol in data:
                _theseLocals[mol] = \
                    janaf7\
                        (
                            Database.chemistry.specie.Molecules.__dict__[mol],
                            data[mol]["lowCpCoeffs"],
                            data[mol]["highCpCoeffs"],
                            data[mol]["Tcommon"],
                            data[mol]["Tlow"],
                            data[mol]["Thigh"]
                        )
                
    except BaseException as err:
        runtimeWarning(f"Failed to load the mixtures database '{fileName}':\n{err}.")

fileName = Database.location + "/data/janaf7.json"
fromJson(fileName)

del fileName
