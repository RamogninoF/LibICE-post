#####################################################################
#                                  DOC                              #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023

Functions for warnings and error messages.
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from functools import wraps
import sys
import traceback
import inspect

import colorama
colorama.init(autoreset=False)

from libICEpost import GLOBALS

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
def enf(msg, style):
    styles = \
        {
            "header":bcolors.HEADER,
            "blue":bcolors.OKBLUE,
            "green":bcolors.OKGREEN,
            "cyan":bcolors.OKCYAN,
            "warning":bcolors.WARNING,
            "fail":bcolors.FAIL,
            "bold":bcolors.BOLD,
            "underline":bcolors.UNDERLINE
        }
    
    return styles[style] + msg + bcolors.ENDC
    

#############################################################################
#                               MAIN FUNCTIONS                              #
#############################################################################
def printStack(e=None):
    """
    Print the current call-stack. If an error was raised,
    print the traceback with the error message.
    """
    formatForWhere = " " + enf("At line","bold") + ": {:n}    " + enf("in","bold") + " '{:s}' " + enf("calling","bold") + " '{:s}'"
    #print("printStack()")
    
    if not(e is None):
        Where = traceback.extract_tb(e.__traceback__)
    else:
        Where = traceback.extract_stack()[:-2]
    
    ii = 0
    for stackLine in Where:
        print (enf(enf(str(ii) + ")","warning"),"bold") + formatForWhere.format(stackLine[1], stackLine[0], stackLine[-1]))
        ii += 1

#############################################################################
def baseRuntimeWarning(WarningMSG, Msg, verbosityLevel=1, stack=True):
    Where = traceback.extract_stack()
    
    if (verbosityLevel <= GLOBALS.__VERBOSITY_LEVEL__):
        tabbedMSG = ""
        for cc in Msg:
            tabbedMSG += cc
            if cc == "\n":
                tabbedMSG += " "*len(WarningMSG)
        print (WarningMSG + tabbedMSG)
        
        if stack:
            printStack()
            print ("")
    
#############################################################################
def runtimeWarning(Msg, verbosityLevel=1, stack=True):
    """
    Print a runtime warning message (Msg) and the call-stack.
    """
    baseRuntimeWarning(enf(enf("Runtime Warning: ", "warning"), "bold"), Msg, verbosityLevel, stack)

#############################################################################
def runtimeError(Msg, verbosityLevel=1, stack=True):
    """
    Print a runtime error message (Msg) and the call-stack.
    """
    baseRuntimeWarning(enf(enf("Runtime Error: ", "warning"), "bold"), Msg, verbosityLevel, stack)
    

#############################################################################
#Decorator for printing helper
def helpOnFail(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            e.add_note(f"help({func.__name__}):\n" + inspect.getdoc(func))
            raise e
            
    return wrapper