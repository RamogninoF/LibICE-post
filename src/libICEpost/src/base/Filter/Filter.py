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

#Import BaseClass class (interface for base classes)
from libICEpost.src.base.BaseClass import BaseClass, abstractmethod

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################

class Filter(BaseClass):
    """
    Class for filtering raw data
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
    """
    
    #########################################################################
    #Properties:
    
    ################################
    
    #########################################################################
    #Class methods and static methods:
    
    #########################################################################
    #Constructor
    
    #########################################################################
    #Dunder methods:
    @abstractmethod
    def __call__(self, x:"list[float]", y:"list[float]") -> "tuple[list[float],list[float]]":
        """
        Filter an array of x,y data. Returns x sampling points and y coordinates
        """
        pass
    
    #########################################################################
    #Methods:
    
#########################################################################
#Create selection table for the class used for run-time selection of type
Filter.createRuntimeSelectionTable()