#####################################################################
#                               IMPORT                              #
#####################################################################

from src.base.Tables.OFtabulation import OFtabulation
from src.thermopysicalModels.laminarFlameSpeed.laminarFlameSpeedModel import laminarFlameSpeedModel

from pylab import exp

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Laminar flame speed computation with Gulder correlation:
class tabulatedLFS(OFtabulation,laminarFlameSpeedModel):
    """
    Class for computation of unstained laminar flame speed from tabulation
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        path:               str
            Path where the tabulation is stored
        
        tableProperties:    dict
            {
                var_ii:   list<float>
                    Contains the list of sampling points for variable 'var_ii'
            }
            Dictionary containing the information retrieved from tableProperties.
        
        varOrder:           list<str>
            Order in which the variables are red convert the scalarLists in tables.
        
        tables:             dict
            {
                'tab_ii':   table
            }
            Contains the tabulations.
        
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
    
    #Name:
    typeName = "tabulatedLFS"
    
    #########################################################################
    #Constructor:
    def __init__(self, tablePath, noWrite=True, **argv):
        """
        Constructors:
            tabulatedLFS(tablePath, noWrite, **argv):
                tablePath:      str
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
                
                Create the tabulation, loading the data located at 'tablePath' path.
            """
        argv["loadLaminarFlameTickness"] = tabulatedLFS.lookupOrDefault(argv, "loadLaminarFlameTickness", True)
        
        OFtabulation.__init__(self, tablePath, noWrite, **argv)
        
        variables = \
        {
            "pValues":"p",
            "tValues":"T",
            "eqvrValues":"phi"
        }
    
        order = ["p", "T", "phi"]
    
        #Check if table contains EGR:
        if "eqvrValues" in self.tableProperties:
            variables["EGRValues"] = "EGR"
            order.append("EGR")
        
        self.readTableProperties(variables)
        
        OFtabulation.setOrder(self, order)
        OFtabulation.readTable(self, "laminarFlameSpeedTable", "Su")
        
        if argv["loadLaminarFlameTickness"]:
            OFtabulation.readTable(self, "deltaLTable", "deltaL")
    
    #########################################################################
    #Disabling function
    def setCoeffs(self, *args, **argv):
        import inspect
        raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, inspect.stack()[0][3]))
    
    #Disabling function
    def setOrder(self, *args, **argv):
        import inspect
        raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, inspect.stack()[0][3]))
    
    #Disabling function
    def readTable(self, *args, **argv):
        import inspect
        raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, inspect.stack()[0][3]))
    
    #########################################################################
    
    #Get SuTable:
    def SuTable(self):
        """
        Returns a copy of the tabulation of laminar flame speed
        """
        
        return tabulatedLFS.cp.deepcopy(self.tables["Su"])
    
    #Get deltaLTable:
    def deltaLTable(self):
        """
        Returns a copy of the tabulation of laminar flame tickness
        """
        
        return tabulatedLFS.cp.deepcopy(self.tables["deltaL"])
    
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
        
        argv = tabulatedLFS.dictFromTemplate(argv, self.opts)
        
        #Compute flame speed:
        if (EGR is None) or ("EGR" not in self.varOrder):
            return self.tables["Su"](p,T,phi, Fatal=argv["Fatal"], extrapolate=argv["extrapolate"])[0]
        else:
            return self.tables["Su"](p,T,phi, EGR, Fatal=argv["Fatal"], extrapolate=argv["extrapolate"])[0]
    
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
        laminarFlameSpeedModel.Su(self,p,T,phi,EGR)
        
        argv = tabulatedLFS.dictFromTemplate(argv, self.opts)
        
        if not "deltaL" in self.tables:
            raise ValueError("Trying to axcess to laminar flame tickness tabulation while it was not loaded.")
        
        #Compute flame thickness:
        if (EGR is None) or ("EGR" not in self.varOrder):
            return self.tables["deltaL"](p,T,phi, Fatal=argv["Fatal"], extrapolate=argv["extrapolate"])[0]
        else:
            return self.tables["deltaL"](p,T,phi, EGR, Fatal=argv["Fatal"], extrapolate=argv["extrapolate"])[0]
    
