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

from .heatTransferModel import heatTransferModel
from ..engineGeometry.engineGeometry import engineGeometry

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Woschni model to compute wall heat transfer coefficient:
class Woschni(heatTransferModel):
    coeffs = \
        {
            "nwos":         1.36,
            "C1":           5.26,
            "C2":           2.28,
            "C2ge":         6.18,
            "C3comp":       0.0,
            "C3comb":       3.24e-3
        }
    
    __doc__ = """
    Class for computation of wall heat transfer with Woschni model:
    
    h = C1 * (p/1000.)^.8 * T^(-0.53) * D^(-0.2) * uwos^(0.8)
    uwos = C2 * upMean + C3 * (p - p_mot) * V * T0 / (p0 * V0)
    p_mot = p * ( V0 / V )**nwos
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        coeffs:   dict
            Container for model constants
    """
    __doc__ += "\t\t{:15s}{:15s}{:15s}\n".format("Variable","Units","Default")
    __doc__ += "\t\t" + "-"*45 + "\n"
    
    for var in coeffs:
        __doc__ += "\t\t{:15s}{:15s}{:15s}\n".format(str(var), type(coeffs[var]).__name__, str(coeffs[var]))
    
    __doc__ += "\t\t" + "-"*45 + "\n"
    
    #########################################################################
    #Constructor:
    def __init__(self, coeffs={}):
        """
        coeffs:   dict
            Container for model constants (see help(Woschni) for default values)
        
        Initialize the parameters required by Woschni model.
        """
        super(self.__class__,self).__init__(self, coeffs)
    
    #########################################################################
    #Cumpute wall heat transfer:
    def h(self, CA, p, T, geometry, initCond):
        """
        CA:         float
            Current CA
        p:          float
            Pressure [Pa]
        T:          float
            Temperature [K]
        geometry:   engineGeometry
            Class containing engine geometry information
        initCond:   dict
            {
                p:      float
                    Initial pressure
                T:      float
                    Initial temperature
                CA:     float
                    Initial instant
            }
            Initial conditions (at IVC or at known point of compression)
        
        Used to compute convective wall heat transfer with Woschni correlation:
        
            h = C1 * (p/1000.)^.8 * T^(-0.53) * geometry.D^(-0.2) * uwos^(0.8)
            uwos = C2 * geometry.upMean + C3 * (p - p_mot) * V * T0 / (p0 * V0)
            p_mot = p * ( V0 / V )**nwos
        """
        
        #Check arguments:
        try:
            self.__class__.checkType(p, float, "p")
            self.__class__.checkType(T, float, "T")
            self.__class__.checkType(geometry, engineGeometry, "geometry")
            self.__class__.checkType(SR, float, "SR")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.h, err)
        
        #Compute heat transfer coefficient:
        uwos = self.uwos(CA, p, initCond, geometry)
        h = self.coeffs["C1"] * (p/1000.)**.8 * T**(-0.53) * geometry.D**(-0.2) * uwos**(0.8)
        
        return h
    
    #########################################################################
    #Compute uwos:
    def uwos(self, CA, p, initCond, geometry):
        """
        CA:         float
            Current CA
        p:          float
            Pressure [Pa]
        geometry:   engineGeometry
            Class containing engine geometry information
        initCond:   dict
            {
                p:      float
                    Initial pressure
                T:      float
                    Initial temperature
                CA:     float
                    Initial instant
            }
            Initial conditions (at IVC or at known point of compression)
        
        uwos = C2 * geometry.upMean + C3 * (p - p_mot) * V * T0 / (p0 * V0)
        p_mot = p * ( V0 / V )**nwos
        """
        #Check arguments:
        try:
            self.__class__.checkType(geometry, engineGeometry, "geometry")
            self.__class__.checkType(SR, float, "SR")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.uwos, err)
        
        if geometry.isComb(CA):
            C3 = self.coeffs["C3comb"]
        else:
            C3 = self.coeffs["C3comp"]
        
        uwos = \
            self.coeffs["C2"] * geometry.upMean + C3 * (p - self.p_mot(p, CA, initCond["CA"], geometry)) * initCond["T"] / (initCond["p"] * geometry.V(initCond["CA"]))
        return uwos
    
    #########################################################################
    #Compute ptr:
    def p_mot(self, p, CA, CA0, geometry):
        """
        p_mot = p * ( V0 / V )**nwos
        """
        #Checking arguments:
        try:
            self.__class__.checkType(p, float, "p")
            self.__class__.checkType(V, float, "V")
            self.__class__.checkType(V0, float, "V0")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.p_mot, err)
        
        ptr = p*(geometry.V(CA0)/geometry.V(CA))**self.coeffs["nwos"]
        return ptr
    
    
