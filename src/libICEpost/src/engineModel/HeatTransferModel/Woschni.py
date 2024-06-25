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

from __future__ import annotations

from typing import Self
from collections.abc import Iterable

from .HeatTransferModel import HeatTransferModel

from libICEpost.src.engineModel.EngineModel import EngineModel
from libICEpost.src.engineModel.functions import upMean

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Woschni model to compute wall heat transfer coefficient:
class Woschni(HeatTransferModel):
    """
    Class for computation of wall heat transfer with Woschni model:
    
    h = C1 * (p/1000.)^.8 * T^(-0.53) * D^(-0.2) * uwos^(0.8)
    uwos = C2 * upMean + C3 * (p - p_mot) * Vs * T0 / (p0 * V0)
    p_mot = p * ( V0 / V )**nwos
    Vs : Displacement volume
    
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
        """
        Construct from dictionary
        {
            nwos    (float, default 1.32)
            C1      (float, default 3.26)
            C2cv    (float, default 2.28)
            C2ge    (float, default 6.18)
            C3comp  (float, default 0.0)
            C3comb  (float, default 3.24e-3)
        }

        Returns:
            Self: Instance of this class
        """
        #Use super
        return super().fromDictionary(dictionary)
    
    #########################################################################
    #Constructor:
    def __init__(self, /,
                 nwos:float=1.32,
                 C1:float=3.26,
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
            
            #Check types
            for c in self.coeffs:
                self.checkType(self.coeffs[c], float, c)
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
            
    #########################################################################
    #Cumpute wall heat transfer:
    def h(self, *, engine:EngineModel.EngineModel, CA:float|Iterable|None=None, **kwargs) -> float:
        """
        Compute convective wall heat transfer with Woschni correlation:
            h = C1 * (p/1000.)^.8 * T^(-0.53) * engine.geometry.D^(-0.2) * uwos^(0.8)
            uwos = C2 * upMean(engine.time, engine.geometry) + C3 * (p - p_mot) * Vs * T0 / (p0 * V0)
            p_mot = p * ( V0 / V )**nwos
        
        Args:
            engine (EngineModel): The engine model from which taking data.
            CA (float | Iterable | None, optional): Time for which computing heat transfer. If None, uses engine.time.time. Defaults to None.

        Returns:
            float: convective wall heat transfer coefficient [W/(m^2 K)]
        """
        
        #Check arguments:
        try:
            self.checkType(engine,EngineModel.EngineModel,"engine")
            if not CA is None:
                self.checkTypes(CA,(float, Iterable),"CA")
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.h, err)
        
        CA = engine.time.time if CA is None else CA
        p = engine.data.p(CA)
        T = engine.data.T(CA)
        geometry = engine.geometry
        
        #Compute heat transfer coefficient:
        uwos = self.uwos(CA=CA, engine=engine)
        h = self.coeffs["C1"] * (p/1000.)**(0.8) * T**(-0.53) * geometry.D**(-0.2) * uwos**(0.8)
        
        return h
    
    #########################################################################
    #Compute uwos:
    def uwos(self, engine:EngineModel.EngineModel, *, CA:float|Iterable|None=None) -> float:
        """
        uwos = C2 * upMean(engine.time, engine.geometry) + C3 * (p - p_mot) * Vs * T_ref / (p_ref * V_ref)
        p_mot = p_ref * ( V_ref / V )**nwos
        
        Args:
            engine (EngineModel): The engine model from which taking data.
            CA (float | Iterable | None, optional): Time for which computing heat transfer. If None, uses engine.time.time. Defaults to None.
        """
        #Check arguments:
        try:
            self.checkTypes(CA, (float, Iterable), "CA")
            self.checkType(engine, EngineModel.EngineModel, "engine")
            
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.uwos, err)
        
        CA = engine.time.time if CA is None else CA
        p = engine.data.p(CA)
        V = engine.geometry.V(CA)
        
        #Using bool operations to extend to vectorization
        C3 = self.coeffs["C3comb"]*engine.time.isCombustion(CA) + self.coeffs["C3comp"]*(1. - engine.time.isCombustion(CA))
        C2 = self.coeffs["C2cv"]*engine.time.isClosedValves(CA) + self.coeffs["C2ge"]*(1. - engine.time.isClosedValves(CA))
        
        refCA = engine.time.startTime if engine.time.isClosedValves(engine.time.startTime) else engine.time.IVC
        refP = engine.data.p(refCA)
        refT = engine.data.T(refCA)
        refV = engine.geometry.V(refCA)
        
        p_mot = self.p_mot(p0=refP, V=V, V0=refV)
        Vs = engine.geometry.Vs
        
        uwos = \
            C2 * upMean(time=engine.time, geometry=engine.geometry) + C3 * Vs * (p - p_mot) * refT / (refP * refV)
        return uwos
    
    #########################################################################
    #Compute ptr:
    def p_mot(self, *, p0:float|Iterable, V:float|Iterable, V0:float|Iterable):
        """
        p_mot = p0 * ( V0 / V )**nwos
        """
        #Checking arguments:
        try:
            self.checkTypes(p0, (float, Iterable), "p")
            self.checkTypes(V, (float, Iterable), "V")
            self.checkTypes(V0, (float, Iterable), "V0")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.p_mot, err)
        
        ptr = p0*(V0/V)**self.coeffs["nwos"]
        return ptr


#########################################################################
#Add to selection table of Base
HeatTransferModel.addToRuntimeSelectionTable(Woschni)