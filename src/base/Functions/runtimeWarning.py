#####################################################################
#                                  DOC                              #
#####################################################################

"""
Functions for warnings and error messages.
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

import traceback
import inspect

from src import GLOBALS

GLOBALS.ERROR_RECURSION = 0
GLOBALS.CUSTOM_ERROR_MESSAGE = True

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
    
    ii = 1
    for stackLine in Where:
        print (">"*ii + formatForWhere.format(stackLine[1], stackLine[0], stackLine[-1]))
        ii += 1

#############################################################################
def baseRuntimeWarning(WarningMSG, Msg):
    Where = traceback.extract_stack()
    
    tabbedMSG = ""
    for cc in Msg:
        tabbedMSG += cc
        if cc == "\n":
            tabbedMSG += " "*len(WarningMSG)
    print (WarningMSG + tabbedMSG)
    printStack()
    print ("")
    
#############################################################################
def runtimeWarning(Msg):
    """
    Print a runtime warning message (Msg) and the call-stack.
    """
    baseRuntimeWarning("WARNING: ", Msg)

#############################################################################
def runtimeError(Msg):
    """
    Print a runtime error message (Msg) and the call-stack.
    """
    baseRuntimeWarning("ERROR: ", Msg)

#############################################################################
def fatalErrorIn(self, func, msg, err=None):
    """
    Raise a RuntimeError.
    """
    funcName = func.__name__
    if not(self is None):
        funcName = self.__class__.__name__ + "." + funcName
    
    argList = func.__code__.co_varnames
    argList = argList[:func.__code__.co_argcount]
    if not(err is None):
        msg += " - " + str(err)
    
    if not(GLOBALS.CUSTOM_ERROR_MESSAGE):
        raise RuntimeError(msg)
    else:
        if GLOBALS.ERROR_RECURSION > 0:
            print("")
            print(enf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", "green"))
            
        args = ""
        for arg in argList:
            args += arg + ","
        args = args[:-1]
        
        print\
        (\
            "--> " + enf(enf("Fatal error in {}".format(funcName + "()"),"fail"),"bold") + \
            ": {}\n\n".format(msg) + \
            enf(enf("help","bold"),"underline") + \
            "({}".format(funcName) + \
            "{}):".format("(" + args + ")") + \
            enf("{}".format(func.__doc__),"cyan")\
        )
        
        print(enf("Printing stack calls:","bold"))
        printStack()
        if not (err is None):
            print("")
            print(enf("Detailed error stack:","bold"))
            printStack(err)
        
        GLOBALS.ERROR_RECURSION += 1
        exit(err)

#############################################################################
def fatalErrorInArgumentChecking(self, func, err=None):
    """
    Raise RuntimeError due to failing argument checking in function call.
    """
    msg = "Argument checking failed"
    fatalErrorIn(self, func, msg, err)
