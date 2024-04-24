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
from PyFoam.RunDictionary.ParsedParameterFile import ParsedFileHeader,ParsedParameterFile
from PyFoam.Basics.DataStructures import BinaryList

from ..Utilities import Utilities

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

#############################################################################
#                               MAIN FUNCTIONS                              #
#############################################################################
#TODO:
#Make it general: define the classes for each base OF type (scalar, vector, tensor, label) and this class a template
class scalarList(list, Utilities):
    
    """
    Class for OpenFOAM scalarList
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        none
    """
    
    _header = \
        {
        "version"   :   2.0,
        "class"     :   "scalarList",
        "object"    :   "",
        "format"    :   "ASCII"
        }
    
    #########################################################################
    #Class methods and static methods:
    @classmethod
    def from_file(cls, fileName:str):
        """
        fileName (str): Name of the OpenFOAM file
        
        Reads an OpenFOAM file storing a scalarList. 
        """
        try:
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
        except BaseException as err:
            cls.fatalErrorInClass(cls.from_file, "Argument checking failed", err)
            
        try:
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
                out = list(struct.unpack("d" * numel, data))
                return cls(out)
                
            else:
                return cls(tab.data)
            
        except BaseException as err:
            cls.fatalErrorInClass(cls.from_file, "Failed loading scalarList", err)
        
    #########################################################################
    #Properties:
    
    #########################################################################
    #Constructor
    def __init__(self, *data:tuple[float], **kwargs):
        """
        data (tuple[float]): the data to fill the list
        """
        return super().__init__(data, **kwargs)
    
    #########################################################################
    #Dunder methods:
    def __repr__(self):
        """
        The representation of the scalarList
        """
        return super().__repr__()
    
    #########################################################################
    #Methods:
    def write(self, fileName:str):
        """
        fileName (str): Name of the OpenFOAM file
        
        Write the scalarList to a file
        """
        #TODO: add possibility to write in binary
        
        file = ParsedParameterFile(fileName, listDictWithHeader=True, dontRead=True, createZipped=False)
        file.header = self._header.copy()
        
        name = fileName.split("/")[-1]
        file.header["object"] = name
        
        file.content = list(self)
        file.writeFile()

