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
    
    Check if instance 'entry' is of type of 'Type'.
    """
    inputs = \
        {
            "intAsFloat":True
        }
    
    inputs.update(argv)
    intAsFloat = inputs["intAsFloat"]
    
    if not(entryName is None):
        if not(isinstance(entryName, str)):
            raise TypeError("Wrong type for entry '{}': '{}' expected but '{}' was found.".format("entryName", str.__name__, entryName.__class__.__name__))
    
    if not(isinstance(intAsFloat, bool)):
        raise TypeError("Wrong type for entry '{}': '{}' expected but '{}' was found.".format("intAsFloat", bool.__name__, intAsFloat.__class__.__name__))
    
    if not(isinstance(Type, type)):
        raise TypeError("Wrong type for entry '{}': '{}' expected but '{}' was found.".format("Type", type.__name__, Type.__class__.__name__))
    
    if (isinstance(entry, int) and (Type == float) and intAsFloat):
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
    
    Check if instance 'entry' is of any of the types in 'TypeList'.
    """
    
    inputs = \
        {
            "intAsFloat":True
        }
    
    inputs.update(argv)
    intAsFloat = inputs["intAsFloat"]
    
    #Argument checking:
    if not(entryName is None):
        checkType(entryName, str, entryName="entryName")
    checkType(intAsFloat, bool, entryName="intAsFloat")
    checkInstanceTemplate(TypeList, [type], entryName="TypeList")
    
    isOk = False
    for Type in TypeList:
        try:
            checkType(entry, Type, intAsFloat=intAsFloat)
            isOk = True
        except:
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
    
    Check if instance 'entry' is of same type of 'templateEntry',
    checking recursively if the instance is a container.
    """
    #Argument checking:
    inputs = \
        {
            "entryName":"",
            "intAsFloat":True
        }
    
    inputs.update(argv)
    intAsFloat = inputs["intAsFloat"]
    
    checkType(entryName, str, entryName="entryName")
    checkType(intAsFloat, bool, entryName="intAsFloat")
    
    #Check entry type:
    checkType(entry, templateEntry.__class__, entryName=entryName, intAsFloat=intAsFloat)
    
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
        raise ValueError("'templateEntry' is a container, but entry '{}' is empty. Cannot apply recursive type-checking on empty container.".format(entryName))
    
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
            checkInstanceTemplate(It, temp, entryName=(entryName + "[\"{}\"]".format(it)), intAsFloat=intAsFloat)
        #3) Others:
        else:
            It = it
            temp = templateEntry[0]
            checkInstanceTemplate(It, temp, entryName=(entryName + "[{}]".format(ii)), intAsFloat=intAsFloat)
        
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
