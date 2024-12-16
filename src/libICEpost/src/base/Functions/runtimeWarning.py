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
def fatalErrorIn(self, func, msg, err=None):
    """
    Raise a RuntimeError.
    """
    MSG = msg

    funcName = func.__name__
    if not(self is None):
        funcName = self.__class__.__name__ + "." + funcName
    
    argList = func.__code__.co_varnames
    argList = argList[:func.__code__.co_argcount]
    if not(err is None):
        msg += " - " + str(err)
    
    if not(GLOBALS.__CUSTOM_ERROR_MESSAGE__):
        raise RuntimeError(msg)
    else:
        if GLOBALS.__ERROR_RECURSION__ > 0:
            print("")
            print(enf(enf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", "warning"), "bold"))
            
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
        
        GLOBALS.__ERROR_RECURSION__ += 1
        exit(RuntimeError(MSG))

#############################################################################
def fatalErrorInClass(cls, func, msg, err=None):
    """
    Raise a RuntimeError.
    """
    MSG = msg
    
    funcName = cls.__name__ + "." + func.__name__
    
    if not(err is None):
        msg += " - " + str(err)
    
    if not(GLOBALS.__CUSTOM_ERROR_MESSAGE__):
        raise RuntimeError(msg)
    else:
        if GLOBALS.__ERROR_RECURSION__ > 0:
            print("")
            print(enf(enf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", "warning"), "bold"))
        
        argList = func.__code__.co_varnames
        argList = argList[:func.__code__.co_argcount]
        args = ""
        for arg in argList:
            args += arg + ","
        args = args[:-1]
        
        print\
        (\
            "--> " + enf(enf("FATAL ERROR IN {}".format(funcName + "()"),"fail"),"bold") + \
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
        
        GLOBALS.__ERROR_RECURSION__ += 1
        exit(RuntimeError(MSG))

#############################################################################
def fatalErrorInFunction(func, msg, err=None):
    """
    Raise a RuntimeError.
    """
    MSG = msg
    
    funcName = func.__name__
    
    argList = func.__code__.co_varnames
    argList = argList[:func.__code__.co_argcount]
    if not(err is None):
        msg += " - " + str(err)
    
    if not(GLOBALS.__CUSTOM_ERROR_MESSAGE__):
        raise RuntimeError(msg)
    else:
        if GLOBALS.__ERROR_RECURSION__ > 0:
            print("")
            print(enf(enf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", "warning"), "bold"))
            
        args = ""
        for arg in argList:
            args += arg + ","
        args = args[:-1]
        
        print\
        (\
            "--> " + enf(enf("FATAL ERROR IN {}".format(funcName + "()"),"fail"),"bold") + \
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
        
        GLOBALS.__ERROR_RECURSION__ += 1
        exit(RuntimeError(MSG))

#############################################################################
def fatalErrorInArgumentChecking(self, func, err=None):
    """
    Raise RuntimeError due to failing argument checking in function call.
    """
    msg = "Argument checking failed"
    fatalErrorIn(self, func, msg, err)

#############################################################################
def fatalError(msg, err=None):
    """
    Raise a RuntimeError.
    """
    MSG = msg
    
    if not(err is None):
        msg += " - " + str(err)
    
    if not(GLOBALS.__CUSTOM_ERROR_MESSAGE__):
        raise RuntimeError(msg)

    if GLOBALS.__ERROR_RECURSION__ > 0:
        print("")
        print(enf(enf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", "warning"), "bold"))
    
    print("")
    print(enf("--> " + enf("FATAL ERROR","fail"),"bold") + ": {}\n".format(msg))
    
    print(enf("Printing stack calls:","bold"))
    printStack()
    if not (err is None):
        print("")
        print(enf("Detailed error stack:","bold"))
        printStack(err)
    
    GLOBALS.__ERROR_RECURSION__ += 1
    exit(RuntimeError(MSG))
