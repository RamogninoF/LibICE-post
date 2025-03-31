"""
Module containing general purpose functions and classes which are the 
base for the ICEpost library.

## Modules

### enum
Enumeration classes that when instantiated with a value not in the enumeration, list the allowed values.
This extends the functionality of the standard enum module, adding debugging information 
by extending the `EnumType` metaclass.

### dataStructures
Useful data structures for the libICEpost library (e.g. TimeSeries, Dictionary, and Tabulation). 

### filters
Module for definition of filter objects, which can be used to pre-process data before the analysis
(resampling, low-pass filtering, etc.). The filters are defined as classes, which can be used to
create filter objects. The filter objects can be used to filter the data throught the `__call__(x, y)`
method, which returns the filtered (x, y) data.

### Functions
Module with general-purpose functions (e.g. type checking, runtime warnings, IO of OpenFOAM files, etc.).

### BaseClass
This module contains the definition of the abstact base class `BaseClass`, which implements
the base functionality for class inheritance and run-time selection which is used in the 
`libICEpost` library.

### Utilities
Defunes the class `Utilities` wrapping general purpose functions as static methods.
All the classes in the library inherit from this class.

@author: F. Ramognino       <federico.ramognino@polimi.it>
"""
