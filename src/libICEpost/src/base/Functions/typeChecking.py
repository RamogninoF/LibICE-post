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
from typing import Any

from libICEpost import GLOBALS

import numpy as np
from typing import _SpecialGenericAlias, Iterable, Mapping

#############################################################################
#                               MAIN FUNCTIONS                              #
#############################################################################

#Check type of an instance:
def checkType(entry:Any, Type:type|Iterable[type|_SpecialGenericAlias], entryName:str|None=None, *, intAsFloat:bool=True, checkForNone:bool=False, **kwargs) -> None:
    """
    Check the type of an instance.

    Arguments:
        entry (Any): Instance to be checked.
        Type (type | Iterable[type | _SpecialGenericAlias]): Type required.
        entryName (str, optional): Name of the entry to be checked (used as info when raising TypeError).
        intAsFloat (bool, optional): Treat int as floats for type-checking (default is True).
        checkForNone (bool, optional): If False, no type checking is performed on Type==NoneType (default is False).
        **kwargs: Additional keyword arguments to discard.

    Raises:
        TypeError: If 'entry' is not of the specified 'Type'.
            
    Returns:
        None
    """
    if not GLOBALS.__TYPE_CHECKING__:
        return
    
    #Argument checking:
    if not(entryName is None):
        if not(isinstance(entryName, str)):
            raise TypeError("Wrong type for entry '{}': '{}' expected but '{}' was found.".format("entryName", str.__name__, entryName.__class__.__name__))
    
    if not(isinstance(intAsFloat, bool)):
        raise TypeError("Wrong type for entry '{}': '{}' expected but '{}' was found.".format("intAsFloat", bool.__name__, intAsFloat.__class__.__name__))
    
    if not(isinstance(checkForNone, bool)):
        raise TypeError("Wrong type for entry '{}': '{}' expected but '{}' was found.".format("checkForNone", bool.__name__, checkForNone.__class__.__name__))
    
    #Check Type for type|Iterable|_SpecialGenericAlias
    if not(isinstance(Type, (type, Iterable, _SpecialGenericAlias))):
        raise TypeError("Wrong type for entry 'Type': 'type' or 'Iterable[type]' expected but '{}' was found.".format(Type.__class__.__name__))
    
    #If Type is Iterable, check all elements for type|_SpecialGenericAlias
    if isinstance(Type, Iterable):
        Type = tuple(Type) #Cast to tuple
        if any([not(isinstance(t, (type,_SpecialGenericAlias))) for t in Type]):
            raise TypeError(f"Wrong type for entry {[isinstance(t, type) for t in Type].count(False)} items in 'Type': 'type|Iterable[type]' expected for entry 'Type'.")
        
    # If checkForNone is False, no type checking is performed on Type==NoneType
    if (Type == None.__class__) and not(checkForNone):
        return
    
    #If intAsFloat is True, treat int as float
    if (isinstance(entry, (int,np.integer))
        and 
        (any([issubclass(t,(float, np.floating)) for t in Type]) if isinstance(Type, Iterable) else issubclass(Type,(float, np.floating))) # Handle iterable of types
        and intAsFloat):
        return
    
    #Check type
    if not(isinstance(entry, Type)):
        if entryName is None:
            raise TypeError("'{}' expected but '{}' was found.".format([t.__name__ for t in Type] if isinstance(Type, Iterable) else Type.__name__, entry.__class__.__name__))
        else:
            raise TypeError("Wrong type for entry '{}': '{}' expected but '{}' was found.".format(entryName, ([t.__name__ for t in Type] if isinstance(Type, Iterable) else Type.__name__), entry.__class__.__name__))

#############################################################################
def checkArray(array:Iterable, Type:type|Iterable[type|_SpecialGenericAlias]|_SpecialGenericAlias, entryName:str="array", **kwargs):
    """
    Check the type of elements in an array.
    
    Arguments:
        array (Iterable): Array to be checked.
        Type (type | Iterable[type | _SpecialGenericAlias]): Type required for the elements.
        entryName (str, optional): Name of the array to be checked (used as info when raising TypeError).
        **kwargs: Additional keyword arguments to pass to checkType function.
    
    Raises:
        TypeError: If any element in 'array' is not of the specified 'Type' or if 'array' is not iterable.
    """
    if not GLOBALS.__TYPE_CHECKING__:
        return
    
    #Check if array is iterable
    checkType(array, Iterable, "array")
    
    if GLOBALS.__SAFE_ITERABLE_CHECKING__: #Check all elements
        [checkType(entry, Type, f"{entryName}[{ii}]", **kwargs) for ii,entry in enumerate(array)]
    elif len(array) > 0: #Check only the first element
        checkType(array[0], Type, f"{entryName}[0]", **kwargs)
    else: #Empty array
        return

#############################################################################
def checkMap(map:Mapping, keyType:type|Iterable[type|_SpecialGenericAlias], valueType:type|Iterable[type|_SpecialGenericAlias], entryName:str="map", **kwargs):
    """
    Check the type of keys and values in a map.
    
    Arguments:
        map (Mapping): Map to be checked.
        keyType (type | Iterable[type | _SpecialGenericAlias]): Type required for the keys.
        valueType (type | Iterable[type | _SpecialGenericAlias]): Type required for the values.
        entryName (str, optional): Name of the map to be checked (used as info when raising TypeError).
        **kwargs: Additional keyword arguments to pass to checkType function.
    
    Raises:
        TypeError: If any key or value in 'map' is not of the specified 'keyType' or 'valueType' or if 'map' is not a dict.
    """
    if not GLOBALS.__TYPE_CHECKING__:
        return
    
    #Check if map is a dict
    checkType(map, Mapping, "map")
    
    if GLOBALS.__SAFE_ITERABLE_CHECKING__: #Check all keys and values
        [checkType(key, keyType, f"{entryName}.keys()[{ii}]", **kwargs) for ii,key in enumerate(map.keys())]
        [checkType(value, valueType, f"{entryName}.values()[{ii}]", **kwargs) for ii,value in enumerate(map.values())]
    elif len(map) > 0: #Check only the first key and value
        checkType(list(map.keys())[0], keyType, f"{entryName}.keys()[0]", **kwargs)
        checkType(list(map.values())[0], valueType, f"{entryName}.values()[0]", **kwargs)
    else: #Empty map
        return