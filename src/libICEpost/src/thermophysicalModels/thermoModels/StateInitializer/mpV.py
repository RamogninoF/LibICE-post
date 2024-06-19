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
from .StateInitializer import StateInitializer, ThermoState

#Other imports

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class mpV(StateInitializer):
    """
    Initialize from (mass,pressure,volume)
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        mix: ThermoMixture
            Reference to the thermodynamic mixture
    """
    
    _state:ThermoState
    
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
            mix (ThermoMixture): the thermodynamic mixture
            m (float): mass [kg]
            p (float): pressure [Pa]
            V (float): volume [m^3]
        }
        """
        try:
            #Create the dictionary for construction
            Dict = {}
            
            #List of mandatory entries in the dictionary.
            entryList = ["mix", "p", "m", "V"]
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
    def __init__(self, /, *, p:float, m:float, V:float, **kwargv):
        """
        Initialize the thermodunamic state
        
        Args:
            p (float): pressure [Pa]
            m (float): mass [kg]
            V (float): volume [m^3]
        """
        #Argument checking:
        try:
            # Check that the arguments satisfy what is expected from the init method

            #Type checking
            self.checkType(p, float, "p")
            self.checkType(m, float, "m")
            self.checkType(V, float, "V")
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        try:
            #Initialize base class
            super().__init__(**kwargv)

            #Compute the state
            stateDict = \
                {
                    "p":p,
                    "V":V,
                    "m":m
                }
                
            #Compute density:
            stateDict["rho"] = stateDict["m"]/stateDict["V"]
            
            #Compute temperature:
            stateDict["T"] = self.mix.EoS.T(stateDict["p"], stateDict["rho"]) #T(p,rho)
            
            #Construct state:
            self._state = ThermoState(**stateDict)

        except BaseException as err:
            self.fatalErrorInClass(self.__init__, f"Failed construction of {self.__class__.__name__}", err)
    
    #########################################################################
    #Dunder methods:
    
    #########################################################################
    #Methods:

#########################################################################
#Add to selection table of Base
StateInitializer.addToRuntimeSelectionTable(mpV)
