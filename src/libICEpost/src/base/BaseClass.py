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
    from typing import Self, Type, TypeVar #Python >= 3.11
except ImportError:
    from typing_extensions import Self, Type, TypeVar  #Python < 3.11

Class = TypeVar("Class")
BaseClassType = TypeVar("BaseClassType")

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
    
    __type:BaseClassType
    """The base class to which the selection table is linked."""
    __db:dict[str,type]
    """Database of available sub-classes in the selection table. Classes are stored through [str->type] map."""
    
    @property
    def type(self) -> BaseClassType:
        """
        The base class to which the selection table is linked.
        """
        return self.__type
    
    @property
    def db(self) -> dict[str,BaseClassType]:
        """
        Database of available sub-classes in the selection table.
        Classes are stored through [str->type] map.
        """
        return self.__db
    
    ##########################################################################################
    def __init__(self, cls:BaseClassType):
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
    def __getitem__(self, typeName:str) -> BaseClassType:
        """
        Get class from selection table.
        
        Args:
            typeName (str): Name of the class to get
        """
        self.checkType(typeName, str, "typeName")
        if not typeName in self:
            string = f"Class {typeName} not found in selection table. Available classes are:"
            for entry in self.__db:
                string += f"\n{entry}"
            raise ValueError(string)
        
        return self.__db[typeName]
    
    ##########################################################################################
    def add(self, cls:type, overwrite:bool=True) -> None:
        """
        Add class to selection table
        
        Args:
            cls (type): Class to add to the selection table
            overwrite (bool, optional): Overwrite if present? Defaults to True.
            
        Raises:
            TypeError: If the class is not derived from the base class of the selection table
        """
        typeName = cls.__name__
        if (typeName in self) and (not overwrite):
            raise ValueError("Subclass '{typeName}' already present in selection table, cannot add to selection table.")
        
        if issubclass(cls, self.type):
            self.__db[typeName] = cls
            _add_TypeName(cls)
        else:
            raise TypeError(f"Class '{cls.__name__}' is not derived from '{self.type.__name__}'; cannot add '{typeName}' to runtime selection table.")
            
    ##########################################################################################
    def check(self, typeName:str) -> bool:
        """
        Checks if a class name is in the selection table.
        
        Args:
            typeName (str): Name of the class to check
        
        Returns:
            bool: True if the class is in the selection table
        
        Raises:
            ValueError: If the class is not in the selection table        
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
            raise ValueError(f"No run-time selection available for class {cls.__name__}.")
        return getattr(cls,f"_{cls.__name__}__selectionTable")

    ##########################################################################################
    @classmethod
    def selector(cls, typeName:str, dictionary:dict) -> BaseClassType:
        """
        Construct an instance of a subclass of this that was added to the selection table.
        
        Args:
            typeName (str): Name of the subclass to instantiate
            dictionary (dict): Dictionary containing the data to construct the class.
        
        Returns:
            BaseClassType: Instance of the specific class.
        """
        cls.checkType(dictionary, dict, "dictionary")
        cls.checkType(typeName, str, "typeName")
    
        #Check if has table
        if not cls.hasSelectionTable():
            raise ValueError(f"No run-time selection table available for class {cls.__name__}")
        
        #Check if class in table
        cls.selectionTable().check(typeName)
        
        #Try instantiation
        instance = cls.selectionTable()[typeName].fromDictionary(dictionary)
        
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
    def fromDictionary(cls, dictionary:dict) -> BaseClassType:
        """
        Construct an instance of this class from a dictionary. To be overwritten by derived class.
        
        Args:
            dictionary (dict): Dictionary containing the data to construct the class.
        
        Returns:
            BaseClassType: Instance of the specific class.
        """
        #Try constructing instance from the dictionary, so that if this classmethod was not overwritten, it will raise an error
        return cls(**dictionary)
        
    ##########################################################################################
    @classmethod
    def addToRuntimeSelectionTable(cls, childClass:BaseClassType, *, overwrite:bool=True) -> None:
        """
        Add the subclass to the database of available subclasses for runtime selection.
        
        Args:
            childClass (BaseClassType): Subclass to add to the selection table
            overwrite (bool, optional): Overwrite if present? Defaults to True.
        """
        if not cls.hasSelectionTable():
            raise ValueError(f"No run-time selection available for class {cls.__name__}.")
        
        cls.selectionTable().add(childClass, overwrite=overwrite)

    ##########################################################################################
    @classmethod
    def createRuntimeSelectionTable(cls) -> None:
        """
        Create the runtime selection table, initializing the property 'selectionTable' of the class.
        """

        if cls.hasSelectionTable():
            raise ValueError(f"A selection table is already present for class {cls.__name__}, cannot generate a new selection table.")
        
        setattr(cls,f"_{cls.__name__}__selectionTable",SelectionTable(cls))
    
    ##########################################################################################
    @classmethod
    def showRuntimeSelectionTable(cls) -> None:
        """
        Prints a list of the available classes in the selection table and if they are instantiable.
        
        Example:
            Available classes in selection table:
                ClassA       (Abstract class)
                ClassB     
                ClassC
        """
        print(cls.selectionTable())