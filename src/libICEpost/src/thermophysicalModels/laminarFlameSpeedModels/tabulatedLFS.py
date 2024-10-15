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

from src.base.dataStructures.Tabulation.OFTabulation import OFTabulation
from .laminarFlameSpeedModel import laminarFlameSpeedModel

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Laminar flame speed computation with Gulder correlation:
class tabulatedLFS(OFTabulation,laminarFlameSpeedModel):
    """
    Class for computation of unstained laminar flame speed from tabulation
    
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
                'tab_ii':   table
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
    #Static data:
    entryNames = \
        {
            "pValues":"p",
            "tValues":"T",
            "eqvrValues":"phi",
            "EGRValues":"EGR"
        }
    
    tableProperties = \
            {
                "p": [],
                "T": [],
                "phi": [],
                "EGR": []
            }
    
    varOrder = ["p", "T", "phi", "EGR"]
    
    tables = \
        {
            "Su":None,
            "deltaL":None
        }
    
    tableFileNames = \
        {
            "Su":"laminarFlameSpeedTable",
            "deltaL":"deltaLTable"
        }
    
    #########################################################################
    #Class methods:
    @classmethod
    def fromFile(cls, tablePath, isLaminarFlameThickness=True, noWrite=OFTabulation.noWrite, **argv):
        """
        tablePath:                  str
            The path where the tabulation is stored
        isLaminarFlameThickness:    bool (True)
            Is the laminar flame thickness to be loaded? (in case it was not tabulated)
        noWrite:        bool (True)
            Handle to prevent write access of this class to the tabulation
        
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
            cls.checkType(noWrite, bool, "noWrite")
            cls.checkType(isLaminarFlameThickness, bool, "isLaminarFlameThickness")
            
            argv = cls.updateKeywordArguments(argv, cls.defaultOpts)
        except BaseException as err:
            cls.fatalErrorInArgumentChecking(cls.empty(), tabulatedLFS.fromFile, err)
        
        try:
            entryNames = cls.entryNames
            tableFileNames = cls.tableFileNames
            varOrder = cls.varOrder
            
            tabProp = tabulatedLFS(tablePath).readTableProperties().tableProperties
            if not("EGR" in tabProp):
                del varOrder[-1]
                del entryNames["EGRValues"]
            
            if isLaminarFlameThickness:
                noRead = []
            else:
                noRead = ["deltaL"]
            
        except BaseException as err:
            cls.fatalErrorInClass(tabulatedLFS.fromFile, "Failed loading the tabulation", err)
        
        #Create the table:
        tab = super(cls, cls).fromFile(tablePath, varOrder, tableFileNames, entryNames, noWrite, noRead, **argv)
        
        return tab
    
    ###################################
    #Class methods:
    @classmethod
    def fromDictionary(cls, dictionary):
        """
        Construct from dictionary containing:
            tablePath:                  str
                The path where the tabulation is stored
            
            [Optional]
            isLaminarFlameThickness:    bool (True)
                Is the laminar flame thickness to be loaded? (in case it was not tabulated)
            noWrite:        bool (True)
                Handle to prevent write access of this class to the tabulation
            Fatal:          bool (False)
                If set to 'True', raises a ValueError in case the input data is outside
                of tabulation range. Otherwise a warning is displayed.
            extrapolate:    bool (True)
                If set to 'True' the value is extrapolated in case accessing the table
                outside of ranges. Otherwise, the value is set to the 'nan'.
        """
        try:
            cls.checkType(dictionary, dict, "dictionary")
            
            if not "tablePath" in dictionary:
                raise ValueError("Entry 'tablePath' not found in dictionary.")
                
            tablePath = dictionary["tablePath"]
            cls.checkType(tablePath, str, f"dictionary[{tablePath}]")
            
            optEntries = \
                {
                    "isLaminarFlameThickness":True,
                    "noWrite":True, 
                    "Fatal":False, 
                    "extrapolate":True
                }
            
            opt = {}
            for entry in optEntries:
                if entry in dictionary:
                    cls.checkType(dictionary[entry], type(optEntries[entry]), f"dictionary[{entry}]")
                    opt[entry] = dictionary[entry]
                else:
                    opt = optEntries[entry]
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, f"Argument checking failed", err)
        
        return cls.fromFile(tablePath, **opt)
    
    #########################################################################
    #Constructor:
    def __init__(self, tablePath=OFTabulation.path, noWrite=OFTabulation.noWrite, **argv):
        """
        tablePath:      str  (None)
            Path where the tabulation is stored
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
        
        Create a class to handle a laminar flame speed tabulation.
        """
        OFTabulation.__init__(self, tablePath, noWrite, **argv)
    
    #########################################################################
    #Disabling function
    def setCoeffs(self, *args, **argv):
        import inspect
        raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, inspect.stack()[0][3]))
    
    #########################################################################
    
    #Get SuTable:
    def SuTable(self):
        """
        Returns a copy of the tabulation of laminar flame speed
        """
        return self.tables["Su"].copy()
    
    ################################
    #Get deltaLTable:
    def deltaLTable(self):
        """
        Returns a copy of the tabulation of laminar flame tickness
        """
        return self.tables["deltaL"].copy()
    
    #########################################################################
    #Cumpute laminar flame speed:
    def Su(self,p,T,phi,EGR=None, **argv):
        """
        p:      float
            Pressure [Pa]
        T:      float
            Temperature [K]
        phi:    float
            Equivalence ratio
        EGR:    float (None)
            Level of exhaust gas recirculation [%]
        
        [keyword arguments]
        Fatal:          bool (False)
            If set to 'True', raises a ValueError in case the input data is outside
            of tabulation range. Otherwise a warning is displayed.
        
        extrapolate:    bool (True)
            If set to 'True' the value is extrapolated in case accessing the table
            outside of ranges. Otherwise, the value is set to 'nan'.
        
        Used to compute laminar flame speed from tabulation.
        """
        #Check arguments:
        laminarFlameSpeedModel.Su(self,p,T,phi,EGR)
        try:
            argv = tabulatedLFS.updateKeywordArguments(argv, self.opts)
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.Su, err)
        
        try:
            #Compute flame speed:
            if (EGR is None) or ("EGR" not in self.varOrder):
                return self.tables["Su"](p,T,phi, Fatal=argv["Fatal"], extrapolate=argv["extrapolate"])[0]
            else:
                return self.tables["Su"](p,T,phi, EGR, Fatal=argv["Fatal"], extrapolate=argv["extrapolate"])[0]
        except:
            self.fatalErrorInClass(self.Su,"Failed computing laminar flame speed", err)
    
    ################################
    #Cumpute laminar flame tickness:
    def deltaL(self,p,T,phi,EGR=None, **argv):
        """
        p:      float
            Pressure [Pa]
        T:      float
            Temperature [K]
        phi:    float
            Equivalence ratio
        EGR:    float
            Level of exhaust gas recirculation [%]
        
        [keyword arguments]
        Fatal:          bool (False)
            If set to 'True', raises a ValueError in case the input data is outside
            of tabulation range. Otherwise a warning is displayed.
        
        extrapolate:    bool (True)
            If set to 'True' the value is extrapolated in case accessing the table
            outside of ranges. Otherwise, the value is set to the one at range limit.
        
        Used to compute laminar flame tickness from tabulation.
        """
        #Check arguments:
        laminarFlameSpeedModel.deltaL(self,p,T,phi,EGR)
        try:
            argv = tabulatedLFS.updateKeywordArguments(argv, self.opts)
            
            if self.tables["deltaL"] is None:
                raise ValueError("Tabulation of laminar flame speed was not loaded.")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.deltaL, err)
        
        try:
            #Compute flame speed:
            if (EGR is None) or ("EGR" not in self.varOrder):
                return self.tables["deltaL"](p,T,phi, Fatal=argv["Fatal"], extrapolate=argv["extrapolate"])[0]
            else:
                return self.tables["deltaL"](p,T,phi, EGR, Fatal=argv["Fatal"], extrapolate=argv["extrapolate"])[0]
        except:
            self.fatalErrorInClass(self.Su,"Failed computing laminar flame thickness", err)
    
#############################################################################
laminarFlameSpeedModel.addToRuntimeSelectionTable(tabulatedLFS)
