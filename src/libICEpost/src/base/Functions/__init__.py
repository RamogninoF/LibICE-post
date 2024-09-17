"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        9/03/2023

Package with useful functions.

Content of the package
    typeChecking
        Functions for type-checking. Defines one global variable:
            GLOBALS.DEBUG = True
                If it is set to False, no type-checking is performed (To increase speed)
        
    functionsForOF:
        Functions for reading/writing OpenFOAM files (PyFoam)
    
    functionsForDictionaries:
        Functions for management of dictionaries (DEPRECATED)
        
    runtimeWarning:
        Functions for handling error/warning messages, 
        printing stack, fatalError, etc. Defines one global variable:
            GLOBALS.CUSTOM_ERROR_MESSAGE = False
                If set to True, when a fatal error is handled 
                within the code, the custom error message of the 
                package is shown instead of the default python print-stack
"""
