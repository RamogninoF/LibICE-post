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

from abc import ABCMeta, abstractmethod

from src.base.Utilities import Utilities

from ..engineModel import engineModel

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Heat transfer model (base class):
class heatTransferModel(Utilities, metaclass=ABCMeta):
    """
    Base class for modeling of wall heat transfer.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        coeffs:   dict
            Container for model constants used to compute the convective heat transfer
            coefficient at cylinder walls (depend on the specific model used)
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Constructors:
        heatTransferModel():
            Raising a 'NotImplementedError' if attempting to construct an object of
            this class. Used only as base class (overwritten from derived classes).
    
    """
    
    #Name:
    typeName = "heatTransferModel"
    coeffs = {}
    
    #########################################################################
    #Constructor:
    def __init__(self, coeffs, verbose=True):
        """
        Constructors:
            heatTransferModel():
                Raising a 'NotImplementedError' if attempting to construct an object of
                this class. Used only as base class (overwritten from derived classes).
        """
        print("Building heatTransferModel instance:")
        print(f"Type:\t{self.__class__.typeName}")
        try:
            self.checkType(coeffs, dict, entryName="coeffs")
            
            Coeffs = self.__class__.coeffs
            for c in coeffs:
                if c in Coeffs:
                    self.checkType(coeffs[c], type(Coeffs[c]), entryName="coeffs[{:}]".format(c))
                    Coeffs[c] = coeffs[c]
                    
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__,err)
        
        print(f"Coefficients:")
        for CC in Coeffs:
            print(f"{CC}:\t{Coeff[CC]}")
            
        self.coeffs = coeffs
    
    #########################################################################
    #Compute laminar flame speed:
    @abstractmethod
    def h(self, CA, engine):
        """
        CA:     float
            Crank angle
        engine: engineModel
            The engine model
        
        Used to compute convective wall heat trasfer. To be overwritten
        """
        try:
            self.checkType(CA, float, entryName="CA")
            self.checkType(engine, engineModel, entryName="engine")
                    
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.h,err)
    
    ##############################
    #Change coefficients (or some of them):
    def setCoeffs(self, coeffs={}, **argv):
        """
        coeffs:     dict ({})
            Dictionary containing the parameters of the model (in heatTransferModel.coeffs) 
            that need to be changed/set. Keyword arguments are also accepted.
        """
        try:
            self.coeffs = Utilities.updateKeywordArguments(coeffs, self.coeffs)
            self.coeffs = Utilities.updateKeywordArguments(argv, self.coeffs)
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.setCoeffs, err)
        
        return self
        
