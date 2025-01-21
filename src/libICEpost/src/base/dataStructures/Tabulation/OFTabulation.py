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

from __future__ import annotations

import copy as cp
import numpy as np
import pandas as pd
import os
import shutil

from bidict import bidict

from libICEpost.src.base.Utilities import Utilities
from .Tabulation import Tabulation
from libICEpost.src.base.Functions.functionsForOF import readOFscalarList, writeOFscalarList

from typing import Iterable, Any, Literal, OrderedDict

from dataclasses import dataclass

from PyFoam.RunDictionary.ParsedParameterFile import FoamStringParser, ParsedParameterFile

#####################################################################
#                            AUXILIARY CLASSES                      #
#####################################################################

@dataclass
class _TableData(object):
    """Dataclass storing the data for a tabulation"""
    
    file:str
    """The name of the file for I/O"""
    
    table:Tabulation
    """The tabulation"""
    
    def __eq__(self, value: object) -> bool:
        return (self.file == value.file) and (self.table == value.table)
    
@dataclass
class _InputProps(object):
    """Dataclass storing properties for each input-variable"""
    
    name:str
    """The name used in the tablePropeties file"""
    
    data:Iterable[float]
    """The data-points"""
    
    @property
    def numel(self):
        return len(self.data)
    
    def __eq__(self, value: object) -> bool:
        return (self.name == value.name) and np.array_equal(np.array(self.data),np.array(value.data))

#############################################################################
#                           AUXILIARY FUNCTIONS                             #
#############################################################################
def toPandas(table:OFTabulation) -> pd.DataFrame:
    """
    Convert an instance of OFTabulation to a pandas.DataFrame with all the points stored in the tabulation.

    Args:
        table (OFTabulation): The OpenFOAM tabulation to convert to a dataframe.

    Returns:
        pd.DataFrame: A dataframe with all the points stored in the tabulation. Columns for input and output variables
    """
    Utilities.checkType(table, OFTabulation, "table")
    
    # Create the dataframe
    df = pd.DataFrame({**{f:[0.0]*table.size for f in table.fields}, **{f:[0.0]*table.size for f in table.inputVariables}})
    
    #Sort the columns to have first the input variables in order
    df = df[table.order + table.fields]
    
    #Fill input variables
    ranges = table.ranges
    df.iloc[:,:len(table._order)] = [[ranges[table._order[rr]][id] for rr,id in enumerate(table._computeIndex(ii))] for ii in range(len(table))]
    
    #Filling the outputs
    for tab in table._data:
        df.loc[:,tab] = table._data[tab].table._data.flatten() if not table._data[tab].table is None else float('nan')
    
    return df

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class OFTabulation(Utilities):
    """
    Class used to store and handle an OpenFOAM tabulation (structured table).
    
    The tabulation is a multi-input multi-output, i.e., it access through a 
    set of input variables (IV) to a set of tabulated variables (TV):
        [IV1, IV2, IV3, ...] -> [TV1, TV2, TV3, ...]
        
    #TODO: allow writing in binary mode
    """
    
    #########################################################################
    #Data:
    _path:str
    """The path where the table is stored"""
    
    _baseTableProperties:dict
    """The additional data in the 'tableProperties' file apart from sampling points."""
    
    _order:list[str]
    """The order in which variable-loops are nested"""
    
    _data:dict[str,_TableData]
    """The data stored in the tabulation"""
    
    _inputVariables:dict[str,_InputProps]
    """The properties of the input variables used to access the tabulation"""
    
    _noWrite:bool
    """Allow writing"""
    
    #########################################################################
    #Properties:
    @property
    def path(self) -> str|None:
        """The path of the tabulation"""
        return self._path
    
    @path.setter
    def path(self, path:str):
        self.checkType(path, str, "path")
        self._path = path
    
    ################################
    @property
    def tableProperties(self) -> dict[str:str]:
        """
        The table properties dictionary (read-only).
        """
        #Additional data
        tabProp = cp.deepcopy(self._baseTableProperties)
        
        #Sampling points
        tabProp.update(**{self._inputVariables[iv].name:self._inputVariables[iv].data for iv in self.order})
        
        #Cast Iterables to lists so that PyFoam can write them
        for var in tabProp:
            if isinstance(tabProp[var], Iterable):
                tabProp[var] = list(tabProp[var])
        
        return tabProp
    
    ################################
    @property
    def names(self) -> dict[str,str]:
        """
        Names to give at the variables found in the 'tableProperties' dictionary (read-only).
        """
        return {v:self._inputVariables[v].name for v in self.order}
    
    ################################
    @property
    def inputVariables(self) -> list[str]:
        """
        The input variables to access the tabulation (read-only).
        """
        return list(self._inputVariables.keys())
    
    ################################
    @property
    def fields(self) -> list[str]:
        """
        The variables tabulated.
        """
        return [var for var in self._data]
    
    ################################
    @property
    def ranges(self) -> dict[str,np.array[float]]:
        """
        The sampling points of the input variables to access the tabulation (read-only).
        """
        return {v:np.array(self._inputVariables[v].data[:]) for v in self.order}
    
    ################################
    @property
    def order(self) -> list[str]:
        """
        The order in which the variable-loops are nested.
        """
        return self._order[:]
    
    @order.setter
    def order(self, order:Iterable[str]):
        self.checkType(order, Iterable, "order")
        if not len(order) == len(self.order):
            raise ValueError(f"Incompatible length of new ordering list ({len(order)})!={len(self.order)}")
        for item in order:
            if not item in self.inputVariables:
                raise ValueError(f"Variable '{item}' not found among input variables of tabulation ({self.order})")
        
        #TODO
        raise NotImplementedError("Reordering not yet implemented.")
        
    ################################
    @property
    def noWrite(self) -> bool:
        """
        Allow writing?
        """
        return self._noWrite
    
    @noWrite.setter
    def noWrite(self, newOpt,bool):
        self.checkType(newOpt, bool, "newOpt")
        self._noWrite = newOpt
    
    ################################
    @property
    def fields(self) -> list[str]:
        """
        The avaliable fields stored in the tabulation (output variables).
        """
        return list(self._data.keys())
    
    ################################
    @property
    def tables(self) -> dict[str,Tabulation|None]:
        """
        The tabulations for each variable (read-only).
        """
        return {v:self._data[v].table.copy() for v in self._data}
    
    ################################
    @property
    def files(self) -> dict[str,str]:
        """
        The name of the files where tables are saved (read-only).
        """
        return {v:self._data[v].file for v in self._data}
    
    ############################
    @property
    def size(self):
        """
        Returns the size of the table, i.e., the number of sampling points.
        """
        return np.prod([self._inputVariables[sp].numel for sp in self.order])
    
    ############################
    @property
    def shape(self) -> tuple[int]:
        """
        The dimensions (dim1, dim2,..., dimn) of the tabulation.
        """
        return tuple([self._inputVariables[sp].numel for sp in self.order])
    
    #######################################
    @property
    def ndim(self) -> int:
        """
        Returns the number of dimentsions of the table.
        """
        return len(self.order)
    
    #########################################################################
    #Setters:
    def setFile(self, variable:str, file:str) -> None:
        """Set the name of the file where to save the table of a variable.

        Args:
            variable (str): The variable to set the file-name of.
            file (str): The name of the file.
        """
        self.checkType(variable, str, "variable")
        self.checkType(file, str, "name")
        
        if not variable in self._data:
            raise ValueError("Variable not stored in the tabulation. Avaliable variables are:\n\t" + "\n\t".join(self.names.keys()))
        
        self._data[variable].file = file
    
    ################################
    def setTable(self, variable:str, table:Tabulation|None) -> None:
        """Set the name of the file where to save the table of a variable.

        Args:
            variable (str): The variable to set the file-name of.
            file (str): The name of the file.
        """
        self.checkType(variable, str, "variable")
        
        #If table is not None
        if not table is None:
            self.checkType(table, Tabulation, "table")
        
            if not variable in self._data:
                raise ValueError("Variable not stored in the tabulation. Avaliable variables are:\n\t" + "\n\t".join(self.names.keys()))
            
            #TODO: check consistency of table
            raise NotImplementedError("Setting of table not yet implemented")
        
        self._data[variable].table = table
    
    ################################
    def addField(self, data:Iterable[float]|float|int|Tabulation=None, *, variable:str, file:str=None, **kwargs):
        """Add a new tabulated field (output variable).

        Args:
            variable (str): The name of the variable.
            data (Iterable | list[float] | float | Tabulation, optional): The data used to construct the tabulation. Defaults to None.
            file (str, optional): The name of the file for I/O. Defaults to None (same as 'variable' value).
            **kwargs: Keyword arguments for construction of each Tabulation object.
        """
        self.checkType(variable, str, "variable")
        self.checkType(file, str, "file")
        
        if variable in self._data:
            raise ValueError("Variable already stored in the tabulation.")
        
        if isinstance(data, Iterable):
            #Construct from list of values
            if not (len(data) == self.size):
                raise ValueError(f"Length of data not compatible with sampling points ({len(data)} != {self.size})")
            table = Tabulation(data, ranges=self.ranges, order=self.order, **kwargs)
            
        elif isinstance(data, (float, int)):
            #Uniform
            table = Tabulation(np.array([data]*self.size), ranges=self.ranges, order=self.order, **kwargs)
        elif isinstance(data, Tabulation):
            #TODO: check consistency
            raise NotImplementedError("Adding field from Tabulation not yet implemented.")
            table = data.copy()
        
        #Store
        self._data[variable] = _TableData(file=file, table=table)
    
    ################################
    def delField(self, variable:str):
        """Set the name of the file where to save the table of a variable.

        Args:
            variable (str): The variable to set the file-name of.
        """
        self.checkType(variable, str, "variable")
        
        if not variable in self._data:
            raise ValueError("Variable not stored in the tabulation. Avaliable variables are:\n\t" + "\n\t".join(self.names.keys()))
        
        del self._data[variable]
    
    ################################
    def setName(self, variable:str, name:str) -> None:
        """Set the name of a input-variable to use in the 'tableProperties' dictionary.

        Args:
            variable (str): The input-variable to set the name of.
            name (str): The name of the input-variable.
        """
        self.checkType(variable, str, "variable")
        self.checkType(name, str, "name")
        
        if not variable in self._names:
            raise ValueError("Variable not stored in the tabulation. Avaliable variables are:\n\t" + "\n\t".join(self.names.keys()))
        
        self._inputVariables[variable] = name
    
    ################################
    def resample(self, **newRanges:dict[str,Iterable[float]]) -> None:
        """Resample the input-variables space. Useful for under-sampling or extending the tabulation.

        Args:
            newRanges (dict[str,Iterable[float]]): The new ranges of input-variables to resample.
        """
        for variable in newRanges:
            range = newRanges[variable]
            
            self.checkArray(range, Iterable, f"{variable}")
            
            if not variable in self._inputVariables:
                raise ValueError("Input variable {} not found in tabulation. Avaliable input variables are:\n\t" + "\n\t".join(self.inputVariables.keys()))
        
        if not variable in self._names:
            raise ValueError("Variable not stored in the tabulation. Avaliable variables are:\n\t" + "\n\t".join(self.names.keys()))
        
        raise NotImplementedError("Resampling not yet implemented")
    
    #########################################################################
    #Class methods:
    @classmethod
    def fromFile(cls, 
                 path:str, 
                 order:Iterable[str]=None, 
                 *, 
                 files:Iterable[str]=None, 
                 outputNames:dict[str,str]=None, 
                 inputNames:dict[str,str]=None, 
                 inputVariables:Iterable[str]=None,
                 noWrite:bool=True, 
                 noRead:Iterable[str]=None, 
                 **kwargs) -> OFTabulation:
        """
        Construct a table from files stored in an OpenFOAM-LibICE tabulation locted at 'path'.
        Directory structure as follows: \\
           path                         \\
           |-tableProperties            \\
           |---constant                 \\
           |   |-variable1              \\
           |   |-variable2              \\
           |   |-...                    \\
           |---system                   \\
               |-controlDict            \\
               |-fvSchemes              \\
               |-fvSolutions

        Args:
            path (str): The master path where the tabulation is stored.
            order (Iterable[str], optional): Nesting order of the input-variables used to access the tabulation. In case not given, lookup for entry 'inputVariables' in 'tableProperties' file.
            files (Iterable[str], optional): Names of files in 'path/constant' where the tables are stored. By default try to load everything.
            outputNames (dict[str,str], optional): Used to (optionally) change the names of the variables stored. Defaults to None.
            inputNames (dict[str,str], optional): Used to (optionally) change the names of the input-variables found in the 'tableProperties'. Defaults to None.
            inputVariables (Iterable[str], optional): Used to retrieve fields in the 'tableProperties' file that give the ranges of the input variables. By default, lookup for all the entries with pattern '<variableName>Values', and associate them with input-variable <variableName>. Defaults to None.
            noWrite (bool, optional): Handle to prevent write access of this class to the tabulation (avoid overwrite). Defaults to True.
            noRead (Iterable[str], optional): Tables that are not to be red from files (set to float('nan')). Defaults to None.
            **kwargs: Optional keyword arguments of Tabulation.__init__ method of each Tabulation object.

        Kwargs:
            outOfBounds (Literal['fatal', 'clamp', 'extrapolate'], optional): Option to perform in case of out-of-bounds data (TODO).
        Returns:
            OFTabulation: The tabulation loaded from files.
        """
        #Argument checking
        cls.checkType(path, str, "path")
        print(f"Loading OpenFOAM tabulation from path '{path}'")
        
        #Order of input-variables
        if not order is None:
            cls.checkType(order, Iterable, "order")
            [cls.checkType(var, Iterable, f"order[{ii}]") for ii,var in enumerate(order)]
        
        #Files
        if not files is None:
            cls.checkType(files, Iterable, "files")
            [cls.checkType(var, str, f"files[{ii}]") for ii,var in enumerate(files)]
        else:
            files = os.listdir(f"{path}/constant/")
        
        #No-write option
        cls.checkType(noWrite, bool, "noWrite")
        
        #No-read option
        if not noRead is None:
            cls.checkType(noRead, Iterable, "noRead")
            for ii,n in enumerate(noRead):
                if not n in files:
                    raise ValueError(f"noRead[{ii}] not found in 'files' entry ({files}).")
                cls.checkType(n, str, f"noRead[{ii}]")
        else:
            noRead = []
        
        #Create an empty table:
        tab = cls(ranges=dict(), data=dict(), path=path, order=[], noWrite=noWrite, **kwargs)
        
        #Read ranges from tableProperties
        tab._readTableProperties(entryNames=inputNames, order=order, inputVariables=inputVariables)
        
        #Renaming fields
        if not outputNames is None:
            cls.checkType(outputNames, dict, "outputNames")
            for n in outputNames:
                if not n in files:
                    raise ValueError(f"Cannot set name for variable '{n}': not found in 'files' entry ({files}).")
                cls.checkType(outputNames[n], str, f"outputNames[{n}]")
        else:
            outputNames = dict()
        outputNames = {var:(outputNames[var] if var in outputNames else var) for var in files}
        
        #Read tables
        for f in files:
            if not(f in noRead):
                tab._readTable(fileName=f, tableName=outputNames[f], **kwargs)
            else:
                tab.addField(data=None, variable=outputNames[f], file=f, **kwargs)
        
        return tab
    
    #########################################################################
    #Constructor:
    def __init__(
        self, 
        ranges:dict[str,Iterable[float]], 
        data:dict[str,Iterable[float]], 
        *, path:str=None, 
        order:Iterable[str], 
        files:Iterable[str]=None, 
        inputNames:dict[str,str]=None, 
        outputNames:dict[str,str]=None, 
        noWrite:bool=True, 
        tablePropertiesParameters:dict[str,Any]=None, 
        **kwargs):
        """
        Construct a tabulation from sampling points and unwrapped list of data-points for each variable to tabulate.

        Args:
            ranges (dict[str,Iterable[float]]): The sampling points for each input-variable.
            data (dict[str,Iterable[float]]): The data of each variable stored in the tabulation. Data can be stored as 1-D array or n-D matrix.
            order (Iterable[str]): The order in which input-variables are looped.
            path (str, optional): The path where to save the tabulation. Defaults to None.
            files (dict[str,str], optional): The name of the files to use for each output variable (by default, the name of the variable). Defaults to None.
            inputNames (dict[str,str], optional): The names of the input variables to use in the 'tableProperties' file. Defaults to None.
            outputNames (dict[str,str], optional): The names to use for each tabulated variable (by default, to the one use in 'data' entry). Defaults to None.
            noWrite (bool, optional): Forbid writing (prevent overwrite). Defaults to True.
            tablePropertiesParameters (dict[str,Any], optional): Additional parameters to store in the tableProperties. Defaults to None.
            **kwargs: Optional keyword arguments of Tabulation.__init__ method of each Tabulation object.
        """
        #Argument checking
        #TODO
        
        if not (len(order) == len(ranges)):
            raise ValueError(f"Length of 'order' does not match number of input-variables in 'ranges' entry ({len(order)}!={len(ranges)})")
        for var in ranges:
            if not var in order:
                raise ValueError(f"Input-variable '{var}' not found in 'order' entry.")
        
        #Check if names of input variables are given
        if not inputNames is None:
            self.checkType(inputNames, dict, "inputNames")
        else:
            inputNames = dict()
        inputNames = {variable:inputNames[variable] if variable in inputNames else variable for variable in ranges}
        
        #Check if names of output variables are given
        if not outputNames is None:
            self.checkType(outputNames, dict, "outputNames")
        else:
            outputNames = dict()
        outputNames = {variable:outputNames[variable] if variable in outputNames else variable for variable in data}
        
        #Check if files are given
        if not files is None:
            self.checkType(files, dict, "files")
        else:
            files = dict()
        files = {variable:files[variable] if variable in files else variable for variable in data}
        
        #Initialize to clear tabulation
        self.clear()
        
        #Sampling points
        self._inputVariables = {sp:_InputProps(name=inputNames[sp], data=ranges[sp]) for sp in ranges}
        
        #Order
        self._order = order[:]
        
        #Add tables
        for variable in data:
            self.addField(data[variable], variable=outputNames[variable], file=files[variable], **kwargs)
        
        #Additional parameters
        self._path = path
        self._noWrite = noWrite
        self._baseTableProperties = OrderedDict() if tablePropertiesParameters is None else OrderedDict(**tablePropertiesParameters)
        
        #Add order to the table properties
        self._baseTableProperties.update(inputVariables=[inputNames[var] for var in self._order])
        
    #########################################################################
    # Dunder methods:   
    def __getitem__(self, index:int|Iterable[int]) -> dict[str,float|None]:
        """
        Get an element in the table.

        Args:
            index (int | Iterable[int]): The index to access.
            
        Returns:
            dict[str,float|None]: A dictionary with the values of input and output variables.
        """
        ranges = self.ranges
        
        if isinstance(index, (int, np.integer)):
            # Convert to access by list
            return self[self._computeIndex(index)]
        elif isinstance(index, Iterable):
            output:dict[str, float] = {}
            for ii,id in enumerate(index):
                self.checkType(id, (int, np.integer), f"index[{ii}]")
                if id >= len(ranges[self.order[ii]]):
                    raise IndexError(f"index[{ii}] {id} out of range for variable {self.order[ii]} ({id} >= {len(ranges[self.order[ii]])})")

                # Input variables
                output[self.order[ii]] = ranges[self.order[ii]][id]
             
            #Output variables
            for var in self._data:
                output[var] =  None if self._data[var] is None else self._data[var].table[index][1]
            return output
        else:
            raise TypeError(f"Cannot access with index of type {index.__class__.__name__}")
    
    #####################################
    #Allow iteration
    def __iter__(self):
        """
        Iterator

        Returns:
            Self
        """
        for ii in range(self.size):
            yield self[ii]
    
    #####################################
    #Allow iteration
    def __len__(self) -> int:
        """The size of the table"""
        return int(self.size)
    
    #####################################
    #Interpolate in a table
    def __call__(self, table:str, *args, **kwargs):
        """
        Interpolate from a specific table stored in the tabulation.

        Args:
            table (str): The name of the table to use to interpolate the data.
            *args: Passed to the '__call__' method of the Tabulation instance to interpolate.
            **kwargs: Passed to the '__call__' method of the Tabulation instance to interpolate.

        Returns:
            float|np.ndarray[float]: The interpolated data from the specified table.
        """
        self.checkType(table, str, "table")
        if not table in self.fields:
            raise ValueError(f"Field '{table}' not found in tabulation. Avaliable fields are:\n\t" + "\n\t".join(self.fields))
        if self._data[table].table is None:
            raise ValueError(f"Table for field '{table}' not yet loaded (None).")
        
        return self._data[table].table(*args, **kwargs)
    
    #########################################################################
    def __eq__(self, value:OFTabulation) -> bool:
        if not isinstance(value, OFTabulation):
            return False
        
        #Shape
        if self.shape != value.shape:
            return False
        
        #Input variables
        if self._inputVariables != value._inputVariables:
            return False
        
        #Order
        if self._order != value._order:
            return False
        
        #Tables
        if self._data != value._data:
            return False
        
        #Meta-data
        if self._path != value._path:
            return False
        if self._baseTableProperties != value._baseTableProperties:
            return False
        
        return True
    
    #########################################################################
    #Provate methods:
    def _readTableProperties(self, *, entryNames:dict[str,str]=None, order:Iterable[str]=None, inputVariables:Iterable[str]=None):
        """
        Read information stored in file 'path/tableProperties'. By convention, 
        the ranges variables are those ending with 'Values'. Use 'entryNames' to
        force detecting those not following this convention.
        
        Args:
            entryNames (dict[str,str], optional): Used to (optionally) change the names 
                of input-variables in the tabulation. Defaults to None.
            order (Iterable[str], optional): Nesting order of the input-variables used to access the tabulation. In case not given, lookup for entry 'inputVariables' in 'tableProperties' file.
            inputVariables (Iterable[str], optional): Used to retrieve fields in the 'tableProperties' file that give the ranges of the input variables. By default, lookup for all the entries with pattern '<variableName>Values', and associate them with input-variable <variableName>. Defaults to None.
        """
        #Cast entryNames to bi-direction map
        if not entryNames is None:
            self.checkType(entryNames, dict, "entryNames")
            entryNames = bidict(**entryNames)
        else:
            entryNames = bidict()
        
        if not inputVariables is None:
            self.checkArray(inputVariables, str, "inputVariables")
            
        #Check directory:
        self.checkDir()
        
        #Read tableProperties into dict
        with open(self.path + "/tableProperties", "r") as file:
            tabProps = OrderedDict(**(FoamStringParser(file.read(), noVectorOrTensor=True).getData()))
        
        #Check that all inputs are present if inputVariables is given
        if not inputVariables is None:
            for ii, var in enumerate(inputVariables):
                if not var in tabProps:
                    raise ValueError(f"Entry {var} (inputVariables[{ii}]) not found in tableProperties file. Avaliable entries are:" + "\n\t".join(tabProps.keys()))
        else:
            #Extract fields enging with "Values"
            inputVariables = [var for var in tabProps if var.endswith("Values")]
            
            #Update entryNames
            entryNames.update(**{var:var.replace("Values", "") for var in inputVariables if not var in entryNames})
        
        #Order
        if order is None:
            if not "inputVariables" in tabProps:
                raise ValueError("Entry 'inputVariables' not found in tableProperties. Cannot detect the input variables (and their ordering).")
            order = tabProps["inputVariables"]
        self.checkArray(order, str, "order")
        
        #Identify the ranges
        variables:dict[str,str] = dict()
        ranges:dict[str,list[float]] = dict()
        for ii,var in enumerate(order):
            # Check that it is in tableProperties
            if not var in tabProps:
                raise ValueError(f"Cannot find range for variable {var} in tableProperties. Avaliable entries are:" + "\n\t".join(tabProps.keys()))
            
            # Variable name
            varName = var
            if var in entryNames:
                varName = entryNames[var]
                order[ii] = entryNames[var]
          
            #Append range
            variables[varName] = var
            ranges[varName] = tabProps.pop(var)
            if not isinstance(ranges[varName], Iterable):
                raise TypeError(f"Error reading ranges from tableProperties: '{var}' range is not an Iterable class ({type(ranges[varName]).__name__}).")
        
        if not len(order) == len(ranges):
            raise ValueError(f"Length of 'order' does not match number of input-variables in 'tableProperties' entry ({len(order)}!={len(ranges)})")
        
        self._order = order[:]
        
        #Store:
        self._baseTableProperties = tabProps #Everything left
        self._inputVariables = {var:_InputProps(name=variables[var],data=ranges[var]) for var in order}
    
    #################################
    #Read table from OF file:
    def _readTable(self,fileName:str, tableName:str, **kwargs):
        """
        Read a tabulation from path/constant/fileName.

        Args:
            fileName (str): The name of the file where the tabulation is stored.
            tableName (str): The name to give to the loaded field in the tabulation.
            
        Returns:
            Self: self
        """
        #Table path:
        tabPath = self.path + "/constant/" + fileName
        if not(os.path.exists(tabPath)):
            raise IOError("Cannot read tabulation. File '{}' not found.".format(tabPath))
        print(f"Loading file '{tabPath}' -> {tableName}")
        
        #Read table:
        tab = readOFscalarList(tabPath)
        
        if not(len(tab) == self.size):
            raise IOError(f"Size of table stored in '{tabPath}' is not consistent with the size of the tabulation ({len(tab)} != {self.size}).")
        
        #Add the tabulation
        self.addField(data=tab, variable=tableName, file=fileName)
        
        return self
    
    #######################################
    def _computeIndex(self, index:int) -> tuple[int]:
        """
        Compute the location of an index inside the table. Getting the index, returns a list of the indices of each input-variable.
        
        Args:
            index (int): The index to access in the flattened dataset.
        
        Returns:
            list[int]

        Returns:
            list[int]: The corresponding index in the nested dataset.
            
        Example:
            >>> self.shape
            (2, 3, 4)
            >>> self._computeIndex(12)
            (0, 0, 1)
        """
        id = [0]*self.ndim
        for ii in range(self.ndim-1):
            size = np.prod(self.shape[ii+1:])
            while index >= size:
                id[ii] += 1
                index -= size
        id[-1] = index
        return tuple(id)
    
    #########################################################################
    #Check that all required files are present in tabulation:
    def checkDir(self):
        """
        Check if all information required to read the tabulation are consistent and present in 'path'. Looking for:
            path
            path/constant
            path/tableProperties
        """
        if (self.path is None):
            raise ValueError("The table directory was not initialized.")
        
        #Folders:
        if not(Utilities.os.path.exists(self.path)):
            raise IOError("Folder not found '{}', cannot read the tabulation.".format(self.path))
        
        if not(Utilities.os.path.exists(self.path + "/constant")):
            raise IOError("Folder not found '{}', cannot read the tabulation.".format(self.path + "/constant"))
        
        #tableProperties:
        if not(Utilities.os.path.exists(self.path + "/tableProperties")):
            raise IOError("File not found '{}', cannot read the tabulation.".format(self.path + "/tableProperties"))
            
    #########################################################################
    # Methods:
    
    #Merge with other table
    # def mergeTable(self, fieldName, secondTable):
    #     """
    #     fieldName:  str
    #         Field to use to append second table
            
    #     secondTable: Tabulation
    #         Tabulation containing the data to introduce
        
    #     Introduce additional data to the tabulation.
    #     """
    #     #Check arguments:
    #     try:
    #         Utilities.checkType(fieldName, str, entryName="fieldName")
    #         Utilities.checkType(secondTable, self.__class__, entryName="secondTable")
            
    #         if not fieldName in self.varOrder:
    #             raise ValueError("Field '{}' not found in table.".format(fieldName))
            
    #         if not fieldName in secondTable.varOrder:
    #             raise ValueError("Field '{}' not found in 'secondTable'.".format(fieldName))
            
    #         if self.varOrder != secondTable.varOrder:
    #             raise ValueError("Tabulation field orders not compatible.\Tabulation fields:\n{}\nFields of tabulation to append:\n{}".format(secondTable.varOrder, self.varOrder))
            
    #         #Check if fields already present:
    #         for item in secondTable.tableProperties[fieldName]:
    #             if item in self.tableProperties[fieldName]:
    #                 raise ValueError("Value '{}' already present in range of field '{}'.".format(item, self.tableProperties[fieldName]))
            
    #         #Check compatibility:
    #         otherFields = [f for f in self.varOrder if f != fieldName]
    #         otherRanges = {f:self.tableProperties[f] for f in otherFields}
    #         otherRangesSecond = {f:secondTable.tableProperties[f] for f in otherFields}
    #         if otherRanges != otherRangesSecond:
    #             raise ValueError("Table ranges of other fields not compatible.\nTable ranges:\n{}\Ranges of table to append:\n{}".format(otherRanges, otherRangesSecond))
            
    #     except BaseException as err:
    #         self.fatalErrorInArgumentChecking(self.mergeTable, err)
        
    #     #Append data:
    #     self.tableProperties[fieldName] += secondTable.tableProperties[fieldName]
    #     self.tableProperties[fieldName] = sorted(self.tableProperties[fieldName])
        
    #     for table in self.tables:
    #         if self.tables[table] is None:
    #             self.tables[table] = secondTable.tables[table]
            
    #         elif not(self.tables[table] is None) and not(secondTable.tables[table] is None):
    #             self.tables[table].mergeTable(fieldName, secondTable.tables[table])
            
    #     return self
    
    #####################################
    def slice(self, slices:Iterable[slice|Iterable[int]|int]) -> OFTabulation:
        """Extract a tabulation with sliced dataset. New table is
        initialized without associated directory (path = None) and 
        in read-only mode (noWrite = True).

        Args:
            slices (Iterable[slice | Iterable[int] | int]): A slicer

        Returns:
            OFTabulation: The sliced tabulation.
        """
        #Check arguments:
        self.checkType(slices, Iterable, "slices")
        if not(len(slices) == len(self.order)):
            raise IndexError("Given {} ranges, while table has {} fields ({}).".format(len(slices), len(self.order), self.order))
        
        for ii, ss in enumerate(slices):
            if isinstance(ss, slice):
                # Ok
                pass
                
            elif isinstance(ss,int):
                if ss >= self.size:
                    raise IndexError(f"Index out of range for slices[{ii}] ({ss} >= {self.size})")
            
            elif isinstance(ss,Iterable):
                for jj,ind in enumerate(ss):
                    if ind >= len(self.ranges[self.order[ii]]):
                        self.checkType(ind, int, f"slices[{ii}][{jj}]")
                        raise IndexError(f"Index out of range for variable {ii}:{self.order[ii]} ({ind} >= {len(self.ranges[self.order[ii]])})")
            else:
                raise TypeError("Type mismatch. Attempting to slice with entry of type '{}'.".format(ss.__class__.__name__))
        
        #Create ranges:
        order = self.order
        ranges =  dict()
        for ii,  Slice in enumerate(slices):
            ranges[order[ii]] = [self.ranges[order[ii]][ss] for ss in Slice]
        
        #Create sliced table:
        newTable = OFTabulation(
            ranges=ranges, 
            order=order, 
            data={var:np.zeros(1,len(ranges[var])) for var in order}, 
            tablePropertiesParameters=self._baseTableProperties, 
            names=self.names, 
            files=self.files)
        
        #Set values
        for field in self.fields:
            newTable.setTable(variable=field, table=(self.tables[field][slices] if not self.tables[field] is None else None))
        
        return newTable
    
    #####################################
    def toPandas(self) -> pd.DataFrame:
        """
        Convert to a pandas.DataFrame with all the points stored in the tabulation. Columns for input and output variables.

        Returns:
            pd.DataFrame
        """
        return toPandas(self)
    
    #####################################
    #Write the table:
    def write(self, path:str=None, binary:bool=False):
        """
        Write the tabulation.
        Directory structure as follows: \\
           path                         \\
           |-tableProperties            \\
           |---constant                 \\
           |   |-variable1              \\
           |   |-variable2              \\
           |   |-...                    \\
           |---system                   \\
               |-controlDict            \\
        
        Args:
            path (str, optional): Path where to save the table. In case not give, self.path is used. Defaults to None.
            binary (bool, optional): Writing in binary? Defaults to False.
        """
        if not path is None:
            self.checkType(path, str, "path")
        
        path = self.path if path is None else path
        if path is None:
            raise ValueError("Cannot save tabulation: path was not defined ('self.path' and 'path' are None)")
        
        if self.noWrite:
            raise IOError("Trying to write tabulation when opered in read-only mode. Set 'noWrite' to False to write files.")
        
        #Remove if found
        if os.path.isdir(path):
            self.runtimeWarning(f"Overwriting table at '{path}'", stack=False)
            shutil.rmtree(path)
        
        #Create path
        os.makedirs(path)
        os.makedirs(path + "/constant")
        os.makedirs(path + "/system")
        
        #Table properties:
        tablePros = ParsedParameterFile(path + "/tableProperties", noHeader=True, dontRead=True, createZipped=False)
        tablePros.content = self.tableProperties
        tablePros.writeFile()
        
        #Tables:
        for table in self.tables:
            if not(self.tables[table] is None): #Check if the table was defined
                writeOFscalarList(
                    self.tables[table].data.flatten(), 
                    path=path + "/constant/" + self.files[table],
                    binary=binary)
        
        #Control dict
        controlDict = ParsedParameterFile(path + "/system/controlDict", dontRead=True, createZipped=False)
        controlDict.header = \
            {
                "class":"dictionary",
                "version":2.0,
                "object":"controlDict",
                "location":path + "/system/",
                "format": "ascii"
            }
        controlDict.content = \
            {
                "startTime"        :    0,
                "endTime"          :    1,
                "deltaT"           :    1,
                "application"      :    "dummy",
                "startFrom"        :    "startTime",
                "stopAt"           :    "endTime",
                "writeControl"     :    "adjustableRunTime",
                "writeInterval"    :    1,
                "purgeWrite"       :    0,
                "writeFormat"      :    "binary" if binary else "ascii",
                "writePrecision"   :    6,
                "writeCompression" :    "uncompressed",
                "timeFormat"       :    "general",
                "timePrecision"    :    6,
                "adjustTimeStep"   :    "no",
                "maxCo"            :    1,
                "runTimeModifiable":    "no",
            }
        controlDict.writeFile()
        
        
    #####################################
    #Clear the table:
    def clear(self):
        """
        Clear the tabulation.
        """
        self._path:str|None = None
        self._noWrite:bool = True
        self._tableProperties:dict[str,Any] = dict()
        self._order:list[str] = []
        self._data:dict[str,_TableData] = dict()
        self._inputVariables:dict[str,_InputProps] = dict()
        
        return self
