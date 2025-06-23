#####################################################################
#                                 DOC                               #
#####################################################################

"""
Data structure for time-series data. It wraps a pandas DataFrame class and adds
some useful I/O methods and defines interpolators of the varibles to easily access
data at generic instants.

Content of the module:
    `TimeSeries` (`class`): data structure for time-series data.
    `TimeSeriesWarning` (`class`): warning for TimeSeries class.
    
@author: F. Ramognino       <federico.ramognino@polimi.it>
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from __future__ import annotations
from typing import Self, Literal, Callable
import os

from libICEpost.src.base.Functions.typeChecking import checkType
from libICEpost.src.base.Utilities import Utilities
from libICEpost.src.base.Functions.runtimeWarning import helpOnFail

import pandas as pd
import numpy as np
import collections.abc
import warnings

#Auxiliary functions
from keyword import iskeyword
def is_valid_variable_name(name):
    return name.isidentifier() and not iskeyword(name)

class TimeSeriesWarning(Warning):
    """Warning for TimeSeries class."""
    pass

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Class used for storing and handling a generic tabulation:
class TimeSeries(Utilities):
    """
    Database for time-series data. Wraps a pandas DataFrame class and adds
    some useful I/O methods and defines interpolators of the varibles to
    easily access data at generic instants.
    """
    
    _interpolators:set[str]
    """The names of the variables that have an interpolator."""
    
    _data:pd.DataFrame
    """The DataFrame instance that stores the data."""
    
    _timeName:str
    """The name of the time column in the DataFrame."""
    
    #########################################################################
    #properties:
    @property
    def columns(self):
        """
        The columns in the DataFrame.

        Returns:
            Index[str]
        """
        return self._data.columns

    @columns.setter
    def columns(self, *args, **kwargs) -> None:
        self._data.columns(*args, **kwargs)

    ##############################
    @property
    def index(self):
        """
        The index list of the DataFrame.

        Returns:
            Index
        """
        return self._data.index

    ##############################
    #Auxiliary access methods
    @property
    def loc(self):
        """
        Access a group of rows and columns by label(s) or a boolean array.
        Calls 'loc' propertie of the DataFrame.
        """
        return self._data.loc
    
    ##############################
    @property
    def iloc(self):
        """
        Purely integer-location based indexing for selection by position.
        Calls 'iloc' propertie of the DataFrame.
        """
        return self._data.iloc

    ##############################
    @property
    def timeName(self):
        """
        The name of the time column in the DataFrame.

        Returns:
            str
        """
        return self._timeName

    #########################################################################
    #Constructor:
    def __init__(self, timeName:str="time"):
        """
        Create the table.
        """
        checkType(timeName, str, "timeName")
        
        self._data = pd.DataFrame(columns={timeName:[]})
        self._interpolators = set()
        self._timeName = timeName

    #########################################################################
    #Dunder methods:
    def __len__(self):
        return self._data.__len__()

    def __str__(self):
        return self._data.__str__()

    def __repr__(self):
        return self._data.__repr__()

    def __getitem__(self, *item) -> pd.Series|pd.DataFrame:
        return self._data.__getitem__(*item)

    def __setitem__(self, key, item) -> None:
        self._data.__setitem__(key, item)

    def __getattribute__(self, name: str) -> os.Any:
        #Check if the interpolator is missing and construct it
        if (name in super().__getattribute__("_data").columns):
            if not name in super().__getattribute__("_interpolators"):
                super(self.__class__, self).__getattribute__("_createInterpolator")(name)
            return super().__getattribute__(name)
        return super().__getattribute__(name)

    def __delitem__(self, item):
        return self._data.__delitem__(item)

    def __call__(self) -> pd.DataFrame:
        """
        Access the DataFrame instance that stores the data.
        Returns:
            pd.DataFrame: The DataFrame instance that stores the data.
        """
        return self._data
    
    #########################################################################
    #Methods:
    @helpOnFail
    def loadFile(
            self,
            fileName:str,
            varName:str , *,
            x_col:int=None,
            y_col:int=None,
            x_off:float=None,
            y_off:float=None,
            x_scale:float=None,
            y_scale:float=None,
            skip_rows:int=None,
            max_rows:int=None,
            comments:str='#',
            delimiter:str=None,
            interpolate:bool=True,
            default:float=float("nan"),
            verbose:bool=True,
            **kwargs) -> Self:
        """
        Load a file containing the time-series of a variable. If data were already 
        loaded, the CA range must be consistent (sub-arrays are also permitted; 
        excess data will be truncated).
        
        **NOTE**: 
            - use delimiter=',' to load CSV files. Automatically removes duplicate times.
            - Resolution order: first offset and then scale.
            
        Args:
            fileName (str): Source file
            varName (str): Name of variable in data structure
            x_col (int, optional): Column of x data (time). Defaults to 0. Aliases: `xCol`, `time_col`, `t_col`, `timeCol`, `tCol`, `CACol` (deprecated).
            y_col (int, optional): Column of y data. Defaults to 1. Aliases: `yCol`, `varCol` (deprecated).
            x_off (float, optional): Offset to sum to x range (time). Defaults to 0.0. Aliases: `xOff`, `time_off`, `t_off`, `timeOff`, `tOff`, `CAOff` (deprecated).
            y_off (float, optional): Offset to sum to y range. Defaults to 0.0. Aliases: `yOff`, `varOff` (deprecated).
            x_scale (float, optional): Scaling factor to apply to x range. Defaults to 1.0. Aliases: `xScale`, `time_scale`, `t_scale`, `timeScale`, `tScale`, `CAscale` (deprecated).
            y_scale (float, optional): Scaling factor to apply to y range. Defaults to 1.0. Aliases: `yScale`, `varScale` (deprecated).
            skip_rows (int, optional): Number of raws to skip at beginning of file. Defaults to 0. Aliases: `skipRows`, `skiprows`.
            max_rows (int, optional): Maximum number of raws to use. Defaults to None. Aliases: `maxRows`.
            comments (str, optional): Character to use to detect comment lines. Defaults to '#'.
            delimiter (str, optional): Delimiter for the columns (defaults to whitespace). Defaults to None.
            interpolate (bool, optional): Interpolate the data-set at existing time range (used to load non-consistent data). Defaults to True.
            default (float, optional): Default value to add in out-of-range values or if `interpolate` is `False`. Defaults to `float("nan")`.
            verbose (bool, optional): If need to print loading information. Defaults to True.
            
        Returns:
            Self: self.
        """
        #Check for equivalent keys
        equivalentKeys:dict[str,list[str]] = {
            "x_col":["x_col", "xCol", "time_col", "t_col", "timeCol", "tCol", "CACol"],
            "y_col":["y_col", "yCol", "varCol"],
            "x_off":["x_off", "xOff", "time_off", "t_off", "timeOff", "tOff", "CAOff"],
            "y_off":["y_off", "yOff", "varOff"],
            "x_scale":["x_scale", "xScale", "time_scale", "t_scale", "timeScale", "tScale", "CAscale"],
            "y_scale":["y_scale", "yScale", "varScale"],
            "skip_rows":["skip_rows", "skipRows", "skiprows"],
            "max_rows":["max_rows", "maxRows"],
        }
        deprecatedKeys:set[str] = {"CACol", "varCol", "CAOff", "varOff", "varScale", "CAscale"}
        
        fullkwargs = {**kwargs}
        if x_col is not None: fullkwargs["x_col"] = x_col
        if y_col is not None: fullkwargs["y_col"] = y_col
        if x_off is not None: fullkwargs["x_off"] = x_off
        if y_off is not None: fullkwargs["y_off"] = y_off
        if x_scale is not None: fullkwargs["x_scale"] = x_scale
        if y_scale is not None: fullkwargs["y_scale"] = y_scale
        if skip_rows is not None: fullkwargs["skip_rows"] = skip_rows
        if max_rows is not None: fullkwargs["max_rows"] = max_rows
        
        foundKeys = set(fullkwargs.keys()).intersection(sum(equivalentKeys.values(), start=[]))
        
        #Check for multiple entries that are equivalent
        keyMap:dict[str,list] = {v:[] for v in equivalentKeys.keys()}
        for key in foundKeys:
            for k in equivalentKeys:
                if key in equivalentKeys[k]:
                    keyMap[k].append(key)
        for key in keyMap:
            if len(keyMap[key]) > 1:
                raise ValueError(f"Key '{key}' found multiple times in kwargs: {keyMap[key]}")
        
        #Check for deprecated keys
        for key in keyMap:
            if len(keyMap[key]) == 0:
                continue
            if keyMap[key][0] in deprecatedKeys:
                warnings.warn(DeprecationWarning(f"Key '{keyMap[key][0]}' is deprecated. Use '{key}' instead."))
        
        #Set equivalent keys
        x_col = fullkwargs.pop(keyMap["x_col"][0]) if len(keyMap["x_col"]) > 0 else 0
        y_col = fullkwargs.pop(keyMap["y_col"][0]) if len(keyMap["y_col"]) > 0 else 1
        x_off = fullkwargs.pop(keyMap["x_off"][0]) if len(keyMap["x_off"]) > 0 else 0.0
        y_off = fullkwargs.pop(keyMap["y_off"][0]) if len(keyMap["y_off"]) > 0 else 0.0
        x_scale = fullkwargs.pop(keyMap["x_scale"][0]) if len(keyMap["x_scale"]) > 0 else 1.0
        y_scale = fullkwargs.pop(keyMap["y_scale"][0]) if len(keyMap["y_scale"]) > 0 else 1.0
        skip_rows = fullkwargs.pop(keyMap["skip_rows"][0]) if len(keyMap["skip_rows"]) > 0 else 0
        max_rows = fullkwargs.pop(keyMap["max_rows"][0]) if len(keyMap["max_rows"]) > 0 else None
        
        #Check for unknown keys
        unknownKeys = set(fullkwargs.keys()).difference(sum(equivalentKeys.values(), start=[]))
        if len(unknownKeys) > 0: raise ValueError(f"Unknown keyword arguments '{unknownKeys}'.")
        
        #Check arguments
        checkType(fileName , str   , "fileName")
        checkType(varName  , str   , "varName" )
        checkType(x_col    , int   , "x_col"   )
        checkType(y_col    , int   , "y_col"   )
        checkType(x_off    , float , "x_off"   )
        checkType(y_off    , float , "y_off"   )
        checkType(x_scale  , float , "x_scale" )
        checkType(y_scale  , float , "y_scale" )
        checkType(comments , str   , "comments")
        checkType(skip_rows , int   , "skip_rows")
        checkType(max_rows   , int , "max_rows", allowNone=True)
        checkType(interpolate, bool, "interpolate")
        checkType(default  , float , "default" )
        checkType(verbose  , bool  , "verbose" )

        data:np.ndarray = np.loadtxt\
            (
                fileName,
                comments=comments,
                usecols=(x_col, y_col),
                skiprows=skip_rows,
                max_rows=max_rows,
                delimiter=delimiter
            )

        if verbose:
            if x_off != 0.0:
                print(f"\tApplying offset {x_off} to time data")
            if y_off != 0.0:
                print(f"\tApplying offset {y_off} to variable data")
            if x_scale != 1.0:
                print(f"\tApplying scaling {x_scale} to time data")
            if y_scale != 1.0:
                print(f"\tApplying scaling {y_scale} to variable data")
        
        data[:,0] += x_off
        data[:,0] *= x_scale
        data[:,1] += y_off
        data[:,1] *= y_scale

        self.loadArray(data, varName, default=default, interpolate=interpolate, verbose=verbose)

        return self

    #######################################
    @helpOnFail
    def loadArray(
        self,
        data:collections.abc.Iterable,
        varName:str,
        *,
        verbose:bool=True,
        default:float=float("nan"),
        interpolate:bool=True,
        dataFormat:Literal["column", "row"]="column") -> Self:
        """
        Load an array into the table. Automatically removes duplicate times.

        Args:
            data (Iterable): Container of shape [N,2] (column) or [2,N] (row), depending \
                on 'dataFormat' value, with first column/row the CA range and second the variable \
                time-series to load.
            varName (str): Name of variable in data structure
            verbose (bool, optional): If need to print loading information. Defaults to True.
            default (float, optional): Default value for out-of-range elements. Defaults to float("nan").
            interpolate (bool, optional): Interpolate the data-set at existing time range (used to load \
                non-consistent data). Defaults to True.
            dataFormat (str, Literal[&quot;column&quot;, &quot;row&quot;], optional): Format of data: \
                'column' -> [N,2] \
                'row' -> [2,N]
        Returns:
            Self: self.

        Examples:
            Creating a 'TimeSeries' instance
            >>> ts = TimeSeries()

            Loading from list containing two lists for CA and variable (by row)
            >>> ts = TimeSeries(timeName="CA")
            >>> data = [[1, 2, 3, 4, 5], [11, 12, 13, 14, 15]]
            >>> ts.loadArray(data, "var1", dataFormat="row")
               CA  var1
            0   1    11
            1   2    12
            2   3    13
            3   4    14
            4   5    15

            Loading second variable from list of (CA,var) pairs (order by column) without interpolation
            >>> data = [(3, 3), (4, 3.5), (5, 2.4), (6, 5.2), (7, 3.14)]
            >>> ts.loadArray(data, "var2", dataFormat="column")
               CA  var1  var2
            0   1  11.0   NaN
            1   2  12.0   NaN
            2   3  13.0  3.00
            3   4  14.0  3.50
            4   5  15.0  2.40
            5   6   NaN  5.20
            6   7   NaN  3.14

            Extend the interval of var2 from a pandas.DataFrame with data by column,
            suppressing the warning for orverwriting.
            >>> from pandas import DataFrame as df
            >>> data = df({"CA":[8, 9, 10, 11], "var":[2, 1, 0, -1]})
            >>> ts.loadArray(data, "var2", dataFormat="column", verbose=False)
                CA  var1  var2
            0    1  11.0   NaN
            1    2  12.0   NaN
            2    3  13.0  3.00
            3    4  14.0  3.50
            4    5  15.0  2.40
            5    6   NaN  5.20
            6    7   NaN  3.14
            7    8   NaN  2.00
            8    9   NaN  1.00
            9   10   NaN  0.00
            10  11   NaN -1.00

            Load a variable var3 from numpy ndarray and interpolate
            >>> import numpy as np
            >>> data = np.array([[-5.5, 5.5],[2.3, 5.4]])
            >>> ts.loadArray(data, "var3", dataFormat="row", interpolate=True)
                  CA  var1  var2      var3
            0   -5.5   NaN   NaN  2.300000
            1    1.0  11.0   NaN  4.131818
            2    2.0  12.0   NaN  4.413636
            3    3.0  13.0  3.00  4.695455
            4    4.0  14.0  3.50  4.977273
            5    5.0  15.0  2.40  5.259091
            6    5.5   NaN  3.80  5.400000
            7    6.0   NaN  5.20       NaN
            8    7.0   NaN  3.14       NaN
            9    8.0   NaN  2.00       NaN
            10   9.0   NaN  1.00       NaN
            11  10.0   NaN  0.00       NaN
            12  11.0   NaN -1.00       NaN
        """
        checkType(varName  , str   , "varName" )
        checkType(data    , collections.abc.Iterable   , "data")
        checkType(verbose  , bool  , "verbose")
        checkType(default  , float  , "default")
        
        #Cast to pandas.DataFrame
        npData = np.array(data)
        if not npData.ndim == 2:
            raise ValueError(f"Array must be of shape (N,2) or (2,N) while {npData.shape} was found.")
        
        if (dataFormat == "column") and (npData.shape[1] != 2):
            raise ValueError(f"Array must be of shape (N,2) while dataFormat='column', while {npData.shape} was found.")
        elif (dataFormat == "row") and (npData.shape[0] != 2):
            raise ValueError(f"Array must be of shape (2,N) while dataFormat='row', while {npData.shape} was found.")
        elif (dataFormat == "row"):
            npData = npData.T
        elif (dataFormat != "column"):
            raise ValueError(f"Unknown dataFormat '{dataFormat}'. Avaliable formats are 'row' and 'column'.")

        df = pd.DataFrame(npData, columns=[self.timeName, varName])
        
        #Check types
        if not all([issubclass(t.type, (np.floating, np.integer, float, int)) for t in df.dtypes]):
            raise TypeError("Data must be numeric (float or int).")
        
        #Remove duplicates
        df.drop_duplicates(subset=self.timeName, keep="first", inplace=True)
        
        #Index with CA (useful for merging)
        reindexedData = self._data.set_index(self.timeName)
        df.set_index(self.timeName, inplace=True)

        #Check if data were already loaded
        firstTime = not (varName in self.columns)
        if (not firstTime) and verbose:
            warnings.warn(TimeSeriesWarning(f"Overwriting existing data for field '{varName}'"))

        #If data were not stored yet, just load this
        if len(reindexedData) < 1:
            newData = reindexedData.join(df, how="right")

        else:
            #Merge the time ranges
            tLeft = reindexedData.index
            tRight = df.index
            consistentTime = tRight.to_list() == tLeft.to_list()
            
            #Update based on time of self
            newData = reindexedData.join(df, how="outer", rsuffix="_new")
            
            #Merge data if overwriting
            if not firstTime:
                newData.update(pd.DataFrame(newData[varName + "_new"].rename(varName)))
                
                # Store the times where data where already present, we won't interpolate at those
                alreadyPresent = np.invert(newData[varName].isna())
                
                #Remove the new column
                newData.drop(varName + "_new", axis="columns", inplace=True)
                
            #Perform interpolation
            if (not consistentTime) and interpolate:
                time = newData.index
                
                #Interpolate original dataset at indexes of the new dataset not present 
                # in the old one
                t = tLeft.to_numpy()
                notMissing = time.isin(t)
                missing = np.invert(notMissing)
                if any(missing):
                    #Interpolate everything but the loaded variable:
                    for ii, var in enumerate(newData.columns):
                        if var == varName:
                            continue
                        newData.iloc[missing, ii] = np.interp(
                            time[missing], 
                            time[notMissing], 
                            newData.iloc[notMissing,ii].to_numpy(),
                            float("nan"), float("nan"))

                #Interpolate loaded dataset if not first time
                t = tRight.to_numpy()
                notMissing = time.isin(t)
                missing = np.invert(notMissing)
                
                #If some data were already present, we don't interpolate there
                if not firstTime:
                    missing = missing & np.invert(alreadyPresent)
                    
                varID = newData.columns.get_loc(varName)
                if any(missing):
                    newData.iloc[missing, varID] = np.interp(
                        time[missing],
                        time[notMissing],
                        newData.iloc[notMissing,varID].to_numpy(),
                        default, default)

        #Return to normal indexing
        newData.reset_index(inplace=True)
        self._data = newData
        
        return self

    #######################################
    def _createInterpolator(self, varName:str):
        """
        Create the interpolator for a variable and defines the method varName(t) which 
        returns the interpolated value of variable 'varName' at instant 't' from the 
        data in self._data
        
        Args:
            varName (str): Name of the variable to interpolate.
        """
        #Check if varName is an allowed variable name, as so that it can be used to access by . operator
        if not is_valid_variable_name(varName):
            raise ValueError(f"Field name '{varName}' is not a valid variable name.")

        #Check if attribute already exists, to prevent overloading existing attribustes.
        if varName in _reservedMethds:
            raise ValueError(f"Name '{varName}' is reserved.")
        
        if not varName in self._data.columns:
            raise ValueError(f"Variable '{varName}' not found. Available fields are:\n\t" + "\n\t".join(self._data.columns))

        def interpolator(self:Self, t:float|collections.abc.Iterable, /) -> float|np.ndarray:
            """
            Linear interpolation at t.
            
            Args:"
                t (float | collections.abc.Iterable): time at which iterpolating data.
                
            Returns:"
                float|np.ndarray: Interpolated data at t.
            """
            return np.interp(t, self._data[self.timeName], self._data[varName], float("nan"), float("nan"))
        
        #Add to the set of interpolators
        self._interpolators.add(varName)
        setattr(self.__class__,varName,interpolator)

    #######################################
    def write(self, fileName:str, *, overwrite:bool=False, sep:str=' ', header:bool=True, na_rep:str='nan', decimal:str='.', **kwargs) -> None:
        """
        Write data to a file.
        
        Args:
            fileName (str): Name of the file where to write the data structure.
            overwrite (bool, optional): Allow to overwrite file if existing. Defaults to `False`.
            sep (str, optional): Separator. Defaults to `' '`.
            header (bool, optional): Write header. Defaults to `True`.
            na_rep (str, optional): String representation of `NaN` values. Defaults to `'nan'`.
            decimal (str, optional): Decimal separator. Defaults to `'.'`.
            **kwargs: Additional arguments to pass to `pandas.DataFrame.to_csv` 
        """
        checkType(fileName, str, "fileName")
        checkType(overwrite, bool, "overwrite")
        checkType(sep, str, "sep")
        checkType(header, bool, "header")

        if os.path.exists(fileName) and not overwrite:
            raise FileExistsError(f"File {fileName} exists. Use overwrite=True keyword to force overwriting data.")

        self._data.to_csv\
            (
                path_or_buf=fileName,
                sep=sep,
                na_rep=na_rep,
                header=header,
                index=False,
                mode='w',
                decimal=decimal,
                **kwargs
            )

    #########################################################################
    #Auxiliary plotting methods
    def plot(self, *args, **kwargs):
        """
        Plotting the data stored in the table. Alias to `pandas.DataFrame.plot` method 
        of the internal DataFrame instance.

        Returns:
            matplotlib.Axes|numpy.ndarray[matplotlib.Axes]: The axes of the plot(s).
        """
        return self().plot(*args, **kwargs)
    
#########################################################################
#Store the reserved methods of the class to prevent overloading
_reservedMethds = dir(TimeSeries)