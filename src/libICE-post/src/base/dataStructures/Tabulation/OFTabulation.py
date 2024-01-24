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

#from app import *
from src.base.Utilities import Utilities
from .Tabulation import Tabulation
from src.base.Functions.functionsForOF import readOFscalarList

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Laminar flame speed computation with Gulder correlation:
class OFTabulation(Utilities):
    """
    Class used to store and handle an OpenFOAM tabulation.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        path:               str
            Path where the tabulation is stored
        
        entryNames:     dict    [{}]
            {
                entri_ii:     str
                    Name to give at the generic entry 'entry_ii' found in the dictionay
                    tableProperties.
            }
            Used to (optionally) change the names of the variables stored in the table.
        
        tableProperties:    dict
            {
                var_ii:   list<float>
                    Contains the list of sampling points for variable 'var_ii'
            }
            Dictionary containing the information retrieved from tableProperties.
        
        varOrder:           list<str>
            Order in which the variables are red convert the scalarLists in tables.
                
        noWrite:        bool
            Label controlling if the class is allowed to write the files
        
        tables:             dict
            {
                'tab_ii':   Tabulation
            }
            Contains the tabulations.
        
        tableFileNames:     dict
            {
                'tab_ii':   str
            }
            Contains the names of files for the tabulations.
        
        opts:       dict
        {
            Fatal:          bool
                If set to 'True', raises a ValueError in case the input data is outside
                of tabulation range. Otherwise a warning is displayed.
            
            extrapolate:    bool
                If set to 'True' the value is extrapolated in case accessing the table
                outside of ranges. Otherwise, the value is set to 'nan'.
        }
    """
    
    #########################################################################
    #Data:
    defaultOpts = \
            {
                "Fatal":False,
                "extrapolate":True
            }
    
    path = None
    entryNames = {}
    tableProperties = {}
    varOrder = []
    tables = {}
    tableFileNames = {}
    noWrite =True
    
    #########################################################################
    #Class methods:
    @classmethod
    def fromFile(cls, tablePath, varOrder, tableFileNames, entryNames={}, noWrite=noWrite, noRead=[], **argv):
        """
        tablePath:      str
            The path where the tabulation is stored
        varOrder:       list<str>
            Order of the variables used to access the tabulation
        tableFileNames: list<str>
            Names of files in 'tablePath/const' where the tables are stored
        entryNames:     dict    ({})
            {
                entri_ii:     str
                    Name to give at the generic entry 'entry_ii' found in the dictionary
                    tableProperties.
            }
            Used to (optionally) change the names of the variables stored in the table.
        noWrite:        bool (True)
            Handle to prevent write access of this class to the tabulation
        noRead:         list<str>   ([])
            Tables that are not to be red from files
        
        [keyword arguments]
        Fatal:          bool (False)
            If set to 'True', raises a ValueError in case the input data is outside
            of tabulation range. Otherwise a warning is displayed.
        
        extrapolate:    bool (True)
            If set to 'True' the value is extrapolated in case accessing the table
            outside of ranges. Otherwise, the value is set to the 'nan'.
        
        Construct a table from files stored in 'tablePath'.
        """
        #Argument checking:
        try:
            cls.checkType(tablePath, str, "tablePath")
            cls.checkInstanceTemplate(varOrder, [""], "varOrder")
            cls.checkInstanceTemplate(tableFileNames, {"":""}, "tableFileNames")
            cls.checkInstanceTemplate(entryNames, {"":""}, "entryNames",allowEmptyContainer=True)
            cls.checkType(noWrite, bool, "noWrite")
            cls.checkInstanceTemplate(noRead, [""], "noRead",allowEmptyContainer=True)
            
            argv = cls.updateKeywordArguments(argv, cls.defaultOpts)
            
        except BaseException as err:
            cls.fatalErrorInArgumentChecking(cls.empty(), cls.fromFile, err)
        
        try:
            #Create the table:
            tab = cls(tablePath, noWrite, **argv)
            tab.readTableProperties(entryNames)
            tab.setOrder(varOrder)
            
            for table in tableFileNames:
                if not(table in noRead):
                    tab.readTable(tableFileNames[table], table)
                else:
                    tab.tables[table] = None
            
        except BaseException as err:
            cls.fatalErrorInClass(cls, cls.fromFile, "Failed loading the tabulation", err)
            
        return tab
    
    #########################################################################
    #Constructor:
    def __init__(self, tablePath=path, noWrite=noWrite, **argv):
        """
        tablePath:      str  (None)
            Path where to read/write the tabulation
        noWrite:        bool (True)
            Label controlling if the class is allowed to write the files. For safety,
            in case 'noWrite' is set to False, a warning is displayed, an a backup
            copy of the tabulation is generated if it already exists.
        
        [keyword arguments]
        Fatal:          bool (False)
            If set to 'True', raises a ValueError in case the input data is outside
            of tabulation range. Otherwise a warning is displayed.
        
        extrapolate:    bool (True)
            If set to 'True' the value is extrapolated in case accessing the table
            outside of ranges. Otherwise, the value is set to the 'nan'.
        
        Create a tabulation in OpenFOAM format, associated to path 'tablePath'.
        """
        #Argument checking:
        try:
            if not(tablePath is None):
                Utilities.checkType(tablePath, str, entryName="tablePath")
            
            Utilities.checkType(noWrite, bool, entryName="noWrite")
            
            #Options:
            self.opts = Utilities.updateKeywordArguments(argv, self.defaultOpts)
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        #Initialize arguments:
        self.clear()
        self.path = tablePath
        self.noWrite = noWrite
        
    #########################################################################
    #__getitem__(slices):
    def __getitem__(self, slices):
        """
        slices:   tuple<slice/list<int>/int>
        
        Extract a tabulation with sliced dataset. New table is
        initialized without associated directory (path = None) and 
        in read-only mode (noWrite = True).
        """
        try:
            #Check arguments:
            if not(len(slices) == len(self.varOrder)):
                raise IndexError("Given {} ranges, while table has {} fields ({}).".format(len(slices), len(self.varOrder), self.varOrder))
            
            newSlices = []
            for ii in range(len(self.varOrder)):
                ss = slices[ii]
                indList = range(len(self.tableProperties[self.varOrder[ii]]))
                
                if isinstance(ss, slice):
                    newSlices.append(indList[ss])
                    
                elif isinstance(ss,int):
                    if not(ss in indList):
                        raise IndexError("Index out of range for field '{}'.".format(self.varOrder[ii]))
                    newSlices.append([ss])
                
                elif isinstance(ss,list):
                    for ind in ss:
                        if not(ind in indList):
                            raise IndexError("Index out of range for field '{}'.".format(self.varOrder[ii]))
                    
                    newSlices.append(ss)
                    
                else:
                    raise TypeError("Type mismatch. Attempting to slice with entry of type '{}'.".format(ss.__class__.__name__))
            
        except BaseException as err:
            self.fatalErrorInClass(self.__getitem__, "Slicing error", err)
        
        #Create ranges:
        order = self.varOrder
        ranges =  {}
        for ii,  Slice in enumerate(newSlices):
            ranges[order[ii]] = [self.tableProperties[order[ii]][ss] for ss in Slice]
        
        #Create sliced table:
        newTable = cp.deepcopy(self)
        
        newTable.clear()
        newTable.varOrder = order
        newTable.tableProperties = ranges
        newTable.entryNames = self.entryNames
        newTable.tableFileNames = self.tableFileNames
        
        for table in self.tables:
            if not (self.tables[table] is None):
                newTable.tables[table] = self.tables[table].__getitem__(slices)
            else:
                newTable.tables[table] = None
        
        return newTable
    
    #########################################################################
    #Read tableProperties file:
    def readTableProperties(self, entryNames={}, **argv):
        """
        entryNames:     dict    [{}]
            {
                entri_ii:     str
                    Name to give at the generic entry 'entry_ii' found in the dictionay
                    tableProperties.
            }
            Used to (optionally) change the names of the variables stored in the table.
        
        Read information stored in file '<path>/tableProperties' related to the ranges
        in the table.
        """
        #Argument checking:
        try:
            Utilities.checkType(entryNames, dict, entryName="entryNames")
            
            #Read keyword arguments:
            entryNames.update(argv)
            self.entryNames.update(entryNames)
            
            #Check again:
            Utilities.checkInstanceTemplate(entryNames, {0:""}, entryName="entryNames", allowEmptyContainer=True)
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.readTableProperties, err)
        
        #Check directory:
        self.checkDir()
        
        #Load class from PyFoam for parsing:
        from PyFoam.RunDictionary.ParsedParameterFile import FoamStringParser
        
        #Read tableProperties into dict:
        tabProps = FoamStringParser(open(self.path + "/tableProperties", "r").read()).getData()
        
        #Store:
        self.tableProperties = {}
        
        for prop in tabProps:
            if prop in self.entryNames:
                self.tableProperties[self.entryNames[prop]] = tabProps[prop]
            else:
                self.tableProperties[prop] = tabProps[prop]
        
        return self
    
    #########################################################################
    def setOrder(self,varOrder=None):
        """
        varOrder:     list<str>
            Looping order (from outern-most to inner-most) in which the variables
            are to be red to convert the scalarList in table.
        """
        #Argument checking:
        try:
            if not (varOrder is None):
                Utilities.checkInstanceTemplate(varOrder, [""], entryName="varOrder")
            else:
                varOrder = self.__class__.varOrder
        
            if not(self.tableProperties):
                raise IOError("Must read tableProperties before setting 'varOrder'.")
            
            #Check if fields are in tableProperties:
            Utilities.checkDictEntries(self.tableProperties,varOrder)
            
            if not(len(varOrder) == len(self.tableProperties)):
                raise ValueError("Length of 'varOrder' does not match length of 'self.tableProperties'.")
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.setOrder, err)
        
        self.varOrder = varOrder[:]
        
        return self
    
    #########################################################################
    
    #Read table from OF file:
    def readTable(self,fileName, tableName, **argv):
        """
        fileName:   str
        tableName:  str
        
        [keyword arguments]
        Fatal:          bool (False)
            If set to 'True', raises a ValueError in case the input data is outside
            of tabulation range. Otherwise a warning is displayed.
        
        extrapolate:    bool (True)
            If set to 'True' the value is extrapolated in case accessing the table
            outside of ranges. Otherwise, the value is set to the 'nan'.
        
            Loads a table stored at in file '<path>/constant/<fileName>'. Saves a 'table'
            instance with the loaded data in self.tables[tableName].
        """
        #Argument checking:
        try:
            Utilities.checkType(fileName, str, entryName="fileName")
            Utilities.checkType(tableName, str, entryName="tableName")
            
            if not(self.tableProperties):
                raise IOError("Must read tableProperties before loading any tabulation.")
            
            if not(self.varOrder):
                raise IOError("Must set 'varOrder' before loading any tabulation.")
            
            #Read opts arguments:
            argv = Utilities.updateKeywordArguments(argv, self.opts)
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.readTable, err)
        
        try:
            #Table path:
            tabPath = self.path + "/constant/" + fileName
            if not(Utilities.os.path.exists(tabPath)):
                raise IOError("Cannot read tabulation. File '{}' not found.".format(tabPath))
            
            #Read table:
            tab = readOFscalarList(tabPath)
            
            order = self.varOrder
            ranges = self.tableProperties
            
            if not(len(tab) == self.size()):
                raise IOError("Size of table stored in '{}' is not consistent with the data in tableProperties file.".format(tabPath))
            
            self.tables[tableName] = Tabulation(tab, ranges, order,**argv)
            self.tableFileNames[tableName] = fileName
            
        except BaseException as err:
            self.fatalErrorInClass(self.__class__,self.readTable,"Failed reading table data for table '{}' from file '{}'.".format(tableName, tabPath), err)
        
        
        #Reorder table properties in ascending order (as tables are stored in order)
        for field in self.varOrder:
            self.tableProperties[field] = sorted(self.tableProperties[field])
        
        return self
        
    #########################################################################
    #Access:
    
    ############################
    #Get ranges:
    def ranges(self):
        """
        Get a dict containing the data ranges in the tabulation (unmutable).
            {
                'var_ii':       list<float>[2]
                    Contains min and max of 'var_ii' sampling points.
            }
        """
        
        return Utilities.cp.deepcopy(self.tableProperties)
    
    ############################
    #Get dimension:
    def ndim(self):
        """
        Returns the dimentsions of the table (int)
        """
        
        return len(self.tableProperties)
    
    ############################
    #Get list of dimensions:
    def shape(self):
        """
        Returns the a tuple<int> containing the dimensions (dim1, dim2,..., dimn) of the tabulation.
        """
        
        dims = []
        for f in self.tableProperties.keys():
            dims.append(len(self.tableProperties[f]))
        
        return tuple(dims)
    
    ############################
    #Get dimensions:
    def size(self):
        """
        Returns the number of data-points stored in the table (int)
        """
        
        size = 1
        for f in self.tableProperties.keys():
            size *= len(self.tableProperties[f])
        
        return size
    
    #########################################################################    
    #Check that all required files are present in tabulation:
    def checkDir(self):
        """
        Check if all information required to read the tabulation are consistent and present in 'path'. Looking for:
            path
            path/constant
            path/tableProperties
        """
        try:
            if (self.path is None):
                raise ValueError("The table directory was not initialized.")
            
            #Folders:
            if not(Utilities.os.path.exists(self.path)):
                raise IOError("Folder not found '{}', cannot read the tabulation.".format(self.path))
            
            if not(Utilities.os.path.exists(self.path + "/constant")):
                raise IOError("Folder not found '{}', cannot read the tabulation.".format(self.path + "/constant"))
            
            #tableProperties:
            if not(Utilities.os.path.exists(self.path + "/tableProperties")):
                raise IOError("Cannot read table ranges in tableProperties. File '{}' not found.".format(self.path + "/tableProperties"))
            
        except BaseException as err:
            self.fatalErrorInClass(self.checkDir, "Failed checking the files required for reading/writing a, OpenFOAM tabulation" , err)
        
    #########################################################################
    #Merge with other table:
    def mergeTable(self, fieldName, secondTable):
        """
        fieldName:  str
            Field to use to append second table
            
        secondTable: Tabulation
            Tabulation containing the data to introduce
        
        Introduce additional data to the tabulation.
        """
        #Check arguments:
        try:
            Utilities.checkType(fieldName, str, entryName="fieldName")
            Utilities.checkType(secondTable, self.__class__, entryName="secondTable")
            
            if not fieldName in self.varOrder:
                raise ValueError("Field '{}' not found in table.".format(fieldName))
            
            if not fieldName in secondTable.varOrder:
                raise ValueError("Field '{}' not found in 'secondTable'.".format(fieldName))
            
            if self.varOrder != secondTable.varOrder:
                raise ValueError("Tabulation field orders not compatible.\Tabulation fields:\n{}\nFields of tabulation to append:\n{}".format(secondTable.varOrder, self.varOrder))
            
            #Check if fields already present:
            for item in secondTable.tableProperties[fieldName]:
                if item in self.tableProperties[fieldName]:
                    raise ValueError("Value '{}' already present in range of field '{}'.".format(item, self.tableProperties[fieldName]))
            
            #Check compatibility:
            otherFields = [f for f in self.varOrder if f != fieldName]
            otherRanges = {f:self.tableProperties[f] for f in otherFields}
            otherRangesSecond = {f:secondTable.tableProperties[f] for f in otherFields}
            if otherRanges != otherRangesSecond:
                raise ValueError("Table ranges of other fields not compatible.\nTable ranges:\n{}\Ranges of table to append:\n{}".format(otherRanges, otherRangesSecond))
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.mergeTable, err)
        
        #Append data:
        self.tableProperties[fieldName] += secondTable.tableProperties[fieldName]
        self.tableProperties[fieldName] = sorted(self.tableProperties[fieldName])
        
        for table in self.tables:
            if self.tables[table] is None:
                self.tables[table] = secondTable.tables[table]
            
            elif not(self.tables[table] is None) and not(secondTable.tables[table] is None):
                self.tables[table].mergeTable(fieldName, secondTable.tables[table])
            
        return self
    
    #########################################################################    
    #Write the table:
    def write(self, tableFolder=None):
        """
        tableFolder:    str
            Path where to save the table. In case not give, self.path is used.
        Write the tabulation.
        """
        try:
            if tableFolder is None:
                if self.path is None:
                    raise ValueError("Cannot write tabulation: path of the tabulation was not initialized.")
                tableFolder = self.path
            else:
                Utilities.checkType(tableFolder, str, entryName="tableFolder")
            
            if self.noWrite:
                raise IOError("Trying to write tabulation when opered in read-only state. Set 'noWrite' to False to write files.")
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.write, err)
        
        #Folders:
        if not(Utilities.os.path.isdir(tableFolder)):
            Utilities.os.makedirs(tableFolder)
            
        if not(Utilities.os.path.isdir(tableFolder + "/constant")):
            Utilities.os.makedirs(tableFolder + "/constant")
        
        from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
        #Table properties:
        tablePros = ParsedParameterFile(tableFolder + "/tableProperties", noHeader=True, dontRead=True, createZipped=False)
        
        tablePros.content = {}
        for props in self.entryNames:
            tablePros.content[props] = self.tableProperties[self.entryNames[props]]
        
        tablePros.writeFile()
        
        #Tables:
        for table in self.tables:
            if not(self.tables[table] is None):
                tabulation = ParsedParameterFile(tableFolder + "/constant/" + self.tableFileNames[table], listDictWithHeader=True, dontRead=True, createZipped=False)
                
                tabulation.content = list(self.tables[table].data().flatten())
                
                header = \
                    {
                        "version":2.0,
                        "format":"ascii",
                        "class":"scalarList",
                        "location":"constant",
                        "object":self.tableFileNames[table]
                    }
                
                tabulation.header = header
                
                tabulation.writeFile()
        
    #########################################################################    
    #Clear the table:
    def clear(self):
        """
        Reset the tabulation arguments to default values.
        """
        #Initialize arguments:
        self.path = self.__class__.path
        self.opts = self.__class__.defaultOpts
        self.noWrite = self.__class__.noWrite
        
        self.entryNames = self.__class__.entryNames
        self.tableProperties = self.__class__.tableProperties
        self.varOrder = self.__class__.varOrder
        self.tables = self.__class__.tables
        self.tableFileNames = self.__class__.tableFileNames
        
        return self
