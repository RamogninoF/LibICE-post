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

import copy as cp
import numpy as np
from pandas import DataFrame

from libICEpost.src.base.Utilities import Utilities
from scipy.interpolate import RegularGridInterpolator

import matplotlib as mpl
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

#####################################################################
#                            AUXILIARY CLASSES                      #
#####################################################################
class _OoBMethod(StrEnum):
    """Out-of-bounds methods"""
    extrapolate = "extrapolate"
    nan = "nan"
    fatal = "fatal"

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
    Utilities.checkType(table, Tabulation, "table")
    
    # Create the dataframe
    df = DataFrame({"output":[0.0]*table.size, **{f:[0.0]*table.size for f in table.inputVariables}})
    
    #Sort the columns to have first the input variables in order
    df = df[table.order + ["output"]]
    
    #Populate
    for ii, item in enumerate(table):
        df.loc[ii, list(item[0].keys())] = [item[0][it] for it in item[0].keys()]
        df.loc[ii, "output"] = item[1]

    return df

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
    def from_pandas(cls, data:DataFrame, order:Iterable[str]) -> Tabulation:
        """_summary_

        Args:
            data (DataFrame): _description_
            order (Iterable[str]): _description_

        Raises:
            NotImplementedError: _description_

        Returns:
            Tabulation: _description_
        """
        #Construct from a data-frame with n+1 columns where n is len(order).
        raise NotImplementedError("Construction from DataFrame not implemented.")
    
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
        return self._order
    
    @order.setter
    def order(self, order:Iterable[str]):
        self.checkArray(order, str, "order")
        
        if not len(order) == len(self.order):
            raise ValueError("Length of new order is inconsistent with number of variables in the table.")
        
        if not all(sorted(self.order) == sorted(order)):
            raise ValueError("Variables for new ordering are inconsistent with variables in the table.")
        
        self._data = self._data.transpose(axes=[self.order.index(o) for o in order])
        self._order = order
        
        #Update interpolator
        self._createInterpolator()
        
    ####################################
    @property
    def ranges(self):
        """
        Get a dict containing the data ranges in the tabulation (read-only).
        """
        return cp.deepcopy(self._ranges)
    
    #######################################
    #Get data:
    @property
    def data(self):
        """
        The data-structure storing the sampling points (read-only).
        """
        return cp.deepcopy(self._data)
    
    #######################################
    #Get interpolator:
    @property
    def interpolator(self) -> RegularGridInterpolator:
        """
        Returns a copy of the stored data structure
        """
        self._createInterpolator()
        return self._interpolator
    
    #######################################
    @property
    def ndim(self) -> int:
        """
        Returns the number of dimentsions of the table.
        """
        return len(self.order)
    
    #######################################
    @property
    def shape(self) -> tuple[int]:
        """
        The shape, i.e., how many sampling points are used for each input-variable.
        """
        return tuple([len(self._ranges[o]) for o in self.order])
    
    #######################################
    @property
    def size(self) -> int:
        """
        Returns the number of data-points stored in the table.
        """
        return np.prod([len(self._ranges[o]) for o in self.order])
    
    #########################################################################
    #Constructor:
    def __init__(self, data:Iterable[float]|Iterable, ranges:dict[str,Iterable[float]], order:Iterable[str], *, outOfBounds:Literal["extrapolate", "fatal", "nan"]="fatal"):
        """
        Construct a tabulation from the data at the interpolation points, 
        the ranges of each input variable, and the order in which the 
        input-variables are nested.

        Args:
            data (Iterable[float]|Iterable): Data structure containing the interpulation values at 
                sampling points of the tabulation. If 1-dimensional array is given, data are stored 
                as a list by recursively looping over the ranges stored in 'ranges', following variable
                hierarchy set in 'order'. If n-dimensional array is given, shape must be consistent 
                with 'ranges'.
            ranges (dict[str,Iterable[float]]): Sampling points used in the tabulation for each input variable.
            order (Iterable[str]): Order in which the input variables are nested.
            outOfBounds (Literal[&quot;extrapolate&quot;, &quot;nan&quot;, &quot;fatal&quot;], optional): Ho to handle out-of-bound access to the tabulation. Defaults to "fatal".
        """
        #Argument checking:
        self.checkType(data, Iterable, entryName="data")
        data = np.array(data) #Cast to numpy
        
        #Ranges
        self.checkMap(ranges, str, Iterable, entryName="ranges")
        [self.checkArray(ranges[var], float, f"ranges[{var}]") for var in ranges]
        
        #Check that ranges are in ascending order
        for r in ranges:
            if not all(ranges[r] == sorted(ranges[r])):
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
        
        #Using a copy
        ranges = cp.deepcopy(ranges)
        order = cp.deepcopy(order)
        
        #Casting to np.array:
        for r in ranges:
            ranges[r] = np.array(ranges[r])
        
        #Ranges and order:
        self._ranges = ranges
        self._order = order
        self._data = data
        
        #Reshape if given list:
        if len(data.shape) == 1:
            self._data = self._data.reshape(self.shape)
        
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
        tab = self.data.squeeze()
        
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
    def _indexList(self) -> list[list[int]]:
        """Compute the list of indexes for unwinding the nested loops.
        
        Example:
            shape = (2, 3, 4)
            output = \
                [
                    [0, 0, 0],
                    [0, 0, 1],
                    [0, 0, 2],
                    [0, 0, 3],
                    [0, 0, 4],
                    [0, 1, 0],
                    [0, 1, 1],
                    ...
                    
                    [1, 2, 3]
                ]

        Returns:
            list[list[int]]
        """
        #The size of the table
        size = self.size
        
        indexList = []
        counterList = [0]*len(self.shape)
        
        indexList.append(cp.copy(counterList))
        for ii in range(1,size):
            #Incremento:
            counterList[-1] += 1
            #Controllo i riporti:
            for jj in range(len(counterList)-1,-1,-1):  #Reversed order
                if counterList[jj] == self.shape[jj]:  #Riporto
                    counterList[jj] = 0
                    counterList[jj-1] += 1
            #Aggiungo a lista:
            indexList.append(cp.copy(counterList))
        
        return indexList
    
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
    #Dunder methods
    
    #Interpolation
    def __call__(self, *args:tuple[float|np.ndarray[float]], outOfBounds:str=None) -> float|np.ndarray[float]:
        """
        Multi-linear interpolation from the tabulation. The number of arguments to be given
        must be the same of the dimensions of the table.

        Args:
            *args:tuple[float]: The input data. Length must be consistent with number of input-variables.
            outOfBounds (str, optional): Overwrite the out-of-bounds method before interpolation. Defaults to None.

        Returns:
            float: The return value.
        """
        
        #Argument checking:
        if len(args) != self.ndim:
            raise ValueError("Number of entries not consistent with number of dimensions stored in the tabulation ({} expected, while {} found).".format(self.ndim, len(args)))
        
        entries = []
        for ii, f in enumerate(self.order):
            #Check for dimension:
            if len(self._ranges[f]) > 1:
                entries.append(args[ii])
            else:
                self.__class__.runtimeWarning("Field '{}' with only one data-point, cannot interpolate along that dimension. Entry for that field will be ignored.".format(f))
        
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
    def __getitem__(self, index:int|Iterable[int]) -> tuple[dict[str,float],float]:
        """
        Get an element in the table.

        Args:
            index (int | Iterable[int]): The index to access.
            
        Returns:
            tuple[dict[str:float],float]: A tuple with a dictionary mapping the names of input-variables to corresponding values, and a float with the value of the sampling point.
        """
        ranges = self.ranges
        
        if isinstance(index, (int, np.integer)):
            # Convert to access by list
            return self[self._computeIndex(index)]
        elif isinstance(index, Iterable):
            output = {}
            for ii,id in enumerate(index):
                self.checkType(id, (int, np.integer), f"index[{ii}]")
                if id >= len(ranges[self.order[ii]]):
                    raise IndexError(f"index[{ii}] {id} out of range for variable {self.order[ii]} ({id} >= {len(ranges[self.order[ii]])})")

                # Input variables
                output[self.order[ii]] = ranges[self.order[ii]][id]
            
            return output,self._data[index]
        else:
            raise TypeError(f"Cannot access with index of type {index.__class__.__name__}")
    
    #######################################
    def __setitem__(self, slices:tuple[slice|Iterable[int]|int], items:float|np.ndarray[float]):
        """
        Set the interpolation values at a slice of the table.

        Args:
            slices (tuple[slice|Iterable[int]|int]): The slicers for each input-variable.
            items (float | np.ndarray[float]): The value to set.
        """
        #Argument checking:
        self.checkType(items, (Iterable, float), "items")
        self.checkType(slices, tuple, "slices")
        
        if not(len(slices) == len(self.order)):
            raise IndexError("Given {} ranges, while table has {} fields ({}).".format(len(slices), len(self.order), self.order))
        
        indTable = []
        for ii,var in enumerate(self.order):
            ss = slices[ii]
            indList = range(len(self.ranges[var]))
            
            if isinstance(ss, slice):
                try:
                    indTable.append(indList[ss])
                except BaseException as err:
                    raise IndexError(f"Slice '{ss}' out of range for field '{var}'.")
                
            elif isinstance(ss,int):
                if not(ss in indList):
                    raise IndexError("Index out of range for field '{}'.".format(var))
                indTable.append([ss])
            
            elif isinstance(ss,Iterable):
                for ind in ss:
                    if not(ind in indList):
                        raise IndexError("Index out of range for field '{}'.".format(var))
                
                indTable.append(ss)
                
            else:
                raise TypeError("Type missmatch. Attempting to slice with entry of type '{}'.".format(ss.__class__.__name__))
        
        #Set values:
        try:
            slTab = np.ix_(*tuple(slices))
            self._data[slTab] = items
        except BaseException as err:
            raise ValueError("Failed setting items in Tabulation")
        
        #Update interpolator
        self._createInterpolator()
    
    #######################################
    def __eq__(self, value:Tabulation) -> bool:
        if not isinstance(value, Tabulation):
            return False
        
        #Ranges
        if False if (self._ranges.keys() != value._ranges.keys()) else any([not np.array_equal(value._ranges[var], self._ranges[var]) for var in self._ranges]):
            return False
        
        #Order
        if self._order != value._order:
            return False
        
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
    
    #########################################################################
    #Public member functions:
    
    #Squeeze 0/1 len dimension
    def squeeze(self):
        """
        Remove dimensions with only 1 data-point.
        """
        dimsToKeep = []
        for ii, dim in enumerate(self.shape):
            if dim > 1:
                dimsToKeep.append(ii)
        
        self._order = map(self.order.__getitem__, dimsToKeep)
        self._ranges = {var:self._ranges[var] for var in self._order}
        self._data = self._data.squeeze()
        
        #Update interpolator
        self._createInterpolator()
    
    #######################################
    def slice(self, slices:Iterable[slice|Iterable[int]|int]=None, ranges:dict[str,Iterable[float]]=None, **argv) -> Tabulation:
        """
        Extract a table with sliced datase. Can access in two ways:
            1) by slicer
            2) sub-set of interpolation points. Keyworld arguments also accepred.

        Args:
            ranges (dict[str,Iterable[float]], optional): Ranges of sliced table. Defaults to None.
            slices (Iterable[slice|Iterable[int]|int]): The slicers for each input-variable.

        Returns:
            Tabulation: The sliced table.
        """
        #Swith access
        if not slices is None:
            #By slices
            
            #Check other args
            if (not ranges is None) or (len(argv) > 0):
                raise ValueError("Cannot access both by slices and ranges")
            
            #Check types
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
            
            #Create slicing table:
            slTab = np.ix_(*tuple(slices))
            data = cp.deepcopy(self.data[slTab])
            
            return self.__class__(data, ranges, order)
        
        else:
            #By ranges
            ranges = dict() if ranges is None else ranges
            
            #Start from the original ranges
            newRanges = self.ranges
            
            #Check arguments:
            ranges = ranges.update(argv)
            self.checkMap(ranges, str, Iterable, entryName="ranges")
            
            for rr in ranges:
                for ii in ranges[rr]:
                    if not(ii in self.ranges[rr]):
                        raise ValueError("Sampling value '{}' not found in range for field '{}'.".format(ii,rr))
            
            #Update ranges
            newRanges.update(**ranges)
            
            #Create slicers to access by index
            slices = []
            for ii, item in enumerate(self.order):
                slices.append([self._ranges[item].index(vv) for vv in ranges[item]])
            
            #Slice by index
            return self.slice(tuple(slices))
    
    #######################################
    def concat(self, table:Tabulation, fieldName:str, *, inplace:bool=False) -> Tabulation|None:
        #Check arguments
        self.checkType(table, Tabulation, "table")
        self.checkType(fieldName, str, "fieldName")
        self.checkType(inplace, bool, "inplace")
        
        if not fieldName in self.order:
            raise ValueError("Field '{}' not found in table.".format(fieldName))
        
        if not fieldName in table.order:
            raise ValueError("Field '{}' not found in 'secondTable'.".format(fieldName))
        
        if (False if (len(self.order) != len(table.order)) else (self.order != table.order)):
            raise ValueError("Table fields not compatible.\nTable fields:\n{}\nFields of table to concatenate:\n{}".format(table.order, self.order))
        
        #Check if fields already present:
        for item in table.ranges[fieldName]:
            if item in self.ranges[fieldName]:
                raise ValueError("Value '{}' already present in range of field '{}'.".format(item, self.ranges[fieldName]))
        
        #Check compatibility:
        otherFields = [f for f in self.order if f != fieldName]
        otherRanges = {f:self.ranges[f] for f in otherFields}
        otherRangesSecond = {f:table.ranges[f] for f in otherFields}
        if otherRanges != otherRangesSecond:
            raise ValueError("Table ranges of other fields not compatible.\nTable ranges:\n{}Ranges of table to append:\n{}".format(otherRanges, otherRangesSecond))
        
        #Append data:
        if inplace:
            fieldIndex = self.order.index(fieldName)
            self._ranges[fieldName] += table.ranges[fieldName]
            self._data = np.append(self._data, table.data, axis=fieldIndex)
        else:
            #Copy and concatenate to copy
            table = self.copy()
            return self.copy().concat(table, fieldName, inplace=True)
    
    #########################################################################
    #Plot:
    # def plot(self, xVar:str, yVar:str, isoSurf=None, **argv):
    #     """
    #     xVar:   str
    #         Name of the field on x-axis
            
    #     yVar:   str
    #         Name of the field on the y-axis
            
    #     isoSurf:    list<dict>
    #         List of dictionaries used to sort which iso-surfaces to plot. Each
    #         element of the list must be a dictionary containing a value for
    #         each remaining field of the tabulation.
    #         It can be optional in case there are three fields in the tabulation,
    #         it will contain each element of the third field. Otherwise it is
    #         mandatory.
            
    #         Exaple:
    #         [
    #             {
    #                 var_ii:value1.1
    #                 var_jj:value2.1
    #                 ...
    #             }
    #             {
    #                 var_ii:value1.2
    #                 var_jj:value2.2
    #                 ...
    #             }
    #             ...
    #         ]
        
    #     [keyworld arguments]
    #     xRange: list<float>
    #         Sampling points of the x-axis field (if want a subset)
        
    #     yRange: list<float>
    #         Sampling points of the y-axis field (if want a subset)
        
    #     Display the sampling points in the tabulation as iso-surfaces and
    #     returns a tuple with handles to figure and axes.
    #     """
    #     try:
    #         #Argument checking:
    #         Utilities.checkType(xVar, str, entryName="xVar")
    #         Utilities.checkType(yVar, str, entryName="yVar")
    #         if not(isoSurf is None):
    #             if len(isoSurf) == 0:
    #                 raise ValueError("dict entry 'isoSurf' is empty, cannot generate the iso-surface plot.")
                
    #             Utilities.checkInstanceTemplate(isoSurf, [{"A":1.0}], entryName="isoSurf")
            
    #         f = ""
    #         for F in self.fields():
    #             f += "\t" + F + "\n"
    #         if not(xVar in self.fields()):
    #             raise ValueError("Entry {} (xVar) not found among table fields. Available fields are:\n{}".format(f))
            
    #         if not(yVar in self.fields()):
    #             raise ValueError("Entry {} (yVar) not found among table fields. Available fields are:\n{}".format(f))
            
    #         defaultArgv = \
    #         {
    #             "xRange":   self.ranges()[xVar],
    #             "yRange":   self.ranges()[yVar]
    #         }
            
    #         argv = Utilities.updateKeywordArguments(argv, defaultArgv)
            
    #     except BaseException as err:
    #         self.fatalErrorInArgumentChecking(self.plot, err)
        
    #     #Ranges
    #     xRange = argv["xRange"]
    #     yRange = argv["yRange"]
        
    #     #Create figure:
    #     fig = plt.figure()
    #     ax = Axes3D(fig)
    #     X, Y = Utilities.np.meshgrid(xRange, yRange)
        
    #     try:
    #         if isoSurf is None:
    #             otherVar = None
    #             for var in self.fields():
    #                 if not ((var == xVar) or (var == yVar)):
    #                     #if not (otherVar is None):
    #                         #raise ValueError("Cannot plot iso-surfaces of table with more then 3 variables stored. Must give the data to plot through 'isoSurf' argument, as a list of dicts determining the iso values of the remaining variables:\n\n[\{var_ii:value1.1, var_jj:value2.1,...\}, {var_ii:value1.2, var_jj:value2.2,...\}, ...]")
    #                     if (otherVar is None):
    #                         otherVar = [var]
    #                     else:
    #                         otherVar.append(var)
                
    #             if otherVar is None:
    #                 Z = self.cp.deepcopy(X)
                    
    #                 for ii in range(X.shape[0]):
    #                     for jj in range(X.shape[1]):
                            
    #                         values = {xVar:X[ii][jj], yVar:Y[ii][jj]}
                            
    #                         #Sort in correct order
    #                         arguments = []
    #                         for field in self.fields():
    #                             if field in values:
    #                                 arguments.append(values[field])
    #                         arguments = tuple(arguments)
                            
    #                         Z[ii][jj] = self(*arguments)
                        
    #                 surf = ax.plot_surface(X, Y, Z)
    #                 surf._facecolors2d=surf._facecolors
    #                 surf._edgecolors2d=surf._edgecolors
                    
    #                 isoSurf = []
                    
    #             else:
    #                 isoSurf = []
    #                 varIDs = [0]*len(otherVar)
    #                 while(True):
    #                     #Append surface
    #                     isoSurf.append({})
    #                     for ii, var in enumerate(otherVar):
    #                         isoSurf[-1][var] = self.ranges()[var][varIDs[ii]]
                        
    #                     #Increase counter
    #                     for ii,var in enumerate(otherVar):
    #                         jj = len(varIDs)-ii-1
                            
    #                         if ii == 0:
    #                             varIDs[jj] += 1
                            
    #                         varIDs[jj], rem = (varIDs[jj]%len(self.ranges()[otherVar[jj]])), (varIDs[jj]//len(self.ranges()[otherVar[jj]]))
    #                         if jj > 0:
    #                             varIDs[jj-1] += rem
                        
    #                     #Check if looped the counter
    #                     if all([ID == 0 for ID in varIDs]):
    #                         break
                
    #         for isoDict in isoSurf:
    #             if not isinstance(isoDict, dict):
    #                 raise TypeError("'isoSurf' entry must be in the form:\n\n[\{var_ii:value1.1, var_jj:value2.1\}, {var_ii:value1.2, var_jj:value2.2\}, ...] \n\n where [var_ii, var_jj,...] are all the remaining dimensions of the tabulation, while valueXX.YY must be float or int.")
    #             elif  not isoDict:
    #                 raise ValueError("Empty entry in list 'isoSurf'. 'isoSurf' entry must be in the form:\n\n[\{var_ii:value1.1, var_jj:value2.1,...\}, {var_ii:value1.2, var_jj:value2.2,...\}, ...] \n\n where [var_ii, var_jj,...] are all the remaining dimensions of the tabulation.")
    #             elif not (len(isoDict) == (len(self.fields()) - 2)):
    #                 raise ValueError("Empty entry in list 'isoSurf'. 'isoSurf' entry must be in the form:\n\n[\{var_ii:value1.1, var_jj:value2.1,...\}, {var_ii:value1.2, var_jj:value2.2,...\}, ...] \n\n where [var_ii, var_jj,...] are all the remaining dimensions of the tabulation, while valueXX.YY must be float or int.")
                
    #             for key in isoDict:
    #                 if not(key in self.fields()):
    #                     raise ValueError("Key '{}' in element of entry 'isoSurf' not found among table fields. 'isoSurf' entry must be in the form:\n\n[\{var_ii:value1.1, var_jj:value2.1,...\}, {var_ii:value1.2, var_jj:value2.2,...\}, ...] \n\n where [var_ii, var_jj,...] are all the remaining dimensions of the tabulation, while valueXX.YY must be float or int.".format(key))
    #                 elif not(isinstance(isoDict[key], (int,float))):
    #                     raise TypeError("Wrong type, expected float or int, {} found. 'isoSurf' entry must be in the form:\n\n[\{var_ii:value1.1, var_jj:value2.1,...\}, {var_ii:value1.2, var_jj:value2.2,...\}, ...] \n\n where [var_ii, var_jj,...] are all the remaining dimensions of the tabulation, while valueXX.YY must be float or int.".format(isoDict[key].__class__.__name__))
                
    #             Z = Utilities.cp.deepcopy(X)
    #             for ii in range(X.shape[0]):
    #                 for jj in range(X.shape[1]):
                        
    #                     values = {xVar:X[ii][jj], yVar:Y[ii][jj]}
                        
    #                     label = ""
    #                     for key in isoDict:
    #                         if label:
    #                             label += " - "
    #                         label += "{}: {}".format(key,isoDict[key])
                            
    #                         values[key] = isoDict[key]
                            
    #                     #Sort in correct order
    #                     arguments = []
    #                     for field in self.fields():
    #                         if field in values:
    #                             arguments.append(values[field])
    #                     arguments = tuple(arguments)
                        
    #                     Z[ii][jj] = self(*arguments)
                
    #             surf = ax.plot_surface(X, Y, Z, label=label)
    #             surf._facecolors2d=surf._facecolors
    #             surf._edgecolors2d=surf._edgecolors
                
    #         ax.legend()
    #         plt.xlabel(xVar)
    #         plt.ylabel(yVar)
        
    #     except BaseException as err:
    #         self.fatalErrorInClass(self.plot, "Failed plotting tabulation", err)
        
    #     return fig, ax

#############################################################################
#                             AUXILIARY FUNCTIONS                           #
#############################################################################
def concat(tables:Iterable[Tabulation], fieldName:str) -> Tabulation:
        """
        Concatenate a list of tables.

        Args:
            tables (Iterable[Tabulation]): Tables to merge
            fieldName (str): Field to use to concatenate the tables

        Returns:
            Tabulation: The merged table
        """
        #Argument checking:
        Utilities.checkType(fieldName, str, entryName="fieldName")
        Utilities.checkType(tables, Iterable, entryName="tables")
        [Utilities.checkType(t, Iterable, entryName=f"tables[{ii}]") for ii,t in enumerate(tables)]
        
        #First table
        output = tables[0]
        
        #Append all
        for tab in output[1:]:
            tab.concat(output, fieldName, inplace=True)
            
        return tab
