#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023

Chemical constants
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from libICEpost.Database import database

database.chemistry.addFolder("constants")

#############################################################################
#                                   DATA                                    #
#############################################################################

database.chemistry.constants.Rgas = 8.314462*1e3

database.chemistry.constants.Tstd = 298.15      # [K]
database.chemistry.constants.pstd = 101325      # [Pa]
