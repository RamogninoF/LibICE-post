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

import json
from libICEpost.Database.chemistry import constants
from libICEpost.Database import database


Tstd = database.chemistry.constants.Tstd

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class constantCp(Thermo):
    """
    Class for computation of thermophysical properties with constant cp cv and gamma.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        Rgas: float
            The mass specific gas constant
        
    """
    
    #########################################################################
    @classmethod
    def fromDictionary(cls,dictionary):
        """
        Create from dictionary:
        {
            Rgas:  float
                Mass specific gas constant
            
            cp:    float (None)
                Mass-specific constant-pressure heat capacity
            
            cv:    float (None)
                Mass-specific constant-volume heat capacity

            gamma: float (None)
                cp/cv ratio
            
            hf:    float (0.0)
                Enthalpy of formation (optional)
        }

        Give 1 out of three of (cp, cv, gamma)
        """
        entryList = ["cp", "cv", "gamma", "hf"]
        Dic = {}
        for entry in entryList:
            if entry in dictionary:
                Dic[entry] = dictionary[entry]
        
        if not "Rgas" in dictionary:
            raise ValueError(f"Mandatory entry 'Rgas' not found in dictionary.")
        
        out = cls(dictionary["Rgas"], **Dic)
        return out
    
    #########################################################################
    #Constructor:
    def __init__(self, Rgas, cp, hf=float('nan')):
        """
        Rgas: float
            The mass specific gas constant
        cp:     float (None)
            Constant pressure heat capacity [J/kgK]
            
        hf:     float (0.0)
            Enthalpy of formation (Optional)
            
        Construct from one of the above data. Give 1 out of three of (cp, cv, gamma)
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
        R = eval(super(self.__class__,self).__repr__())
        R["cp"]   = self._cp 
        R["hf"]  = self._hf
                       
        return R.__repr__()
    
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
