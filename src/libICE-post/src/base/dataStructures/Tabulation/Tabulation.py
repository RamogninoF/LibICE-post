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

from src.base.Utilities import Utilities
from scipy.interpolate import RegularGridInterpolator

import matplotlib as mpl
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Class used for storing and handling a generic tabulation:
class Tabulation(Utilities):
    """
    Class used for storing and handling a generic tabulation.
    """
    #########################################################################
    #Data:
    defaultOpts = \
            {
                "Fatal":False,
                "extrapolate":True
            }
    
    #Plotting:
    mpl = mpl
    plt = plt
    
    #########################################################################
    #Constructor:
    def __init__(self, data, ranges, order, **argv):
        """
        data:       list<float> or numpy.ndarray
            Data structure containing the interpulation values at sampling points
            of the tabulation.
            If list<float> is given, data are stored as a list by recursively
            looping over the ranges stored in 'ranges', following variable
            hierarchy set in 'order'.
            If numpy.ndarray is given, data are stored as a n-dimensional array with
            consistent shape with 'ranges'.
        ranges:             dict
            {
                var1:   list<float>
                var2:   list<float>
                ...
                varn:   list<float>
            }
            Sampling points used in the tabulation for each input variable.
        order:              list<str>
            Order used to store the tabulation.
            
        [keyword arguments]
        Fatal:          bool (False)
            If set to 'True', raises a ValueError in case the input data is outside
            of tabulation range. Otherwise a warning is displayed.
        
        extrapolate:    bool (True)
            If set to 'True' the value is extrapolated in case accessing the table
            outside of ranges. Otherwise, the value is set to 'nan'.
        
        Creates a tabulation from the data stored in 'data'.
        """
        #Argument checking:
        try:
            Utilities.checkTypes(data,[list,Utilities.np.ndarray],entryName="data")
            Utilities.checkInstanceTemplate(ranges,{"A":[1.0]},entryName="ranges")
            Utilities.checkInstanceTemplate(order,[""],entryName="order")
            
            if not(len(ranges) == len(order)):
                raise ValueError("Length missmatch. Keys of 'ranges' must be the same of the elements of 'order'.")
            
            for key in ranges:
                if not(key in order):
                    raise ValueError("key '{}' not found in entry 'order'. Keys of 'ranges' must be the same of the elements of 'order'.")
            
            if isinstance(data,list):
                if not(len(data) == Utilities.np.prod([len(ranges[r]) for r in ranges])):
                    raise ValueError("Size of 'data' is not consistent with the data-set given in 'ranges'.")
            else:
                if not(data.size == Utilities.np.prod([len(ranges[r]) for r in ranges])):
                    raise ValueError("Size of 'data' is not consistent with the data-set given in 'ranges'.")
                
                if not(data.shape == tuple([len(ranges[o]) for o in order])):
                    raise ValueError("Shape of 'data' is not consistent with the data-set given in 'ranges'.")
            
            #Options:
            self.opts = Utilities.updateKeywordArguments(argv, self.defaultOpts)
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        #Casting ints to floats:
        for r in ranges:
            for i, x in enumerate(ranges[r]):
                ranges[r][i] = float(x)
        
        #Ranges and order:
        self.ranges_ = ranges
        self.fields_ = order
        
        #If given list:
        if isinstance(data,list):
            #List of indexes to populate the table:
            indexList = self.__IndexList(self.shape())
            
            #Populate the table:
            self.data_ = Utilities.np.ndarray(tuple(self.shape()))
            for ii in range(self.size()):
                self.data_.itemset(tuple(indexList[ii]),data[ii])
            
        #If given ndarray:
        else:
            self.data_ = Utilities.cp.deepcopy(data)
        
        #Reorder data and interpolator:
        self.__dataOld = None
        self.update()
    
    #########################################################################
    #Private member functions:
    
    #Create interpolator:
    def __createInterpolator(self):
        if (self.data_ != self.__dataOld).any():
            #Create grid:
            ranges = []
            for f in self.fields():
                #Check for dimension:
                range_ii = self.ranges()[f] 
                if len(range_ii) > 1:
                    ranges.append(range_ii)
            
            tab = self.data().squeeze()
            
            #Extrapolation method:
            if self.opts["extrapolate"]:
                fill_value = None
            else:
                fill_value = float('nan')
            
            self.interpolator_ = RegularGridInterpolator(tuple(ranges), tab, bounds_error=self.opts["Fatal"], fill_value=fill_value)
            
            self.__dataOld = self.data_
            
        return self
    
    #######################################
    
    #Reorder data with ascending order:
    def __reorderData(self):
        
        newTab = self.data()
        numDims = len(newTab.shape)
        newRanges = self.ranges()
        
        ID = [0] * numDims
        for dim in range(numDims):
            fieldName = self.fields()[dim]
            
            #Check if needed reordering along dimension:
            if newRanges[fieldName] != sorted(newRanges[fieldName]):
                
                order = Utilities.np.argsort(newRanges[fieldName])
                newRanges[fieldName] = sorted(newRanges[fieldName])
                
                newTab = Utilities.np.take(newTab, order, axis=dim)
        
        self.data_ = newTab
        self.ranges_ = newRanges
        
        return self
    
    #######################################
    
    #List of indexes to populate the table:
    def __IndexList(self, shape):
        size = 1
        for dim in shape:
            size *= dim
        
        indexList = []
        counterList = [0]*len(shape)
        
        indexList.append(Utilities.cp.copy(counterList))
        for ii in range(1,size):
            #Incremento:
            counterList[-1] += 1
            #Controllo i riporti:
            for jj in range(len(counterList)-1,-1,-1):  #Reversed order
                if counterList[jj] == shape[jj]:  #Riporto
                    counterList[jj] = 0
                    counterList[jj-1] += 1
            #Aggiungo a lista:
            indexList.append(Utilities.cp.copy(counterList))
        
        return indexList
    
    #########################################################################
    
    #Interpolation:
    def __call__(self, *args, **argv):
        """
        args:   float
        
        [keyword arguments]
        Fatal:          bool
            If set to 'True', raises a ValueError in case the input data is outside
            of tabulation range. Otherwise a warning is displayed.
        
        extrapolate:    bool
            If set to 'True' the value is extrapolated in case accessing the table
            outside of ranges. Otherwise, the value is set to 'nan'.
        
        Multi-linear interpolation from the tabulation. The number of arguments to be given
        must be the same of the dimensions of the table.
        """
        
        #Argument checking:
        try:
            Utilities.checkInstanceTemplate(args, (1.0,), entryName="*args")
            if len(args) != self.ndim():
                raise ValueError("Number of entries not consistent with number of dimensions stored in the tabulation ({} expected, while {} found).".format(self.ndim(), len(args)))
            
            argv = Utilities.updateKeywordArguments(argv, self.opts)
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__call__, err)
        
        entries = []
        for ii, f in enumerate(self.fields()):
            #Check for dimension:
            if len(self.ranges()[f]) > 1:
                entries.append(args[ii])
            else:
                self.__class__.runtimeWarning("Field '{}' with only one data-point, cannot interpolate along that dimension. Entry for that field will be ignored.".format(f))
        
        returnValue = None
        if len(argv):
            returnValue = self.copy().setOpts(**argv).interpolator()(entries)
        else:
            returnValue = self.interpolator()(entries)
        
        if len(returnValue) == 1:
            return returnValue[0]
        else:
            return returnValue
    
    #######################################
    
    #__getitem__(slices):
    def __getitem__(self, slices):
        """
        slices:   tuple<slice/list<int>/int>
        
        Extract a table with sliced dataset.
        """
        #Argument checking:
        try:
            if not(len(slices) == len(self.fields())):
                raise IndexError("Given {} ranges, while table has {} fields ({}).".format(len(slices), len(self.fields()), self.fields()))
            
            newSlices = []
            for ii in range(len(self.fields())):
                ss = slices[ii]
                indList = range(len(self.ranges()[self.fields()[ii]]))
                
                if isinstance(ss, slice):
                    newSlices.append(indList[ss])
                    
                elif isinstance(ss,int):
                    if not(ss in indList):
                        raise IndexError("Index out of range for field '{}'.".format(self.fields()[ii]))
                    newSlices.append([ss])
                
                elif isinstance(ss,list):
                    for ind in ss:
                        if not(ind in indList):
                            raise IndexError("Index out of range for field '{}'.".format(self.fields()[ii]))
                    
                    newSlices.append(ss)
                    
                else:
                    raise TypeError("Type missmatch. Attempting to slice with entry of type '{}'.".format(ss.__class__.__name__))
                
        except BaseException as err:
            self.fatalErrorInClass(self.__getitem__, "Slicing error", err)
        
        #Create ranges:
        order = self.fields()
        ranges =  {}
        for ii,  Slice in enumerate(newSlices):
            ranges[order[ii]] = [self.ranges()[order[ii]][ss] for ss in Slice]
        
        #Create slicing table:
        slTab = Utilities.np.ix_(*tuple(newSlices))
        data = Utilities.cp.deepcopy(self.data()[slTab])
        
        return self.__init__(data, ranges, order).setOpts(self.opts)
    
    
    #######################################
    def __setitem__(self, slices, items):
        """
        slices:   tuple<slice/list<int>/int>
        items:    float / np.ndarray<float/int>
        
        Set the interpolation values at a slice of the table
        """
        #Argument checking:
        try:
            self.checkTypes(items, [self.np.ndarray, float], "items")
            
            if not(len(slices) == len(self.fields())):
                raise IndexError("Given {} ranges, while table has {} fields ({}).".format(len(slices), len(self.fields()), self.fields()))
            
            indTable = []
            for ii in range(len(self.fields())):
                ss = slices[ii]
                indList = range(len(self.ranges()[self.fields()[ii]]))
                
                if isinstance(ss, slice):
                    try:
                        indTable.append(indList[ss])
                    except BaseException as err:
                        raise IndexError(f"Slice '{ss}' out of range for field '{self.fields()[ii]}'.")
                    
                elif isinstance(ss,int):
                    if not(ss in indList):
                        raise IndexError("Index out of range for field '{}'.".format(self.fields()[ii]))
                    indTable.append([ss])
                
                elif isinstance(ss,list):
                    for ind in ss:
                        if not(ind in indList):
                            raise IndexError("Index out of range for field '{}'.".format(self.fields()[ii]))
                    
                    indTable.append(ss)
                    
                else:
                    raise TypeError("Type missmatch. Attempting to slice with entry of type '{}'.".format(ss.__class__.__name__))
                
        except BaseException as err:
            self.fatalErrorInClass(self.__getitem__, "Slicing error", err)
        
        #Set values:
        try:
            slTab = Utilities.np.ix_(*tuple(newSlices))
            self.data()[slTab] = items
        except BaseException as err:
            self.fatalErrorInClass("Failed setting items in Tabulation", err)
        
        self.update()
    
    #########################################################################
    #Access functions:
    
    #Get ranges:
    def ranges(self):
        """
        Get a dict containing the data ranges in the tabulation (unmutable).
        """
        return Utilities.cp.deepcopy(self.ranges_)
    
    #######################################
    
    #Get fields:
    def fields(self):
        """
        Returnts a list with the fields used for accessing to the tabulation (in order)
        """
        return Utilities.cp.deepcopy(self.fields_)
    
    #######################################
    
    #Get data:
    def data(self):
        """
        Returns a copy of the stored data structure
        """
        return Utilities.cp.deepcopy(self.data_)
    
    #######################################
    
    #Get interpolator:
    def interpolator(self):
        """
        Returns a copy of the stored data structure
        """
        self.__createInterpolator()
        return self.interpolator_
    
    #######################################
    
    #Get dimensions:
    def ndim(self):
        """
        ndim():
            Returns the number of dimentsions of the table (int)
        """
        return len(self.ranges())
    
    #######################################
    
    #Get list of dimensions:
    def shape(self):
        """
        Returns a list with the dimentsions of the table
        """
        return tuple([len(self.ranges()[o]) for o in self.fields()])
    
    #######################################
    
    #Get dimensions:
    def size(self):
        """
        Returns the number of data-points stored in the table (int)
        """
        return Utilities.np.prod([len(self.ranges()[r]) for r in self.ranges()])
    
    #########################################################################
    #Public member functions:
    def update(self):
        """
        Update interpolator.
        """
        #Reorder data:
        self.__reorderData()
        
        #Create the interpolator:
        self.__createInterpolator()
    
    #######################################
    
    #Set opts:
    def setOpts(self, **argv):
        """
        [keyword arguments]
        Fatal:          bool
            If set to 'True', raises a ValueError in case the input data is outside
            of tabulation range. Otherwise a warning is displayed.
        
        extrapolate:    bool
            If set to 'True' the value is extrapolated in case accessing the table
            outside of ranges. Otherwise, the value is set to the one at range limit.
                
        Set the options in 'opts' dictionary, either by giving dictionary or keyword
        arguments.
        """
        self.opts = Utilities.updateKeywordArguments(argv, self.opts)
        self.update()
        
        return self
    
    #######################################
    
    #Squeeze 0/1 len dimension:
    def squeeze(self):
        """
        Remove dimensions with only 1 data-point.
        """
        dimsToKeep = []
        for ii, dim in enumerate(self.shape()):
            if dim > 1:
                dimsToKeep.append(ii)
        
        self.fields_ = map(self.fields().__getitem__, dimsToKeep)
        self.ranges_ = {self.fields_[ii]:Range for ii, Range in enumerate(map(self.ranges().__getitem__, self.fields()))}
        self.data_ = self.data().squeeze()
        
        self.update()
        
        return self
    
    #######################################
    
    #Slice:
    def Slice(self, ranges={}, **argv):
        """
        ranges:   dict
        
        Extract a table with sliced datase, according to the sub-set of interpolation 
        points given in 'ranges'. Keyworld arguments also accepred.
        """
        #Check arguments:
        Utilities.checkType(ranges, dict, entryName="ranges")
        
        ranges = ranges.update(argv)
        ranges = Utilities.dictFromTemplate(ranges, self.ranges())
        
        for rr in ranges:
            for ii in ranges[rr]:
                if not(ii in self.ranges()[rr]):
                    raise ValueError("Sampling value '{}' not found in range for field '{}'.".format(ii,rr))
        
        order = self.fields()
        
        #Create slices:
        slices = []
        for ii, item in enumerate(order):
            slices.append([self.ranges()[item].index(vv) for vv in ranges[item]])
        
        return self.__getitem__(tuple(slices))
    
    #######################################
    
    #Merge with other table:
    def mergeTable(self, fieldName, secondTable):
        """
        fieldName:  str
            Field to use to append second table
            
        secondTable: table
            Tabulation containing the data to introduce
        
        Introduce additional data to the tabulation.
        """
        try:
            #Argument checking:
            Utilities.checkType(fieldName, str, entryName="fieldName")
            Utilities.checkType(secondTable, self.__class__, entryName="secondTable")
            
            if not fieldName in self.fields():
                raise ValueError("Field '{}' not found in table.".format(fieldName))
            
            if not fieldName in secondTable.fields():
                raise ValueError("Field '{}' not found in 'secondTable'.".format(fieldName))
            
            if self.fields() != secondTable.fields():
                raise ValueError("Table fields not compatible.\nTable fields:\n{}\nFields of table to append:\n{}".format(secondTable.fields(), self.fields()))
            
            #Check if fields already present:
            for item in secondTable.ranges()[fieldName]:
                if item in self.ranges()[fieldName]:
                    raise ValueError("Value '{}' already present in range of field '{}'.".format(item, self.ranges()[fieldName]))
            
            #Check compatibility:
            otherFields = [f for f in self.fields() if f != fieldName]
            otherRanges = {f:self.ranges()[f] for f in otherFields}
            otherRangesSecond = {f:secondTable.ranges()[f] for f in otherFields}
            if otherRanges != otherRangesSecond:
                raise ValueError("Table ranges of other fields not compatible.\nTable ranges:\n{}\Ranges of table to append:\n{}".format(otherRanges, otherRangesSecond))
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.mergeTable, err)
        
        #Append data:
        fieldIndex = self.fields().index(fieldName)
        self.ranges_[fieldName] += secondTable.ranges()[fieldName]
        self.data_ = self.np.append(self.data(), secondTable.data(), axis=fieldIndex)
        
        #Update:
        self.update()
        
        return self
    
    #########################################################################
    #Plot:
    def plot(self, xVar, yVar, isoSurf=None, **argv):
        """
        xVar:   str
            Name of the field on x-axis
            
        yVar:   str
            Name of the field on the y-axis
            
        isoSurf:    list<dict>
            List of dictionaries used to sort which iso-surfaces to plot. Each
            element of the list must be a dictionary containing a value for
            each remaining field of the tabulation.
            It can be optional in case there are three fields in the tabulation,
            it will contain each element of the third field. Otherwise it is
            mandatory.
            
            Exaple:
            [
                {
                    var_ii:value1.1
                    var_jj:value2.1
                    ...
                }
                {
                    var_ii:value1.2
                    var_jj:value2.2
                    ...
                }
                ...
            ]
        
        [keyworld arguments]
        xRange: list<float>
            Sampling points of the x-axis field (if want a subset)
        
        yRange: list<float>
            Sampling points of the y-axis field (if want a subset)
        
        Display the sampling points in the tabulation as iso-surfaces and
        returns a tuple with handles to figure and axes.
        """
        try:
            #Argument checking:
            Utilities.checkType(xVar, str, entryName="xVar")
            Utilities.checkType(yVar, str, entryName="yVar")
            if not(isoSurf is None):
                if len(isoSurf) == 0:
                    raise ValueError("dict entry 'isoSurf' is empty, cannot generate the iso-surface plot.")
                
                Utilities.checkInstanceTemplate(isoSurf, [{"A":1.0}], entryName="isoSurf")
            
            f = ""
            for F in self.fields():
                f += "\t" + F + "\n"
            if not(xVar in self.fields()):
                raise ValueError("Entry {} (xVar) not found among table fields. Available fields are:\n{}".format(f))
            
            if not(yVar in self.fields()):
                raise ValueError("Entry {} (yVar) not found among table fields. Available fields are:\n{}".format(f))
            
            defaultArgv = \
            {
                "xRange":   self.ranges()[xVar],
                "yRange":   self.ranges()[yVar]
            }
            
            argv = Utilities.updateKeywordArguments(argv, defaultArgv)
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.plot, err)
        
        #Ranges
        xRange = argv["xRange"]
        yRange = argv["yRange"]
        
        #Create figure:
        fig = plt.figure()
        ax = Axes3D(fig)
        X, Y = Utilities.np.meshgrid(xRange, yRange)
        
        try:
            if isoSurf is None:
                otherVar = None
                for var in self.fields():
                    if not ((var == xVar) or (var == yVar)):
                        #if not (otherVar is None):
                            #raise ValueError("Cannot plot iso-surfaces of table with more then 3 variables stored. Must give the data to plot through 'isoSurf' argument, as a list of dicts determining the iso values of the remaining variables:\n\n[\{var_ii:value1.1, var_jj:value2.1,...\}, {var_ii:value1.2, var_jj:value2.2,...\}, ...]")
                        if (otherVar is None):
                            otherVar = [var]
                        else:
                            otherVar.append(var)
                
                if otherVar is None:
                    Z = self.cp.deepcopy(X)
                    
                    for ii in range(X.shape[0]):
                        for jj in range(X.shape[1]):
                            
                            values = {xVar:X[ii][jj], yVar:Y[ii][jj]}
                            
                            #Sort in correct order
                            arguments = []
                            for field in self.fields():
                                if field in values:
                                    arguments.append(values[field])
                            arguments = tuple(arguments)
                            
                            Z[ii][jj] = self(*arguments)
                        
                    surf = ax.plot_surface(X, Y, Z)
                    surf._facecolors2d=surf._facecolors
                    surf._edgecolors2d=surf._edgecolors
                    
                    isoSurf = []
                    
                else:
                    isoSurf = []
                    varIDs = [0]*len(otherVar)
                    while(True):
                        #Append surface
                        isoSurf.append({})
                        for ii, var in enumerate(otherVar):
                            isoSurf[-1][var] = self.ranges()[var][varIDs[ii]]
                        
                        #Increase counter
                        for ii,var in enumerate(otherVar):
                            jj = len(varIDs)-ii-1
                            
                            if ii == 0:
                                varIDs[jj] += 1
                            
                            varIDs[jj], rem = (varIDs[jj]%len(self.ranges()[otherVar[jj]])), (varIDs[jj]//len(self.ranges()[otherVar[jj]]))
                            if jj > 0:
                                varIDs[jj-1] += rem
                        
                        #Check if looped the counter
                        if all([ID == 0 for ID in varIDs]):
                            break
                
            for isoDict in isoSurf:
                if not isinstance(isoDict, dict):
                    raise TypeError("'isoSurf' entry must be in the form:\n\n[\{var_ii:value1.1, var_jj:value2.1\}, {var_ii:value1.2, var_jj:value2.2\}, ...] \n\n where [var_ii, var_jj,...] are all the remaining dimensions of the tabulation, while valueXX.YY must be float or int.")
                elif  not isoDict:
                    raise ValueError("Empty entry in list 'isoSurf'. 'isoSurf' entry must be in the form:\n\n[\{var_ii:value1.1, var_jj:value2.1,...\}, {var_ii:value1.2, var_jj:value2.2,...\}, ...] \n\n where [var_ii, var_jj,...] are all the remaining dimensions of the tabulation.")
                elif not (len(isoDict) == (len(self.fields()) - 2)):
                    raise ValueError("Empty entry in list 'isoSurf'. 'isoSurf' entry must be in the form:\n\n[\{var_ii:value1.1, var_jj:value2.1,...\}, {var_ii:value1.2, var_jj:value2.2,...\}, ...] \n\n where [var_ii, var_jj,...] are all the remaining dimensions of the tabulation, while valueXX.YY must be float or int.")
                
                for key in isoDict:
                    if not(key in self.fields()):
                        raise ValueError("Key '{}' in element of entry 'isoSurf' not found among table fields. 'isoSurf' entry must be in the form:\n\n[\{var_ii:value1.1, var_jj:value2.1,...\}, {var_ii:value1.2, var_jj:value2.2,...\}, ...] \n\n where [var_ii, var_jj,...] are all the remaining dimensions of the tabulation, while valueXX.YY must be float or int.".format(key))
                    elif not(isinstance(isoDict[key], (int,float))):
                        raise TypeError("Wrong type, expected float or int, {} found. 'isoSurf' entry must be in the form:\n\n[\{var_ii:value1.1, var_jj:value2.1,...\}, {var_ii:value1.2, var_jj:value2.2,...\}, ...] \n\n where [var_ii, var_jj,...] are all the remaining dimensions of the tabulation, while valueXX.YY must be float or int.".format(isoDict[key].__class__.__name__))
                
                Z = Utilities.cp.deepcopy(X)
                for ii in range(X.shape[0]):
                    for jj in range(X.shape[1]):
                        
                        values = {xVar:X[ii][jj], yVar:Y[ii][jj]}
                        
                        label = ""
                        for key in isoDict:
                            if label:
                                label += " - "
                            label += "{}: {}".format(key,isoDict[key])
                            
                            values[key] = isoDict[key]
                            
                        #Sort in correct order
                        arguments = []
                        for field in self.fields():
                            if field in values:
                                arguments.append(values[field])
                        arguments = tuple(arguments)
                        
                        Z[ii][jj] = self(*arguments)
                
                surf = ax.plot_surface(X, Y, Z, label=label)
                surf._facecolors2d=surf._facecolors
                surf._edgecolors2d=surf._edgecolors
                
            ax.legend()
            plt.xlabel(xVar)
            plt.ylabel(yVar)
        
        except BaseException as err:
            self.fatalErrorInClass(self.plot, "Failed plotting tabulation", err)
        
        return fig, ax
