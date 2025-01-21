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

from .Functions.typeChecking import checkType, checkArray, checkMap
from .Functions.runtimeWarning import runtimeWarning, runtimeError, printStack

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
    def checkArray(*args, **argv):
        return checkArray(*args, **argv)
    
    @staticmethod
    def checkMap(*args, **argv):
        return checkMap(*args, **argv)
    
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


