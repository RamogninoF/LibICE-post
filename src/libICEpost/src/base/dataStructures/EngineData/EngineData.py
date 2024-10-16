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
from typing import Self, Literal
import os

from libICEpost.src.base.Utilities import Utilities

import pandas as pd
import numpy as np
import collections.abc

#Auxiliary functions
from keyword import iskeyword
def is_valid_variable_name(name):
    return name.isidentifier() and not iskeyword(name)

from functools import wraps
from time import time

def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print('func:%r took: %2.4f sec' % \
          (f.__name__, te-ts))
        return result
    return wrap

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Class used for storing and handling a generic tabulation:
class EngineData(Utilities):
    """
    Database for engine data. Wraps a pandas DataFrame class and adds
    some useful I/O methods and defines interpolators of the varibles to
    easily access data at generic instants.
    """
    #########################################################################
    #properties:
    @property
    def columns(self) -> list[str]:
        return self.data.columns

    @columns.setter
    def columns(self, *args, **kwargs) -> None:
        self.data.columns(*args, **kwargs)

    @property
    def loc(self):
        return self.data.loc

    @loc.setter
    def loc(self, *args):
        return self.data.loc[*args]
    @property
    def iloc(self):
        return self.data.iloc

    @iloc.setter
    def iloc(self, *args):
        return self.data.iloc[*args]

    #########################################################################
    #Constructor:
    def __init__(self):
        """
        Create the table.
        """
        self.data = pd.DataFrame(columns=["CA"])

    #########################################################################
    #Dunder methods:
    def __len__(self):
        return len(self.data)

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return repr(self.data)

    def __getitem__(self, item):
        return self.data.__getitem__(item)

    def __setitem__(self, key, item):
        new = False
        if not key in self.columns:
            new = True

        self.data.__setitem__(key, item)

        #Create interpolator if not present
        if new:
            self.createInterpolator(key)

    def __delitem__(self, item):
        return self.data.__delitem__(item)

    #########################################################################
    #Methods:
    def loadFile(
            self,
            fileName:str,
            varName:str, / , *,
            CACol:int=0,
            varCol:int=1,
            CAOff:float=0.0,
            varOff:float=0.0,
            CAscale:float=1.0,
            varScale:float=1.0,
            skipRows:int=0,
            maxRows:int=None,
            interpolate:bool=False,
            comments:str='#',
            verbose:bool=True,
            delimiter:str=None,
            default:float=float("nan")
            ) -> Self:
        """
        Load a file containing the time-series of a variable. If
        data were already loaded, the CA range must be consistent
        (sub-arrays are also permitted; excess data will be truncated).
        Note: use delimiter=',' to load CSV files. Automatically removes
        duplicate times.

        Args:
            | Variable  |  Type  |  Default  |  Description                                                                          |
            |*---------*|*------*|*---------*|*-------------------------------------------------------------------------------------*|
            |fileName   | str    | -         | Source file                                                                           |
            |varName    | str    | -         | Name of variable in data structure                                                    |
            |CACol      | int    | 0         | Column of CA list                                                                     |
            |varCol     | int    | 1         | Column of data list                                                                   |
            |CAOff      | float  | 0.0       | Offset to sum to CA range                                                             |
            |varOff     | float  | 0.0       | Offset to sum to variable range                                                       |
            |CAscale    | float  | 1.0       | Scaling factor to apply to CA range                                                   |
            |varScale   | float  | 1.0       | Scaling factor to apply to variable range                                             |
            |comments   | str    | '#'       | Character to use to detect comment lines                                              |
            |delimiter  | str    | None      | Delimiter for the columns (defaults to whitespace)                                    |
            |skipRows   | int    | 0         | Number of raws to skip at beginning of file                                           |
            |maxRows    | int    | None      | Maximum number of raws to use                                                         |
            |interpolate| bool   | False     | Interpolate the data-set at existing CA range (used to load non-consistent data)      |
            |verbose    | bool   | True      | Print info/warnings                                                                   |
            |default    | float  | nan       | Default value to add in out-of-range values                                           |

        Returns:
            Self: self.
        """
        if verbose:
            print(f"{self.__class__.__name__}: Loading... '{fileName}' -> '{varName}'")

        try:
            self.checkType(fileName , str   , "fileName")
            self.checkType(varName  , str   , "varName" )
            self.checkType(CACol    , int   , "CACol"   )
            self.checkType(varCol   , int   , "varCol"  )
            self.checkType(CAOff    , float , "CAOff"   )
            self.checkType(varOff   , float , "varOff"  )
            self.checkType(CAscale  , float , "CAscale" )
            self.checkType(varScale , float , "varScale")
            self.checkType(comments , str   , "comments")
            self.checkType(skipRows , int   , "skipRows")
            self.checkType(verbose  , bool  , "verbose")
            if not maxRows is None:
                self.checkType(maxRows   , int , "maxRows")

            data:np.ndarray = np.loadtxt\
                (
                    fileName,
                    comments=comments,
                    usecols=(CACol, varCol),
                    skiprows=skipRows,
                    max_rows=maxRows,
                    delimiter=delimiter
                )

            data[:,0] *= CAscale
            data[:,0] += CAOff
            data[:,1] *= varScale
            data[:,1] += varOff

            self.loadArray(data, varName, verbose, default, interpolate)

        except BaseException as err:
            self.fatalErrorInClass(self.loadFile, f"Failed loading field '{varName}' from file '{fileName}'", err)

        return self

    #######################################
    @timing
    def loadArray(
        self,
        data:collections.abc.Iterable,
        varName:str,
        verbose:bool=True,
        default:float=float("nan"),
        interpolate:bool=False,
        dataFormat:Literal["column", "row"]="column") -> Self:
        """
        Load an array into the table. Automatically removes duplicate times.

        Args:
            data (collections.abc.Iterable): Container of shape [N,2] (column) or [2,N] (row), depending
                on 'dataFormat' value, with first column/row the CA range and second the variable
                time-series to load.
            varName (str): Name of variable in data structure
            verbose (bool, optional): If need to print loading information. Defaults to True.
            default (float, optional): Default value for out-of-range elements. Defaults
                to float("nan").
            interpolate (bool, optional): Interpolate the data-set at existing CA
                range (used to load non-consistent data). Defaults to False.
            dataFormat (str, Literal[&quot;column&quot;, &quot;row&quot;], optional): Format of data:
                column -> [N,2]
                row -> [2,N]
        Returns:
            Self: self.

        Examples:

            Creating a 'EngineData' instance
            >>> ed = EngineData()

            Loading from list containing two lists for CA and variable (by row)
            >>> ed = EngineData()
            >>> data = [[1, 2, 3, 4, 5], [11, 12, 13, 14, 15]]
            >>> ed.loadArray(data, "var1", dataFormat="row")
               CA  var1
            0   1    11
            1   2    12
            2   3    13
            3   4    14
            4   5    15

            Loading second variable from list of (CA,var) pairs (order by column) without interpolation
            >>> data = [(3, 3), (4, 3.5), (5, 2.4), (6, 5.2), (7, 3.14)]
            >>> ed.loadArray(data, "var2", dataFormat="column")
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
            >>> ed.loadArray(data, "var2", dataFormat="column", verbose=False)
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
            >>> ed.loadArray(data, "var3", dataFormat="row", interpolate=True)
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
        try:
            self.checkType(varName  , str   , "varName" )
            self.checkType(data    , collections.abc.Iterable   , "data")
            self.checkType(verbose  , bool  , "verbose")
            self.checkType(default  , float  , "default")

            #Cast to pandas.DataFrame
            df:pd.DataFrame = pd.DataFrame(data=data)
            if (dataFormat == "column") and (len(df.columns) != 2):
                raise ValueError(f"Array must be of shape (N,2) while dataFormat='column', while ({len(df.columns)},{len(df)}) was found.")
            elif (dataFormat == "row") and (len(df) != 2):
                raise ValueError(f"Array must be of shape (2,N) while dataFormat='row', while ({len(df.columns)},{len(df)}) was found.")
            elif (dataFormat == "row"):
                df = df.transpose()
            elif (dataFormat != "column"):
                raise ValueError(f"Unknown dataFormat '{dataFormat}'. Avaliable formats are 'row' and 'column'.")

            #Set column names
            df.columns = ["CA", varName]

            #Remove duplicates
            df.drop_duplicates(subset="CA", keep="first", inplace=True)

            #Index with CA (useful for merging)
            self.data.set_index("CA", inplace=True)
            df.set_index("CA", inplace=True)

            #Check types
            if any([t not in [float, int] for t in df.dtypes]):
                raise TypeError("Data must be numeric (float or int).")

            #Check if data were already loaded
            firstTime = not (varName in self.columns)
            if (not firstTime) and verbose:
                self.runtimeWarning(f"Overwriting existing data for field '{varName}'", stack=False)

            #If data were not stored yet, just load this
            if len(self.data) < 1:
                #Cannot use interpolate here
                if interpolate:
                    raise ValueError("Cannot load first with 'interpolate' method")

                #Update based on CA of right
                self.data = self.data.join(df, how="right")

            else:
                #Check if index are not consistent, to perform interpolation later
                consistentCA = False if (len(self.data.index) != len(df.index)) else all(self.data.index == df.index)
                if (not consistentCA) and interpolate:
                    CAold = self.data.index

                #Update based on CA of self
                self.data = self.data.join(df, how="outer", rsuffix="_new")

                #Merge data if overwriting
                if not firstTime:
                    self.data.update(pd.DataFrame(self.data[varName + "_new"].rename(varName)))
                    self.data.drop(varName + "_new", axis="columns", inplace=True)

                #Perform interpolation
                if (not consistentCA) and interpolate:
                    #Interpolate original dataset
                    missingCA = self.data.index[pd.DataFrame(self.data.index).apply((lambda x:not CAold.__contains__(x),))["CA"]["<lambda>"]]
                    if len(missingCA > 0):
                        #Interpolate everything but the loaded variable:
                        for var in [v for v in self.columns if not v == varName]:
                            self[var].loc[missingCA] = self.np.interp(missingCA, CAold, self.data.loc[CAold,var], float("nan"), float("nan"))

                    #Interpolate loaded dataset (needed if new variable):
                    if firstTime:
                        missingCA = self.data.index[pd.DataFrame(self.data.index).apply((lambda x:not df.index.__contains__(x),))["CA"]["<lambda>"]]
                        if len(missingCA > 0):
                            self[varName].loc[missingCA] = self.np.interp(missingCA, df.index, df[varName], float("nan"), float("nan"))

                #Return to normal indexing
                self.data.reset_index(inplace=True)

            #If first time this entry is set, create the interpolator:
            if firstTime:
                self.createInterpolator(varName)

        except BaseException as err:
            self.fatalErrorInClass(self.loadArray, f"Failed loading array", err)

        return self

    #######################################
    def createInterpolator(self, varName:str):
        """
        varName:    str

        Create the interpolator for a variable and defines the method varName(CA) which returns the interpolated value of variable 'varName' at instant 'CA' from the data in self.data
        """
        try:
            #Check if varName is an allowed variable name, as so that it can be used to access by . operator
            if not is_valid_variable_name(varName):
                raise ValueError(f"Field name '{varName}' is not a valid variable name.")

            #Check if attribute already exists, to prevent overloading existing attribustes.
            if varName in _reservedMethds:
                raise ValueError(f"Name '{varName}' is reserved.")

            if not varName in self.data.columns:
                raise ValueError(f"Variable '{varName}' not found. Available fields are:" + "\t" + "\n\t".join(self.data.columns))

            def interpolator(self, CA:float|collections.abc.Iterable) -> float|collections.abc.Iterable:
                try:
                    self.checkTypes(CA, (float,collections.abc.Iterable), "CA")
                    return self.np.interp(CA, self.data["CA"], self.data[varName], float("nan"), float("nan"))
                except BaseException as err:
                    self.fatalErrorInClass(getattr(self,varName), "Failed interpolation", err)

            interpolator.__doc__  = f"Linear interpolation of {varName} at CA."
            interpolator.__doc__ += f"\n\Args:"
            interpolator.__doc__ += f"\n\t\tCA (float | collections.abc.Iterable): CA at which iterpolating data."
            interpolator.__doc__ += f"\n\tReturns:"
            interpolator.__doc__ += f"\n\t\tCA at which iterpolating data."

            setattr(self.__class__, varName, interpolator)

        except BaseException as err:
            self.fatalErrorInClass(self.createInterpolator, f"Failed creating interpolator for variable '{varName}'", err)

    #######################################
    def write(self, fileName:str, overwrite:bool=False, sep:str=' '):
        """
        fileName:   str
            Name of the file where to write the data structure
        overwrite:  bool (False)
            Allow to overwrite file if existing
        sep:        str ('')
            Separator

        Write data to a file
        """
        try:
            self.checkType(fileName, str, "fileName")
            self.checkType(overwrite, bool, "overwrite")

            if os.path.exists(fileName) and not overwrite:
                self.fatalErrorInClass(self.write, "File {fileName} exists. Use overwrite=True keyword to force overwriting data.")

            self.data.to_csv\
                (
                    path_or_buf=fileName,
                    sep=sep,
                    na_rep='nan',
                    columns=None,
                    header=True,
                    index=False,
                    mode='w',
                    decimal='.'
                )

        except BaseException as err:
            self.fatalErrorInClass(self.write, f"Failed writing data to file '{fileName}'", err)

#Store copy of default EngineData class. This is used to identify reserved methods for createInterpolator
_reservedMethds = dir(EngineData)