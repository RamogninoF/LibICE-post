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
from .typeChecking import checkType
    
# Import functions to read OF files:
import PyFoam
from PyFoam.RunDictionary.ParsedParameterFile import ParsedFileHeader,ParsedParameterFile
from PyFoam.Basics.DataStructures import BinaryList

#############################################################################
#                               MAIN FUNCTIONS                              #
#############################################################################
#Read a OpenFOAM file with a tabulation:
def readOFscalarList(fileName):
    """
    fileName:        str
        Name of the OpenFOAM file
    
    Reads an OpenFOAM file storing a scalarList. 
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
    File = ParsedParameterFile(fileName, listDictWithHeader=True, binaryMode=True)
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
