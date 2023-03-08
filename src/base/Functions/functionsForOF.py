#####################################################################
#                                  DOC                              #
#####################################################################

"""
Functions used to handle OpenFOAM files
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

#Type checking
from src.base.Functions.typeChecking import checkType
    
# Import functions to read OF files:
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
    
    #Load table:
    tab = ParsedParameterFile(fileName,listDictWithHeader=True).content
    
    #Load data:
    if isinstance(tab, BinaryList):
        numel = tab.length
        
        import struct
        return list(struct.unpack("d" * numel, tab.data))
    else:
        return tab
