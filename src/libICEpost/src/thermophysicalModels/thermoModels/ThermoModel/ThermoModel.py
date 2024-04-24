#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023
"""

# Necessito:
# 1) Definire lo stato del sistema (dataclass?)
# 2) Metodi update() _update() per aggiornare il sistema e propagare in basso, eventualmente fornendo un nuovo stato (tramite dizionario? dataclass?)

# Nelle classi derivate devo:
# 1) Definire metodo _update()
# 2) Definire I/O dei parametri (properties) che a loro volta aggiornino lo stato

#####################################################################
#                               IMPORT                              #
#####################################################################

from libICEpost.src.base.BaseClass import BaseClass

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class ThermoModel(BaseClass):
    """
    Base class for handling a thermodynamic model
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    """
    #Nothing by now
    pass
    #########################################################################
    #Properties:
    
    #########################################################################
    #Constructor:
    
    #########################################################################
    #Operators:
    
    ################################
    
    #########################################################################
    #Methods:
    
    ################################
    
#########################################################################
#Create selection table:
ThermoModel.createRuntimeSelectionTable()