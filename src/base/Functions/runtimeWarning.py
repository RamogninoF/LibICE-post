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

#############################################################################
#                               MAIN FUNCTIONS                              #
#############################################################################
def printStack(e=None):
    """
    Print the current call-stack. If an error was raised,
    print the traceback with the error message.
    """
    formatForWhere = " At line: {:n}    in '{:s}' calling '{:s}'"
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
    msg += " - " + str(err)
    
    args = ""
    for arg in argList:
        args += arg + ","
    args = args[:-1]
    
    print("Fatal error in {}: {}\n\nhelp({}):\n{}".format(funcName + "()", msg , funcName + "(" + args + ")", func.__doc__))
    
    print("Printing stack calls:")
    printStack()
    if not (err is None):
        print("")
        print("With detailed error:")
        printStack(err)
    
    exit()

#############################################################################
def fatalErrorInArgumentChecking(self, func, err=None):
    """
    Raise RuntimeError due to failing argument checking in function call.
    """
    msg = "Argument checking failed"
    fatalErrorIn(self, func, msg, err)
