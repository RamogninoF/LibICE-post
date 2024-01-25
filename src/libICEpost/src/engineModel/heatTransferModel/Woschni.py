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
            "C2cv":         2.28,
            "C2ge":         6.18,
            "C3comp":       0.0,
            "C3comb":       3.24e-3,
            #"C3_t":         0.308,
            #"turbCorr":     False,
        }
    
    __doc__ = """
    Class for computation of wall heat transfer with Woschni model:
    
    h = C1 * (p/1000.)^.8 * T^(-0.53) * D^(-0.2) * uwos^(0.8)
    uwos = C2 * upMean + C3 * (p - p_mot) * V * T0 / (p0 * V0)
    p_mot = p * ( V0 / V )**nwos
    
    Where:
        1) C2 changes depending if at closed-valves (C2cv) or during gas-exchange (C2ge)
        2) C3 changes depending if during compression (C3comp) or during combustion/expansion (C3comb)
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        coeffs:   dict
            Container for model constants
            
        ref: dict
            {
                p:      float
                    Reference pressure
                T:      float
                    Reference temperature
                CA:     float
                    Reference instant
            }
            Reference conditions
    """
    __doc__ += "\t\t{:15s}{:15s}{:15s}\n".format("Variable","Units","Default")
    __doc__ += "\t\t" + "-"*45 + "\n"
    
    for var in coeffs:
        __doc__ += "\t\t{:15s}{:15s}{:15s}\n".format(str(var), type(coeffs[var]).__name__, str(coeffs[var]))
    
    __doc__ += "\t\t" + "-"*45 + "\n"
    
    ref = \
        {
            "p":float('nan'),
            "T":float('nan'),
            "CA":float('nan')
        }
    
    #########################################################################
    #Constructor:
    def __init__(self, coeffs={}, ref=None):
        """
        coeffs:   dict
            Container for model constants (see help(Woschni) for default values)
        
        Initialize the parameters required by Woschni model.
        """
        try:
            super(self.__class__,self).__init__(self, coeffs)
            
            if not ref is None:
                ref = Utilities.updateKeywordArguments(ref, self.__class__.ref)
            else:
                ref = self.__class__.ref
                
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
            
    #########################################################################
    #Cumpute wall heat transfer:
    def h(self, CA, engine, ref=None):
        """
        CA:     float
            Crank angle
        engine: engineModel
            The engine model
        ref:   dict
            {
                p:      float
                    Reference pressure
                T:      float
                    Reference temperature
                CA:     float
                    Reference instant
            }
            Reference conditions (at IVC or at known point of compression). If not given, uses those given at construction
        
        Used to compute convective wall heat transfer with Woschni correlation:
        
            h = C1 * (p/1000.)^.8 * T^(-0.53) * engine.geometry.D^(-0.2) * uwos^(0.8)
            uwos = C2 * engine.geometry.upMean + C3 * (p - p_mot) * V * T0 / (p0 * V0)
            p_mot = p * ( V0 / V )**nwos
        """
        
        #Check arguments:
        try:
            super(self.__class__,self).h(self, CA, engine)
            
            if not ref is None:
                ref = Utilities.updateKeywordArguments(ref, self.ref)
            else:
                ref = self.ref
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.h, err)
        
        p = engine.data.p(CA)
        T = engine.data.T(CA)
        geometry = engine.geometry
        
        #Compute heat transfer coefficient:
        uwos = self.uwos(CA, engine, ref)
        h = self.coeffs["C1"] * (p/1000.)**.8 * T**(-0.53) * geometry.D**(-0.2) * uwos**(0.8)
        
        return h
    
    #########################################################################
    #Compute uwos:
    def uwos(self, CA, engine, ref=None):
        """
        CA:     float
            Crank angle
        engine: engineModel
            The engine model
        ref:   dict
            {
                p:      float
                    Reference pressure
                T:      float
                    Reference temperature
                CA:     float
                    Reference instant
            }
            Reference conditions (at IVC or at known point of compression). If not given, uses those given at construction
        
        uwos = C2 * geometry.upMean + C3 * (p - p_mot) * V * T_ref / (p_ref * V_ref)
        p_mot = p * ( V_ref / V )**nwos
        """
        #Check arguments:
        try:
            self.checkType(CA, float, entryName="CA")
            self.checkType(engine, engineModel, entryName="engine")
            
            if not ref is None:
                ref = Utilities.updateKeywordArguments(ref, self.ref)
            else:
                ref = self.ref
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.uwos, err)
        
        p = engine.data.p(CA)
        geometry = engine.geometry
        
        if engine.time.isCombustion(CA):
            C3 = self.coeffs["C3comb"]
        else:
            C3 = self.coeffs["C3comp"]
        
        if engine.time.isClosedValves(CA):
            C2 = self.coeffs["C2"]
        else:
            C2 = self.coeffs["C2ge"]
        
        uwos = \
            C2 * engine.upMean() + C3 * (p - self.p_mot(p, CA, ref["CA"], geometry)) * ref["T"] / (ref["p"] * geometry.V(ref["CA"]))
        return uwos
    
    #########################################################################
    #Compute ptr:
    def p_mot(self, p, CA, CA0, geometry):
        """
        p_mot = p * ( V0 / V )**nwos
        """
        #Checking arguments:
        try:
            self.checkType(p, float, "p")
            self.checkType(V, float, "V")
            self.checkType(V0, float, "V0")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.p_mot, err)
        
        ptr = p*(geometry.V(CA0)/geometry.V(CA))**self.coeffs["nwos"]
        return ptr
    
    ##############################
    #Change reference conditions:
    def setRef(self, ref={}, **argv):
        """
        ref:     dict ({})
            Dictionary containing the reference conditions Woschni.ref 
            that need to be changed/set. Keyword arguments are also accepted.
        """
        try:
            self.ref = Utilities.updateKeywordArguments(ref, self.ref)
            self.ref = Utilities.updateKeywordArguments(argv, self.ref)
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.setRef, err)
        
        return self
