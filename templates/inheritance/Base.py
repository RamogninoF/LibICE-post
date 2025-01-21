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

class Base(BaseClass):
    """
    Template of base class in inheritance tree
    
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
    #This constructor cannot be used in instantiation as a base class is virtual
    #i.e. it cannot be instantiated. But can be called in sub-classes for some
    #initialization or type-checking shared by all sub-classes in the inheritance tree
    def __init__(self, arg1:<type_arg1>=default_val):
        """
        arg1 (<type_arg1>): Description (default: default_val)
        """
        #Argument checking:
        # Check that the arguments satisfy what is expected from the init method

        #Type checking
        self.checkType(arg1, type_arg1, "arg1")
        
        #Initialize the object
        pass
    
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

    #################################
    #Example of abstract method that is required to be defined in child class
    #This will be a common interface that needs to be followed by child classes
    @abstractmethod
    def absMeth1(self, arg:TYPE):
        """
        Arguments and description of the method
        """
        #Used for type-checking only
        # Check that the arguments satisfy what is expected from the method

        #Type checking
        self.checkType(arg, TYPE, "arg")
    
#########################################################################
#Create selection table for the class used for run-time selection of type
Base.createRuntimeSelectionTable()