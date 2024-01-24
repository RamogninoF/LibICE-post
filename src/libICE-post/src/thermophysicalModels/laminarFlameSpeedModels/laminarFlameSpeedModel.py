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
from src.base.BaseClass import BaseClass

from abc import ABCMeta, abstractmethod

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Laminar flame speed (base class):
class laminarFlameSpeedModel(BaseClass, Utilities, metaclass=ABCMeta):
    """
    Base class for computation of laminar flame speed.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        coeffs:   dict
            Container for model constants used to compute the laminar flame speed
            (depend on the specific correlation used)
    """
    #########################################################################
    
    coeffs = {}
    
    #########################################################################
    #Constructor:
    def __init__(self):
        """
        Base (virtual) class: does not support instantiation.
        """
        pass
        
    #########################################################################
    #Cumpute laminar flame speed:
    @abstractmethod
    def Su(self,p,T,phi,EGR=None):
        """
        p:      float
            Pressure [Pa]
        T:      float
            Temperature [K]
        phi:    float
            Equivalence ratio
        EGR:    float (None)
            Level of exhaust gas recirculation [%]
        
        Used to compute laminar flame speed in derived class. Here in the base class
        it is used only for argument checking.
        """
        try:
            Utilities.checkType(p, float, entryName="p")
            Utilities.checkType(T, float, entryName="T")
            Utilities.checkType(phi, float, entryName="phi")
            if not(EGR is None):
                Utilities.checkType(EGR, float, entryName="EGR")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.Su, err)
        
        return None
    
    ##############################
    #Cumpute laminar flame thickness:
    @abstractmethod
    def deltaL(self,p,T,phi,EGR=None):
        """
        p:      float
            Pressure [Pa]
        T:      float
            Temperature [K]
        phi:    float
            Equivalence ratio
        EGR:    float
            Level of exhaust gas recirculation [%]
        
        Used to compute laminar flame thickness in derived class. Here in the base class
        it is used only for argument checking.
        """
        try:
            Utilities.checkType(p, float, entryName="p")
            Utilities.checkType(T, float, entryName="T")
            Utilities.checkType(phi, float, entryName="phi")
            if not(EGR is None):
                Utilities.checkType(EGR, float, entryName="EGR")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.deltaL, err)
        
        return None

    ##############################
    #Change coefficients (or some of them):
    def setCoeffs(self,coeffs={}, **argv):
        """
        coeffs:     dict ({})
            Dictionary containing the parameters of the model (in laminarFlameSpeed.coeffs) 
            that need to be changed/set. Keyword arguments are also accepted.
        """
        try:
            self.coeffs = Utilities.updateKeywordArguments(coeffs, self.coeffs)
            self.coeffs = Utilities.updateKeywordArguments(argv, self.coeffs)
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.setCoeffs, err)
        
        return self
        
#############################################################################
laminarFlameSpeedModel.createRuntimeSelectionTable("laminarFlameSpeedModel")
