#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino (federico.ramognino@polimi.it)
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from ._Filter import Filter
from ..dataStructures import TimeSeries

from typing import Iterable

from libICEpost.src.base.Functions.typeChecking import checkType, checkArray

#####################################################################
#                               FUNCTIONS                           #
#####################################################################

def filter(ts:TimeSeries, filter:Filter, *, fields:Iterable[str]=None, verbose:bool=True) -> TimeSeries:
    """
    Apply a filter to the fields of a TimeSeries object, returning a
    new TimeSeries object with the filtered data.
    
    Args:
        ts (TimeSeries): The TimeSeries object to filter.
        filter (Filter): The filter to apply.
        fields (Iterable[str], optional): The fields to filter. If None, all fields are filtered. Defaults to None.
        verbose (bool, optional): Whether to print information about the filtering process. Defaults to True.
    """
    checkType(ts, TimeSeries, "ts")
    checkType(filter, Filter, "filter")
    if fields is None: fields = [c for c in ts.columns if not c == ts.timeName]
    checkArray(fields, str, "fields")
    checkType(verbose, bool, "verbose", optional=True)
    
    if verbose:
        print(f"Filtering fields {fields} with filter {filter}...", end="\n\t")
    
    # Create a new TimeSeries object to store the filtered data
    ts_filtered = TimeSeries(timeName=ts.timeName)
    
    for f in fields:
        # Forbid loading the time field
        if f == ts.timeName:
            raise ValueError(f"Cannot filter the time field ({ts.timeName})")
        
        if verbose:
            print(f"{f}, ", end="", flush=True)
        
        ts_filtered.loadArray(
                filter(
                    ts[ts.timeName].to_numpy(),
                    ts[f].to_numpy()
                ),
                f,
                dataFormat="row"
            )
    if verbose:
        print(" DONE")
    
    return ts_filtered