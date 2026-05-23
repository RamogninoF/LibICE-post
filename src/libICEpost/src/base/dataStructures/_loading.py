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
    - `load_stitched` (function): stitch multiple fields together into a TimeSeries object
    - `load_cumulative` (function): load a field as a cumulative integral of another field in the TimeSeries object
    - `LoadingMethod` (enum.EnumStr): enumeration of the loading methods for TimeSeries objects

@author: F. Ramognino       <federico.ramognino@polimi.it>
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from ._TimeSeries import TimeSeries
from libICEpost.src.base.Functions.typeChecking import checkType, checkArray
from libICEpost.src.base import enum

from scipy import integrate
from typing import Callable, Iterable, Literal
import os
import re
import inspect
import math
from wcmatch.glob import glob as _wc_glob, EXTGLOB, GLOBSTAR
import numpy as np
import warnings

class FieldDependencyError(ValueError, RuntimeError):
    """
    Exception raised when a field is dependent on another field that is not loaded yet.
    """

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
    # Stitching multiple fields together
    stitch = "stitch"
    # Cumulative integral of a field
    cumulative = "cumulative"
    integrate = "integrate"
    # Load and merge from multiple files
    files = "files"
    # Conditional element-wise merge of two fields/constants
    conditional = "conditional"
    cond        = "cond"

######################################################################
class ConditionalOperator(enum.StrEnum):
    """
    Enumeration of comparison operators for the conditional loading method.
    Each operator defines a condition F3 <op> F4 that selects between F1 (true)
    and F2 (false) at each time step.
    """
    gt    = ">"
    gte   = ">="
    lt    = "<"
    lte   = "<="
    eq    = "=="
    ne    = "!="
    isnan = "isnan"   # unary — checks np.isnan(F3); F4 is ignored

# Registry: ConditionalOperator → callable(v3, v4, **op_kwargs) → bool ndarray
# Unary operators receive v4=None and must ignore it.
_CONDITIONAL_OPERATORS: dict = {
    ConditionalOperator.gt:    lambda v3, v4, **kw: v3 > v4,
    ConditionalOperator.gte:   lambda v3, v4, **kw: v3 >= v4,
    ConditionalOperator.lt:    lambda v3, v4, **kw: v3 < v4,
    ConditionalOperator.lte:   lambda v3, v4, **kw: v3 <= v4,
    ConditionalOperator.eq:    lambda v3, v4, **kw: np.isclose(
                                   v3, v4,
                                   rtol=kw.get("rel_tol", 1e-6),
                                   atol=kw.get("abs_tol", 1e-12)),
    ConditionalOperator.ne:    lambda v3, v4, **kw: ~np.isclose(
                                   v3, v4,
                                   rtol=kw.get("rel_tol", 1e-6),
                                   atol=kw.get("abs_tol", 1e-12)),
    ConditionalOperator.isnan: lambda v3, v4, **kw: np.isnan(v3),
}

# Operators that do not consume f4
_UNARY_CONDITIONAL_OPERATORS: frozenset = frozenset({ConditionalOperator.isnan})

######################################################################
#                               FUNCTIONS                            #
######################################################################
def load_file(ts: TimeSeries, field: str, fileName: str, root:str|None=None, verbose:bool=True, **kwargs) -> None:
    """
    Load a field from a file into a TimeSeries object.
    
    Args:
        ts (TimeSeries): TimeSeries object to load the field into.
        field (str): Name of the field to load.
        fileName (str): Name of the file to load the field from.
        root (str, optional): Root directory for the file. If None, the file is loaded directly. Default is None.
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
        raise FieldDependencyError("TimeSeries is empty. Cannot load uniform field.")
    
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
        raise FieldDependencyError("TimeSeries is empty. Cannot load function field.")
    
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
        
    # Get the positional arguments via inspect to handle non-lambda callables
    # and avoid __code__ brittleness (breaks for builtins, C extensions, keyword-only args).
    try:
        sig = inspect.signature(function)
    except (ValueError, TypeError):
        raise TypeError(f"Cannot introspect signature of {function!r}. Use a plain Python function or lambda.")
    args = tuple(
        name for name, p in sig.parameters.items()
        if p.kind in (inspect.Parameter.POSITIONAL_ONLY,
                      inspect.Parameter.POSITIONAL_OR_KEYWORD)
    )
    
    # Load the field as a function of data already in the TimeSeries object
    if verbose:
        print(f"Loading field '{field}' as a function of {args}...")
    
    if len(ts) == 0:
        raise FieldDependencyError("TimeSeries is empty. Cannot load calculated field.")
    
    # Get the values of the arguments from the TimeSeries object
    for var in args:
        if var not in ts.columns:
            raise FieldDependencyError(f"Variable '{var}' not found in TimeSeries object. Available variables are: {ts.columns}")
    
    if len(args) == 1:
        data = [ts[args[0]].to_numpy()]
    elif len(args) > 1:
        data = [ts[var].to_numpy() for var in args]
    else:
        raise ValueError("Function must have at least one argument.")
    out = function(*data)
    
    time = ts[ts.timeName].to_list()
    ts.loadArray([time, out], varName=field, verbose=verbose, dataFormat="row", **kwargs)

#######################################################################
def load_stitched(ts: TimeSeries, field:str, fields: list[str], stitchingMethod:Literal["begin", "end", "user-defined"], times:list[float]|None=None, verbose:bool=True, **kwargs) -> None:
    """
    Stitch multiple fields together into a TimeSeries object.

    Args:
        ts (TimeSeries): TimeSeries object to load the fields into.
        field (str): Name of the field to create from the stitched fields.
        fields (list[str]): Names of the fields to stitch together.
        stitchingMethod (str): Method to stitch the fields. Can be one of the following:
            - `begin`: Stitch fields at the first non-nan value of the following field.
            - `end`: Stitch fields at the last non-nan value of the previous field.
            - `user-defined`: Stitch fields at user-defined points.
        times (list[float], optional): User-defined times to stitch the fields together.
            Required if stitching method is `user-defined`, with length 1 less than `fields`.
        verbose (bool, optional): If True, print information about the loading process. Default is True.
        **kwargs: Additional keyword arguments to pass to the loading function.

    Returns:
        None
    """
    checkType(ts, TimeSeries, "ts")
    checkArray(fields, str, "fields", allowEmpty=False)
    checkType(verbose, bool, "verbose")

    fields = list(fields)  # ensure subscriptable regardless of input type

    if not stitchingMethod in ("begin", "end", "user-defined"):
        raise ValueError(f"Method '{stitchingMethod}' is not valid. Must be one of 'begin', 'end', or 'user-defined'.")

    # Check if the fields are already in the TimeSeries object
    if field in ts.columns and verbose:
        print(f"Field '{field}' already exists in the TimeSeries object. Overwriting...")

    for f in fields:
        if f not in ts.columns:
            raise FieldDependencyError(f"Field '{f}' not found in TimeSeries object. Available fields are: {ts.columns}")

    # Load the fields as a stitched array
    if verbose:
        print(f"Stitching fields {fields} together...")

    # Construct the stitch times
    stitch_times: list[float | None]
    if stitchingMethod == "user-defined":
        checkArray(times, float, "times")
        if len(times) != len(fields) - 1:  # type: ignore[arg-type]
            raise ValueError(f"Number of times ({len(times)}) must be one less than the number of fields ({len(fields)}).")  # type: ignore[arg-type]
        stitch_times = list(times)  # type: ignore[arg-type]
    elif stitchingMethod == "begin":
        # First non-nan index of the following field marks the start of that segment
        idx = [ts[f].first_valid_index() for f in fields[1:]]
        t_arr = ts[ts.timeName].to_numpy()
        stitch_times = [float(t_arr[int(ii)]) if ii is not None else None  # type: ignore[arg-type]
                        for ii in idx]
    elif stitchingMethod == "end":
        # Stitch after the last non-nan index of the previous field:
        # the previous field keeps its last valid step; the next field starts
        # at the following time point.
        idx = [ts[f].last_valid_index() for f in fields[:-1]]
        t_arr = ts[ts.timeName].to_numpy()
        stitch_times = [float(t_arr[int(ii) + 1]) if ii is not None else None  # type: ignore[arg-type]
                        for ii in idx]
    else:
        raise ValueError(f"Method '{stitchingMethod}' is not valid. Must be one of 'begin', 'end', or 'user-defined'.")

    # Check that the times are valid
    if any(t is None for t in stitch_times):
        raise ValueError("Some times are None. This means that some field is non-nan everywhere, so the begin/end for automatic stitching cannot be computed. Use 'user-defined' method to specify the times manually.")

    valid_times: list[float] = stitch_times  # type: ignore[assignment]

    if verbose:
        t0 = float(ts[ts.timeName].iloc[0])
        t_end = float(ts[ts.timeName].to_numpy()[-1])
        print(f"Stitching times:\n{t0:.3g} -> " + " -> ".join([f"{f} -> {t:.3g}" for f, t in zip(fields, valid_times + [t_end])]))

    # Compute the stitched data
    index = []
    t0 = float(ts[ts.timeName].iloc[0])
    t_end = float(ts[ts.timeName].to_numpy()[-1])
    extended_times: list[float] = [t0] + valid_times + [t_end]
    for i in range(len(fields)):
        t_lo, t_hi = extended_times[i], extended_times[i + 1]
        if i < len(fields) - 1:
            mask = (ts[ts.timeName] >= t_lo) & (ts[ts.timeName] < t_hi)
        else:
            mask = (ts[ts.timeName] >= t_lo) & (ts[ts.timeName] <= t_hi)
        index.append(ts.index[mask.to_numpy()].to_list())
    
    # Merge the data from the fields at the specified indices
    data = sum([ts.loc[idx,f].tolist() for f, idx in zip(fields, index)], [])
    
    # Load in the TimeSeries object
    ts.loadArray([ts[ts.timeName], data], varName=field, verbose=verbose, dataFormat="row", **kwargs)
    
######################################################################
def load_cumulative(ts: TimeSeries, field: str, input: str, reference:float=None, verbose:bool=True, **kwargs) -> None:
    """
    Load a field as a cumulative integral of another field in the TimeSeries object.
    
    Args:
        ts (TimeSeries): TimeSeries object to load the field into.
        field (str): Name of the field to load.
        input (str): Name of the field to integrate.
        reference (float, optional): Reference value for the cumulative integral (instant where to set the integral to zero)
            If `None`, the integral is set to zero at the first time step. Default is None.
        verbose (bool, optional): If True, print information about the loading process. Default is True.
        **kwargs: Additional keyword arguments to pass to the loading function.
    """
    checkType(ts, TimeSeries, "ts")
    checkType(field, str, "field")
    checkType(input, str, "input")
    checkType(reference, float, "reference", allowNone=True)
    checkType(verbose, bool, "verbose")
    
    # Check if the field is already in the TimeSeries object
    if field in ts.columns and verbose:
        print(f"Field '{field}' already exists in the TimeSeries object. Overwriting...")
        
    # Check if the input field is in the TimeSeries object
    if input not in ts.columns:
        raise FieldDependencyError(f"Input field '{input}' not found in TimeSeries object. Available fields are: {ts.columns}")
    
    # Load the field as a cumulative integral
    if verbose:
        print(f"Loading field '{field}' as a cumulative integral of '{input}'...")
    
    if len(ts) == 0:
        raise FieldDependencyError("TimeSeries is empty. Cannot load cumulative field.")
    
    time = ts[ts.timeName].to_numpy()
    data = ts[input].to_numpy()
    
    # Compute the cumulative integral
    cum_data = integrate.cumulative_trapezoid(data, time, initial=0.0)
    if reference is not None:
        if reference < time[0]:
            raise ValueError(f"Reference time {reference} is before the first time step {time[0]}.")
        if reference > time[-1]:
            raise ValueError(f"Reference time {reference} is after the last time step {time[-1]}.")
        if verbose:
            print(f"Setting cumulative integral to zero at reference time {reference}...")
        ref_idx = int((time >= reference).argmax())
        cum_data -= cum_data[ref_idx]
    
    # Load in the TimeSeries object
    ts.loadArray([time, cum_data], varName=field, verbose=verbose, dataFormat="row", **kwargs)

######################################################################
def _resolve_per_file_kwargs(filepath: str, per_file_kwargs: dict | None, global_kwargs: dict) -> dict:
    """Merge global kwargs with per-file overrides whose regex key matches the file's basename."""
    merged = {**global_kwargs}
    if per_file_kwargs:
        for pattern, overrides in per_file_kwargs.items():
            if re.search(pattern, os.path.basename(filepath)):
                merged.update(overrides)
    return merged


######################################################################
def load_files(ts: TimeSeries, field: str, files: str | list, root: str | None = None,
               per_file_kwargs: dict | None = None, verbose: bool = True, permissive: bool = False, **kwargs) -> None:
    """
    Load a field by merging multiple files (glob patterns allowed) into a TimeSeries object.

    Files are sorted by their transformed start time (after applying x_off and x_scale).
    If multiple files share the same start time, the one with the latest end time is kept
    and the others are discarded (with a RuntimeWarning). Merging uses the 'begin' stitching
    strategy: each file takes over from the first time point of the following file.

    All intermediate loading is performed on a temporary isolated TimeSeries. The merged
    result is loaded back into `ts` via loadArray, so `ts` is never left in a corrupted
    state if an error occurs.

    Args:
        ts (TimeSeries): TimeSeries object to load the field into.
        field (str): Name of the field to load.
        files (str | list[str]): Glob pattern string or list of glob patterns / explicit paths.
        root (str, optional): Root directory prepended to each pattern before glob expansion.
            Defaults to None.
        per_file_kwargs (dict[str, dict], optional): Per-file keyword argument overrides.
            Keys are regex patterns matched against the **basename** of each resolved file.
            All matching entries are merged on top of global **kwargs (later keys win).
            Defaults to None.
        verbose (bool, optional): Print progress information. Defaults to True.
        permissive (bool, optional): If True, error conditions (no files found, empty files, file read errors) are treated as warnings and loading proceeds with the remaining valid files. Defaults to False.
        **kwargs: Global keyword arguments forwarded to every load_file call
            (e.g. x_col, y_col, x_scale, y_scale, skip_rows, comments, delimiter).

    Returns:
        None

    Raises:
        ValueError: If no files are resolved from the given patterns.
        ValueError: If a resolved file contains no valid data rows.
        TypeError: If arguments have wrong types.
        FieldDependencyError: When ``permissive=True`` and no valid files are loaded
            (or no files match), a NaN placeholder field is written via
            :func:`load_uniform`. This requires ``ts`` to already contain a
            non-empty time axis. If ``ts`` is empty a ``FieldDependencyError``
            is raised even with ``permissive=True`` — this is **intentional**:
            there is no time grid on which to define the placeholder.
    """
    checkType(ts, TimeSeries, "ts")
    checkType(field, str, "field")
    checkType(files, (str, list), "files")
    checkType(root, str, "root", allowNone=True)
    checkType(per_file_kwargs, dict, "per_file_kwargs", allowNone=True)
    checkType(verbose, bool, "verbose")
    checkType(permissive, bool, "permissive")
    # Validate per_file_kwargs regex keys up-front
    if per_file_kwargs is not None:
        for pattern in per_file_kwargs:
            checkType(pattern, str, f"per_file_kwargs key '{pattern}'")
            try:
                re.compile(pattern)
            except re.error as e:
                raise ValueError(f"per_file_kwargs key '{pattern}' is not a valid regex pattern: {e}") from e
            checkType(per_file_kwargs[pattern], dict, f"per_file_kwargs['{pattern}']")

    # Normalise files to a list
    if isinstance(files, str):
        files = [files]

    # Glob-expand each pattern and collect unique resolved paths (preserving first-seen order)
    resolved: list[str] = []
    seen: set[str] = set()
    for pattern in files:
        full_pattern = os.path.join(root, pattern) if root else pattern
        matches = sorted(_wc_glob(full_pattern, flags=EXTGLOB | GLOBSTAR))
        for m in matches:
            if m not in seen:
                resolved.append(m)
                seen.add(m)

    if not resolved:
        msg = f"No files found for field '{field}'. Patterns searched: {files}" + (f" (root: {root})" if root else "")
        if permissive:
            warnings.warn(msg, RuntimeWarning)
            # Load an empty field with NaN values to avoid leaving ts without the requested field
            return load_uniform(ts, field, value=float("nan"), verbose=verbose)
        else:
            raise ValueError(msg)

    if verbose:
        print(f"Loading field '{field}' from {len(resolved)} file(s)...")

    # Check if field already exists in ts
    if field in ts.columns and verbose:
        print(f"Field '{field}' already exists in the TimeSeries object. Overwriting...")

    # ------------------------------------------------------------------
    # Peek at each file to get transformed time range for sorting
    # ------------------------------------------------------------------
    def _peek(filepath: str, file_kwargs: dict) -> tuple[float, float]:
        x_col      = file_kwargs.get("x_col",      file_kwargs.get("xCol",      0))
        x_off      = file_kwargs.get("x_off",      file_kwargs.get("xOff",      0.0))
        x_scale    = file_kwargs.get("x_scale",    file_kwargs.get("xScale",    1.0))
        skip_rows  = file_kwargs.get("skip_rows",  file_kwargs.get("skipRows",  file_kwargs.get("skiprows", 0)))
        comments   = file_kwargs.get("comments",   "#")
        delimiter  = file_kwargs.get("delimiter",  None)
        max_rows   = file_kwargs.get("max_rows",   file_kwargs.get("maxRows",   None))
        try:
            t_raw = np.loadtxt(filepath, usecols=(x_col,), skiprows=skip_rows,
                               max_rows=max_rows, comments=comments, delimiter=delimiter)
        except Exception as e:
            raise ValueError(f"Failed reading time column from file '{filepath}': {e}") from e
        if t_raw.ndim == 0:
            t_raw = t_raw.reshape(1)
        if len(t_raw) == 0:
            raise ValueError(f"File '{filepath}' contains no valid data rows.")
        t = (t_raw + float(x_off)) * float(x_scale)
        return float(t[0]), float(t[-1])

    file_info: list[tuple[float, float, str, dict]] = []
    for filepath in resolved:
        file_kwargs = _resolve_per_file_kwargs(filepath, per_file_kwargs, kwargs)
        try:
            t_start, t_end = _peek(filepath, file_kwargs)
        except Exception as e:
            raise ValueError(f"Failed peeking time range for field '{field}': {e}") from e
        file_info.append((t_start, t_end, filepath, file_kwargs))

    # ------------------------------------------------------------------
    # Sort by transformed start time
    # ------------------------------------------------------------------
    file_info.sort(key=lambda x: x[0])

    # ------------------------------------------------------------------
    # Conflict resolution: same t_start → keep file with latest t_end
    # ------------------------------------------------------------------
    deduped: list[tuple[float, float, str, dict]] = []
    i = 0
    while i < len(file_info):
        group = [file_info[i]]
        j = i + 1
        while j < len(file_info) and math.isclose(file_info[j][0], file_info[i][0], rel_tol=1e-9, abs_tol=1e-9):
            group.append(file_info[j])
            j += 1
        # Keep the one with max t_end
        keeper = max(group, key=lambda x: x[1])
        for item in group:
            if item is not keeper:
                warnings.warn(RuntimeWarning(
                    f"File '{item[2]}' shares start time {item[0]} with '{keeper[2]}' "
                    f"and has a shorter time range. Discarding it."
                ))
        deduped.append(keeper)
        i = j

    if verbose:
        print(f"  Merging {len(deduped)} file(s) after conflict resolution:")
        for t_start, t_end, filepath, _ in deduped:
            print(f"    [{t_start:.6g}, {t_end:.6g}]  {os.path.basename(filepath)}")

    # ------------------------------------------------------------------
    # Load each file into an isolated temp TimeSeries
    # ------------------------------------------------------------------
    temp_ts = TimeSeries(timeName=ts.timeName)
    temp_field_names: list[str] = []

    for idx, (t_start, t_end, filepath, file_kwargs) in enumerate(deduped):
        temp_name = f"field_{idx}"
        temp_field_names.append(temp_name)
        try:
            load_file(temp_ts, temp_name, filepath, verbose=verbose, **file_kwargs)
        except Exception as e:
            if permissive:
                warnings.warn(RuntimeWarning(f"Failed loading file '{filepath}' for field '{field}': {e}. Skipping this file."))
                temp_field_names.pop()  # Remove the temp field name since loading failed
                continue
            raise ValueError(f"Failed loading file '{filepath}' for field '{field}': {e}") from e

    # ------------------------------------------------------------------
    # Stitch in temp_ts using 'begin' method
    # ------------------------------------------------------------------
    if len(temp_field_names) == 1:
        # Single file: no stitching needed, just rename
        time = temp_ts[temp_ts.timeName].to_numpy()
        data = temp_ts[temp_field_names[0]].to_numpy()
    elif len(temp_field_names) == 0:
        if permissive:
            warnings.warn(RuntimeWarning(f"No valid files loaded for field '{field}'. Loading an empty field with NaN values."))
            return load_uniform(ts, field, value=float("nan"), verbose=verbose)
        else:
            raise ValueError(f"No valid files loaded for field '{field}'.")
    else:
        load_stitched(temp_ts, field, temp_field_names, stitchingMethod="begin", verbose=verbose)
        time = temp_ts[temp_ts.timeName].to_numpy()
        data = temp_ts[field].to_numpy()

    if verbose:
        print(f"  Successfully loaded {len(temp_field_names)} file(s).")
        print(f"  Time range: [{time[0]:.6g}, {time[-1]:.6g}] with {len(time)} points.")
    
    # ------------------------------------------------------------------
    # Load merged result into original ts
    # ------------------------------------------------------------------
    if len(ts) > 0:
        ts_time = ts[ts.timeName].to_numpy()
        # Extend ts_time to cover the full range of the merged files, if needed, to avoid dropping data outside ts's original time range.
        if time[0] < ts_time[0]:
            ts_time = np.concatenate((time[time < ts_time[0]], ts_time))
        if time[-1] > ts_time[-1]:
            ts_time = np.append(ts_time, time[time > ts_time[-1]])
        result = np.full(len(ts_time), float("nan"))
        
        # ts already has a time axis (e.g. cold-flow loaded first).
        # Interpolate per file segment so that ts time points falling in gaps
        # between files get NaN instead of being linearly interpolated across.
        for t_start, t_end, _, _ in deduped:
            mask = (ts_time >= t_start) & (ts_time <= t_end)
            seg  = (time   >= t_start) & (time   <= t_end)
            if np.any(mask) and np.any(seg):
                result[mask] = np.interp(ts_time[mask], time[seg], data[seg])
    else:
        ts_time = time
        result = data
    
    if verbose:
        print(f"    Loading merged field '{field}' into TimeSeries object...")
        print(f"    Final time range in TimeSeries: [{ts_time[0]:.6g}, {ts_time[-1]:.6g}] with {len(ts_time)} points.")
    ts.loadArray([ts_time, result], varName=field, verbose=verbose, dataFormat="row")


######################################################################
def _resolve_operand(ts: TimeSeries, x: str | float) -> "np.ndarray | float":
    """Resolve a conditional operand: field name → numpy array, float → scalar."""
    if isinstance(x, str):
        if x not in ts.columns:
            raise FieldDependencyError(
                f"Field '{x}' not found in TimeSeries. "
                f"Available fields: {list(ts.columns)}"
            )
        return ts[x].to_numpy()
    return float(x)


######################################################################
def load_conditional(
    ts: TimeSeries,
    field: str,
    f1: "str | float",
    operator: str,
    f2: "str | float",
    f3: "str | float | None" = None,
    f4: "str | float | None" = None,
    verbose: bool = True,
    **operator_kwargs,
) -> None:
    """
    Load a field by element-wise conditional selection between two values:

        result[t] = F1[t]   if   F3[t] <operator> F4[t]
                    F2[t]   otherwise

    F3 and F4 default to F1 and F2 respectively, so the common case of
    selecting the larger/smaller of two fields requires no extra arguments.
    For unary operators (e.g. `isnan`), F4 is ignored entirely.

    Args:
        ts (TimeSeries): TimeSeries object to load the field into.
        field (str): Name of the resulting field.
        f1 (str | float): True-branch value — existing field name or scalar constant.
        operator (str): Comparison operator. Must be a valid `ConditionalOperator`
            value: `>`, `>=`, `<`, `<=`, `==`, `!=`, `isnan`.
        f2 (str | float): False-branch value — existing field name or scalar constant.
        f3 (str | float | None): Condition LHS. Defaults to `f1`.
        f4 (str | float | None): Condition RHS. Defaults to `f2`. Ignored for
            unary operators.
        verbose (bool, optional): Print progress. Defaults to True.
        **operator_kwargs: Extra keyword arguments forwarded to the operator function.
            For `==` / `!=`: `rel_tol` (default 1e-6), `abs_tol` (default 1e-12).

    Returns:
        None

    Raises:
        FieldDependencyError: If a field name operand is not yet in the TimeSeries,
            or if the TimeSeries is empty.
        ValueError: If `operator` is not a recognised `ConditionalOperator` value.
        TypeError: If arguments have wrong types.
    """
    checkType(ts, TimeSeries, "ts")
    checkType(field, str, "field")
    checkType(f1, (str, float), "f1")
    checkType(operator, str, "operator")
    checkType(f2, (str, float), "f2")
    checkType(f3, (str, float), "f3", allowNone=True)
    checkType(f4, (str, float), "f4", allowNone=True)
    checkType(verbose, bool, "verbose")

    # Validate operator via the enum (raises ValueError with clear message on failure)
    op = ConditionalOperator(operator)

    # Require non-empty TimeSeries
    if len(ts) == 0:
        raise FieldDependencyError("TimeSeries is empty. Cannot load conditional field.")

    # Notify if overwriting
    if field in ts.columns and verbose:
        print(f"Field '{field}' already exists in the TimeSeries object. Overwriting...")

    # Resolve effective condition operands
    f3_eff = f3 if f3 is not None else f1
    f4_eff = f4 if f4 is not None else f2

    if verbose:
        is_unary = op in _UNARY_CONDITIONAL_OPERATORS
        lhs_desc = f"{op.value}({f3_eff})" if is_unary else f"{f3_eff} {op.value} {f4_eff}"
        print(f"Loading field '{field}' as conditional: {f1} if ({lhs_desc}) else {f2}...")

    # Resolve all operands to arrays or scalars
    v1 = _resolve_operand(ts, f1)
    v2 = _resolve_operand(ts, f2)
    v3 = _resolve_operand(ts, f3_eff)
    v4 = None if op in _UNARY_CONDITIONAL_OPERATORS else _resolve_operand(ts, f4_eff)

    # Evaluate condition and select
    condition = _CONDITIONAL_OPERATORS[op](v3, v4, **operator_kwargs)
    result = np.where(condition, v1, v2)

    # Broadcast to 1-D if all operands were scalars (0-d result)
    result = np.asarray(result)
    if result.ndim == 0:
        result = np.broadcast_to(result, len(ts)).copy()

    time = ts[ts.timeName].to_numpy()
    ts.loadArray([time, result], varName=field, verbose=verbose, dataFormat="row")


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
            - `stitch`: stitch multiple fields together into a TimeSeries object.
            - `cumulative`: load a field as a cumulative integral of another field in the TimeSeries object. Aliases: `integrate`
            - `files`: load and merge multiple files (glob patterns allowed) sorted by transformed start time.
            - `conditional`: element-wise `F1 if (F3 op F4) else F2`. Aliases: `cond`
        inplace (bool, optional): If True, the field will be loaded into the TimeSeries object.
            If False, a new TimeSeries object will be created with the loaded field. Default is True.
        verbose (bool, optional): If True, print information about the loading process. Default is True.
        **kwargs: Additional keyword arguments to pass to the loading method.
        
    Returns:
        TimeSeries|None: The TimeSeries object with the loaded field if inplace is False, otherwise None.
    """
    # Type checking — all checks before any branching
    checkType(ts, TimeSeries, "ts")
    checkType(field, str, "field")
    checkType(method, str, "method")
    checkType(inplace, bool, "inplace")
    checkType(verbose, bool, "verbose")

    if not inplace:
        ts = ts.copy()
        loadField(ts, field, method, inplace=True, verbose=verbose, **kwargs)
        return ts

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
    elif method_ == LoadingMethod.stitch:
        load_stitched(ts, field, **kwargs, verbose=verbose)
    elif method_ in (LoadingMethod.cumulative, LoadingMethod.integrate):
        load_cumulative(ts, field, **kwargs, verbose=verbose)
    elif method_ == LoadingMethod.files:
        load_files(ts, field, **kwargs, verbose=verbose)
    elif method_ in (LoadingMethod.conditional, LoadingMethod.cond):
        load_conditional(ts, field, **kwargs, verbose=verbose)