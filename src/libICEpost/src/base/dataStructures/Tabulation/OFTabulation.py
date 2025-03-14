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

import numpy as np
import pandas as pd
import os
import shutil

from bidict import bidict

from libICEpost.src.base.dataStructures.Tabulation.Tabulation import Tabulation, tableIndex
from libICEpost.src.base.Functions.typeChecking import checkType, checkArray
from libICEpost.src.base.Utilities import Utilities
from libICEpost.src.base.Functions.functionsForOF import readOFscalarList, writeOFscalarList

from typing import Iterable, Any, OrderedDict

from dataclasses import dataclass


# Import functions to read OF files:
try:
    from PyFoam.RunDictionary.ParsedParameterFile import FoamStringParser, ParsedParameterFile
except Exception as e:
    if not isinstance(e, ImportError):
        print("Error importing PyFoam. This might be an issue related to the PyFoam installation. Try performing the patching procedure running 'libICEpost-applyPatches' script.") 
    raise e

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
    Convert an instance of OFTabulation to a pandas.DataFrame with all 
    the points stored in the tabulation.

    Args:
        table (OFTabulation): The OpenFOAM tabulation to convert to a dataframe.

    Returns:
        pd.DataFrame: A dataframe with all the points stored in the tabulation. 
        Columns for input and output variables
    """
    checkType(table, OFTabulation, "table")
    
    # Create the dataframe
    df = pd.DataFrame(**{f:[float("nan")]*table.size for f in table.fields}, **{f:[0.0]*table.size for f in table.ranges})
    
    #Sort the columns to have first the input variables in order
    df = df[table.order + table.fields]
    
    #Populate
    for ii, item in enumerate(table):
        input = table.getInput(ii)
        df.loc[ii, list(input.keys())] = [input[it] for it in input.keys()]
        df.loc[ii, "output"] = item
    
    return df

#Aliases
to_pandas = toPandas

#############################################################################
def concat(table:OFTabulation, *tables:tuple[OFTabulation], inplace:bool=False, **kwargs):
    """
    Extend the table with the data of other tables. The tables must have the same fields but 
    not necessarily in the same order. The data of the second table is appended to the data 
    of the first table, preserving the order of the fields.
    
    If fillValue is not given, the ranges of the second table must be consistent with those
    of the first table in the fields that are not concatenated. If fillValue is given, the
    missing sampling points are filled with the given value.
    
    Args:
        table (OFTabulation): The table to which the data is appended.
        *tables (tuple[OFTabulation]): The tables to append.
        inplace (bool, optional): If True, the operation is performed in-place. Defaults to False.
        fillValue (float, optional): The value to fill missing sampling points. Defaults to None.
        overwrite (bool, optional): If True, overwrite the data of the first table with the data 
            of the second table in overlapping regions. Otherwise raise an error. Defaults to False.
    
    Returns:
        OFTabulation|None: The concatenated table if inplace is False, None otherwise.
    """
    #Check arguments
    checkType(table, OFTabulation, "table")
    checkArray(tables, OFTabulation, "tables")
    checkType(inplace, bool, "inplace")
    
    if not inplace:
        table = table.copy()
        concat(table, *tables, inplace=True, **kwargs)
        return table
    
    for ii, tab in enumerate(tables):
        #Check compatibility
        if not (sorted(table.order) == sorted(tab.order)):
            raise ValueError(f"Tables must have the same fields to concatenate (table[{ii}] incompatible).")
        
        #Check fields
        if not (table.fields == tab.fields):
            raise ValueError(f"Tables must have the same fields to concatenate (table[{ii}] incompatible).")
        
        #Merge the ranges
        ranges = {f:np.unique(np.concatenate([table.ranges[f], tab.ranges[f]])) for f in table.order}
        table._inputVariables = {f:_InputProps(name=table._inputVariables[f].name, data=ranges[f]) for f in table.order}
        
        #Merge the tables
        for f in table.fields:
            #Check that either both tables are loaded or none
            if (table.tables[f] is None) != (tab.tables[f] is None):
                raise ValueError(f"Table '{f}' not loaded in one of the tables to concatenate.")
            
            #Concatenate the tables
            if table._data[f].table is not None:
                table._data[f].table.concat(tab.tables[f], inplace=True, **kwargs)

#Aliases
merge = concat

#############################################################################
def writeOFTable(table:OFTabulation, path:str=None, binary:bool=False):
    """
    Write the tabulation.
    Directory structure as follows: 
    ```   
    path                         
    |-tableProperties            
    |-constant                 
    | |-variable1              
    | |-variable2              
    | |-...                    
    |-system                   
      |-controlDict            
    ```
    Args:
        table (OFTabulation): The tabulation to write.
        path (str, optional): Path where to save the table. In case not give, self.path is used. Defaults to None.
        binary (bool, optional): Writing in binary? Defaults to False.
    """
    if not path is None:
        checkType(path, str, "path")
    
    path = table.path if path is None else path
    if path is None:
        raise ValueError("Cannot save tabulation: path was not defined ('table.path' and 'path' are None)")
    
    if table.noWrite:
        raise IOError("Trying to write tabulation when opered in read-only mode. Set 'noWrite' to False to write files.")
    
    #Remove if found
    if os.path.isdir(path):
        table.runtimeWarning(f"Overwriting table at '{path}'", stack=False)
        shutil.rmtree(path)
    
    #Create path
    os.makedirs(path)
    os.makedirs(path + "/constant")
    os.makedirs(path + "/system")
    
    #Table properties:
    tablePros = ParsedParameterFile(path + "/tableProperties", noHeader=True, dontRead=True, createZipped=False)
    tablePros.content = table.tableProperties
    tablePros.writeFile()
    
    #Tables:
    for table in table.tables:
        if not(table.tables[table] is None): #Check if the table was defined
            writeOFscalarList(
                table.tables[table].data.flatten(), 
                path=path + "/constant/" + table.files[table],
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
    
#############################################################################
def sliceOFTable(table:OFTabulation, *, slices:Iterable[slice|Iterable[int]|int]=None, ranges:dict[str,float|Iterable[float]]=None, **argv) -> OFTabulation:
    """
    Extract a table with sliced datase. Can access in two ways:
        1) by slicer
        2) sub-set of interpolation points. Keyword arguments also accepred.
        
    For safety, the new table will not be writable and the path will be set to None.
    
    Args:
        table (Tabulation): The table
        slices (Iterable[slice|Iterable[int]|int], optional): The slices to extract the table. Defaults to None.
        ranges (dict[str,float|Iterable[float]], optional): The ranges to extract the table. Defaults to None.
        **argv: Keyword arguments to pass to the ranges.
    Returns:
        OFTabulation: The sliced table.
    """
    #Update ranges with keyword arguments
    ranges = dict() if ranges is None else ranges
    ranges.update(argv)
    if len(ranges) == 0:
        ranges = None
    
    if (slices is None) and (ranges is None):
        raise ValueError("Must provide either 'slices' or 'ranges' to slice the table.")
    elif not(slices is None) and not(ranges is None):
        raise ValueError("Cannot provide both 'slices' and 'ranges' to slice the table.")
    
    #Swith access
    if not slices is None: #By slices
        slices = list(slices) #Cast to list (mutable)
        
        #Check types
        table.checkType(slices, Iterable, "slices")
        if not(len(slices) == len(table.order)):
            raise IndexError("Given {} slices, while table has {} fields ({}).".format(len(slices), len(table.order), table.order))
        
        for ii, ss in enumerate(slices):
            if isinstance(ss, slice):
                #Convert to list of indexes
                slices[ii] = list(range(*ss.indices(table.shape[ii])))
                
            elif isinstance(ss,(int, np.integer)):
                if ss >= table.shape[ii]:
                    raise IndexError(f"Index out of range for slices[{ii}] ({ss} >= {table.shape[ii]})")
            
            elif isinstance(ss, Iterable):
                table.checkArray(ss, (int, np.integer), f"slices[{ii}]")
                slices[ii] = sorted(ss) #Sort
                for jj,ind in enumerate(ss): #Check range
                    if ind >= table.shape[ii]:
                        table.checkType(ind, int, f"slices[{ii}][{jj}]")
                        raise IndexError(f"Index out of range for variable {ii}:{table.order[ii]} ({ind} >= {table.shape[ii]})")
            else:
                raise TypeError("Type mismatch. Attempting to slice with entry of type '{}'.".format(ss.__class__.__name__))
        
        #Create ranges:
        order = table.order
        ranges =  dict()
        for ii,  Slice in enumerate(slices):
            ranges[order[ii]] = [table.ranges[order[ii]][ss] for ss in Slice]
        
        #Create a copy of the table
        newTable = table.copy()
        newTable._inputVariables = {f:_InputProps(name=table._inputVariables[f].name, data=ranges[f]) for f in table.order}
        
        #Set not to write
        newTable.noWrite = True
        newTable.path = None
        
        #Slice the tables
        for var in table.fields:
            if not table.tables[var] is None:
                newTable.tables[var] = table.tables[var].slice(slices=slices)
            
        return newTable
    
    elif not ranges is None: #By ranges
        #Start from the original ranges
        newRanges = table.ranges
        
        #Check arguments:
        table.checkMap(ranges, str, Iterable, entryName="ranges")
        
        for rr in ranges:
            for ii in ranges[rr]:
                if not(ii in table.ranges[rr]):
                    raise ValueError(f"Sampling value '{ii}' not found in range for field '{rr}' with points:\n{table.ranges[rr]}")
        
        #Update ranges
        newRanges.update(**ranges)
        
        #Create slicers to access by index
        slices = []
        for ii, item in enumerate(table.order):
            slices.append(np.where(np.isin(table.ranges[item], newRanges[item]))[0])
        
        #Slice by index
        return table.slice(slices=tuple(slices))

#############################################################################


#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class OFTabulation(Utilities):
    """
    Class used to store and handle an OpenFOAM tabulation (structured table).
    
    The tabulation is a multi-input multi-output, i.e., it access through a 
    set of input variables (IV) to a set of tabulated variables (TV):
        [IV1, IV2, IV3, ...] -> [TV1, TV2, TV3, ...]
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
        tabProp = {**self._baseTableProperties}
        
        #Sampling points
        tabProp.update(**{self._inputVariables[iv].name + "Values":self._inputVariables[iv].data for iv in self.order})
        
        #Fields
        tabProp.update(fields=[self._data[f].file for f in self.fields])
        
        #Input variables
        tabProp.update(inputVariables=[self._inputVariables[iv].name for iv in self.order])
        
        #Cast Iterables to lists so that PyFoam can write them
        for var in tabProp:
            if isinstance(tabProp[var], Iterable) and not isinstance(tabProp[var], str):
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
        if not set(order) == set(self.order):
            raise ValueError("New order must contain the same fields as the previous one.")
        
        self._order = list(order)
        #Reorder all the tables
        for var in self.fields:
            if not self._data[var].table is None:
                self._data[var].table.order = order
        
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
        else:
            raise TypeError(f"Cannot add field '{variable}' from data of type {data.__class__.__name__}")
        
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
        
        #Create an empty table:
        tab = cls(ranges=dict(), data=dict(), path=path, order=[], noWrite=noWrite, **kwargs)
        
        #Read ranges from tableProperties
        tab._readTableProperties(entryNames=inputNames, inputVariables=inputVariables)
        
        #Files
        if not files is None:
            cls.checkType(files, Iterable, "files")
            [cls.checkType(var, str, f"files[{ii}]") for ii,var in enumerate(files)]
        elif "fields" in tab._baseTableProperties:
            files = tab._baseTableProperties["fields"]
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
        files:dict[str,str]=None, 
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
        if set(ranges.keys()) != set(order):
            raise ValueError("Inconsistent order of input-variables and ranges.")
        
        #Check if names of input variables are given
        if not inputNames is None:
            self.checkMap(inputNames, str, str, "inputNames")
            if any([not f in ranges for f in inputNames]):
                raise ValueError("Some input variables not found in 'ranges' entry")
        else:
            inputNames = dict()
        inputNames = {variable:inputNames[variable] if variable in inputNames else variable for variable in ranges}
        
        #Check if names of output variables are given
        if not outputNames is None:
            self.checkMap(outputNames, str, str, "outputNames")
            if any([not f in data for f in outputNames]):
                raise ValueError("Some output variables not found in 'data' entry.")
        else:
            outputNames = dict()
        outputNames = {variable:outputNames[variable] if variable in outputNames else variable for variable in data}
        
        #Check if files are given
        if not files is None:
            self.checkMap(files, str, str, "files")
            if any([not f in data for f in files]):
                raise ValueError("Some files not found in 'data' entry.")
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
        if not(os.path.exists(self.path)):
            raise IOError("Folder not found '{}', cannot read the tabulation.".format(self.path))
        
        if not(os.path.exists(self.path + "/constant")):
            raise IOError("Folder not found '{}', cannot read the tabulation.".format(self.path + "/constant"))
        
        #tableProperties:
        if not(os.path.exists(self.path + "/tableProperties")):
            raise IOError("File not found '{}', cannot read the tabulation.".format(self.path + "/tableProperties"))
            
    #########################################################################
    # Methods:
    def copy(self):
        """
        Return a copy of the tabulation. For safety, the new table will not be writable and the path will be set to None.
        """
        return self.__class__(
            ranges=self.ranges, 
            data={var:self._data[var].table.copy() for var in self.fields}, 
            path=None, 
            order=self.order, 
            noWrite=True, 
            tablePropertiesParameters=self._baseTableProperties)
    
    #####################################
    slice = sliceOFTable
    concat = merge = append = concat
    
    toPandas = to_pandas = toPandas
    write = writeOFTable    #Write the table
    
    #####################################
    #Clear the table:
    def clear(self):
        """
        Clear the tabulation.
        """
        self._path = None
        self._noWrite = True
        self._baseTableProperties = dict()
        self._order = []
        self._data = dict()
        self._inputVariables = dict()
        
        return self
    
    #########################################################################
    #Private methods:
    def _readTableProperties(self, *, entryNames:dict[str,str]=None, inputVariables:Iterable[str]=None):
        """
        Read information stored in file 'path/tableProperties'. By convention, 
        the ranges variables are those ending with 'Values'. Use 'entryNames' to
        force detecting those not following this convention.
        
        Args:
            entryNames (dict[str,str], optional): Used to (optionally) change the names 
                of input-variables in the tabulation. Defaults to None.
            inputVariables (Iterable[str], optional): Input variables in the correct nesting order used to access the tabulation.  In case not given, lookup for entry 'inputVariables' in 'tableProperties' file.
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
        
        #Input variables and order
        if inputVariables is None:
            if not "inputVariables" in tabProps:
                raise ValueError("Entry 'inputVariables' not found in tableProperties. Cannot detect the input variables (and their ordering).")
            inputVariables = tabProps["inputVariables"]
        self.checkArray(inputVariables, str, "inputVariables")
        
        order = inputVariables[:]
        
        #Check that all input arrays are present
        for ii, var in enumerate(inputVariables):
            if not var + "Values" in tabProps:
                raise ValueError(f"Entry {var} (inputVariables[{var + 'Values'}]) not found in tableProperties file. Avaliable entries are:" + "\n\t".join(tabProps.keys()))
        
        entryNames.update(**{var:var + "Values" for var in inputVariables if not var in entryNames})
        
        #Identify the ranges
        variables:dict[str,str] = dict()
        ranges:dict[str,list[float]] = dict()
        for ii,var in enumerate(order):
            # Check that it is in tableProperties
            if not entryNames[var] in tabProps:
                raise ValueError(f"Cannot find range for variable {var} in tableProperties. Avaliable entries are:" + "\n\t".join(tabProps.keys()))
            
            # Variable name
            varName = var
            if var in entryNames:
                varName = entryNames[var]
                order[ii] = var

            #Append range
            variables[var] = varName
            ranges[var] = tabProps.pop(varName)
            if not isinstance(ranges[var], Iterable):
                raise TypeError(f"Error reading ranges from tableProperties: '{varName}' range is not an Iterable class ({type(ranges[varName]).__name__}).")
        
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
    _computeIndex = tableIndex
    
    #########################################################################
    # Dunder methods:   
    def __getitem__(self, index:int|Iterable[int]|slice) -> dict[str,float]|dict[str,np.ndarray[float]]:
        """
        Get an element in the table.

        Args:
            index (int | Iterable[int] | slice | Iterable[slice]): Either:
                - An index to access the table (flattened).
                - A tuple of the x,y,z,... indices to access the table.
                - A slice to access the table (flattened).
                - A tuple of slices to access the table.
            
        Returns:
            dict[str,float]|dict[str,np.ndarray[float]]: The data stored in the table.
            - If a single index is given, a dictionary with the output variables at that index.
            - If slice|Iterable[slice] is given, a dictionary with the output variables at that slice.
        """
        return {var:(self._data[var].table[index] if (not self._data[var].table is None) else None) for var in self._data}
    
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
    
    #####################################
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
        
        #Removed check of metadata
        
        return True

    #####################################
    def __add__(self, table:OFTabulation) -> OFTabulation:
        """
        Concatenate two tables. Alias for 'concat'.
        """
        return self.concat(table, inplace=False, fillValue=None, overwrite=False)
    
    def __iadd__(self, table:OFTabulation) -> OFTabulation:
        """
        Concatenate two tables in-place. Alias for 'concat'.
        """
        self.concat(table, inplace=True, fillValue=None, overwrite=False)
        return self