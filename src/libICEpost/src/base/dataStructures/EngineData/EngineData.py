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
    #Data:
    
    #########################################################################
    #Constructor:
    def __init__(self):
        """
        Create the table.
        """
        self.columns = ["CA"]
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
        return self.data.__setitem__(key, item)
    
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
            comments:str='#', 
            verbose:bool=True, 
            delimiter:str=None
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
        verbose    | bool   | True      | Print info/warnings
        
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
            
            self.loadArray(data, varName, verbose)
            
        except BaseException as err:
            self.fatalErrorInClass(self.loadFile, f"Failed loading field '{varName}' from file '{fileName}'", err)
        
        return self
    
    #######################################
    def loadArray(self, data:collections.abc.Iterable, varName:str, verbose=True) -> EngineData:
        """
        data:       numpy.ndarray<float>, list<list<float>>
            Container of shape (N,2) with first column the CA range and 
            second the variable time-series to load.
        varName:    str
            Name of variable in data structure
            
        Load an ndarray of shape (N,2) with first column the CA range and 
        second the variable time-series to load. Automatically removes duplicate times.
        """
        try:
            self.checkType(varName  , str   , "varName" )
            self.checkTypes(data    , [list, self.np.ndarray]   , "data"   )
            self.checkType(verbose  , bool  , "verbose")
            
            if isinstance(data, list):
                data = self.np.array(data)
            
            if not ((data.dtype == float) or (data.dtype == int)):
                raise TypeError("Data must be numeric (float or int).")
            
            if not len(data.shape) == 2:
                raise ValueError(f"Data must be with shape (N,2), {data.shape} found.")
            else:
                if not data.shape[1] == 2:
                    raise ValueError(f"Data must be with shape (N,2), {data.shape} found.")
            
            if not varName in self.data:
                self.data.insert(len(self.data.columns), varName, [float("nan")]*len(self.data))
            else:
                if verbose:
                    self.runtimeWarning(f"Overwriting existing data for field '{varName}'", stack=False)
            
            #Remove duplicate CAs:
            _, idx = np.unique(data[:,0], return_index=True)
            data = data[idx,:]
            
            if not (len(self.data) > 0):
                self.data["CA"] = data[:,0]
                self.data[varName] = data[:,1]
            
            else:
                CA = data[:,0]
                var = data[:,1]
                
                ID_MIN = 0
                ID_MIN_CA = 0
                ID_MAX = len(self.data)+1
                ID_MAX_CA = len(CA)+1
                
                #Checking for sublists
                #Match minimum CA
                try:
                    ID_MIN = self.np.array(self.data["CA"] == CA[0]).tolist().index(True)
                except:
                    pass
                
                try:
                    ID_MIN_CA = self.np.array(CA == self.data["CA"][0]).tolist().index(True)
                except:
                    pass
                    
                #Match maximum CA
                try:
                    ID_MAX = self.np.array(self.data["CA"] == CA[-1]).tolist().index(True) + 1
                except:
                    pass
                
                try:
                    ID_MAX_CA = self.np.array(CA == self.data["CA"][-1]).tolist().index(True) + 1
                except:
                    pass
                
                #Check sublist
                if (self.data["CA"][ID_MIN:ID_MAX] != CA[ID_MIN_CA:ID_MAX_CA]).any():
                    raise ValueError("CA range in file not consistent with the one alredy loaded in data-structure")
                
                self.data[varName][ID_MIN:ID_MAX] = var[ID_MIN_CA:ID_MAX_CA]
                
            if not varName in self.columns:
                self.createInterpolator(varName)
                self.columns.append(varName)
            
            # Set CA as first column
            #TODO
            
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
            #Check if attribute already exists, to prevent overloading existing attribustes.
            if hasattr(self, varName):
                raise ValueError(f"Name '{varName}' is either reserved or the interpolation method was already created for this variable")
            
            if not varName in self.data.columns:
                raise ValueError(f"Variable '{varName}' not found. Available fields are:" + "\t" + "\n\t".join(self.data.columns))
            
            def interpolator(CA):
                try:
                    self.checkType(CA, float, "CA")
                    return self.np.interp(CA, self.data["CA"], self.data[varName], float("nan"), float("nan"))
                except BaseException as err:
                    self.fatalErrorInClass(self.varName, "Failed interpolation", err)
            
            setattr(self, varName, interpolator)
        
        except BaseException as err:
            self.fatalErrorInClass(self.createInterpolator, "Failed creating interpolator for variable '{varName}'", err)
    
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
