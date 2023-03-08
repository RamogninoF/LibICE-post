#####################################################################
#                               IMPORT                              #
#####################################################################

from src.base.Functions.typeChecking import *
from src.base.Functions.functionsForDictionaries import *
from src.base.Functions.runtimeWarning import runtimeWarning, runtimeError, printStack, fatalErrorIn, fatalErrorInArgumentChecking

import numpy as np
import copy as cp
import os

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class Utilities(object):
    """
    Class wrapping useful methods (virtual).
    """
    
    #Type checking:
    checkType = checkType
    checkTypes = checkTypes
    checkInstanceTemplate = checkInstanceTemplate
    updateKeywordArguments = updateKeywordArguments
    
    #Dictionaries
    lookupOrDefault = lookupOrDefault
    dictFromTemplate = dictFromTemplate
    checkDictEntries = checkDictEntries
    checkDictTypes = checkDictTypes
    
    #Errors
    runtimeError = runtimeError
    runtimeWarning = runtimeWarning
    printStack = printStack
    
    fatalErrorIn = fatalErrorIn
    fatalErrorInArgumentChecking = fatalErrorInArgumentChecking
    
    #Copy
    def copy(self):
        """
        Wrapper of copy.deepcopy function.
        """
        return cp.deepcopy(self)
    
    #Numpy:
    np = np
    cp = cp
    os = os

    ##########################################################################################
    #Return empty instance of the class:
    @classmethod
    def empty(cls):
        """
        Return an empty instance of class.
        """
        return cls.__new__(cls)
    
    
