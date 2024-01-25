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
from src.thermophysicalModels.specie.specie.Atom import Atom

#############################################################################
#                                   DATA                                    #
#############################################################################

#Periodic table of atoms
for ii, atom in enumerate(periodic.symbols):
    locals()[atom] = \
        Atom\
            (
                atom,
                periodic.relative_atomic_masses[ii]
            )

del ii, atom
