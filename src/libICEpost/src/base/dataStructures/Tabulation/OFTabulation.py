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
import matplotlib.pyplot as plt

from bidict import bidict

from libICEpost.src.base.dataStructures.Tabulation.BaseTabulation import BaseTabulation
from libICEpost.src.base.dataStructures.Tabulation.Tabulation import Tabulation
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
    
    #Cast to numpy array
    def __post_init__(self):
        self.data = np.array(self.data)
    
    @property
    def numel(self):
        return len(self.data)
    
    def __eq__(self, value: object) -> bool:
        return (self.name == value.name) and np.array_equal(self.data,value.data)

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
    df = pd.DataFrame({**{f:[float("nan")]*table.size for f in table.fields}, **{f:[0.0]*table.size for f in table.ranges}})
    
    #Sort the columns to have first the input variables in order
    df = df[table.order + table.fields]
    
    #Populate
    for ii, item in enumerate(table):
        input = table.getInput(ii)
        df.loc[ii, list(input.keys())] = [input[it] for it in input.keys()]
        for jj, f in enumerate(table.fields):
            df.loc[ii, f] = item[f]
    
    return df

#Aliases
to_pandas = toPandas

#############################################################################
def concat(table:OFTabulation, *tables:OFTabulation, inplace:bool=False, verbose:bool=True, **kwargs):
    """
    Extend the table with the data of other tables. The tables must have the same variables but 
    not necessarily in the same order. The data of the second table is appended to the data 
    of the first table, preserving the order of the variables.
    
    If fillValue is not given, the ranges of the second table must be consistent with those
    of the first table in the variables that are not concatenated. If fillValue is given, the
    missing sampling points are filled with the given value.
    
    Args:
        table (OFTabulation): The table to which the data is appended.
        *tables (OFTabulation): The tables to append.
        inplace (bool, optional): If True, the operation is performed in-place. Defaults to False.
        verbose (bool, optional): Print information. Defaults to True.
        **kwargs: Keyword arguments to pass to the 'concat' method of the Tabulation objects.
    
    Keyword Args:
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
    
    order = table.order
    ranges = table.ranges
    for ii, tab in enumerate(tables):
        #Check compatibility
        if not (sorted(order) == sorted(tab.order)):
            raise ValueError(f"Tables must have the same variables to concatenate (table[{ii}] incompatible).")
        
        #Check fields
        if not (table.fields == tab.fields):
            raise ValueError(f"Tables must have the same fields to concatenate (table[{ii}] incompatible).")
        
        #Merge the ranges
        ranges = {f:np.unique(np.concatenate([ranges[f], tab.ranges[f]])) for f in order}
    table._inputVariables = {f:_InputProps(name=table._inputVariables[f].name, data=ranges[f]) for f in order}
    
    if verbose: print("Concatenating tables...")
    for f in table.fields:
        #Get the tables
        tabs = [table._data[f].table] + [tab._data[f].table for tab in tables]
        
        #Check if all tables are loaded and concatenate
        if verbose: print(f"\tField '{f}'")
        if not all([tab is None for tab in tabs]):
            if not any([tab is None for tab in tabs]):
                table._data[f].table.concat(*[tab._data[f].table for tab in tables], inplace=True, **kwargs)
            else:
                raise ValueError(f"Table '{f}' not loaded in {sum([1 for tab in tabs if tab is None])} tables to concatenate.")


#Aliases
merge = concat

#############################################################################
def writeOFTable(table:OFTabulation, path:str=None, *, binary:bool=False, overwrite:bool=False):
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
        overwrite (bool, optional): Overwrite the table if found? Defaults to False.
    """
    if not path is None:
        checkType(path, str, "path")
    
    path = table.path if path is None else path
    if path is None:
        raise ValueError("Cannot save tabulation: path was not defined ('table.path' and 'path' are None)")
    
    if table.noWrite:
        raise IOError("Trying to write tabulation when opered in read-only mode. Set 'noWrite' to False to write files.")
    
    if os.path.exists(path) and not overwrite:
        raise IOError(f"Table already exists at '{path}'. Set 'overwrite' to True to overwrite.")
    elif os.path.exists(path):
        shutil.rmtree(path)
    
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
    for tab in table.tables:
        if not(table.tables[tab] is None): #Check if the table was defined
            writeOFscalarList(
                table.tables[tab].data.flatten(), 
                path=path + "/constant/" + table.files[tab],
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
def sliceOFTable(table:OFTabulation, *, slices:Iterable[slice|Iterable[int]|int]=None, ranges:dict[str,float|Iterable[float]]=None, inplace=False, **argv) -> OFTabulation|None:
    """
    Extract a table with sliced datase. Can access in two ways:
        1) by slicer
        2) sub-set of interpolation points. Keyword arguments also accepred.
        
    For safety, the new table will not be writable and the path will be set to None.
    
    Args:
        table (Tabulation): The table
        slices (Iterable[slice|Iterable[int]|int], optional): The slices to extract the table. Defaults to None.
        ranges (dict[str,float|Iterable[float]], optional): The ranges to extract the table. Defaults to None.
        inplace (bool, optional): If True, the operation is performed in-place. Defaults to False.
        **argv: Keyword arguments to pass to the ranges.
    Returns:
        OFTabulation|None: The sliced table if inplace is False, None otherwise.
    """
    checkType(table, OFTabulation, "table")
    checkType(inplace, bool, "inplace")
    
    # Code implemented for inplace operations
    if not inplace:
        table = table.copy()
        sliceOFTable(table, slices=slices, ranges=ranges, inplace=True, **argv)
        return table
    
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
        checkType(slices, Iterable, "slices")
        if isinstance(slices, str):
            raise TypeError("Type mismatch. Attempting to slice with entry of type 'str'.")
        
        slices = list(slices) #Cast to list (mutable)
        if not(len(slices) == len(table.order)):
            raise IndexError("Given {} slices, while table has {} variables ({}).".format(len(slices), len(table.order), table.order))
        
        for ii, ss in enumerate(slices):
            if isinstance(ss, slice):
                #Convert to list of indexes
                slices[ii] = list(range(*ss.indices(table.shape[ii])))
                
            elif isinstance(ss,(int, np.integer)):
                if ss >= table.shape[ii]:
                    raise IndexError(f"Index out of range for slices[{ii}] ({ss} >= {table.shape[ii]})")
            
            elif isinstance(ss, Iterable):
                checkArray(ss, (int, np.integer), f"slices[{ii}]")
                slices[ii] = sorted(ss) #Sort
                for jj,ind in enumerate(ss): #Check range
                    if ind >= table.shape[ii]:
                        checkType(ind, int, f"slices[{ii}][{jj}]")
                        raise IndexError(f"Index out of range for variable {ii}:{table.order[ii]} ({ind} >= {table.shape[ii]})")
            else:
                raise TypeError("Type mismatch. Attempting to slice with entry of type '{}'.".format(ss.__class__.__name__))
        
        #Create ranges:
        order = table.order
        ranges =  dict()
        for ii,  Slice in enumerate(slices):
            ranges[order[ii]] = [table.ranges[order[ii]][ss] for ss in Slice]
        
        #Create a copy of the table
        table._inputVariables = {f:_InputProps(name=table._inputVariables[f].name, data=ranges[f]) for f in table.order}
        
        #Set not to write
        table.noWrite = True
        table.path = None
        
        #Slice the tables
        for var in table.fields:
            if not table.tables[var] is None:
                table._data[var].table.slice(slices=slices, inplace=True)
    
    elif not ranges is None: #By ranges
        #Start from the original ranges
        newRanges = table.ranges
        
        #Check arguments:
        table.checkMap(ranges, str, Iterable, entryName="ranges")
        
        for rr in ranges:
            for ii in ranges[rr]:
                if not(ii in table.ranges[rr]):
                    raise ValueError(f"Sampling value '{ii}' not found in range for variable '{rr}' with points:\n{table.ranges[rr]}")
        
        #Update ranges
        newRanges.update(**ranges)
        
        #Create slicers to access by index
        slices = []
        for ii, item in enumerate(table.order):
            slices.append(np.where(np.isin(table.ranges[item], newRanges[item]))[0])
        
        #Slice by index
        table.slice(slices=tuple(slices), inplace=True)

#############################################################################
def clipOFTable(table:OFTabulation, *, ranges:dict[str,tuple[float,float]]=None, inplace:bool=False, **kwargs) -> OFTabulation|None:
    """
    Clip the table to the given ranges. The ranges are given as a dictionary with the 
    variable names as keys and a tuple with the minimum and maximum values.
    
    Args:
        table (OFTabulation): The table to clip.
        ranges (dict[str,tuple[float|None,float|None]], optional): The ranges to clip for each input-variable. If min or max is None, the range is unbounded.
        inplace (bool, optional): If True, the operation is performed in-place. Defaults to False.
        **kwargs: Can access also by keyword arguments.
        
    Returns:
        OFTabulation|None: The clipped table if inplace is False, None otherwise.
    """
    checkType(table, OFTabulation, "table")
    checkType(inplace, bool, "inplace")
    checkType(ranges, dict, "ranges", allowNone=True)
    
    if not inplace:
        table = table.copy()
        clipOFTable(table, ranges=ranges, inplace=True, **kwargs)
        return table
    
    #Update ranges with keyword arguments
    ranges = dict() if ranges is None else ranges
    for kw in kwargs:
        if kw in ranges:
            raise ValueError(f"Keyword argument '{kw}' is already present in 'ranges'.")
    ranges.update(kwargs)
    if len(ranges) == 0:
        ranges = None
    
    if ranges is None:
        raise ValueError("Must provide 'ranges' to clip the table.")
    
    #Check arguments
    table.checkMap(ranges, str, tuple, entryName="ranges")
    
    #Compute clipped ranges
    newRanges = {}
    for var in ranges:
        if not var in table.order:
            raise ValueError(f"Variable '{var}' not found in table.")
        
        if not len(ranges[var]) == 2:
            raise ValueError(f"Invalid range for variable '{var}'. Must be a tuple with two values (min, max).")
        
        if not (ranges[var][0] is None) or not (ranges[var][1] is None):
            newRanges[var] = table.ranges[var]
            
        if not (ranges[var][0] is None):
            newRanges[var] = newRanges[var][(newRanges[var] >= ranges[var][0])]
        if not (ranges[var][1] is None):
            newRanges[var] = newRanges[var][(newRanges[var] <= ranges[var][1])]

    if any([len(newRanges[var]) == 0 for var in newRanges]):
        raise ValueError("Clipping would result in empty table (zero-size range).")
    
    #Clip
    for var in ranges:
        if not var in table.order:
            raise ValueError(f"Variable '{var}' not found in table.")
        
        if not (ranges[var][0] is None):
            table._inputVariables[var].data = table._inputVariables[var].data[(table._inputVariables[var].data >= ranges[var][0])]
        if not (ranges[var][1] is None):
            table._inputVariables[var].data = table._inputVariables[var].data[(table._inputVariables[var].data <= ranges[var][1])]
    
    #Clip the tables
    for var in table.fields:
        if not table.tables[var] is None:
            table._data[var].table.clip(ranges=ranges, inplace=True)
    
#############################################################################
def insertDimension(table:OFTabulation, *, variable:str, value:float, index:int=None, inplace:bool=False) -> OFTabulation|None:
    """
    Insert a new dimension in the table by adding a new variable with constant value.
    
    Args:
        table (OFTabulation): The table to insert the dimension.
        variable (str): The name of the input variable to insert.
        value (float): The value to assign to the new variable.
        index (int, optional): The index where to insert the new variable. Defaults to None (append at the end).
        inplace (bool, optional): If True, the operation is performed in-place. Defaults to False.
    
    Returns:
        OFTabulation|None: The new table with the inserted dimension if inplace is False, None otherwise.
    """
    #Check arguments
    table.checkType(variable, str, "variable")
    table.checkType(value, (float, int), "value")
    table.checkType(index, int, "index", allowNone=True)
    table.checkType(inplace, bool, "inplace")
    
    if index is None:
        index = len(table.order)
    
    if not inplace:
        table = table.copy()
        insertDimension(table, variable=variable, value=value, index=index, inplace=True)
        return table
    
    #Check index
    if not(index >= 0 and index <= table.ndim):
        raise IndexError(f"Index out of range for insertion ({index} not in [0,{table.ndim}])")
    
    #Insert the new input variable
    table._order.insert(index, variable)
    table._inputVariables[variable] = _InputProps(name=variable, data=[value])
    
    #Insert the new variable in the tables
    for var in table.fields:
        if not table.tables[var] is None:
            table._data[var].table.insertDimension(variable=variable, value=value, index=index, inplace=True)

#############################################################################
def squeeze(table:OFTabulation, *, inplace:bool=False) -> OFTabulation|None:
    """
    Remove dimensions with only one sampling point.
    
    Args:
        table (OFTabulation): The table to squeeze.
        inplace (bool, optional): If True, the operation is performed in-place. Defaults to False.
    
    Returns:
        OFTabulation|None: The squeezed table if inplace is False, None otherwise.
    """
    #Check arguments
    table.checkType(inplace, bool, "inplace")
    
    if not inplace:
        table = table.copy()
        squeeze(table, inplace=True)
        return table
    
    #Squeeze the tables
    for var in table.fields:
        if not table.tables[var] is None:
            table.tables[var].squeeze(inplace=True)
    
    #Squeeze the order
    table._order = [var for var in table.order if table._inputVariables[var].numel > 1]
    
    #Squeeze the input variables
    table._inputVariables = {f:table._inputVariables[f] for f in table.order}

#############################################################################
def plotOFTable(table:OFTabulation, field:str, **kwargs) -> plt.Axes:
    """
    Plot a field of a tabulation.

    Args:
        table (OFTabulation): The tabulation to plot.
        field (str): The field to plot.
        **kwargs: Keyword arguments to pass to the 'plot' method of the Tabulation object.
        
    Returns:
        plt.Axes: The axis where the plot is drawn.
    """
    if not field in table.fields:
        raise ValueError(f"Field '{field}' not found in the tabulation. Avaliable fields are:\n\t" + "\n\t".join(table.fields))
    
    #Set y-label if not given
    if not "ylabel" in kwargs:
        kwargs["ylabel"] = field
    
    return table.tables[field].plot(**kwargs)

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class OFTabulation(BaseTabulation):
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
        self.checkType(path, str, "path", allowNone=True)
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
        The fields tabulated.
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
    @BaseTabulation.order.setter
    def order(self, order:Iterable[str]):
        BaseTabulation.order.fset(self, order)
        
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
    def noWrite(self, newOpt:bool):
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
    #Class methods:
    @classmethod
    def fromFile(cls, 
                 path:str, 
                 order:Iterable[str]=None, 
                 *, 
                 inputNames:dict[str,str]=None, 
                 fields:Iterable[str]=None,
                 outputNames:dict[str,str]=None, 
                 files:dict[str,str]=None, 
                 noRead:Iterable[str]=None, 
                 verbose:bool=True,
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
            inputNames (dict[str,str], optional): Renaming the input variables found in the 'tableProperties' file. Defaults to None.
            fields (Iterable[str], optional): The name of the fields to use for each output variable (by default, lookup for entry 'fields' in 'tableProperties' file). Defaults to None.
            outputNames (dict[str,str], optional): Renaming the output variables found in the 'tableProperties' file. Defaults to None.
            files (dict[str,str], optional): The name of the files to use for each output variable (by default, the name of the fields). Defaults to None.
            noRead (Iterable[str], optional): Do not read the data of the given variables. Defaults to None.
            verbose (bool, optional): Print information. Defaults to True.
            **kwargs: Optional keyword arguments of Tabulation.__init__ method of each Tabulation object.
            
        Kwargs:
            outOfBounds (Literal['fatal', 'clamp', 'extrapolate'], optional): Option to perform in case of out-of-bounds data (TODO).
        
        Returns:
            OFTabulation: The tabulation loaded from files.
        """
        #Check arguments
        cls.checkType(path, str, "path")
        if not order is None:
            cls.checkArray(order, str, "order")
        if not inputNames is None:
            cls.checkMap(inputNames, str, str, "inputNames")
        if not outputNames is None:
            cls.checkMap(outputNames, str, str, "outputNames")
        if not files is None:
            cls.checkMap(files, str, str, "files")
        if not noRead is None:
            cls.checkArray(noRead, str, "noRead")
        else:
            noRead = []
        cls.checkType(verbose, bool, "verbose")
        
        #Create an empty tabulation
        tab = OFTabulation(ranges=dict(), data=dict(), order=[], path=path, **kwargs)
        
        #Read table properties
        fields = tab._readTableProperties(inputNames=inputNames, inputVariables=order, fields=fields)
        
        #Update output names and files
        if outputNames is None: outputNames = dict()
        if files is None: files = dict()
        for f in fields:
            if not(f in outputNames):
                outputNames[f] = f
            if not(f in files):
                files[f] = f
        
        #Read tables
        for f in fields:
            if not(f in noRead):
                tab._readTable(fileName=files[f], tableName=outputNames[f], verbose=verbose, **kwargs)
            else:
                tab.addField(data=None, field=outputNames[f], file=files[f], **kwargs)
        
        return tab
    
    ##################################
    @classmethod
    def from_pandas(cls, data:pd.DataFrame, order:Iterable[str], **kwargs):
        """
        Construct a tabulation from a pandas DataFrame.

        Args:
            data (pd.DataFrame): The data to construct the tabulation.
            order (Iterable[str]): The order of the input-variables.
            **kwargs: Optional keyword arguments of OFTabulation.__init__ method.
        
        Kwargs:
            outOfBounds (Literal['fatal', 'clamp', 'extrapolate'], optional): Option to perform in case of out-of-bounds data (TODO).
        
        Returns:
            OFTabulation: The tabulation constructed from the pandas DataFrame.
        """
        checkType(data, pd.DataFrame, "data")
        checkArray(order, str, "order")
        
        #Check if all variables are present
        if not all([var in data.columns for var in order]):
            raise ValueError("Some input variables not found in the DataFrame.")
        
        #Determine the fields
        fields = [var for var in data.columns if not var in order]
        if len(fields) == 0:
            raise ValueError("No fields found in the DataFrame.")
        
        #Sort the dataframe to match the nesting order of the tabulation
        data_sorted = data.sort_values(by=order, ascending=True, ignore_index=True)
        
        #Extract the data
        ranges = {var:data[var].unique() for var in order}
        data = {var:data_sorted[var].values for var in fields}
        
        return cls(ranges=ranges, data=data, order=order, **kwargs)
        
    #Aliases
    fromPandas = from_pandas
    
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
        
        Kwargs:
            outOfBounds (Literal['fatal', 'clamp', 'extrapolate'], optional): Option to perform in case of out-of-bounds data (TODO).
        
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
            self.addField(data[variable], field=outputNames[variable], file=files[variable], **kwargs)
        
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
    clip = clipOFTable
    
    toPandas = to_pandas = toPandas
    write = writeOFTable    #Write the table
    
    insertDimension = insertDimension
    squeeze = squeeze
    
    plot = plotOFTable
    
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
    #Access (setter/getter):
    def setFile(self, field:str, file:str) -> None:
        """Set the name of the file where to save the table of a field.

        Args:
            field (str): The field to set the file-name of.
            file (str): The name of the file.
        """
        self.checkType(field, str, "field")
        self.checkType(file, str, "name")
        
        if not field in self._data:
            raise ValueError("Field not stored in the tabulation. Avaliable field are:\n\t" + "\n\t".join(self.names.keys()))
        
        self._data[field].file = file
    
    ################################
    def setTable(self, field:str, table:Tabulation|None) -> None:
        """Overwrite the table of a field.

        Args:
            field (str): The field to set the file-name of.
            file (str): The name of the file.
        """
        self.checkType(field, str, "field")
        if not field in self._data:
            raise ValueError("Field not stored in the tabulation. Avaliable field are:\n\t" + "\n\t".join(self.names.keys()))
            
        #If table is not None
        if not table is None:
            self.checkType(table, Tabulation, "table")

            #check consistency of table
            if not table.order == self.order:
                raise ValueError("Inconsistent order of input-variables between the tabulation and the table to set.")
            for rr in table.ranges:
                if not np.allclose(table.ranges[rr], self.ranges[rr]):
                    raise ValueError(f"Inconsistent ranges for variable '{rr}' between the tabulation and the table to set.")
            table = table.copy()
            
        #Set the table
        self._data[field].table = table
    
    ################################
    def addField(self, data:Iterable[float]|float|int|Tabulation|None, *, field:str, file:str=None, **kwargs):
        """Add a new tabulated field (output variable).

        Args:
            field (str): The name of the variable.
            data (Iterable | list[float] | float | Tabulation): The data used to construct the tabulation. Defaults to None.
            file (str, optional): The name of the file for I/O. Defaults to None (same as 'field' value).
            **kwargs: Keyword arguments for construction of each Tabulation object.
        """
        self.checkType(field, str, "variable")
        self.checkType(file, str, "file", allowNone=True)
        
        if field in self._data:
            raise ValueError("Field already stored in the tabulation.")
        
        if file is None:
            file = field
        
        elif isinstance(data, Tabulation):
            #Check consistency
            if not data.order == self.order:
                raise ValueError("Inconsistent order of input-variables between the tabulation and the table to set.")
            for rr in data.ranges:
                if not np.allclose(data.ranges[rr], self.ranges[rr]):
                    raise ValueError(f"Inconsistent ranges for variable '{rr}' between the tabulation and the table to set.")
            table = Tabulation(data, ranges=self.ranges, order=self.order, **kwargs)
        if isinstance(data, (float, int)): #Uniform data
            table = Tabulation(np.array([data]*self.size), ranges=self.ranges, order=self.order, **kwargs)
        elif isinstance(data, Iterable): #Construct from list of values
            if not (len(data) == self.size):
                raise ValueError(f"Length of data not compatible with sampling points ({len(data)} != {self.size})")
            table = Tabulation(data, ranges=self.ranges, order=self.order, **kwargs)
        else:
            raise TypeError(f"Cannot add field '{field}' from data of type {data.__class__.__name__}")
        
        #Store
        self._data[field] = _TableData(file=file, table=table)
    
    ################################
    def delField(self, field:str):
        """
        Delete a field from the tabulation.

        Args:
            field (str): The field to delete.
        """
        self.checkType(field, str, "field")
        
        if not field in self._data:
            raise ValueError("Variable not stored in the tabulation. Avaliable field are:\n\t" + "\n\t".join(self.names.keys()))
        
        del self._data[field]
    
    ################################
    def setName(self, variable:str, name:str) -> None:
        """
        Set the name of a input-variable to use in the 'tableProperties' dictionary.

        Args:
            variable (str): The input-variable to set the name of.
            name (str): The name of the input-variable.
        """
        self.checkType(variable, str, "variable")
        self.checkType(name, str, "name")
        
        if not variable in self._inputVariables:
            raise ValueError("Variable not stored in the tabulation. Avaliable variables are:\n\t" + "\n\t".join(self.names.keys()))
        
        self._inputVariables[variable].name = name
    
    ################################
    def outOfBounds(self, field:str, method:str=None) -> str|None:
        """Get/set the out-of-bounds method for a field.
        
        Args:
            field (str): The field to get/set the out-of-bounds method.
            method (str, optional): The method to set. Defaults to None.
            
        Returns:
            str|None: The out-of-bounds method for the field if method is not None, None otherwise.
        """
        checkType(field, str, "field", allowNone=True)
        checkType(method, str, "method", allowNone=True)
        if not method is None:
            self._data[field].table.outOfBounds = method
        else:
            return self._data[field].table.outOfBounds
    
    ################################
    def setRange(self, variable:str, range:Iterable[float]) -> None:
        """
        Set the range of a variable.

        Args:
            variable (str): The variable to set the range of.
            range (Iterable[float]): The range of the variable.
        """
        self.checkType(variable, str, "variable")
        self.checkArray(range, float, "range")
        
        if not variable in self._inputVariables:
            raise ValueError("Variable not stored in the tabulation. Avaliable variables are:\n\t" + "\n\t".join(self.names.keys()))
        
        if not len(range) == self._inputVariables[variable].numel:
            raise ValueError(f"Length of range not compatible with sampling points ({len(range)} != {self._inputVariables[variable].numel})")

        if not len(range) == len(set(range)):
            raise ValueError(f"New range contains duplicated values.")
        
        if not list(range) == sorted(range):
            raise ValueError(f"New range for variable '{variable}' not sorted in ascending order.")
        
        self._inputVariables[variable].data = range
        for var in self.fields:
            if not self._data[var].table is None:
                self._data[var].table.setRange(variable=variable, range=range)
    
    #########################################################################
    #Private methods:
    def _readTableProperties(self, *, inputNames:dict[str,str]=None, inputVariables:Iterable[str]=None, fields:Iterable[str]=None) -> Iterable[str]:
        """
        Read information stored in file 'path/tableProperties'.
        
        Args:
            inputNames (dict[str,str], optional): The names to give to the input variables (optionally). Defaults to None.
            inputVariables (Iterable[str], optional): The input variables in correct nesting order. If not given, lookup for entry `inputVariables` in `tableProperties` file. Defaults to None.
            fields (Iterable[str], optional): The names of the fields to use for each output variable (by default, lookup for entry `fields` in `tableProperties` file). Defaults to None.
        
        Returns:
            Iterable[str]: The names of the fields stored in the tabulation.
        """
        #Check arguments
        if not inputNames is None:
            self.checkMap(inputNames, str, str, "inputNames")
        else:
            inputNames = dict()
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
        
        #Rename input variables and update order
        inputNames.update(**{var:var for var in inputVariables if not var in inputNames})
        #Check that entryNames are unique
        if len(inputNames.values()) != len(set(inputNames.values())):
            raise ValueError(f"Some input-variable names are not unique ({inputNames}).")
        
        #Check that all input arrays are present
        for ii, varName in enumerate(inputNames):
            if not varName + "Values" in tabProps:
                raise ValueError(f"Entry {varName + 'Values'} not found in tableProperties file. Avaliable entries are:\n\t" + "\n\t".join(tabProps.keys()))
        
        #Identify the ranges
        variables:dict[str,str] = dict()
        ranges:dict[str,list[float]] = dict()
        for ii,varName in enumerate(inputNames):
            # Variable name
            var = inputNames[varName]

            #Append range
            variables[var] = varName
            ranges[var] = tabProps.pop(varName + "Values")
            if not isinstance(ranges[var], Iterable):
                raise TypeError(f"Error reading ranges from tableProperties: '{varName + 'Values'}' range is not an Iterable class ({type(ranges[var]).__name__}).")
        
        #The final order
        order = list(variables.keys())
        
        if not len(order) == len(ranges):
            raise ValueError(f"Length of 'order' does not match number of input-variables in 'tableProperties' entry ({len(order)}!={len(ranges)})")
        
        #Fields
        if fields is None:
            if not "fields" in tabProps:
                raise ValueError("Entry 'fields' not found in tableProperties. Cannot detect the fields.")
            fields = tabProps.pop("fields")
        self.checkArray(fields, str, "fields")
        
        #Store:
        self._order = order[:]
        self._baseTableProperties = tabProps #Everything left
        self._inputVariables = {var:_InputProps(name=variables[var],data=ranges[var]) for var in order}

        return fields
    
    #################################
    #Read table from OF file:
    def _readTable(self,fileName:str, tableName:str, *, verbose:bool=True, **kwargs):
        """
        Read a tabulation from path/constant/fileName.

        Args:
            fileName (str): The name of the file where the tabulation is stored.
            tableName (str): The name to give to the loaded field in the tabulation.
            verbose (bool, optional): Print information about the loading process. Defaults to True.
            **kwargs: Optional keyword arguments of Tabulation.__init__ method of each Tabulation object.
            
        Returns:
            Self: self
        """
        #Table path:
        tabPath = self.path + "/constant/" + fileName
        if not(os.path.exists(tabPath)):
            raise IOError("Cannot read tabulation. File '{}' not found.".format(tabPath))
        if verbose: print(f"Loading file '{tabPath}' -> {tableName}")
        
        #Read table:
        tab = readOFscalarList(tabPath)
        
        if not(len(tab) == self.size):
            raise IOError(f"Size of table stored in '{tabPath}' is not consistent with the size of the tabulation ({len(tab)} != {self.size}).")
        
        #Add the tabulation
        self.addField(data=tab, field=tableName, file=fileName)
        
        return self
    
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
    #Setitem not allowed
    def __setitem__(self, index:int|Iterable[int]|slice, value:dict[str,float]|dict[str,np.ndarray[float]]) -> None:
        """
        Setting values in the table is not allowed.
        """
        raise NotImplementedError("Setting values in the table is not allowed.")
    
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
            raise NotImplementedError("Cannot compare OFTabulation with object of type '{}'.".format(value.__class__.__name__))
        
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
    def __repr__(self):
        return  super().__repr__() + f", fields={self.fields}, ...)"
    
    def __str__(self):
        str = super().__str__()
        str += f"Path: {self.path}\n"
        str += f"Fields: {self.fields}\n"
        return str