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

import copy as cp

from .Utilities import Utilities

from abc import ABCMeta, abstractmethod
import inspect

try:
    from typing import Self, Type #Python >= 3.11
except ImportError:
    from typing_extensions import Self, Type  #Python < 3.11

#############################################################################
#                             Auxiliary functions                           #
#############################################################################
def _add_TypeName(cls:type):
    """
    Function used to add the TypeName a class.
    """
    cls.TypeName = cls.__name__

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
# SelectionTable
class SelectionTable(Utilities):
    """
    Table for storing classes for run-time selection.
    """
    
    __type:type
    __db:dict[str:type]
    
    @property
    def type(self) -> type:
        """
        The base class to which the selection table is linked.
        """
        return self.__type
    
    @property
    def db(self) -> dict[str:type]:
        """
        Database of available sub-classes in the selection table.
        Classes are stored through [str->type] map.
        """
        return self.__db
    
    ##########################################################################################
    def __init__(self, cls:type):
        """
        cls: str
            The base class for which needs to be generated the selection table
        """

        self.__type = cls
        self.__db = {cls.__name__:cls}

        _add_TypeName(cls)
    
    ##########################################################################################
    def __str__(self):
        """
        Printing selection table
        """
        string = f"Run-time selection table for class {self.type.__name__}:"
        for className, classType in [(CLSNM, self[CLSNM]) for CLSNM in self.__db]:
            string += "\n\t{:40s}{:s}".format(className, "(Abstract class)" if inspect.isabstract(classType) else "")
        
        return string
    
    def __repr__(self):
        """
        Representation of selection table
        """
        string = f"SelectionTable({self.type.__name__})["
        for className in self.__db:
            string += f" {className}"
        
        return string + " ]"
    
    ##########################################################################################
    def __contains__(self, typeName:str) -> bool:
        """
        typeName: str
            Name of the class to look-up

        Check if the selection table contains a selectable class called 'typeName'.
        """
        
        return typeName in self.__db

    ##########################################################################################
    def __getitem__(self, typeName:str):
        """
        Get from database
        """
        try:
            self.checkType(typeName, str, "typeName")
            if not typeName in self:
                string = f"Class {typeName} not found in selection table. Available classes are:"
                for entry in self.__db:
                    string += f"\n{entry}"
                raise ValueError(string)
        except BaseException as err:
            self.fatalErrorInClass(self.__getitem__, f"Argument checking failed", err)
        
        return self.__db[typeName]
    
    ##########################################################################################
    def add(self, cls:type, overwrite=True) -> None:
        """
        cls: type
            Subclass to add to the selection table
        overwrite: bool (True)
            Overwrite?
        Add class to selection table
        """
        typeName = cls.__name__
        if (typeName in self) and (not overwrite):
            self.fatalErrorInClass(self.add,f"Subclass '{typeName}' already present in selection table, cannot add to selection table.")
        
        if issubclass(cls, self.type):
            self.__db[typeName] = cls
            _add_TypeName(cls)
        else:
            self.fatalErrorInClass(self.add,f"Class '{cls.__name__}' is not derived from '{self.type.__name__}'; cannot add '{typeName}' to runtime selection table.")
            
    ##########################################################################################
    def check(self, typeName:str) -> bool:
        """
        typeName: str
            Name of class to be checked

        Checks if a class name is in the selection table, raises ValueError if false
        """

        if not typeName in self:
            string = f"No class '{typeName}' found in selection table for class {self.__type.__name__}. Available classes are:"
            for className, classType in [(CLSNM, self[CLSNM]) for CLSNM in self.__db]:
                string += "\n\t{:40s}{:s}".format(className, "(Abstract class)" if inspect.isabstract(classType) else "")
            
            raise ValueError(string)
        return True

##########################################################################################
#Base class
class BaseClass(Utilities, metaclass=ABCMeta):
    """
    Class wrapping useful methods for base virtual classes (e.g. run-time selector)
    """
    ##########################################################################################
    @classmethod
    def selectionTable(cls) -> SelectionTable:
        """
        The run-time selection table associated to this class.
        """
        if not cls.hasSelectionTable():
            cls.fatalErrorInClass(cls.selectionTable,f"No run-time selection available for class {cls.__name__}.")
        return getattr(cls,f"_{cls.__name__}__selectionTable")

    ##########################################################################################
    @classmethod
    def selector(cls, typeName:str, dictionary:dict) -> Self:
        """
        typeName:  str
            Name of the class to be constructed
            
        dictionary: dict
            Dictionary used for construction
        
        Construct an instance of a subclass of this that was added to the selection table.
        """
        try:
            cls.checkType(dictionary, dict, "dictionary")
            cls.checkType(typeName, str, "typeName")
        except BaseException as err:
            cls.fatalErrorInClass(cls.selector, f"Argument checking failed", err)
        
        try:
            #Check if has table
            if not cls.hasSelectionTable():
                raise ValueError(f"No run-time selection table available for class {cls.__name__}")
            
            #Check if class in table
            cls.selectionTable().check(typeName)
            
            #Try instantiation
            instance = cls.selectionTable()[typeName].fromDictionary(dictionary)
        except BaseException as err:
            cls.fatalErrorInClass(cls.selector, f"Failed constructing instance of type '{cls.selectionTable()[typeName].__name__}'", err)
        
        return instance
    
    ##########################################################################################
    @classmethod
    def hasSelectionTable(cls) -> bool:
        """
        Check if selection table was defined for this class.
        """
        return hasattr(cls, f"_{cls.__name__}__selectionTable")
    
    ##########################################################################################
    @classmethod
    @abstractmethod
    def fromDictionary(cls, dictionary) -> Self:
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
    
    ##########################################################################################
    @classmethod
    def addToRuntimeSelectionTable(cls, childClass:type, /, *, overwrite=True) -> None:
        """
        childClass:  class
            The class to be added to the selection table
        overwrite: bool (True)
            Overwrite if already present in selection table, otherwise rise error.
            
        Add the subclass to the database of available subclasses for runtime selection.
        """
        if not cls.hasSelectionTable():
            cls.fatalErrorInClass(cls.addToRuntimeSelectionTable,f"No run-time selection available for class {cls.__name__}.")
        
        cls.selectionTable().add(childClass, overwrite=True)

    ##########################################################################################
    @classmethod
    def createRuntimeSelectionTable(cls) -> None:
        """
        Create the runtime selection table, initializing the property 'selectionTable' of the class.
        """

        if cls.hasSelectionTable():
            cls.fatalErrorInClass(cls.createRuntimeSelectionTable,f"A selection table is already present for class {cls.__name__}, cannot generate a new selection table.")
        
        setattr(cls,f"_{cls.__name__}__selectionTable",SelectionTable(cls))
    
    ##########################################################################################
    @classmethod
    def showRuntimeSelectionTable(cls) -> None:
        """
        Prints a string containing a list of available classes in the selection table and if they are instantiable.
        
        E.g.:
        
        Available classes in selection table:
            ClassA       (Abstract class)
            ClassB     
            ClassC
        """
        print(cls.selectionT)