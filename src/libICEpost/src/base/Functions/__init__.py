"""
Module with general-purpose functions.

## Modules

### typeChecking
This module provides functions to check the type of variables and their
elements, including arrays and maps. It raises TypeError if the types
do not match the expected ones.
It defines:
- `checkType` (function): Check the type of an instance.
- `checkArray` (function): Check the type of elements in an Iterable.
- `checkMap` (function): Check the type of keys and values in a Mapping.

### runtimeWarning
This module provides functions for warnings and error messages.
It defines:
- `printStack` (function): print the current call-stack (`deprecated`)
- `runtimeWarning` (function): print a runtime warning message and the call-stack (`deprecated`)
- `runtimeError` (function): print a runtime error message and the call-stack (`deprecated`)
- `helpOnFail` (decorator): decorator for printing the help of a function in case of failure

### functionsForOF
This module provides functions used to handle OpenFOAM files.
It defines:
- `readOFscalarList` (function): Read an OpenFOAM file with a scalar list.
- `writeOFscalarList` (function): Write an OpenFOAM file with a scalar list.

@author: F. Ramognino       <federico.ramognino@polimi.it>
"""