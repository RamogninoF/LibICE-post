"""
Module for definition of tabulation objects, which can be used to store data in a tabular format.

## Modules

### BaseTabulation
Abstract base class and geneal-purpose functions for tabulations, containing data in a 
structured grid in an n-dimensional space of input-variables.

### Tabulation
Tabulation class for storing, accessing, and manipulating tabulated data.
It provides methods for slicing, concatenating, and plotting the data, as well as for
interpolating between data points. The class is designed to work with n-dimensional data
and can handle missing data points.
    
### OFTabulation
OpenFOAM tabulation class. The tabulation is a multi-input multi-output, i.e., it access through a
set of input variables (IV) to a set of tabulated variables (TV):
    [IV1, IV2, IV3, ...] -> [TV1, TV2, TV3, ...]

@author: F. Ramognino       <federico.ramognino@polimi.it>
"""
