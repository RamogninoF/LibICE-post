#####################################################################
#                                 DOC                               #
#####################################################################

"""
Interface functions to easily load fields into `libICEpost` `TimeSeries` objects.

Content of the module:
    - `loadField` (function): basic interface function to load a field into a TimeSeries object
    - `load_file` (function): load a field from a file into a TimeSeries object
    - `load_array` (function): load a field from an array into a TimeSeries object
    - `load_uniform` (function): load a constant field into a TimeSeries object
    - `load_function` (function): load a field as a function of time into a TimeSeries object
    - `load_calculated` (function): load a field as a function of data already in the TimeSeries object
    - `LoadingMethod` (enum.EnumStr): enumeration of the loading methods for TimeSeries objects

@author: F. Ramognino       <federico.ramognino@polimi.it>
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from ._TimeSeries import TimeSeries
from libICEpost.src.base.Functions.typeChecking import checkType
from libICEpost.src.base import enum

from typing import Callable, Iterable, Literal
import os

#####################################################################
class LoadingMethod(enum.StrEnum):
    """
    Enumeration of the loading methods for TimeSeries objects.
    """
    # File
    file = "file"
    # Array
    array = "array"
    vector = "vector"
    # Uniform
    uniform = "uniform"
    const = "const"
    constant = "constant"
    # Function
    function = "function"
    func = "func"
    func_time = "func_time"
    # Calculated
    calc = "calc"
    calculated = "calculated"

######################################################################
#                               FUNCTIONS                            #
######################################################################
def load_file(ts: TimeSeries, field: str, fileName: str, root:str=None, verbose:bool=True, **kwargs) -> None:
    """
    Load a field from a file into a TimeSeries object.
    
    Args:
        ts (TimeSeries): TimeSeries object to load the field into.
        field (str): Name of the field to load.
        fileName (str): Name of the file to load the field from.
        root (str): Root directory for the file. If None, the file is loaded directly. Default is None.
        verbose (bool, optional): If True, print information about the loading process. Default is True.
        **kwargs: Additional keyword arguments to pass to the loading function.
        
    Returns:
        None
    """
    checkType(ts, TimeSeries, "ts")
    checkType(field, str, "field")
    checkType(fileName, str, "fileName")
    checkType(root, str, "root", allowNone=True)
    checkType(verbose, bool, "verbose")
    
    # Check if the field is already in the TimeSeries object
    if field in ts.columns and verbose:
        print(f"Field '{field}' already exists in the TimeSeries object. Overwriting...")
        
    # Load the field from the file
    if root is not None: fileName = os.path.join(root, fileName)
    if verbose:
        print(f"Loading field '{field}' from file '{fileName}'...")
    ts.loadFile(fileName=fileName, varName=field, verbose=verbose, **kwargs)

#######################################################################
def load_array(ts: TimeSeries, field: str, array: Iterable, verbose:bool=True, **kwargs) -> None:
    """
    Load a field from an array into a TimeSeries object.
    
    Args:
        ts (TimeSeries): TimeSeries object to load the field into.
        field (str): Name of the field to load.
        array (Iterable): Array to load the field
        verbose (bool, optional): If True, print information about the loading process. Default is True.
        **kwargs: Additional keyword arguments to pass to the loading function.
    
    Returns:
        None
    """
    checkType(ts, TimeSeries, "ts")
    checkType(field, str, "field")
    checkType(array, Iterable, "array")
    checkType(verbose, bool, "verbose")
    
    # Check if the field is already in the TimeSeries object
    if field in ts.columns and verbose:
        print(f"Field '{field}' already exists in the TimeSeries object. Overwriting...")
        
    # Load the field from the array
    if verbose:
        print(f"Loading field '{field}' from array...")
    ts.loadArray(array, varName=field, verbose=verbose, **kwargs)

######################################################################
def load_uniform(ts: TimeSeries, field: str, value: float, verbose:bool=True, **kwargs) -> None:
    """
    Load a constant field into a TimeSeries object.
    
    Args:
        ts (TimeSeries): TimeSeries object to load the field into.
        field (str): Name of the field to load.
        value (float): Value of the constant field.
        verbose (bool, optional): If True, print information about the loading process. Default is True.
        **kwargs: Additional keyword arguments to pass to the loading function.
        
    Returns:
        None
    """
    checkType(ts, TimeSeries, "ts")
    checkType(field, str, "field")
    checkType(value, float, "value")
    checkType(verbose, bool, "verbose")
    
    # Check if the field is already in the TimeSeries object
    if field in ts.columns and verbose:
        print(f"Field '{field}' already exists in the TimeSeries object. Overwriting...")
        
    # Load the field as a uniform value
    if verbose:
        print(f"Loading field '{field}' as a uniform value {value}...")
    
    if len(ts) == 0:
        raise ValueError("TimeSeries is empty. Cannot load uniform field.")
    
    time = ts[ts.timeName].to_numpy()
    ts.loadArray([(time[0], value), (time[-1], value)], varName=field, verbose=verbose, dataFormat="column", **kwargs)

######################################################################
def load_function(ts: TimeSeries, field: str, function: Callable[[float],float], verbose:bool=True, **kwargs) -> None:
    """
    Load a field as a function of time into a TimeSeries object.
    
    Args:
        ts (TimeSeries): TimeSeries object to load the field into.
        field (str): Name of the field to load.
        function (Callable[[float],float]): Function to load the field as a function of time.
        verbose (bool, optional): If True, print information about the loading process. Default is True.
        **kwargs: Additional keyword arguments to pass to the loading function.
        
    Returns:
        None
    """
    checkType(ts, TimeSeries, "ts")
    checkType(field, str, "field")
    checkType(function, Callable, "function")
    checkType(verbose, bool, "verbose")
    
    # Check if the field is already in the TimeSeries object
    if field in ts.columns and verbose:
        print(f"Field '{field}' already exists in the TimeSeries object. Overwriting...")
        
    # Load the field as a function of time
    if verbose:
        print(f"Loading field '{field}' as a function of time...")
    
    if len(ts) == 0:
        raise ValueError("TimeSeries is empty. Cannot load function field.")
    
    time = ts[ts.timeName].to_list()
    out = [function(t) for t in time]
    ts.loadArray([time, out], varName=field, verbose=verbose, dataFormat="row", **kwargs)

######################################################################
def load_calculated(ts: TimeSeries, field: str, function: Callable, verbose:bool=True, **kwargs) -> None:
    """
    Load a field as a function of data already in the TimeSeries object.
    
    Args:
        ts (TimeSeries): TimeSeries object to load the field into.
        field (str): Name of the field to load.
        function (Callable): Function to load the field as a function of data already in the TimeSeries object.
        verbose (bool, optional): If True, print information about the loading process. Default is True.
        **kwargs: Additional keyword arguments to pass to the loading function.
        
    Returns:
        None
    """
    checkType(ts, TimeSeries, "ts")
    checkType(field, str, "field")
    checkType(function, Callable, "function")
    checkType(verbose, bool, "verbose")
    
    # Check if the field is already in the TimeSeries object
    if field in ts.columns and verbose:
        print(f"Field '{field}' already exists in the TimeSeries object. Overwriting...")
        
    # Get the arguments of the function
    args = function.__code__.co_varnames[:function.__code__.co_argcount]
    
    # Load the field as a function of data already in the TimeSeries object
    if verbose:
        print(f"Loading field '{field}' as a function of {args}...")
    
    if len(ts) == 0:
        raise ValueError("TimeSeries is empty. Cannot load calculated field.")
    
    # Get the values of the arguments from the TimeSeries object
    for var in args:
        if var not in ts.columns:
            raise ValueError(f"Variable '{var}' not found in TimeSeries object. Available variables are: {ts.columns}")
    
    if len(args) == 1:
        data = [ts[args[0]].to_numpy()]
    elif len(args) > 1:
        data = [ts[var].to_numpy() for var in args]
    else:
        raise ValueError("Function must have at least one argument.")
    out = function(*data)
    
    time = ts[ts.timeName].to_list()
    ts.loadArray([time, out], varName=field, verbose=verbose, dataFormat="row", **kwargs)

######################################################################
#                               INTERFACE                            #
######################################################################
def loadField(ts: TimeSeries, field: str, method:Literal["file", "array", "uniform", "function", "calculated"],
              *, inplace:bool=True, verbose:bool=True, **kwargs) -> TimeSeries|None:
    """
    Load a field into a TimeSeries object.

    Args:
        ts (TimeSeries): TimeSeries object to load the field into.
        field (str): Name of the field to load. 
        method (str): Method to load the field. Can be one of the following::
            - `file`: load a field from a file.
            - `array`: load a field from an array. Aliases: `vector`
            - `uniform`: load a constant field given a value. Aliases: `const`, `constant`
            - `function`: load a field as a function of time. Aliases: `func`, `func_time`
            - `calculated`: load a field as a function of data already in the TimeSeries object. Aliases: `calc`
        inplace (bool, optional): If True, the field will be loaded into the TimeSeries object.
            If False, a new TimeSeries object will be created with the loaded field. Default is True.
        verbose (bool, optional): If True, print information about the loading process. Default is True.
        **kwargs: Additional keyword arguments to pass to the loading method.
        
    Returns:
        TimeSeries|None: The TimeSeries object with the loaded field if inplace is False, otherwise None.
    """
    # Type checking
    checkType(ts, TimeSeries, "ts")
    
    if not inplace:
        # Create a new TimeSeries object
        ts = ts.copy()
        loadField(ts, field, method, inplace=True, verbose=verbose, **kwargs)
        return ts
    
    # Type checking
    checkType(field, str, "field")
    checkType(method, str, "method")
    checkType(inplace, bool, "inplace")
    checkType(verbose, bool, "verbose")
    
    # Cast the method to the enum
    method_ = LoadingMethod(method).value
    
    # Run the appropriate loading method
    if method_ == LoadingMethod.file:
        load_file(ts, field, **kwargs, verbose=verbose)
    elif method_ in (LoadingMethod.array, LoadingMethod.vector):
        load_array(ts, field, **kwargs, verbose=verbose)
    elif method_ in (LoadingMethod.uniform, LoadingMethod.const, LoadingMethod.constant):
        load_uniform(ts, field, **kwargs, verbose=verbose)
    elif method_ in (LoadingMethod.function, LoadingMethod.func, LoadingMethod.func_time):
        load_function(ts, field, **kwargs, verbose=verbose)
    elif method_ in (LoadingMethod.calc, LoadingMethod.calculated):
        load_calculated(ts, field, **kwargs, verbose=verbose)
    else: # This should never happen if the enum is used correctly
        raise RuntimeError(f"Something went wrong...")