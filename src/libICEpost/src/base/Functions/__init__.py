"""
Module with general-purpose functions.

## Modules

### typeChecking
This module provides functions to check the type of variables and their
elements, including arrays and maps. It raises TypeError if the types
do not match the expected ones.

### runtimeWarning
This module provides functions for warnings and error messages.

### functionsForOF
This module provides functions used to handle OpenFOAM files.

@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        9/03/2023

Package with useful functions.

Content of the package
    typeChecking
        Functions for type-checking. Defines one global variable:
            GLOBALS.DEBUG = True
                If it is set to False, no type-checking is performed (To increase speed)
        
    functionsForOF:
        Functions for reading/writing OpenFOAM files (foamlib)
    
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
