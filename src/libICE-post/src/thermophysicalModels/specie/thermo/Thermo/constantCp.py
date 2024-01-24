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

from src.base.Functions.runtimeWarning import runtimeWarning

from .Thermo import Thermo

import json
import Database
from Database import database
from numpy import math

Tstd = database["constants"]["Tstd"]

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class constantCp(Thermo):
    """
    Class for computation of thermophysical properties with constant cp cv and gamma.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        specie: Molecule
            Chemical specie for which the thermodynamic properties are defined
        
    """
    
    #########################################################################
    
    numCoeffs = 7
    
    #########################################################################
    #Constructor:
    def __init__(self, specie, cp=None, cv=None, gamma=None, hf=0.0):
        """
        cp:     float (None)
            Constant pressure heat capacity [J/kgK]
        cv:     float (None)
            Constant volume heat capacity [J/kgK]
        gamma:  float (None)
            cp/cv ratio [-]
            
        hf:     float (0.0)
            Enthalpy of formation (Optional)
            
        Construct from one of the above data.
        """
        #Argument checking:
        super(self.__class__, self).__init__(specie)
        try:
            cpNone, cvNone, gammaNone = True, True, True
            
            if not cp is None:
                cpNone = False
                self.checkType(cp, float, entryName="cp")
                self._cp = cp
                self._cv = cp - self.specie.Rgas()
                self._gamma = self._cp / self._cv
            
            if not cv is None:
                cvNone = False
                self.checkType(cv, float, entryName="cv")
                self._cv = cv
                self._cp = cv + self.specie.Rgas()
                self._gamma = self._cp / self._cv
            
            if not gamma is None:
                gammaNone = False
                self.checkType(gamma, float, entryName="gamma")
                self._gamma = gamma
                self._cv = self.specie.Rgas()/(gamma - 1.0)
                self._cp = self._cv + self.specie.Rgas()
            
            if len([i for i in [cpNone, cvNone, gammaNone] if i]) != 1:
                raise ValueError("Trying to construct from more then one input (cp, cv, gamma).")
            
            self._hf = hf
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
    #########################################################################
    #Operators:
    
    ################################
    #Print:
    def __str__(self):
        StrToPrint = Thermo.__str__(self)
        StrToPrint += "\n"
        StrToPrint += f"cp = {self._cp} [J/kgK]\n"
        StrToPrint += f"cv = {self._cv} [J/kgK]\n"
        StrToPrint += f"cp/cv = {self._gamma} [-]"
        
        return StrToPrint
    
    ##############################
    #Representation:
    def __repr__(self):
        R = eval(super(self.__class__,self).__repr__())
        R["cp"]   = self._cp 
        R["cv"]  = self._cv 
        R["gamma"]     = self._gamma 
                       
        return R.__repr__()
    
    #########################################################################
    #Member functions:
    
    ################################
    def cp(self, p, T):
        """
        Constant pressure heat capacity [J/kg/K]
        """
        #Argument checking
        super(self.__class__,self).cp(p,T)
        return self._cp
    
    ##################################
    #Constant volume heat capacity
    def cv(self,p,T):
        """
        Constant volume heat capacity [J/kg/K]
        """
        #Argument checking
        super(self.__class__,self).cv(p,T)
        return self._cv
    
    ##################################
    #Gamma
    def gamma(self,p,T):
        """
        Heat capacity ratio cp/cv [-]
        """
        #Argument checking
        super(self.__class__,self).gamma(p,T)
        return self._gamma
    
    ################################
    def ha(self, p, T):
        """
        Absolute enthalpy [J/kg]
        If the temperature is not within Tlow and Thigh, a
        warning is displayed.
        
                
        ha(T) = cp * (T - Tstd) + hf
        """
        
        #Argument checking
        super(self.__class__,self).ha(p,T)
        return self._cp * (T - Tstd) + self._hf
    
    ##################################
    def hf(self):
        """
        Enthalpy of formation [J/kg]
        
        hf = ha(Tstd)
        """
        return self.ha(0.,Tstd)
    
    ################################
    def dcpdT(self, p, T):
        """
        dcp/dT [J/kg/K^2]
        """
        super(self.__class__,self).dcpdT(p,T)
        
        return 0.0
    
    #########################################################################
    @classmethod
    def fromDictionary(cls,dictionary):
        """
        Create from dictionary.
        """
        try:
            entryList = ["cp", "cv", "gamma", "hf"]
            Dic = {}
            for entry in entryList:
                if entry in dictionary:
                    Dic[entry] = dictionary[entry]
            
            if not "specie" in dictionary:
                raise ValueError(f"Mandatory entry 'specie' not found in dictionary.")
            
            out = cls(dictionary["specie"], **Dic)
            return out
            
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed construction from dictionary", err)
    
#############################################################################
janaf7.addToRuntimeSelectionTable("constant")
