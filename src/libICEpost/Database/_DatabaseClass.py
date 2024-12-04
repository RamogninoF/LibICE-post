#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        25/21/2024
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from typing import Any, Mapping
import types
from libICEpost.src.base.BaseClass import BaseClass

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class _DatabaseClass(BaseClass, dict, Mapping):
    def __init__(self, name:str, **values):
        """
        Initialize as named database
        """
        super().__setattr__("_name", name)
        super().__init__(**values)

    def addFolder(self, name:str, **dict):
        """
        Add sub-database (folder)
        """
        #If already present, merge
        if name in self:
            for key in dict:
                self[key] = dict[key]
        else:
            #Else, generate it
            self[name] = _DatabaseClass(f"{name}", **dict)
            
        return self[name]

    def __getattribute__(self, __name: str) -> Any:
        """
        Points to __getitem__ of dict class
        """
        #if accessing builtin '__<name>__' then use the super() method instead
        if isinstance(__name, str):
            if __name.startswith("__") and __name.endswith("__"):
                return super().__getattribute__(__name)

        try:
            #Try to return with __getattribute__ first
            return super().__getattribute__(__name)
        except:
            if not (__name in self):
                string = f"{__name} not found in database '{self._name}'. Available entries are:\n"
                for item in self:
                    string += f"\t{item}\n"
                raise ValueError(string)
        return super().__getitem__(__name)
    
    def __setattr__(self, __name: str, __value: Any) -> None:
        """
        Points to __setitem__ of dict class
        """
        #if accessing builtin '__<name>__' then use the super() method instead
        if isinstance(__name, str):
            if __name.startswith("__") and __name.endswith("__"):
                return super().__setattr__(__name,__value)

        #If is a function, use __setattr__
        if isinstance(__value, types.FunctionType):
            return super().__setattr__(__name, __value)
        
        #Else append to dictionary
        return super().__setitem__(__name, __value)

    def __repr__(self):
        string=f"Database({self._name})[{len(self)}]\n"
        for item in self:
            aux=repr(self[item]).replace(f"\n",f"\n|  ")
            string += f"|- {item}: {aux}\n"

        return string

    def __str__(self):
        return f"Printing database:\n{repr(self)}"
    
    def __contains__(self, item):
        return super().__contains__(item)
    
    def __setitem__(self, __key: Any, __value: Any) -> None:
        return super().__setitem__(__key, __value)
    
    def __getitem__(self, __key: Any) -> Any:
        if not __key in self:
            string = f"Key {__key} not found in database. Available entries are:"
            for item in self:
                string += f"\n{item}"
            raise ValueError(string)
        
        return super().__getitem__(__key)