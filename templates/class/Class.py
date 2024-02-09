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

#Import Utilites class (interface with some convenient functions in this package)
from libICEpost.src.base.Utilites import Utilites

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################

class Class(Utilites):
    """
    Template of class
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        attr1:  <type>
            Description
    """
    
    #########################################################################
    #Properties:
    @property
    def prop1(self):
        """
        Description of the property
        """
        #getter of the property
        pass
    
    ################################
    
    #########################################################################
    #Class methods and static methods:
    @classmethod
    def cm1(cls):
        """
        Description of the class method
        """
        pass
    
    ################################
    @staticmethod
    def sm1(arg):
        """
        Description of the class method
        """
        pass
    
    #########################################################################
    #Constructor
    def __init__(self, arg1:<type_arg1>=default_val):
        """
        arg1 (<type_arg1>): Description (default: default_val)
        """
        #Argument checking:
        try:
            # Check that the arguments satisfy what is expected from the init method

            #Type checking
            self.checkType(arg1, type_arg1, "arg1")
            
            #...
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        try:
            #Initialize the object
            pass
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, "Failed construction of ...", err)
    
    #########################################################################
    #Dunder methods:
    def __repr__(self):
        """
        The representation of the class
        """
        #The representation ...
        pass
    
    #########################################################################
    #Methods:
    def method1(self):
        """
        Arguments and description of the method
        """
        ...
    
#############################################################################
#                               FRIENT METHODS                              #
#############################################################################
#Functions that interact with this class
