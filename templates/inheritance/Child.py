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
from .Base import Base

#Other imports

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class Child(Base):
    """
    Sample of child class
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        attr1:  <type>
            Description
    """
    
    #########################################################################
    #Properties:

    #########################################################################
    #Class methods and static methods:
    
    #Child classes need to have definition of the method fromDictionary, which is
    #used by the selector to construct the specific class. This is an interface to
    #the __init__ method of the specific class.
    @classmethod
    def fromDictionary(cls, dictionary):
        """
        Create from dictionary.

        {
            arg1 (<type_arg1>): Description (default: default_val1)
            arg2 (<type_arg2>): Description
        }
        """
        try:
            #Create the dictionary for construction
            Dict = {}
            
            #List of mandatory entries in the dictionary. Here only arg2 as it does not
            #have a default value
            entryList = ["arg2"]
            for entry in entryList:
                if not entry in dictionary:
                    raise ValueError(f"Mandatory entry '{entry}' not found in dictionary.")
                #Set the entry
                Dict[entry] = dictionary[entry]
            
            #Constructing this class with the specific entries
            out = cls\
                (
                    **Dict
                )
            return out
        
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed construction from dictionary", err)
    
    #########################################################################
    def __init__(self, arg2:<type_arg2>, arg1:<type_arg1>=default_val1):
        """
        arg2 (<type_arg2>): Description
        arg1 (<type_arg1>): Description (default: default_val1)
        """
        #Argument checking:
        try:
            # Check that the arguments satisfy what is expected from the init method

            #Type checking
            self.checkType(arg2, type_arg2, "arg2")

            #Here I only check for arg2 as arg1 is already handled bu the __init__ of class Base
            
            #...
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        try:
            #Initialize the object
            #Here might be convenient to call the __init__ method of the base
            #class to initialize arg1 which is shared with the base class Base.
            #To do so i use the function super()

            super().__init__(arg1)

            #Other stuff to initialize specific of Child


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
    
    #################################
    #Example of definition of the abstract method defined in Base
    @abstractmethod
    def absMeth1(self, arg:TYPE):
        """
        Arguments and description of the method
        """
        #Argument checking in base:
        super()self.absMeth1(arg)

        #Do stuff...

#########################################################################
#Add to selection table of Base
Base.addToRuntimeSelectionTable(Child)
