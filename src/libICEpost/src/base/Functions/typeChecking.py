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

from libICEpost.src import GLOBALS
GLOBALS.DEBUG = True

#############################################################################
#                               MAIN FUNCTIONS                              #
#############################################################################

#Check type of an instance:
def checkType(entry:str, Type:type|tuple[type], entryName:str|None=None, *, intAsFloat:bool=True, checkForNone:bool=False, **kwargs):
    """
    entry:          Instance
        Instance to be checked
    Type:           type|tuple[type]
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
    if not(GLOBALS.DEBUG):
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
        
        #Check Type for type|tuple[type]
        if not(isinstance(Type, (type, tuple))):
            raise TypeError("Wrong type for entry 'Type': 'type' or 'tuple[type]' expected but '{}' was found.".format(Type.__class__.__name__))
        #If Type is tuple, check all elements for type
        if isinstance(Type, tuple):
            if any([not(isinstance(t, type)) for t in Type]):
                raise TypeError(f"Wrong type for entry {[isinstance(t, type) for t in Type].count(False)} items in 'Type': 'type|tuple[type]' expected for entry 'Type'.")
    except BaseException as err:
        fatalErrorInArgumentChecking(None, checkType, err)
        
    if (Type == None.__class__) and not(checkForNone):
        return
    
    if (isinstance(entry, int) and (Type == float) and intAsFloat):
        return
    
    if not(isinstance(entry, Type)):
        if entryName is None:
            raise TypeError("'{}' expected but '{}' was found.".format([t.__name__ for t in Type] if isinstance(Type, tuple) else Type.__name__, entry.__class__.__name__))
        else:
            raise TypeError("Wrong type for entry '{}': '{}' expected but '{}' was found.".format(entryName, Type.__name__, entry.__class__.__name__))

#############################################################################
#Check multiple types of an instance:
def checkTypes(entry, TypeList, entryName=None, **argv):
    """
    entry:          Instance
        Instance to be checked
    TypeList:       list<type>
        Possible types
    entryName:      str  (None)
        Name of the entry to be checked (used as info when raising TypeError)
        
    Keyword arguments:
    
    intAsFloat:     bool (True)
        Treat int as floats for type-checking
    checkForNone:   bool (False)
        If False, no type checking is performed on Type==NoneType
    
    Check if instance 'entry' is of any of the types in 'TypeList'.
    """
    if not(GLOBALS.DEBUG):
        return
    
    inputs = \
        {
            "intAsFloat":True,
            "checkForNone":False
        }
    
    try:
        checkType(entryName, str, entryName="entryName")
        
        inputs.update(argv)
        argv = inputs
        checkType(inputs["intAsFloat"], bool, entryName="intAsFloat")
        checkType(inputs["checkForNone"], bool, entryName="checkForNone")
    except BaseException as err:
        fatalErrorInArgumentChecking(None, checkTypes, err)
    
    isOk = False
    for Type in TypeList:
        try:
            checkType(entry, Type, **argv)
            isOk = True
        except BaseException as e:
            pass
    if not(isOk):
        listNames = ""
        for Type in TypeList:
            listNames += "\n\t" + "{}".format(Type.__name__)
        raise TypeError("Wrong type for entry '{}': '{}' was found, while acceptable types are:{}".format(entryName, entry.__class__.__name__, listNames))


#############################################################################
#Check type of an instance:
def checkInstanceTemplate(entry, templateEntry, entryName=None, **argv):
    """
    entry:          Instance
        Instance to be checked
    templateEntry:  Instance
        Instance to be used as template for argument checking. If the template
        is a container (for example: list) with [len > 0] the check is
        performed recursively for each element of 'entry', comparing against
        the first element of 'templateEntry' instance.
    entryName:      str  (None)
        Name of the entry to be checked (used as info when raising TypeError)
        
    Keyword arguments:
    intAsFloat:     bool (True)
        Treat int as floats for type-checking
    checkForNone:   bool (False)
        If True, check for NoneType in case a template entry is None,
        otherwise it means no check is needed
    allowEmptyContainer:   bool (False)
        If applying recursive type-checking, allow an entry to be an
        empty container even if the template has elements in it.
    
    Check if instance 'entry' is of same type of 'templateEntry',
    checking recursively if the instance is a container.
    """
    if not(GLOBALS.DEBUG):
        return
    
    #Argument checking:
    inputs = \
        {
            "intAsFloat":True,
            "checkForNone":False,
            "allowEmptyContainer":False
        }
    
    try:
        checkType(entryName, str, entryName="entryName")
        
        inputs.update(argv)
        argv = inputs
        checkType(inputs["intAsFloat"], bool, entryName="intAsFloat")
        checkType(inputs["checkForNone"], bool, entryName="checkForNone")
        checkType(inputs["allowEmptyContainer"], bool, entryName="allowEmptyContainer")
    except BaseException as err:
        fatalErrorInArgumentChecking(None, checkInstanceTemplate, err)
    
    #Check entry type:
    checkType(entry, templateEntry.__class__, entryName=entryName, **argv)
    
    #Check for container:
    try:
        test = iter(templateEntry)
    except TypeError:
        return
    
    #If container:
    
    #1) string
    if isinstance(templateEntry, str):
        return
    
    if len(templateEntry) == 0:
        return
    
    if len(entry) == 0:
        if not(inputs["allowEmptyContainer"]):
            raise ValueError("Empty container not allowed for entry '{}'.".format(entryName))
        else:
            return
    
    ii = 0
    for it in entry:
        #2) dict:
        if isinstance(entry, dict):
            #Check only the types of the elements, not types of the keys:
            It = entry[it]
            
            if it in templateEntry:
                key = it
            else:
                key = sorted(list(templateEntry.keys()))[0]
            
            temp = templateEntry[key]
            checkInstanceTemplate(It, temp, entryName=(entryName + "[\"{}\"]".format(it)), **argv)
        else:
            It = it
            temp = templateEntry[0]
            checkInstanceTemplate(It, temp, entryName=(entryName + "[{}]".format(ii)), **argv)
        
        ii += 1
        
#############################################################################
#Check type of an instance:
def updateKeywordArguments(Argv, defaultArgv, **argv):
    """
    Argv:           dict
        Keyword arguments
    defaultArgv:    dict
        Default keyword argumentspeError)
        
    Keyword arguments:
    intAsFloat:     bool (True)
        Treat int as floats for type-checking
    checkForNone:   bool (False)
        If True, check for NoneType in case a template entry is None,
        otherwise it means no check is needed
    allowEmptyContainer:   bool (False)
        If applying recursive type-checking, allow an entry to be an
        empty container even if the template has elements in it.
        
    Check keyword arguments.
    """
    try:
        checkType(Argv, dict, "Argv")
        checkType(defaultArgv, dict, "defaultArgv")
    except BaseException as err:
        fatalErrorInArgumentChecking(None, updateKeywordArguments, err)
    
    #for entry in Argv:
        #if not entry in defaultArgv:
            #raise ValueError("Unknown keyword argument '{}'".format(entry))
        
        checkInstanceTemplate(Argv[entry], defaultArgv[entry], entry, **argv)
    
    out = cp.deepcopy(defaultArgv)
    out.update(Argv)
    
    return out

#############################################################################
#Check type of an instance:
def checkContainer(entry, container, itemType, entryName=None, **argv):
    """
    entry:          Instance
        Instance to be checked
    container:      Type
        Container type
    itemType:       Type
        Type of the elements of the container
    entryName:      str  (None)
        Name of the entry to be checked (used as info when raising TypeError)
        
    Keyword arguments:
    intAsFloat:     bool (True)
        Treat int as floats for type-checking
    allowEmptyContainer:   bool (False)
        Allow the entry to be an empty container.
    
    Check if instance 'entry' is a container of type 'container<itemType>'.
    """
    if not(GLOBALS.DEBUG):
        return
    
    #Argument checking:
    inputs = \
        {
            "intAsFloat":True,
            "allowEmptyContainer":False
        }
    
    try:
        checkType(entryName, str, entryName="entryName")
        checkType(itemType, type, "itemType")
        checkType(container, type, "container")
        
        if not "__iter__" in dir(container):
            raise TypeError("Entry 'container' must be a type that admits iteration for its instaces.")
        
        inputs.update(argv)
        argv = inputs
        checkType(inputs["intAsFloat"], bool, entryName="intAsFloat")
        checkType(inputs["allowEmptyContainer"], bool, entryName="allowEmptyContainer")
    except BaseException as err:
        fatalErrorInArgumentChecking(None, checkInstanceTemplate, err)
    
    #Check container type:
    checkType(entry, container, entryName=entryName, **argv)
    
    #Check if empty:
    if not(inputs["allowEmptyContainer"]) and (len(entry) == 0):
        raise ValueError("Empty container not allowed for entry '{}'.".format(entryName))
    
    #1) string
    if issubclass(container,str):
        return
    
    for it in entry:
        #2) dict:
        if issubclass(container,dict):
            It = entry[it]
            checkType(It, itemType, entryName=(entryName + "[\"{}\"]".format(it)), **argv)
        #3) Others:
        else:
            It = it
            checkType(It, itemType, entryName=(entryName + "[\"{}\"]".format(it)), **argv)
