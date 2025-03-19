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

from typing import Iterable, Any, Self

import numpy as np
from pandas import DataFrame

from abc import ABCMeta, abstractmethod
from libICEpost.src.base.Functions.typeChecking import checkType
from libICEpost.src.base.Utilities import Utilities

#############################################################################
#                           AUXILIARY FUNCTIONS                             #
#############################################################################
def getInput(table:BaseTabulation, index:int|Iterable[int]) -> dict[str,float]:
    """
    Get the input values at a slice of the table.

    Args:
        table (BaseTabulation): The table to access.
        index (int | Iterable[int]): The index to access.
        
    Returns:
        dict[str:float]: A tuple with a dictionary mapping the names of input-variables to corresponding values
    """
    checkType(table, BaseTabulation, "table")
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
def tableIndex(table:BaseTabulation, index:int|Iterable[int]|slice) -> tuple[int]|Iterable[tuple[int,...]]:
    """
    Compute the location of an index inside a table. Getting the index, returns a list of the indices of each input-variable.
    
    Args:
        table (BaseTabulation): The table to access.
        index (int | Iterable[int] | slice): The index to access.
    
    Returns:
        tuple[int] | Iterable[tuple[int,...]]: The index/indices:
            - If int is given, returns tuple[int].
            - If slice or Iterable[int] is given, returns Iterable[tuple[int,...]].
        
    Example:
        >>> table.shape
        (2, 3, 4)
        >>> table._computeIndex(12)
        (1, 0, 0)
        >>> table._computeIndex([0, 1, 2])
        [(0, 0, 0), (0, 0, 1), (0, 0, 2)]
        >>> table._computeIndex(slice(0, 3))
        [(0, 0, 0), (0, 0, 1), (0, 0, 2)]
    """
    # If slice, convert to list of index
    if isinstance(index, slice):
        index = list(range(*index.indices(table.size)))
        index = np.array(index, dtype=np.intp)
    
    #Compute index
    out = np.unravel_index(index, table.shape)
    
    #Check if out is a tuple of array, if so reshape
    if isinstance(out[0], np.ndarray):
        out = [tuple(row) for row in np.transpose(out)]
    return out

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Class used for storing and handling a generic tabulation:
class BaseTabulation(Utilities, metaclass=ABCMeta):
    """
    Class used for storing and handling a tabulation from a structured grid in an n-dimensional space of input-variables. 
    """

    _order:list[str]
    """The order in which the input variables are nested"""
    
    #########################################################################
    #Class methods:
    @classmethod
    @abstractmethod
    def from_pandas(cls, data:DataFrame, order:Iterable[str], *args, **kwargs) -> Self:
        """
        Construct a tabulation from a pandas.DataFrame with n+x columns where n is len(order).
        
        Args:
            data (DataFrame): The data-frame to use.
            order (Iterable[str]): The order in which the input variables are nested.
            **kwargs: Additional arguments to pass to the constructor.
            
        Returns:
            Self: The tabulation.
        """
        
    #Alias
    fromPandas = from_pandas
    
    #########################################################################
    #Properties:
    @property
    def order(self) -> list[str]:
        """
        The order in which variables are nested.

        Returns:
            list[str]
        """
        return self._order[:]
    
    @order.setter
    @abstractmethod
    def order(self, order:Iterable[str]):
        self.checkArray(order, str, "order")
        
        if not len(order) == len(self.order):
            raise ValueError("Length of new order is inconsistent with number of variables in the table.")
        
        if not sorted(self.order) == sorted(order):
            raise ValueError("Variables for new ordering are inconsistent with variables in the table.")
        
        self._order = order
        
    ####################################
    @property
    @abstractmethod
    def ranges(self):
        """
        Get a dict containing the data ranges in the tabulation (read-only).
        """
    
    #######################################
    @property
    @abstractmethod
    def ndim(self) -> int:
        """
        Returns the number of dimentsions of the table.
        """
    
    #######################################
    @property
    @abstractmethod
    def shape(self) -> tuple[int]:
        """
        The shape, i.e., how many sampling points are used for each input-variable.
        """
    
    #######################################
    @property
    @abstractmethod
    def size(self) -> int:
        """
        Returns the number of data-points stored in the table.
        """
    
    #########################################################################
    #Private member functions:
    _computeIndex = tableIndex
        
    #########################################################################
    #Public member functions:
    getInput = getInput
    
    @abstractmethod
    def insertDimension(self, variable:str, value:float, index:int=None, *, inplace:bool=False) -> BaseTabulation|None:
        """
        Insert an axis to the dimension-set of the table with a single value. 
        This is useful to merge two tables with respect to an additional variable.
        
        Args:
            table (BaseTabulation): The table to modify.
            variable (str): The name of the variable to insert.
            value (float): The value for the range of the corresponding variable.
            index (int, optional): The index where to insert the variable in nesting order. If None, append the variable at the end. Defaults to None.
            inplace (bool, optional): If True, the operation is performed in-place. Defaults to False.
            
        Returns:
            BaseTabulation|None: The table with the inserted dimension if inplace is False, None otherwise.
            
        Example:
            Create a table with two variables:
            ```
            >>> tab1 = Tabulation([1, 2, 3, 4], {"x":[0, 1], "y":[0, 1]}, ["x", "y"])
            >>> tab1.insertDimension("z", 0.0, 1)
            >>> tab1.ranges
            {"x":[0, 1], "z":[0.0], "y":[0, 1]}
            ```
            Create a second table with the same variables:
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
    
    @abstractmethod
    def slice(self, *, slices:Iterable[slice|Iterable[int]|int]=None, ranges:dict[str,float|Iterable[float]]=None, inplace:bool=False) -> Self|None:
        """
        Extract a table with sliced data. Can access in two ways:
            1) by slicer
            2) sub-set of interpolation points. Keyword arguments also accepred.
        
        Args:
            slices (Iterable[slice|Iterable[int]|int]): The slicers for each input-variable.
            ranges (dict[str,float|Iterable[float]], optional): Ranges of sliced table. Defaults to None.
            inplace (bool, optional): If True, the operation is performed in-place. Defaults to False.
        
        Returns:
            Self|None: The sliced table if inplace is False, None otherwise.
        """
    
    @abstractmethod
    def clip(self, ranges:dict[str,tuple[float|None,float|None]]=None, *, inplace:bool=False, **kwargs) -> Self|None:
        """
        Clip the table to the given ranges. The ranges are given as a dictionary with the 
        variable names as keys and a tuple with the minimum and maximum values.
    
        Args:
            ranges (dict[str,tuple[float|None,float|None]], optional): The ranges to clip for each input-variable. If min or max is None, the range is unbounded.
            inplace (bool, optional): If True, the operation is performed in-place. Defaults to False.
            **kwargs: Can access also by keyword arguments.
        
        Returns:
            Self|None: The clipped table if inplace is False, None otherwise.
        """
    
    @abstractmethod
    def concat(self, *tables:BaseTabulation, inplace:bool=False, fillValue:float=None, overwrite:bool=False) -> Self|None:
        """
        Extend the table with the data of other tables. The tables must have the same variables but 
        not necessarily in the same order. The data of the second table is appended to the data 
        of the first table, preserving the order of the variables.
        
        If fillValue is not given, the ranges of the second table must be consistent with those
        of the first table in the variables that are not concatenated. If fillValue is given, the
        missing sampling points are filled with the given value.
        
        Args:
            *tables (BaseTabulation): The tables to append.
            inplace (bool, optional): If True, the operation is performed in-place. Defaults to False.
            fillValue (float, optional): The value to fill missing sampling points. Defaults to None.
            overwrite (bool, optional): If True, overwrite the data of the first table with the data 
                of the second table in overlapping regions. Otherwise raise an error. Defaults to False.
        
        Returns:
            Self|None: The concatenated table if inplace is False, None otherwise.
        """
    
    append = merge = concat
    
    @abstractmethod
    def slice(self, slices:Iterable[slice|Iterable[int]|int]=None, ranges:dict[str,float|Iterable[float]]=None, inplace=False) -> Self:
        """
        Extract a table with sliced data. Can access in two ways:
            1) by slicer
            2) sub-set of interpolation points. Keyword arguments also accepred.
        
        Args:
            slices (Iterable[slice|Iterable[int]|int]): The slicers for each input-variable.
            ranges (dict[str,float|Iterable[float]], optional): Ranges of sliced table. Defaults to None.
            inplace (bool, optional): If True, the operation is performed in-place. Defaults to False.
            
        Returns:
            Self: The sliced table.
        """
        
    @abstractmethod
    def squeeze(self, inplace:bool=False) -> Self|None:
        """
        Remove dimensions with only 1 data-point.
        
        Args:
            inplace (bool, optional): If True, the operation is performed in-place. Defaults to False.
        
        Returns:
            Self|None: The squeezed tabulation if inplace is False, None otherwise.
        """
    
    #Conversion
    @abstractmethod
    def to_pandas(self) -> DataFrame:
        """
        Convert the tabulation to a pandas.DataFrame.
        
        Returns:
            DataFrame: The data-frame.
        """
    toPandas = to_pandas
    
    #Plotting
    @abstractmethod
    def plot(self, *args, **kwargs) -> None:
        """
        Plot the tabulation.
        """
    
    #########################################################################
    #Dunder methods
    
    #Interpolation
    @abstractmethod
    def __call__(self, *args, **kwargs) -> float|np.ndarray[float]:
        """
        Interpolate the table at a given point(s).
        """
        pass
    
    #######################################
    @abstractmethod
    def __getitem__(self, index:int|Iterable[int]|slice) -> Any | Iterable[Any]:
        """
        Get an element in the table.

        Args:
            index (int | Iterable[int] | slice | Iterable[slice]): Either:
                - An index to access the table (flattened).
                - A tuple of the x,y,z,... indices to access the table.
                - A slice to access the table (flattened).
                - A tuple of slices to access the table.
        
        Returns:
            Any | Iterable[Any]: The value(s) stored in the table.
        """
    
    #######################################
    @abstractmethod
    def __setitem__(self, index:int|Iterable[int]|slice|tuple[int|Iterable[int]|slice], value:float|np.ndarray[float]) -> None:
        """
        Set the interpolation values at a slice of the table through np.ndarray.__setitem__ but:
        - If int|Iterable[int]|slice is given, set the value at the index/indices in the flattened dataset.
        - If tuple[int|Iterable[int]|slice] is given, set the value at the index/indices in the nested dataset.
        """
    
    #######################################
    @abstractmethod
    def __eq__(self, value) -> bool:
        if not isinstance(value, self.__class__):
            raise NotImplementedError(f"Cannot compare {self.__class__.__name__} with object of type '{value.__class__.__name__}'.")
    
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
    
    def __len__(self) -> int:
        """
        Returns the number of data-points stored in the table.
        """
        return self.size
    
    #######################################
    def __add__(self, table:BaseTabulation) -> BaseTabulation:
        """
        Concatenate two tables. Alias for 'concat'.
        """
        return self.concat(table, inplace=False, fillValue=None, overwrite=False)
    
    def __iadd__(self, table:BaseTabulation) -> BaseTabulation:
        """
        Concatenate two tables in-place. Alias for 'concat'.
        """
        self.concat(table, inplace=True, fillValue=None, overwrite=False)
        return self

    #######################################
    @abstractmethod
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(size={self.size}, order={self.order}, ranges={self.ranges}, shape={self.shape}"

    @abstractmethod
    def __str__(self) -> str:
        string = f"{self.__class__.__name__} with {self.size} data-points:\n"
        string += f"Shape: {self.shape}\n"
        string += f"Order: {self.order}\n"
        string += f"Ranges:\n"
        for o in self.order:
            string += f"\t{o}: {self.ranges[o]}\n"
        return string