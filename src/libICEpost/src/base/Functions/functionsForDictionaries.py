#####################################################################
#                                  DOC                              #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023

Functions for handling dictionaries.
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from .typeChecking import *

#############################################################################
#                               MAIN FUNCTIONS                              #
#############################################################################

#Lookup or default from dictionary:
def lookupOrDefault(Dict,Entry,Default):
    """
    Dict:       dict
    Entry:      -
    Default:    -
    
    Look from 'Entry' in 'Dict'. If not found, return 'Default'.
    """
    #Argument checking:
    checkType(Dict, dict, entryName="Dict")
    
    import copy as cp
    if not(Entry in Dict):
        return cp.deepcopy(Default)
    else:
        return cp.deepcopy(Dict[Entry])

#############################################################################
#Set dictionary from template:
def dictFromTemplate(Dict,TemplateDict, **argv):
    """
    Dict:           dict
    TemplateDict:   dict
    
    Keyword arguments:
    intAsFloat:     bool (True)
        Treat int as floats for type-checking
    
    Set the entries in a dictionaries from a template dictionary.
    """
    inputs = \
        {
            "intAsFloat":True
        }
    
    inputs.update(argv)
    intAsFloat = inputs["intAsFloat"]
    
    #Argument checking:
    checkType(Dict, dict, entryName="Dict")
    checkType(TemplateDict, dict, entryName="TemplateDict")
    checkType(intAsFloat, bool, entryName="intAsFloat")
    
    outDict = {}
    for key in TemplateDict:
        outDict[key] = lookupOrDefault(Dict,key,TemplateDict[key])
        
        try:
            checkType(outDict[key], type(TemplateDict[key]), intAsFloat=intAsFloat)
        except TypeError:
            raise TypeError("Type missmatch: entry '{}' in source dictionary is of type '{}' while type '{}' is found in template dictionary.".format(key, type(outDict[key]), type(TemplateDict[key])))
        
    return outDict

#############################################################################
#Check if entries are found in dictionary:
def checkDictEntries(Dict,entryList):
    """
    Dict:           dict
        Dictionary to be checked
    entryList:      list
        List of entries to assess if present in the dicitonary
    
    Keyword arguments:
    intAsFloat:     bool (True)
        Treat int as floats for type-checking
    
    Checks if all the keys in entryList are present in the dictionary.
    """
    #Argument checking:
    checkType(Dict, dict, entryName="Dict")
    checkType(entryList, list, entryName="entryList")
    
    notFound = []
    for entry in entryList:
        if not(entry in Dict):
            notFound.append(entry)
    
    if len(notFound):
        missing = ""
        for nf in notFound:
            missing += "\t{}\n".format(nf)
        
        available = ""
        for av in Dict:
            available += "\t{}\n".format(av)
        
        raise ValueError("Following entries are missing from the dictionary:\n{}\nAvailable entries are:\n{}".format(missing, available))

#############################################################################
#Check types of entries in dictionary:
def checkDictTypes(Dict,entryTypes):
    """
    Dict:           dict
        Dictionary to be checked
    entryTypes:     dict
        {
            'entry_ii':     tuple<type>
        }
        Dictionary containing the acceptable types for each entry to be
        checked.
    
    Checks if all the keys of entryTypes are present in the dictionary and
    of correct type.
    """
    
    #Argument checking:
    checkInstanceTemplate( entryTypes, { 0:(type,) }, entryName="entryTypes" )
    checkType(Dict, dict, entryName="Dict")
    checkDictEntries(Dict,list(entryTypes.keys()))
    
    for item in entryTypes:
        check = False
        for TT in entryTypes[item]:
            try:
                checkType(Dict[item], TT)
                check = True
                break
            except:
                pass
        
        if not(check):
            raise TypeError("Wrong type for entry '{}': '{}' expected but '{}' was found.".format(item, [T.__name__ for T in entryTypes[item]], Dict[item].__class__.__name__))
