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

from .Utilities import Utilities

from abc import ABCMeta, abstractmethod
import inspect

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class BaseClass(Utilities, metaclass=ABCMeta):
    """
    Class wrapping useful methods for base virtual classes (e.g. run-time selector)
    """
    
    ##########################################################################################
    @classmethod
    def selector(cls, typeName, dictionary):
        """
        typeName:  str
            Name of the class to be constructed
            
        dictionary: dict
            Dictionary used for construction
        
        Construct an instance of a subclass of this method that was added to the selection table.
        """
        try:
            cls.checkType(dictionary, dict, "dictionary")
            cls.checkType(typeName, str, "typeName")
        except BaseException as err:
            cls.fatalErrorInClass(cls.selector, f"Argument checking failed", err)
        
        if not cls.hasSelectionTable():
            cls.fatalErrorInClass(cls.selector,"No run-time selection available")
        
        if not typeName in cls.selectionTable["db"]:
            cls.fatalErrorInClass(cls.selector,f"No class '{typeName}' found in selection table\n" + cls.showRuntimeSelectionTable())
        
        try:
            instance = cls.selectionTable["db"][typeName].fromDictionary(dictionary)
        except BaseException as err:
            cls.fatalErrorInClass(cls.selector, f"Failed constructing instance of type '{cls.selectionTable['db'][typeName].__name__}'", err)
        
        return instance
    
    ##########################################################################################
    @classmethod
    def hasSelectionTable(cls):
        """
        Check if selection table was defined.
        """
        return hasattr(cls, "selectionTable")
    
    ##########################################################################################
    @classmethod
    @abstractmethod
    def fromDictionary(cls, dictionary):
        """
        dictionary: dict ({})
            Dictionary used for construction
        
        Construct an instance of this class from a dictionary. To be overwritten by derived class.
        """
        try:
            cls.checkType(dictionary, dict, "dictionary")
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, f"Argument checking failed", err)
        
        if inspect.isabstract(cls):
            cls.fatalErrorInClass(cls.fromDictionary, f"Can't instantiate abstract class {cls.__name__} with abstract methods: " + ", ".join(am for am in cls.__abstractmethods__) + ".")
    
    ########################
    @classmethod
    def addToRuntimeSelectionTable(cls, typeName):
        """
        typeName:  str
            Name of the class to be added to the database
            
        Add the subclass to the database of available subclasses for runtime selection.
        """
        try:
            cls.checkType(typeName, str, "typeName")
        except BaseException as err:
            cls.fatalErrorInClass(cls.addToRuntimeSelectionTable, f"Argument checking failed", err)
        
        if not cls.hasSelectionTable():
            cls.fatalErrorInClass(cls.addToRuntimeSelectionTable,"No run-time selection available.")
        
        if not typeName in cls.selectionTable["db"]:
            if issubclass(cls, cls.selectionTable["type"]):
                cls.selectionTable["db"][typeName] = cls
            else:
                cls.fatalErrorInClass(cls.addToRuntimeSelectionTable,f"Class '{cls.__name__}' is not derived from '{cls.selectionTable['type']}'; cannot add '{typeName}' to runtime selection table.")
        else:
            cls.fatalErrorInClass(cls.addToRuntimeSelectionTable,f"Subclass '{typeName}' already present in selection table, cannot add to selection table.")
        
        cls.TypeName = typeName

    ########################
    @classmethod
    def createRuntimeSelectionTable(cls, typeName):
        """
        typeName:  str
            Name of the class to be added to the selection table
        
        Create the runtime selection table, adding the attribute 'selectionTable' to the class.
        """
        try:
            cls.checkType(typeName, str, "typeName")
        except BaseException as err:
            cls.fatalErrorInClass(cls.createRuntimeSelectionTable, f"Argument checking failed", err)
        
        if cls.hasSelectionTable():
            cls.fatalErrorInClass(cls.createRuntimeSelectionTable,"A selection table is already present for this class, cannot generate a new selection table.")
        
        cls.selectionTable = \
            {
                "type":cls,
                "db":\
                    {
                        typeName:cls
                    }
            }
        
        cls.TypeName = typeName
    
    ########################
    @classmethod
    def showRuntimeSelectionTable(cls):
        """
        Returns a string containing a list of available classes in the selection table and if they are instantiable.
        
        E.g.:
        
        Available classes in selection table:
            ClassA       (Abstract class)
            ClassB     
            ClassC
        """
        if not cls.hasSelectionTable():
            cls.fatalErrorInClass(cls.selector,"No run-time selection available.")
            
        string = "Available classes in selection table:"
        for  className, classType in [(CLSNM, cls.selectionTable["db"][CLSNM]) for CLSNM in cls.selectionTable["db"]]:
            string += "\n\t{:40s}{:s}".format(className, "(Abstract class)" if inspect.isabstract(classType) else "")
        
        return string
