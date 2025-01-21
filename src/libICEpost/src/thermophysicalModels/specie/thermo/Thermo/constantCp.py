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

from .Thermo import Thermo

from libICEpost import Dictionary
import json
from libICEpost.Database.chemistry import constants
from libICEpost.Database import database

Tstd = database.chemistry.constants.Tstd

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class constantCp(Thermo):
    """
    Class for computation of thermophysical properties with constant cp.
    
    Attibutes:
        - Rgas (float): The mass specific gas constant
        
    """
    
    #########################################################################
    @classmethod
    def fromDictionary(cls,dictionary):
        """
        Construct from dictionary containing the following keys:
        - Rgas (float): The mass specific gas constant
        - cp (float): Constant pressure heat capacity [J/kg/K]
        - hf (float): Enthalpy of formation [J/kg] (Optional)
        
        Args:
            dictionary (dict): The dictionary containing the data
        """
        dictionary = Dictionary(**dictionary)
        #Here check only the presence of the keys, argument checking is done in the constructor
        return cls(
            dictionary.lookup("Rgas"),
            dictionary.lookup("cp"),
            dictionary.lookupOrDefault("hf", float('nan'))
            )
    
    #########################################################################
    #Constructor:
    def __init__(self, Rgas, cp, hf=float('nan')):
        """
        Construct from the mass specific gas constant and the normalized constant cp.
        
        Args:
            Rgas (float): The mass specific gas constant
            cp (float): Constant pressure heat capacity [J/kg/K]
            hf (float): Enthalpy of formation [J/kg] (Optional)
        """
        #Argument checking:
        super().__init__(Rgas)
        self.checkType(cp, float, entryName="cp")
        self.checkType(hf, float, entryName="hf")
        
        self._cp = cp
        self._hf = hf
        
    #########################################################################
    #Operators:
    
    ################################
    #Print:
    def __str__(self):
        StrToPrint = Thermo.__str__(self)
        StrToPrint += "\n"
        StrToPrint += f"cp = {self._cp} [J/kgK]\n"
        StrToPrint += f"hf = {self._hf} [J/kg]\n"
        
        return StrToPrint
    
    ##############################
    #Representation:
    def __repr__(self):
        R = {}
        R["Rgas"] = self.Rgas
        R["cp"]   = self._cp 
        R["hf"]  = self._hf
                       
        return f"{self.TypeName}{R.__repr__()}"
    
    #########################################################################
    #Member functions:
    
    ################################
    def cp(self, p:float, T:float) -> float:
        """
        Constant pressure heat capacity [J/kg/K]
        """
        #Argument checking
        super().cp(p,T)
        return self._cp
    
    ################################
    def ha(self, p:float, T:float) -> float:
        """
        Absolute enthalpy [J/kg]
                
        ha(T) = cp * (T - Tstd) + hf
        """
        #Check argument types
        try:
            super().ha(p,T)
        except NotImplementedError:
            #Passed the check of p and T
            pass
            
        return self._cp * (T - Tstd) + self._hf
    
    ##################################
    def hf(self) -> float:
        """
        Enthalpy of formation [J/kg]
        
        hf = ha(Tstd)
        """
        return self.ha(0.,Tstd)
    
    ################################
    def dcpdT(self, p:float, T:float) -> float:
        """
        dcp/dT [J/kg/K^2]
        """
        super().dcpdT(p,T)
        
        return 0.0
    
#############################################################################
Thermo.addToRuntimeSelectionTable(constantCp)

#############################################################################
#Load database:
import libICEpost.Database.chemistry.thermo.Thermo.constantCp
