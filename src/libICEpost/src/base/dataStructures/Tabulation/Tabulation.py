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

from typing import Iterable, Literal
from enum import StrEnum

import pandas as pd
import numpy as np
from pandas import DataFrame

from libICEpost.src.base.Functions.typeChecking import checkType, checkArray, checkMap
from libICEpost.src.base.Utilities import Utilities
from scipy.interpolate import RegularGridInterpolator

import matplotlib as mpl
import matplotlib.colors as mcolors
from matplotlib import pyplot as plt

import itertools
import warnings

#####################################################################
#                            AUXILIARY CLASSES                      #
#####################################################################
class _OoBMethod(StrEnum):
    """Out-of-bounds methods"""
    extrapolate = "extrapolate"
    nan = "nan"
    fatal = "fatal"

class TabulationAccessWarning(Warning):
    """Warning from Tabulation access"""
    pass

#############################################################################
#                           AUXILIARY FUNCTIONS                             #
#############################################################################
def toPandas(table:Tabulation) -> DataFrame:
    """
    Convert an instance of Tabulation to a pandas.DataFrame with all the points stored in the tabulation.
    The columns are the input variables plus "output", which stores the sampling points.
    
    Args:
        table (Tabulation): The table to convert to a dataframe.

    Returns:
        DataFrame
    """
    checkType(table, Tabulation, "table")
    
    # Create the dataframe
    df = DataFrame({"output":[0.0]*table.size, **{f:[0.0]*table.size for f in table.ranges}})
    
    #Sort the columns to have first the input variables in order
    df = df[table.order + ["output"]]
    
    #Populate
    for ii, item in enumerate(table):
        input = table.getInput(ii)
        df.loc[ii, list(input.keys())] = [input[it] for it in input.keys()]
        df.loc[ii, "output"] = item

    return df

#Alias
to_pandas = toPandas

#############################################################################
def getInput(table:Tabulation, index:int|Iterable[int]) -> dict[str,float]:
    """
    Get the input values at a slice of the table.

    Args:
        table (Tabulation): The table to access.
        index (int | Iterable[int]): The index to access.
        
    Returns:
        dict[str:float]: A tuple with a dictionary mapping the names of input-variables to corresponding values
    """
    checkType(table, Tabulation, "table")
    ranges = table.ranges
    
    if isinstance(index, (int, np.integer)): #Single index
        # Convert to access by list
        return {table.order[ii]:ranges[table.order[ii]][id] for ii,id in enumerate(table._computeIndex(index))}
    elif isinstance(index, Iterable): #List of indexes
        output = {}
        for ii,id in enumerate(index):
            table.checkType(id, (int, np.integer), f"index[{ii}]")
            if id >= len(ranges[table.order[ii]]):
                raise IndexError(f"index[{ii}] {id} out of range for variable {table.order[ii]} ({id} >= {len(ranges[table.order[ii]])})")

            # Input variables
            output[table.order[ii]] = ranges[table.order[ii]][id]
        
        return output
    else:
        raise TypeError(f"Cannot access table with index of type {index.__class__.__name__}")

#############################################################################
def insertDimension(table:Tabulation, field:str, value:float, index:int, inplace:bool=False) -> Tabulation|None:
    """
    Insert an axis to the dimension-set of the table with a single value. 
    This is useful to merge two tables with respect to an additional field.
    
    Args:
        table (Tabulation): The table to modify.
        field (str): The name of the field to insert.
        value (float): The value for the range of the corresponding field.
        index (int): The index where to insert the field in nesting order.
        inplace (bool, optional): If True, the operation is performed in-place. Defaults to False.
        
    Returns:
        Tabulation|None: The table with the inserted dimension if inplace is False, None otherwise.
        
    Example:
        Create a table with two fields:
        ```
        >>> tab1 = Tabulation([1, 2, 3, 4], {"x":[0, 1], "y":[0, 1]}, ["x", "y"])
        >>> tab1.insertDimension("z", 0.0, 1)
        >>> tab1.ranges
        {"x":[0, 1], "z":[0.0], "y":[0, 1]}
        ```
        Create a second table with the same fields:
        ```
        >>> tab2 = Tabulation([5, 6, 7, 8], {"x":[0, 1], "y":[0, 1]}, ["x", "y"])
        >>> tab2.insertDimension("z", 1.0, 1)
        >>> tab2.ranges
        {"x":[0, 1], "z":[1.0], "y":[0, 1]}
        ```
        
        Concatenate the two tables:
        ```
        >>> tab1.concat(tab2, inplace=True)
        >>> tab1.ranges
        {"x":[0, 1], "z":[0.0, 1.0], "y":[0, 1]}
        ```
    """
    if not inplace:
        tab = table.copy()
        tab.insertDimension(field, value, index, inplace=True)
        return tab
    
    #Check arguments
    table.checkType(field, str, "field")
    table.checkType(value, float, "value")
    table.checkType(index, int, "index")
    table.checkType(inplace, bool, "inplace")
    
    #Check index
    if not (0 <= index <= table.ndim):
        raise ValueError(f"Index out of range. Must be between 0 and {table.ndim}.")
    #Insert field
    table._order.insert(index, field)
    table._ranges[field] = [value]
    table._data = table._data.reshape([len(table._ranges[f]) for f in table.order])

#############################################################################
def concat(table:Tabulation, *tables:tuple[Tabulation], inplace:bool=False, fillValue:float=None, overwrite:bool=False) -> Tabulation|None:
    """
    Extend the table with the data of other tables. The tables must have the same fields but 
    not necessarily in the same order. The data of the second table is appended to the data 
    of the first table, preserving the order of the fields.
    
    If fillValue is not given, the ranges of the second table must be consistent with those
    of the first table in the fields that are not concatenated. If fillValue is given, the
    missing sampling points are filled with the given value.
    
    Args:
        table (Tabulation): The table to which the data is appended.
        *tables (tuple[Tabulation]): The tables to append.
        inplace (bool, optional): If True, the operation is performed in-place. Defaults to False.
        fillValue (float, optional): The value to fill missing sampling points. Defaults to None.
        overwrite (bool, optional): If True, overwrite the data of the first table with the data 
            of the second table in overlapping regions. Otherwise raise an error. Defaults to False.
    
    Returns:
        Tabulation|None: The concatenated table if inplace is False, None otherwise.
    """
    #Check arguments
    checkType(table, Tabulation, "table")
    checkArray(tables, Tabulation, "tables")
    checkType(inplace, bool, "inplace")
    checkType(overwrite, bool, "overwrite")
    if not fillValue is None:
        checkType(fillValue, float, "fillValue")
    
    if not inplace:
        tab = table.copy()
        tab.concat(*tables, inplace=True, fillValue=fillValue, overwrite=overwrite)
        return tab
    
    for ii, tab in enumerate(tables):
        #Check compatibility
        if not (sorted(table.order) == sorted(tab.order)):
            raise ValueError(f"Tables must have the same fields to concatenate (table[{ii}] incompatible).")
        
        #Cast the two tables to dataframes
        df1 = toPandas(table)
        df1.set_index(table.order, inplace=True)
        df2 = toPandas(tab)[table.order + ["output"]]
        df2.set_index(table.order, inplace=True)
        
        #Check for overlapping regions between sampling points of the two tables
        sp1 = set(df1.index.values)
        sp2 = set(df2.index.values)
        if (not overwrite) and (len(sp1.intersection(sp2)) > 0):
            raise ValueError("Overlapping regions between the two tables. Set 'overwrite' to True to overwrite the data in the overlapping regions.")
        
        #Merge second to first
        merged = pd.concat([df1.drop(axis=0, index=sp2.intersection(sp1)), df2], axis=0, sort=True)
        
        #New ranges
        index = merged.index
        newRanges = {f:sorted(index.get_level_values(f).unique()) for f in table.order}
        
        #Check for missing sampling points
        samplingPoints = itertools.product(*[newRanges[f] for f in table.order])
        for sp in samplingPoints:
            if not sp in merged.index:
                if fillValue is None:
                    raise ValueError("Missing sampling point in the second table. Cannot concatenate without 'fillValue' argument.")
                merged.loc[sp] = fillValue
        
        #Sort
        merged.sort_index(inplace=True)
        
        #Create new table
        table._ranges = newRanges
        table._data = merged["output"].values.reshape([len(newRanges[f]) for f in table.order])

#############################################################################
def squeeze(table:Tabulation, *, inplace:bool=False) -> Tabulation|None:
    """
    Remove dimensions with only 1 data-point.
    
    Args:
        table (Tabulation): The table to squeeze.
        inplace (bool, optional): If True, the operation is performed in-place. Defaults to False.
    
    Returns:
        Tabulation|None: The squeezed tabulation if inplace is False, None otherwise.
    """
    if not inplace:
        tab = table.copy()
        tab.squeeze(inplace=True)
        return tab
    
    #Find dimensions with more than one data-point
    dimsToKeep = []
    for ii, dim in enumerate(table.shape):
        if dim > 1:
            dimsToKeep.append(ii)
    
    #Extract data
    table._order = list(map(table.order.__getitem__, dimsToKeep))
    table._ranges = {var:table._ranges[var] for var in table._order}
    table._data = table._data.squeeze()
    
    #Update interpolator
    table._createInterpolator()

#########################################################################
def sliceTable(table:Tabulation, *, slices:Iterable[slice|Iterable[int]|int]=None, ranges:dict[str,float|Iterable[float]]=None, **argv) -> Tabulation:
    """
    Extract a table with sliced datase. Can access in two ways:
        1) by slicer
        2) sub-set of interpolation points. Keyword arguments also accepred.
    Args:
        table (Tabulation): The table
        ranges (dict[str,float|Iterable[float]], optional): Ranges of sliced table. Defaults to None.
        slices (Iterable[slice|Iterable[int]|int]): The slicers for each input-variable.
    Returns:
        Tabulation: The sliced table.
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
        
        #Create slicing table:
        slTab = np.ix_(*tuple(slices))
        data = table.data[slTab]
        
        return Tabulation(data, ranges, order)
    
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
#Plot:
def plotTable(   table:Tabulation, 
            x:str, c:str, iso:dict[str,float], 
            *,
            ax:plt.Axes=None,
            colorMap:str="turbo",
            xlabel:str=None,
            ylabel:str=None,
            clabel:str=None,
            title:str=None,
            xlim:tuple[float]=(None, None),
            ylim:tuple[float]=(None, None),
            clim:tuple[float]=(None, None),
            figsize:tuple[float]=(8, 6),
            **kwargs) -> plt.Axes:
    """
    Plot a table in a 2D plot with a color-map.
    
    Args:
        x (str): The x-axis field.
        c (str): The color field.
        iso (dict[str,float]): The iso-values to plot.
        ax (plt.Axes, optional): The axis to plot on. Defaults to None.
        colorMap (str, optional): The color-map to use. Defaults to "turbo".
        xlabel (str, optional): The x-axis label. Defaults to None.
        ylabel (str, optional): The y-axis label. Defaults to None.
        clabel (str, optional): The color-bar label. Defaults to None.
        title (str, optional): The title of the plot. Defaults to None.
        xlim (tuple[float], optional): The x-axis limits. Defaults to (None, None).
        ylim (tuple[float], optional): The y-axis limits. Defaults to (None, None).
        clim (tuple[float], optional): The color-bar limits. Defaults to (None, None).
        figsize (tuple[float], optional): The size of the figure. Defaults to (8, 6).
        **kwargs: Additional arguments to pass to the plot
    
    Returns:
        plt.Axes: The axis of the plot.
    """
    
    #Check arguments
    checkType(table, Tabulation, "table")
    checkType(x, str, "x")
    checkType(c, str, "c")
    checkMap(iso, str, float, "iso")
    checkType(ax, plt.Axes, "ax", allowNone=True)
    checkType(colorMap, str, "colorMap")
    checkType(xlabel, str, "xlabel", allowNone=True)
    checkType(ylabel, str, "ylabel", allowNone=True)
    checkType(clabel, str, "clabel", allowNone=True)
    checkType(title, str, "title", allowNone=True)
    checkType(xlim, tuple, "xlim")
    checkType(ylim, tuple, "ylim")
    checkType(clim, tuple, "clim")
    checkType(figsize, tuple, "figsize")
    
    #Check fields
    if not x in table.order:
        raise ValueError(f"Field '{x}' not found in table.")
    if not c in table.order:
        raise ValueError(f"Field '{c}' not found in table.")
    
    #Check iso-values
    for f in iso:
        if not f in table.order:
            raise ValueError(f"Field '{f}' not found in table.")
        if not iso[f] in table.ranges[f]:
            raise ValueError(f"Iso-value for field '{f}' not found in the table.")
    
    if not (set(table.order) == set(iso.keys()).union({x, c})):
        raise ValueError("Iso-values must be given for all but x and c fields.")
    
    #Create the axis
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    
    #Default plot style
    if not any(s in kwargs for s in ["marker", "m"]):
        kwargs.update(marker="o")
    if not any(s in kwargs for s in ["linestyle", "ls"]):
        kwargs.update(linestyle="--")
    
    #Slice the data-set
    tab = table.slice(ranges={f:[iso[f]] for f in iso})
    
    #Update color-bar limits
    if clim[0] is None:
        clim = (tab.ranges[c].min(), clim[1])
    if clim[1] is None:
        clim = (clim[0], tab.ranges[c].max())
    
    #Plot
    cmap = mpl.colormaps[colorMap]
    norm = mcolors.Normalize(vmin=clim[0], vmax=clim[1])
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    
    for ii, val in enumerate(tab.ranges[c]):
        data = tab.slice(ranges={c:[val]})
        ax.plot(
            data.ranges[x],
            data.data.flatten(),
            color=cmap(norm(val)),
            **kwargs)
    
    #Color-bar
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label(clabel if not clabel is None else c)
    
    #Labels
    ax.set_xlabel(xlabel if not xlabel is None else x)
    ax.set_ylabel(ylabel)
    ax.set_title(title if not title is None else " - ".join([f"{f}={iso[f]}" for f in iso]))
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    
    return ax

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Class used for storing and handling a generic tabulation:
class Tabulation(Utilities):
    """
    Class used for storing and handling a tabulation from a structured grid in an n-dimensional space of input-variables. 
    """
    
    _ranges:dict[str,np.ndarray]
    """The sampling points for each input-variable"""
    
    _order:list[str]
    """The order in which the input variables are nested"""
    
    _data:np.ndarray
    """The n-dimensional dataset of the table"""
    
    _outOfBounds:_OoBMethod
    """How to handle out-of-bounds access to table."""
    
    _interpolator:RegularGridInterpolator
    """The interpolator."""
    
    #########################################################################
    #Class methods:
    @classmethod
    def from_pandas(cls, data:DataFrame, order:Iterable[str], field:str, **kwargs) -> Tabulation:
        """
        Construct a tabulation from a pandas.DataFrame with n+x columns where n is len(order).
        
        Args:
            data (DataFrame): The data-frame to use.
            order (Iterable[str]): The order in which the input variables are nested.
            field (str): The name of the field containing the output values.
            **kwargs: Additional arguments to pass to the constructor.
            
        Returns:
            Tabulation: The tabulation.
        """
        #Argument checking:
        cls.checkType(data, DataFrame, "data")
        cls.checkArray(order, str, "order")
        cls.checkType(field, str, "field")
        if not len(data.columns) > len(order):
            raise ValueError("DataFrame must have n+x columns, where n is the number of input variables.")
        for f in order:
            if not f in data.columns:
                raise ValueError(f"Field '{f}' not found in DataFrame.")
        if not field in data.columns:
            raise ValueError(f"Field '{field}' not found in DataFrame.")
        
        #Create ranges:
        ranges = {}
        for f in order:
            ranges[f] = np.array(sorted(data[f].unique()))
        
        #Sort data in the correct order
        data_sorted = data.sort_values(by=order, ascending=True, ignore_index=True)
        
        #Check that all combinations of input variables are present and in the correct order
        samplingPoints = itertools.product(*[ranges[f] for f in order])
        
        for ii, sp in enumerate(samplingPoints):
            for jj, f in enumerate(order):
                if not data_sorted.iloc[ii][f] == sp[jj]:
                    raise ValueError(f"Data not consistent with sampling points. Expected {sp} at index {ii} for field '{f}'.")
        
        #Create data and return
        return cls(data_sorted[field].values, ranges, order, **kwargs)
    
    #Alias
    fromPandas = from_pandas
    
    #########################################################################
    #Properties:
    @property
    def outOfBounds(self) -> str:
        """The current method of handling out-of-bounds access to tabulation."""
        return self._outOfBounds.value
    
    @outOfBounds.setter
    def outOfBounds(self, outOfBounds:Literal["extrapolate", "fatal", "nan"]):
        self.checkType(outOfBounds, str, "outOfBounds")
        self._outOfBounds = _OoBMethod(outOfBounds)
        
        #Update interpolator
        self._createInterpolator()
    
    ####################################
    @property
    def order(self) -> list[str]:
        """
        The order in which variables are nested.

        Returns:
            list[str]
        """
        return self._order[:]
    
    @order.setter
    def order(self, order:Iterable[str]):
        self.checkArray(order, str, "order")
        
        if not len(order) == len(self.order):
            raise ValueError("Length of new order is inconsistent with number of variables in the table.")
        
        if not sorted(self.order) == sorted(order):
            raise ValueError("Variables for new ordering are inconsistent with variables in the table.")
        
        self._data = self._data.transpose(*[self.order.index(o) for o in order])
        self._order = order
        
        #Update interpolator
        self._createInterpolator()
        
    ####################################
    @property
    def ranges(self):
        """
        Get a dict containing the data ranges in the tabulation (read-only).
        """
        return {r:self._ranges[r].copy() for r in self._ranges}
    
    #######################################
    #Get data:
    @property
    def data(self):
        """
        The data-structure storing the sampling points (read-only).
        """
        return self._data.copy()
    
    #######################################
    #Get interpolator:
    @property
    def interpolator(self) -> RegularGridInterpolator:
        """
        Returns the interpolator.
        """
        return self._interpolator
    
    #######################################
    @property
    def ndim(self) -> int:
        """
        Returns the number of dimentsions of the table.
        """
        return self._data.ndim
    
    #######################################
    @property
    def shape(self) -> tuple[int]:
        """
        The shape, i.e., how many sampling points are used for each input-variable.
        """
        return self._data.shape
    
    #######################################
    @property
    def size(self) -> int:
        """
        Returns the number of data-points stored in the table.
        """
        return self._data.size
    
    #########################################################################
    #Constructor:
    def __init__(self, data:Iterable[float]|Iterable, ranges:dict[str,Iterable[float]], order:Iterable[str], *, outOfBounds:Literal["extrapolate", "fatal", "nan"]="fatal"):
        """
        Construct a tabulation from the data at the interpolation points, 
        the ranges of each input variable, and the order in which the 
        input-variables are nested.

        Args:
            data (Iterable[float]|Iterable): Data structure containing the interpulation values at 
                sampling points of the tabulation.
                - If 1-dimensional array is given, data are stored as a list by recursively looping over the ranges stored in 'ranges', following variable
                hierarchy set in 'order'. 
                - If n-dimensional array is given, shape must be consistent with 'ranges'.
            ranges (dict[str,Iterable[float]]): Sampling points used in the tabulation for each input variable.
            order (Iterable[str]): Order in which the input variables are nested.
            outOfBounds (Literal[&quot;extrapolate&quot;, &quot;nan&quot;, &quot;fatal&quot;], optional): Ho to handle out-of-bound access to the tabulation. Defaults to "fatal".
        
        Raises:
            TypeError: If data is a DataFrame. Use 'from_pandas' method to create a Tabulation from a DataFrame.
        """
        if isinstance(data, DataFrame):
            raise TypeError("Use 'from_pandas' method to create a Tabulation from a DataFrame.")
        
        #Argument checking:
        self.checkType(data, Iterable, entryName="data")
        data = np.array(data) #Cast to numpy
        
        #Ranges
        self.checkMap(ranges, str, Iterable, entryName="ranges")
        [self.checkArray(ranges[var], float, f"ranges[{var}]") for var in ranges]
        
        #Check that ranges are in ascending order
        for r in ranges:
            if not (list(ranges[r]) == sorted(ranges[r])):
                raise ValueError(f"Range for variable '{r}' not sorted in ascending order.")
        
        #Order
        self.checkArray(order, str,entryName="order")
        
        #Order consistent with ranges
        if not(len(ranges) == len(order)):
            raise ValueError("Length missmatch. Keys of 'ranges' must be the same of the elements of 'order'.")
        for key in ranges:
            if not(key in order):
                raise ValueError(f"key '{key}' not found in entry 'order'. Keys of 'ranges' must be the same of the elements of 'order'.")
        
        #check size of data
        numEl = np.prod([len(ranges[r]) for r in ranges])
        if len(data.shape) <= 1:
            if not(len(data) == numEl):
                raise ValueError("Size of 'data' is not consistent with the data-set given in 'ranges'.")
        else:
            if not(data.size == numEl):
                raise ValueError("Size of 'data' is not consistent with the data-set given in 'ranges'.")
            
            if not(data.shape == tuple([len(ranges[o]) for o in order])):
                raise ValueError("Shape of 'data' is not consistent with the data-set given in 'ranges'.")
        
        #Storing copy
        ranges = {r:list(ranges[r][:]) for r in ranges}
        order = list(order[:])
        
        #Casting to np.array:
        for r in ranges:
            ranges[r] = np.array(ranges[r])
        
        #Ranges and order:
        self._ranges = ranges
        self._order = order
        self._data = data
        
        #Reshape if given list:
        if len(data.shape) == 1:
            self._data = self._data.reshape([len(ranges[o]) for o in order])
        
        #Options
        self._outOfBounds = _OoBMethod(outOfBounds)
        self._createInterpolator()
    
    #########################################################################
    #Private member functions:
    def _createInterpolator(self) -> None:
        """Create the interpolator.
        """
        #Create grid:
        ranges = []
        for f in self.order:
            #Check for dimension:
            range_ii = self._ranges[f]
            if len(range_ii) > 1:
                ranges.append(range_ii)
        
        #Remove empty directions
        tab = self._data.squeeze()
        
        #Extrapolation method:
        opts = {"bounds_error":False}
        if self.outOfBounds == _OoBMethod.fatal:
            opts.update(bounds_error=True)
        elif self.outOfBounds == _OoBMethod.nan:
            opts.update(fill_value=float('nan'))
        elif self.outOfBounds == _OoBMethod.extrapolate:
            opts.update(fill_value=None)
        else:
            raise ValueError(f"Unexpecred out-of-bound method {self.outOfBounds}")
        
        self._interpolator = RegularGridInterpolator(tuple(ranges), tab, **opts)
    
    #######################################
    def _computeIndex(self, index:int|Iterable[int]|slice) -> tuple[int]|Iterable[tuple[int,...]]:
        """
        Compute the location of an index inside the table. Getting the index, returns a list of the indices of each input-variable.
        
        Args:
            index (int | Iterable[int] | slice): The index to access.
        
        Returns:
            tuple[int] | Iterable[tuple[int,...]]: The index/indices:
                - If int is given, returns tuple[int].
                - If slice or Iterable[int] is given, returns Iterable[tuple[int,...]].
            
        Example:
            >>> self.shape
            (2, 3, 4)
            >>> self._computeIndex(12)
            (1, 0, 0)
            >>> self._computeIndex([0, 1, 2])
            [(0, 0, 0), (0, 0, 1), (0, 0, 2)]
            >>> self._computeIndex(slice(0, 3))
            [(0, 0, 0), (0, 0, 1), (0, 0, 2)]
        """
        # If slice, convert to list of index
        if isinstance(index, slice):
            index = list(range(*index.indices(self.size)))
            index = np.array(index, dtype=np.intp)
        
        #Compute index
        out = np.unravel_index(index, self.shape)
        
        #Check if out is a tuple of array, if so reshape
        if isinstance(out[0], np.ndarray):
            out = [tuple(row) for row in np.transpose(out)]

        return out
        
    #########################################################################
    #Public member functions:
    getInput = getInput
    append = merge = concat = concat
    insertDimension = insertDimension
    slice = sliceTable
    squeeze = squeeze
    
    def copy(self):
        """
        Create a copy of the tabulation.
        """
        return Tabulation(self.data, self.ranges, self.order, outOfBounds=self.outOfBounds)
    
    #Conversion
    toPandas = to_pandas = toPandas
    
    #Plotting
    plot = plotTable
    
    #########################################################################
    #Dunder methods
    
    #Interpolation
    def __call__(self, *args:tuple[float,...]|tuple[tuple[float,...],...], outOfBounds:str=None) -> float|np.ndarray[float]:
        """
        Multi-linear interpolation from the tabulation. The input data must be consistent with the number of input-variables stored in the tabulation.

        Args:
            *args (tuple[float,...] | Iterable[tuple[float,...]]): The input data to interpolate.
            - If tuple[float,...] is given, returns float.
            - If tuple[tuple[float,...]] is given, returns np.ndarray[float], where each entry is the result of the interpolation.
            outOfBounds (str, optional): Overwrite the out-of-bounds method before interpolation. Defaults to None.

        Returns:
            float: The return value.
        """
        #Check arguments
        self.checkType(args, (tuple, Iterable), "args")
        
        #Check for single entry
        if not isinstance(args[0], Iterable):
            args = [args]
        
        #Pre-processing: check for dimension and extract active dimensions
        entries = []
        self.checkArray(args, Iterable, "args")
        for ii, entry in enumerate(args):
            self.checkArray(entry, float, f"args[{ii}]")
            
            #Check for dimension
            if len(entry) != self.ndim:
                raise ValueError("Number of entries not consistent with number of dimensions stored in the tabulation ({} expected, while {} found).".format(self.ndim, len(entry)))
            
            #extract active dimensions
            entries.append([])
            for ii, f in enumerate(self.order):
                #Check for dimension:
                if len(self._ranges[f]) > 1:
                    entries[-1].append(entry[ii])
                else:
                    if entry[ii] != self._ranges[f][0]:
                        warnings.warn(
                            TabulationAccessWarning(
                                f"Field '{f}' with only one data-point, cannot " +
                                "interpolate along that dimension. Entry for that " +
                                "field will be ignored.")
                            )
        
        #Update out-of-bounds
        if not outOfBounds is None:
            oldOoB = self.outOfBounds
            self.outOfBounds = outOfBounds
        
        #Compute
        returnValue = self.interpolator(entries)
        
        #Reset oob
        if not outOfBounds is None:
            self.outOfBounds = oldOoB
        
        #Give results
        if len(returnValue) == 1:
            return returnValue[0]
        else:
            return returnValue
    
    #######################################
    def __getitem__(self, index:int|Iterable[int]|slice) -> float|np.ndarray[float]:
        """
        Get an element in the table.

        Args:
            index (int | Iterable[int] | slice | Iterable[slice]): Either:
                - An index to access the table (flattened).
                - A tuple of the x,y,z,... indices to access the table.
                - A slice to access the table (flattened).
                - A tuple of slices to access the table.
            
        Returns:
            float | Iterable[float]: The value at the index/indices:
                - If int|Iterable[int] is given, returns float.
                - If slice|Iterable[slice] is given, returns np.ndarray[float].
        """
        # If not list of index/slice, flatten access
        if isinstance(index, (int, np.integer, slice)):
            return self._data.flatten()[index]
        elif isinstance(index, tuple) and all(isinstance(i, (int, np.integer)) for i in index):
            return self._data.flatten()[np.ravel_multi_index(index, self.shape)]
        return self._data[index]
    
    #######################################
    def __setitem__(self, index:int|Iterable[int]|slice|tuple[int|Iterable[int]|slice], value:float|np.ndarray[float]) -> None:
        """
        Set the interpolation values at a slice of the table through np.ndarray.__setitem__ but:
        - If int|Iterable[int]|slice is given, set the value at the index/indices in the flattened dataset.
        - If tuple[int|Iterable[int]|slice] is given, set the value at the index/indices in the nested dataset.
        """
        try:
            #Check nested access
            if isinstance(index, tuple):
                if len(index) != self.ndim:
                    raise ValueError("Number of entries not consistent with number of dimensions stored in the tabulation ({} expected, while {} found).".format(self.ndim, len(index)))
                
                #Use ndarray.__setitem__
                self._data.__setitem__(index, value)
            
            #Flattened access
            elif isinstance(index, (int, np.integer, slice, Iterable)):
                if isinstance(index, Iterable):
                    self.checkArray(index, (int, np.integer), "index")
                
                nestedId = self._computeIndex(index)
                if isinstance(nestedId, tuple): #Single index -> convert to list[tuple]
                    nestedId = [nestedId]
                
                if not isinstance(value, Iterable): #Single value -> convert to list
                    value = [value]
                
                if not len(value) == len(nestedId):
                    raise ValueError("Number of entries not consistent with number of dimensions stored in the tabulation ({} expected, while {} found).".format(len(nestedId), len(value)))
                
                for idx, val in zip(nestedId, value):
                    self._data.__setitem__(idx, val)
            
            else:
                raise TypeError("Cannot access with index of type '{}'.".format(index.__class__.__name__))
            
        except BaseException as err:
            raise ValueError("Failed setting items in Tabulation: {}".format(err))
        
        #Update interpolator
        self._createInterpolator()
    
    #######################################
    def __eq__(self, value:Tabulation) -> bool:
        if not isinstance(value, Tabulation):
            raise NotImplementedError("Cannot compare Tabulation with object of type '{}'.".format(value.__class__.__name__))
        
        #Ranges
        if False if (self._ranges.keys() != value._ranges.keys()) else any([not np.array_equal(value._ranges[var], self._ranges[var]) for var in self._ranges]):
            return False
        
        #Order
        if self._order != value._order:
            return False
        
        #Data
        if not np.array_equal(value._data, self._data):
            return False
        
        return True
    
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
    
    #######################################
    def __add__(self, table:Tabulation) -> Tabulation:
        """
        Concatenate two tables. Alias for 'concat'.
        """
        return self.concat(table, inplace=False, fillValue=None, overwrite=False)
    
    def __iadd__(self, table:Tabulation) -> None:
        """
        Concatenate two tables in-place. Alias for 'concat'.
        """
        self.concat(table, inplace=True, fillValue=None, overwrite=False)