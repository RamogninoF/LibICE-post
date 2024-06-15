import sys

from libICEpost.src.base.BaseClass import BaseClass

#from libICEpost.src import GLOBALS
#GLOBALS.CUSTOM_ERROR_MESSAGE = False

#Testing BaseClass funtionalities (run-time selection, derived classes, etc)
#Base class
class testBase(BaseClass):
    pass
#Create selection table
testBase.createRuntimeSelectionTable()

#Derived class
class testChild(testBase):
    def __init__(self):
        pass

    @classmethod
    def fromDictionary(cls, dict):
        return cls()
    
#Add to selection table
testBase.addToRuntimeSelectionTable(testChild)
testBase.showRuntimeSelectionTable()

#Add sub-table:
testChild.createRuntimeSelectionTable()

#Print sub-table:
testChild.showRuntimeSelectionTable()

assert isinstance(testBase.selector("testChild", {}), testChild), "selected Child"
assert isinstance(testBase.selector("testChild", {}), testBase), "Child derived from Base"
assert testChild.__name__ in testBase.selectionTable(), "child in selectionTable"
assert testBase.selectionTable()[testChild.__name__] == testChild , "selected right class"