#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from typing import Self

from .Functions.typeChecking import *
from .Functions.functionsForDictionaries import *
from .Functions.runtimeWarning import runtimeWarning, runtimeError, printStack, fatalErrorIn, fatalErrorInClass, fatalErrorInFunction, fatalErrorInArgumentChecking, fatalError

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
    @staticmethod
    def checkType(*args, **argv):
        return checkType(*args, **argv)
        
    @staticmethod
    def checkTypes(*args, **argv):
        return checkTypes(*args, **argv)
        
    @staticmethod
    def checkInstanceTemplate(*args, **argv):
        return checkInstanceTemplate(*args, **argv)
        
    @staticmethod
    def updateKeywordArguments(*args, **argv):
        return updateKeywordArguments(*args, **argv)
        
    @staticmethod
    def checkContainer(*args, **argv):
        return checkContainer(*args, **argv)
    
    #Dictionaries
    @staticmethod
    def lookupOrDefault(*args, **argv):
        return lookupOrDefault(*args, **argv)
        
    @staticmethod
    def dictFromTemplate(*args, **argv):
        return dictFromTemplate(*args, **argv)
        
    @staticmethod
    def checkDictEntries(*args, **argv):
        return checkDictEntries(*args, **argv)
        
    @staticmethod
    def checkDictTypes(*args, **argv):
        return checkDictTypes(*args, **argv)
    
    #Errors
    @staticmethod
    def runtimeError(*args, **argv):
        return runtimeError(*args, **argv)
            
    @staticmethod
    def runtimeWarning(*args, **argv):
        return runtimeWarning(*args, **argv)
        
    @staticmethod
    def printStack(*args, **argv):
        return printStack(*args, **argv)
    
    @classmethod
    def fatalErrorInClass(cls, *args, **argv):
        return fatalErrorInClass(cls, *args, **argv)
    
    @staticmethod
    def fatalErrorInFunction(*args, **argv):
        return fatalErrorInFunction(*args, **argv)
    
    @staticmethod
    def fatalErrorInFunctionArgumentChecking(*args, **argv):
        return fatalErrorInFunctionArgumentChecking(*args, **argv)
        
    @classmethod
    def fatalErrorInClassArgumentChecking(*args, **argv):
        return fatalErrorInClassArgumentChecking(*args, **argv)
    
    fatalErrorIn = fatalErrorIn
    fatalErrorInArgumentChecking = fatalErrorInArgumentChecking
    
    #Copy
    def copy(self) -> Self:
        """
        Wrapper of copy.deepcopy function.
        """
        return cp.deepcopy(self)
    
    #Useful packages:
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
        out = cls.__new__(cls)
        return out
    
    
