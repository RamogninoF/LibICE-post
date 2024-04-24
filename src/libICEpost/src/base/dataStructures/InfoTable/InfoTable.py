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

from src.base.Utilities import Utilities
from pandas import DataFrame

from abc import ABCMeta, abstractmethod

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Class used for storing and handling a generic tabulation:
class InfoTable(Utilities, metaclass=ABCMeta):
    """
    Base class for the information related to class attributes or method entries.
    
    Attributes:
        columns:    list<str>
            Columns of the table
        
        Data:   pandas.DataFrame
            Data
    """
    #########################################################################
    #Data:
    columns = ["Name", "Type(s)", "Description"]
    Data = DataFrame(columns=columns)
    
    #########################################################################
    #Dictionary constructor:
    def __init__(cls, names, types, descriptions):
        """
        Initialize the table from dictionary with the informations required.
        """
        try:
            for col in cls.columns:
                if not col in dictionary:
                    raise ValueError(f"Entry '{col}' not found in dictionary.")
            
            self.Data = DataFrame.from_dictionary(dictionary)
        except BaseException as err:
            self.fatalErrorInClass(self.__init__,"Failed constucting the information table", err)
    
    #########################################################################
    def __str__(self):
        raise NotImplementedError("__str__() not implemented")
    
    #######################################
    def __repr__(self):
        raise NotImplementedError("__repr__() not implemented")

    #########################################################################
    def checkEntry(self, name, entry):
        """
        name:   str
            Name of the variable
        entry:  instance
            The variable to be checked
        
        Checks if the variable 'entry' with name 'name' is in the InfoTable and consistent with the requirements. If not, rises an exception, depending on the source of error.
        """
        try:
            self.checkType(name, str, "name")
        except BaseException as err:
            cls.fatalErrorInClass("Argument checking failed", err)
        
        if not name in self["name"]:
            raise ValueError(f"Entry '{name}' not found in '{self.__class__.__name__}' instance.")
        
        #TODO
    
    #######################################
    def validateDict(self, dictionary):
        """
        dictionary: dict
            Dictionary with keyword arguments to be checked if consistent with the definition. In case data are not consistent, rises an exception. Otherwise returns the validated keyword arguments.
        """
        pass
    
    #######################################
    @abstractmethod
    def addEntry(self, Entry name):
        """
        Add an entry to the InfoTable. To be overwritten by derived class, depending on the specific kind of information needed.
        """
