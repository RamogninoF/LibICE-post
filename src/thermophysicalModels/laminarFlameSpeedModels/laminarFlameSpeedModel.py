#####################################################################
#                               IMPORT                              #
#####################################################################

from src.base.Utilities import Utilities

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Laminar flame speed (base class):
class laminarFlameSpeedModel(Utilities):
    """
    Base class for computation of laminar flame speed.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        coeffs:   dict
            Container for model constants used to compute the laminar flame speed
            (depend on the specific correlation used)
    """
    #########################################################################
    
    #Name:
    typeName = "laminarFlameSpeedModel"
    
    #########################################################################
    #Constructor:
    def __init__(self):
        """
        Raising a 'NotImplementedError' if attempting to construct an object of
        this class. Used only as base class (overwritten from derived classes).
        """
        
        raise NotImplementedError
        
    #########################################################################
    #Cumpute laminar flame speed:
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
        return Su(p,T,phi,EGR)

    ##############################
    #Change coefficients (or some of them):
    def setCoeffs(self, **argv):
        """
        coeffs:     dict ({})
            Dictionary containing the parameters of the model (in laminarFlameSpeed.coeffs) 
            that need to be changed/set. Keyword arguments are also accepted.
        """
        try: 
            self.coeffs = Utilities.updateKeywordArguments(argv, self.coeffs)
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.setCoeffs, err)
        
        return self
        
