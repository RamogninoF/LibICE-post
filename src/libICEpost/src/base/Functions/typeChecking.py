#####################################################################
#                                  DOC                              #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023

Functions for type checking.
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

import copy as cp
import inspect
from .runtimeWarning import fatalErrorInArgumentChecking

from libICEpost import GLOBALS

import numpy as np
from typing import _SpecialGenericAlias, Iterable

#############################################################################
#                               MAIN FUNCTIONS                              #
#############################################################################

#Check type of an instance:
def checkType(entry:str, Type:type|Iterable[type|_SpecialGenericAlias], entryName:str|None=None, *, intAsFloat:bool=True, checkForNone:bool=False, **kwargs):
    """
    entry:          Instance
        Instance to be checked
    Type:           type|_SpecialGenericAlias|Iterable[type|_SpecialGenericAlias]
        Type required
    entryName:      str  (None)
        Name of the entry to be checked (used as info when raising TypeError)
        
    Keyword arguments:
    
    intAsFloat:     bool (True)
        Treat int as floats for type-checking
    checkForNone:   bool (False)
        If False, no type checking is performed on Type==NoneType
    
    Check if instance 'entry' is of type of 'Type'.
    """
    if not(GLOBALS.__DEBUG__):
        return
    
    #Argument checking:
    try:
        if not(entryName is None):
            if not(isinstance(entryName, str)):
                raise TypeError("Wrong type for entry '{}': '{}' expected but '{}' was found.".format("entryName", str.__name__, entryName.__class__.__name__))
        
        if not(isinstance(intAsFloat, bool)):
            raise TypeError("Wrong type for entry '{}': '{}' expected but '{}' was found.".format("intAsFloat", bool.__name__, inputs["intAsFloat"].__class__.__name__))
        
        if not(isinstance(checkForNone, bool)):
            raise TypeError("Wrong type for entry '{}': '{}' expected but '{}' was found.".format("checkForNone", bool.__name__, inputs["checkForNone"].__class__.__name__))
        
        #Check Type for type|Iterable[type]
        if not(isinstance(Type, (type, Iterable, _SpecialGenericAlias))):
            raise TypeError("Wrong type for entry 'Type': 'type' or 'Iterable[type]' expected but '{}' was found.".format(Type.__class__.__name__))
        #If Type is tuple, check all elements for type
        if isinstance(Type, Iterable):
            Type = tuple(Type) #Cast to tuple
            if any([not(isinstance(t, (type,_SpecialGenericAlias))) for t in Type]):
                raise TypeError(f"Wrong type for entry {[isinstance(t, type) for t in Type].count(False)} items in 'Type': 'type|Iterable[type]' expected for entry 'Type'.")
    except BaseException as err:
        fatalErrorInArgumentChecking(None, checkType, err)
        
    if (Type == None.__class__) and not(checkForNone):
        return
    
    if (isinstance(entry, (int,np.integer))
        and 
        (any([issubclass(t,(float, np.floating)) for t in Type]) if isinstance(Type, Iterable) else issubclass(Type,(float, np.floating))) # Handle iterable of types
        and intAsFloat):
        return
    
    if not(isinstance(entry, Type)):
        if entryName is None:
            raise TypeError("'{}' expected but '{}' was found.".format([t.__name__ for t in Type] if isinstance(Type, Iterable) else Type.__name__, entry.__class__.__name__))
        else:
            raise TypeError("Wrong type for entry '{}': '{}' expected but '{}' was found.".format(entryName, ([t.__name__ for t in Type] if isinstance(Type, Iterable) else Type.__name__), entry.__class__.__name__))