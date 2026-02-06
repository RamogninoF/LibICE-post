#####################################################################
#                                  DOC                              #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023

Functions used to handle OpenFOAM files
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

#Type checking
from libICEpost.src.base.Functions.typeChecking import checkType

import struct
import os
from typing import Iterable

# Import functions to read OF files:
from foamlib import FoamFile
import numpy as np

#############################################################################
#                               MAIN FUNCTIONS                              #
#############################################################################
#Read a OpenFOAM file with a scalar list:
def readOFscalarList(fileName:str) -> Iterable[float]:
    """
    Reads an OpenFOAM file storing a scalarList. Automatically detects if the file is binary or not.

    Args:
        fileName (str): Name of the OpenFOAM file.
    
    Raises:
        IOError: If the file does not exist or if it does not store a scalarList
    
    Returns:
        Iterable[float]: The data stored in the file.
    """
    #Argument checking:
    checkType(fileName, str, entryName="fileName")
    
    #Check path:
    import os
    if not(os.path.isfile(fileName)):
        raise IOError("File '{}' not found.".format(fileName))
    
    with FoamFile(fileName) as f:
        if f.class_ != "scalarList":
            raise IOError("File '{}' does not store a scalarList.".format(fileName))
        
        data = f[None]
        # Check if the data were correctly read as float, otherwise convert them
        if isinstance(data, np.ndarray) and data.dtype == np.int64:
            data.dtype = np.float64
        
        return data

#############################################################################
#Write OF file with scalar list
def writeOFscalarList(values:Iterable[float], path:str, *, overwrite:bool=False, binary:bool=False) -> None:
    """
    Write an OpenFOAM file storing a scalarList. 

    Args:
        values (Iterable[float]): The data to store.
        path (str): The location where to file the scalarList.
        overwrite (bool, optional): Overwrite if found? Defaults to False.
        binary (bool, optional): Write in binary? Defaults to False.
    
    Raises:
        IOError: If the file exists and overwrite is False.
    """
    #Argument checking:
    checkType(values, Iterable, entryName="values")
    [checkType(val, float, entryName=f"values[{ii}]")for ii,val in enumerate(values)]
    checkType(overwrite, bool, entryName="overwrite")
    checkType(binary, bool, entryName="binary")
    checkType(path, str, entryName="path")
    
    #Check path:
    if os.path.isfile(path) and not overwrite:
        raise IOError("File '{}' exists. Run with overwrite=True.".format(path))
    
    #Create the file object
    with FoamFile(path) as File:
        if File.path.exists():
            File.path.unlink()
        File.path.touch()
        root, file = os.path.split(path)
        File.add("FoamFile", {
            "class":"scalarList",
            "version":2.0,
            "object":file,
            "location":os.path.split(root)[1],
            "format": "binary" if binary else "ascii"
        })
        File.format = "binary" if binary else "ascii"
        File.add(None,np.array(values).flatten())