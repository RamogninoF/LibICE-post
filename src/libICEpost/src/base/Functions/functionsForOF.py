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
from PyFoam.RunDictionary.ParsedParameterFile import ParsedFileHeader,ParsedParameterFile
from PyFoam.Basics.DataStructures import BinaryList

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
    
    #Check header:
    header = ParsedFileHeader(fileName).header
    if not(header["class"] == "scalarList"):
        raise IOError("File '{}' does not store a scalarList, instead '{}' was found.".format(fileName, header["class"]))
    binary = False
    if header["format"] == "binary":
        binary = True
        
    #Load table:
    File = ParsedParameterFile(fileName, listDictWithHeader=True, binaryMode=binary)
    tab = File.content
    #Load data:
    if isinstance(tab, BinaryList):
        numel = tab.length
        
        import struct
        with open(fileName, "rb") as f:
            while True:
                ch = f.read(1)
                if ch == b'(':
                    break
            data = f.read(8*tab.length)
        return list(struct.unpack("d" * numel, data))
    else:
        return tab

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
    File = ParsedParameterFile(path, noBody=True, binaryMode=True, dontRead=True, createZipped=False)
    
    #Header
    path = os.path.abspath(path)
    root, file = os.path.split(path)
    File.header = \
        {
            "class":"scalarList",
            "version":2.0,
            "object":file,
            "location":os.path.split(root)[1],
            "format": "binary" if binary else "ascii"
        }
    
    #Empty at first
    File.writeFile(content={})
    
    #Data
    with open(path, "ba") as file:
        file.write(f"{len(values)}".encode())
        file.write(f"\n(".encode())
    
    from array import array
    if binary:
        with open(path, "a+b") as file:
            file.write(struct.pack('d' * len(values), *tuple([float(v) for v in values])))
    else:
        with open(path, "a") as file:
            file.write(" ".join([str(v) for v in values]))
    
    with open(path, "ba") as file:
        file.write(f")\n\n".encode())