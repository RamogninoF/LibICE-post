#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023

Atomic specie
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from chempy.util import periodic
from libICEpost.src.thermophysicalModels.specie.specie.Atom import Atom

from libICEpost.Database import database, _DatabaseClass
periodicTable:dict[str,Atom] = database.chemistry.specie.addFolder("periodicTable")

#############################################################################
#                                   DATA                                    #
#############################################################################

#Periodic table of atoms
for ii, atom in enumerate(periodic.symbols):
    periodicTable[atom] = \
        Atom\
            (
                atom,
                periodic.relative_atomic_masses[ii]
            )

del ii, atom