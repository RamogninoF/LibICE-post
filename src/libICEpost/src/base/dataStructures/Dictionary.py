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


from ..Utilities import Utilities
from collections import OrderedDict

from types import ModuleType
from typing import TypeVar
T = TypeVar("T")

import os.path as path

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################

class Dictionary(OrderedDict, Utilities):
    """
    Ordered dictionary embedding some useful OpenFOAM-like methods.
    """
    path:str|None
    file:str|None
    
    #############################################################################
    def __init__(self, *args, _fileName:str=None, **argv):
        """
        Same constructor as collections.OrderedDict class.
        """
        try:
            if _fileName is None:
                # no file assosiaction
                self.fileName = None
                self.path = None
            else:
                #Relative  or absolute path
                base, file = path.split(_fileName)
                
                #Path
                if (base == "") or (base is None):
                    self.path = "." + path.sep
                else:
                    self.path = base
                
                #File name:
                if (file == "") or (file is None):
                    raise ValueError(f"Invalid file name {_fileName}")
                self.fileName = file
            
            super().__init__(*args,**argv)
                
        except BaseException as err:
            self.fatalErrorInClass(self.__init__,f"Construction of {self.__class__.__name__} entry failed", err)
    
    #############################################################################
    @classmethod
    def fromFile(cls, fileName:str):
        """
        fileName:   str
            Path of the file
        Read the variables stored in a python file (Runs the code in the file and retrieves the local variables)
        
        NOTE: local variable 'this' for this file. You can access the local folder as 'this.path' within the dictionary.
        """
        try:
            cls.checkType(fileName, str, "fileName")
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromFile,f"Argument checking failed", err)
            
        try:
            this = cls(_fileName=fileName)
            
            _LOCALS = locals().copy()
            _OLDLOCALS = list(_LOCALS)
            
            with open(fileName) as _FILE:
                exec(_FILE.read())
            
            _LOCALS = locals().copy()
            for l in _LOCALS.keys():
                if not l in (_OLDLOCALS + ["_OLDLOCALS", "_LOCALS", "_FILE"]) and (not isinstance(_LOCALS[l], ModuleType)):
                    this[l] = _LOCALS[l]
            
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromFile,f"Error reading {cls.__name__} from file {fileName}", err)
        
        return this
        
    #############################################################################
    def lookup(self, entryName:str):
        """
        entryName:  str
            Name of the entry to look for
        
        Same as __getitem__ but embeds error handling
        """
        try:
            self.checkType(entryName, str, "entryName")
        except BaseException as err:
            self.fatalErrorInClass(self.lookup,f"Argument checking failed", err)
            
        if not entryName in self:
            self.fatalErrorInClass(self.lookup, f"Entry '{entryName}' not found in Dictionary. Available entries are:\n\t" + "\n\t".join([str(k) for k in self.keys()]))
        else:
            return self[entryName]
    
    #############################################################################
    def pop(self, entryName:str):
        """
        entryName:  str
            Name of the entry to look for
        
        Same as dictionary.pop but embeds error handling
        """
        try:
            self.checkType(entryName, str, "entryName")
        except BaseException as err:
            self.fatalErrorInClass(self.lookup,f"Argument checking failed", err)
            
        if not entryName in self:
            self.fatalErrorInClass(self.lookup, f"Entry '{entryName}' not found in Dictionary. Available entries are:\n\t" + "\n\t".join([str(k) for k in self.keys()]))
        else:
            return super().pop(entryName)
    
    ######################################
    def lookupOrDefault(self, entryName:str, default:T, fatal:bool=True) -> T:
        """
        entryName:  str
            Name of the entry to look for
        default:    instance
            Instance to return in case the value is not found. It is also used for typeChecking
        fatal:      bool (True)
            If the type is not consistent rise a FatalError
            
        Lookup of give a default value if not found
        """
        try:
            self.checkType(entryName, str, "entryName")
            self.checkType(fatal, bool, "fatal")
        except BaseException as err:
            self.fatalErrorInClass(self.lookupOrDefault,"Argument checking failed", err)
        
        if not entryName in self:
            return default
        else:
            if not isinstance(self[entryName], type(default)) and fatal:
                self.fatalErrorInClass(self.lookupOrDefault,f"Inconsistent type of returne value ({type(self[entryName]).__name__}) with default ({type(default).__name__}).", err)
            return self[entryName]
    
    ######################################
    def _correctSubdicts(self):
        """
        Convert ricorsively every subdictionary into Dictionary classes.
        """
        try:
            for entry in self:
                if isinstance(self[entry], dict) and not isinstance(self[entry], Dictionary):
                    self[entry] = Dictionary(**self[entry])
            return self
        except BaseException as err:
            self.fatalErrorInClass(self._correctSubdicts,f"Error updating subdictionary types", err)
    
    
    ######################################
    def __setitem__(self, *args, **argv):
        try:
            super().__setitem__(*args, **argv)
            self._correctSubdicts()
            return self
        except BaseException as err:
            self.fatalErrorInClass(self.__setitem__,f"Error setting Dictionary item", err)
    
    ######################################
    def update(self, **kwargs):
        """
        kwargs:    dict
            Keyword-argumentrs to be updated in dictionary
            
        Performs like dict.update() method but recursively updates sub-dictionaries
        """
        try:
            for key in kwargs:
                if (isinstance(kwargs[key],dict)) and (key in self):
                    self[key].update(**kwargs[key])
                else:
                    super().update({key:kwargs[key]})
                    
            self._correctSubdicts()
        except BaseException as err:
            self.fatalErrorInClass(self.update,f"Error updating dictionary keys", err)
        
        return self
