#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: <N. Surname>       <e-mail>
Last update:        DD/MM/YYYY
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

#load the base class
from .Filter import Filter

#Other imports
from types import FunctionType

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class UserDefinedFilter(Filter):
    """
    User defined filter from body of "__call__(x,y)" method
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
    """
    
    #########################################################################
    #Properties:
    @property
    def code(self):
        """
        the code of the __call__(x,y) method

        Returns:
            str
        """
        return self._code
    
    #########################################################################
    #Class methods and static methods:
    @classmethod
    def fromDictionary(cls, dictionary):
        """
        Create from dictionary.

        {
            code (str): the code of the __call__(x,y) method
        }
        """
        #Create the dictionary for construction
        Dict = {}
        
        entryList = ["function"]
        for entry in entryList:
            if not entry in dictionary:
                raise ValueError(f"Mandatory entry '{entry}' not found in dictionary.")
            #Set the entry
            Dict[entry] = dictionary[entry]
        
        #Constructing this class with the specific entries
        out = cls(**Dict)
        return out
    
    #########################################################################
    def __init__(self, function:FunctionType):
        """
        function (FunctionType): the filtering function f(x,y)->(xp,yp)
        
        Construct user-defined filter giving the __call__(x,y) method to 
        filter the (x,y) data, returning the filtered (xp,yp) data
        """
        #Argument checking:
        #Type checking
        self.checkType(function, FunctionType, "function")
        self.__call__ = function
    
    #########################################################################
    #Dunder methods:
    def __call__(self, x:"list[float]", y:"list[float]")-> "tuple[list[float],list[float]]":
        """
        Filter a set of (x,y) data executing the user-defined code
        """
        return self.__call__(x,y)
    
    ###################################
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
    
    #########################################################################
    #Methods:
    

#########################################################################
#Add to selection table of Base
Filter.addToRuntimeSelectionTable(UserDefinedFilter)
