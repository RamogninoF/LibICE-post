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
import os

from libICEpost.src.base.Utilities import Utilities

import pandas as pd
import numpy as np
import collections.abc

#Auxiliary functions
from keyword import iskeyword
def is_valid_variable_name(name):
    return name.isidentifier() and not iskeyword(name)

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
        
    
    #########################################################################
    #Constructor:
    def __init__(self):
        """
        Create the table.
        """
        self.data = pd.DataFrame()
    
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
            ) -> EngineData:
        """
        [Variable] | [Type] | [Default] | [Description]
        -----------|--------|-----------|---------------------------------------------
        fileName   | str    | -         | Source file
        varName    | str    | -         | Name of variable in data structure
        CACol      | int    | 0         | Column of CA list
        varCol     | int    | 1         | Column of data list
        CAOff      | float  | 0.0       | Offset to sum to CA range
        varOff     | float  | 0.0       | Offset to sum to variable range
        CAscale    | float  | 1.0       | Scaling factor to apply to CA range
        varScale   | float  | 1.0       | Scaling factor to apply to variable range
        comments   | str    | '#'       | Character to use to detect comment lines
        delimiter  | str    | None      | Delimiter for the columns (defaults to whitespace)
        skipRows   | int    | 0         | Number of raws to skip at beginning of file
        maxRows    | int    | None      | Maximum number of raws to use
        interpolate| bool   | False     | Interpolate the data-set at existing CA range (used to load non-consistent data)
        verbose    | bool   | True      | Print info/warnings
        default    | float  | nan       | Default value to add in out-of-range values
        
        Load a file containing the time-series of a variable. If 
        data were already loaded, the CA range must be consistent 
        (sub-arrays are also permitted; excess data will be truncated).
        Note: use delimiter=',' to load CSV files. Automatically removes 
        duplicate times.
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
    def loadArray(
        self,
        data:collections.abc.Iterable,
        varName:str,
        verbose:bool=True,
        default:float=float("nan"),
        interpolate:bool=False) -> EngineData:
        """
        Load an ndarray of shape (N,2) with first column the CA range and 
        second the variable time-series to load. Automatically removes duplicate times.
            
        Args:
            data (collections.abc.Iterable): Container of shape (N,2) with first 
                column the CA range and second the variable time-series to load.
            varName (str): Name of variable in data structure
            verbose (bool, optional): If need to print loading information. 
                Defaults to True.
            default (float, optional): Default value for out-of-range elements. 
                Defaults to float("nan").
            interpolate (bool, optional): Interpolate the data-set at existing CA 
                range (used to load non-consistent data). Defaults to False.

        Returns:
            EngineData: self
        """
        try:
            self.checkType(varName  , str   , "varName" )
            self.checkType(data    , collections.abc.Iterable   , "data")
            self.checkType(verbose  , bool  , "verbose")
            self.checkType(default  , float  , "default")
            
            #Cast to numpy array
            data:np.ndarray = self.np.array(data)
            
            #Check for type
            if not ((data.dtype == float) or (data.dtype == int)):
                raise TypeError("Data must be numeric (float or int).")
            
            if not len(data.shape) == 2:
                raise ValueError(f"Data must be with shape (N,2), {data.shape} found.")
            else:
                if not data.shape[1] == 2:
                    raise ValueError(f"Data must be with shape (N,2), {data.shape} found.")
            
            #Check if data are already present
            firstTime = False
            if not varName in self.data:
                self.data[varName] = default
                firstTime = True
            else:
                if verbose:
                    self.runtimeWarning(f"Overwriting existing data for field '{varName}'", stack=False)
            
            #Remove duplicate CAs:
            _, idx = np.unique(data[:,0], return_index=True)
            data = data[idx,:]
            
            #Remove nan:
            if np.isnan(data[:,0]).any():
                data = data[np.array([not np.isnan(v) for v in data[:,0]])]
            if np.isnan(data[:,1]).any():
                data = data[np.array([not np.isnan(v) for v in data[:,1]])]
            
            #If data were not stored yet, just load this
            if len(self.data) == 0:
                #Cannot use interpolate here
                if interpolate:
                    raise ValueError("Cannot load first with 'interpolate' method")
                
                self.data["CA"] = data[:,0]
                self.data[varName] = data[:,1]
                
            elif interpolate:
                #Interpolate data at CA range
                CA = self.data["CA"]
                var  = np.interp(CA, data[:,0], data[:,1])
                self.data[varName] = var
                
            else:
                CA = data[:,0]
                var = data[:,1]
                
                #NOTE: can only extend range on right (higher CA)
                if CA[0] < self["CA"][0]:
                    raise ValueError("CA not consistent: can only extend range to the right (higher CA)")
                
                #Check indicies of already present data:
                index = self.data.index[[ca in CA for ca in self["CA"]]]
                
                #Overwritten data must be contiguous
                if not (len(index) == (index[-1] - index[0] + 1)):
                    #Missing data in between
                    raise ValueError("CA not consistent: overwrited data must be contiguous (0)")
                elif not (index.to_numpy() == np.array(range(index[0], index[-1]+1))).all():
                    # Already loaded data to overwrite are not contiguous
                    raise ValueError("CA not consistent: overwrited data must be contiguous (1)")
                elif (index[-1] < (len(self) - 1)) and (CA[-1] > self["CA"][index[-1]]):
                    #Last index not at end, but there are other data left
                    raise ValueError("CA not consistent: overwrited data must be contiguous (2)")
                
                #Identify extended elements:
                if CA[-1] > self["CA"][len(self.data)-1]:
                    numNewCA = len(CA) - len(index)
                    newIndex = list(range(len(self.data),len(self.data)+numNewCA))
                    index = index.to_list() + newIndex
                    
                    #Add new indicies:
                    newData = pd.DataFrame(columns=self.data.columns, index=range(len(newIndex)))
                    self.data = pd.concat([self.data, newData], ignore_index=True)
                
                self.data["CA"][index] = CA
                self.data[varName][index] = var
                                
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