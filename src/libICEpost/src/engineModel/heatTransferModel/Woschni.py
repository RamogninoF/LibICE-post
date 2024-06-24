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

from typing import Self

from .heatTransferModel import HeatTransferModel, EngineModel

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Woschni model to compute wall heat transfer coefficient:
class Woschni(HeatTransferModel):
    """
    Class for computation of wall heat transfer with Woschni model:
    
    h = C1 * (p/1000.)^.8 * T^(-0.53) * D^(-0.2) * uwos^(0.8)
    uwos = C2 * upMean + C3 * (p - p_mot) * V * T0 / (p0 * V0)
    p_mot = p * ( V0 / V )**nwos
    
    Where:
        1) C2 changes depending if at closed-valves (C2cv) or during gas-exchange (C2ge)
        2) C3 changes depending if during compression (C3comp) or during combustion/expansion (C3comb)
        3) Reference conditions (0) are at IVC or startTime if it is in closed-valve region.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        coeffs:   dict
            Container for model constants
    """
    
    #########################################################################
    #Class methods:
    @classmethod
    def fromDictionary(cls, dictionary) -> Self:
        try:
            return cls(**dictionary)
            
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed contruction from dictionary", err)
    
    #########################################################################
    #Constructor:
    def __init__(self, /,
                 nwos:float=1.36,
                 C1:float=5.26,
                 C2cv:float=2.28,
                 C2ge:float=6.18,
                 C3comp:float=0.0,
                 C3comb:float=3.24e-3):
        """
        Initialize the parameters required by Woschni model.
        """
        try:
            self.coeffs = \
            {
                 "nwos"   : nwos   ,
                 "C1"     : C1     ,
                 "C2cv"   : C2cv   ,
                 "C2ge"   : C2ge   ,
                 "C3comp" : C3comp ,
                 "C3comb" : C3comb ,
            }
                
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
            
    #########################################################################
    #Cumpute wall heat transfer:
    def h(self, engine:EngineModel, *, CA:float|None=None) -> float:
        """
        Compute convective wall heat transfer with Woschni correlation:
            h = C1 * (p/1000.)^.8 * T^(-0.53) * engine.geometry.D^(-0.2) * uwos^(0.8)
            uwos = C2 * engine.geometry.upMean + C3 * (p - p_mot) * V * T0 / (p0 * V0)
            p_mot = p * ( V0 / V )**nwos
        
        Args:
            engine (EngineModel): The engine model from which taking data.
            CA (float | None, optional): Time for which computing heat transfer. If None, uses engine.time.time. Defaults to None.

        Returns:
            float: convective wall heat transfer coefficient
        """
        
        #Check arguments:
        try:
            super(self.__class__,self).h(self, engine, CA)
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.h, err)
        
        CA = engine.time.time if CA is None else CA
        p = engine.data.p(CA)
        T = engine.data.T(CA)
        geometry = engine.geometry
        
        #Compute heat transfer coefficient:
        uwos = self.uwos(CA, engine)
        h = self.coeffs["C1"] * (p/1000.)**.8 * T**(-0.53) * geometry.D**(-0.2) * uwos**(0.8)
        
        return h
    
    #########################################################################
    #Compute uwos:
    def uwos(self, engine:EngineModel, *, CA:float|None=None) -> float:
        """
        uwos = C2 * geometry.upMean + C3 * (p - p_mot) * V * T_ref / (p_ref * V_ref)
        p_mot = p * ( V_ref / V )**nwos
        
        Args:
            engine (EngineModel): The engine model from which taking data.
            CA (float | None, optional): Time for which computing heat transfer. If None, uses engine.time.time. Defaults to None.
        """
        #Check arguments:
        try:
            self.checkType(CA, float, "CA")
            self.checkType(engine, EngineModel, "engine")
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.uwos, err)
        
        CA = engine.time.time if CA is None else CA
        p = engine.data.p(CA)
        V = engine.geometry.V(CA)
        
        C3 = self.coeffs["C3comb"] if engine.time.isCombustion(CA) else self.coeffs["C3comp"]
        C2 = self.coeffs["C2"] if engine.time.isClosedValves(CA) else self.coeffs["C2ge"]
        
        refCA = engine.time.startTime if engine.time.isClosedValves(engine.time.startTime) else engine.time.IVC
        refP = engine.data.p(refCA)
        refT = engine.data.T(refCA)
        refV = engine.geometry.V(refCA)
        
        uwos = \
            C2 * engine.upMean() + C3 * (p - self.p_mot(p=p, V=V, V0=refV)) * refT / (refP * refV)
        return uwos
    
    #########################################################################
    #Compute ptr:
    def p_mot(self, *, p:float, V:float, V0:float):
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
        
        ptr = p*(V0/V)**self.coeffs["nwos"]
        return ptr


#########################################################################
#Add to selection table of Base
HeatTransferModel.addToRuntimeSelectionTable(Woschni)