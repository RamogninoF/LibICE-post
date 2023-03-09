#####################################################################
#                                  DOC                              #
#####################################################################

"""
Functions for type checking.
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

import copy as cp
import inspect

from src import GLOBALS
GLOBALS.DEBUG = True

#############################################################################
#                               MAIN FUNCTIONS                              #
#############################################################################

#Check type of an instance:
def checkType(entry, Type, entryName=None, **argv):
    """
    entry:          Instance
        Instance to be checked
    Type:           type
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
    
    inputs = \
        {
            "intAsFloat":True,
            "checkForNone":False
        }
    
    inputs.update(argv)
    
    if not(entryName is None):
        if not(isinstance(entryName, str)):
            raise TypeError("Wrong type for entry '{}': '{}' expected but '{}' was found.".format("entryName", str.__name__, entryName.__class__.__name__))
    
    if not(isinstance(inputs["intAsFloat"], bool)):
        raise TypeError("Wrong type for entry '{}': '{}' expected but '{}' was found.".format("intAsFloat", bool.__name__, inputs["intAsFloat"].__class__.__name__))
    
    if not(isinstance(inputs["checkForNone"], bool)):
        raise TypeError("Wrong type for entry '{}': '{}' expected but '{}' was found.".format("checkForNone", bool.__name__, inputs["checkForNone"].__class__.__name__))
    
    if not(isinstance(Type, type)):
        raise TypeError("Wrong type for entry '{}': '{}' expected but '{}' was found.".format("Type", type.__name__, Type.__class__.__name__))
    
    if (Type == None.__class__) and not(inputs["checkForNone"]):
        return
    
    if (isinstance(entry, int) and (Type == float) and inputs["intAsFloat"]):
        return
    
    if not(isinstance(entry, Type)):
        if entryName is None:
            raise TypeError("'{}' expected but '{}' was found.".format(Type.__name__, entry.__class__.__name__))
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
    
    checkType(entryName, str, entryName="entryName")
    
    inputs.update(argv)
    argv = inputs
    checkType(inputs["intAsFloat"], bool, entryName="intAsFloat")
    checkType(inputs["checkForNone"], bool, entryName="checkForNone")
    
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
        If True, check for NoneType in case an entry is None,
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
    
    
    checkType(entryName, str, entryName="entryName")
    
    inputs.update(argv)
    argv = inputs
    checkType(inputs["intAsFloat"], bool, entryName="intAsFloat")
    checkType(inputs["checkForNone"], bool, entryName="checkForNone")
    checkType(inputs["allowEmptyContainer"], bool, entryName="allowEmptyContainer")
    
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
        #3) Others:
        else:
            It = it
            temp = templateEntry[0]
            checkInstanceTemplate(It, temp, entryName=(entryName + "[{}]".format(ii)), **argv)
        
        ii += 1
        
#############################################################################
#Check type of an instance:
def updateKeywordArguments(argv, defaultArgv):
    """
    argv:           dict
        Keyword arguments
    defaultArgv:    dict
        Default keyword arguments
        
    Check keyword arguments.
    """
    checkType(argv, dict, "argv")
    checkType(defaultArgv, dict, "defaultArgv")
    
    for entry in argv:
        if not entry in defaultArgv:
            raise ValueError("Unknown keyword argument '{}'".format(entry))
        
        checkInstanceTemplate(argv[entry], defaultArgv[entry], entry)
    
    out = cp.deepcopy(defaultArgv)
    out.update(argv)
    
    return out
