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

from libICEpost.src.base.Functions.typeChecking import checkType
from .EngineGeometry import EngineGeometry

from collections.abc import Iterable

import numpy as np
from numpy import cos, sin, sqrt, radians, pi

import pandas as pd
from typing import ClassVar

_pistonPos = lambda CA, S, lam, delta: S/2.0 * \
    (
        1.0
        - cos(radians(CA))
        + 1.0/lam *(1. - cos(np.arcsin((sin(radians(CA)) + delta)*lam)))
    )
def pistonPosition(CA:float|Iterable[float], *, S:float, lam:float, delta:float) -> float|Iterable[float]:
    """
    Returns the piston position at CA [m] (reference to TDC).
    
    Args:
        CA (float | Iterable[float]): Time in CA
        S (float): Stroke [m]
        lam (float): conRodLen/crankRadius [-]
        delta (float): pinOffset/crankRadius [-]
    
    Returns:
        float|Iterable[float]: Piston position [m]
    """
    checkType(CA, (float, Iterable), "CA")
    return _pistonPos(CA, S, lam, delta)


_pistonPosDerivative = lambda CA, S, lam, delta: 0.5 * S * \
    (
        lam*cos(radians(CA))*(delta + sin(radians(CA)))
        /
        sqrt(1. - (lam**2.)*((delta + sin(radians(CA)))**2.)) + sin(radians(CA))
    ) * pi/180.0
def pistonPosDerivative(CA:float|Iterable[float], *, S:float, lam:float, delta:float) -> float|Iterable[float]:
    """
    Returns the time (in CA) derivative of instantaneous piston position at CA [m/CA].
    
    Args:
        CA (float | Iterable[float]): Time in CA
        S (float): Stroke [m]
        lam (float): conRodLen/crankRadius [-]
        delta (float): pinOffset/crankRadius [-]
    
    Returns:
        float|Iterable[float]: ds/dCA [m/CA]
    """
    checkType(CA, (float, Iterable), "CA")
    return _pistonPosDerivative(CA, S, lam, delta)

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class ConRodGeometry(EngineGeometry):
    """
    Geometry for engine piston.
    
    Attibutes:
        - CR (float): Compression ratio [-]
        - lam (float): conRodLen/crankRadius [-]
        - delta (float): pinOffset/crankRadius [-]
        - D (float): Bore [m]
        - S (float): Stroke [m]
        - l (float): connecting-rod length [m]
        - pinOffset (float): Piston pin offset [m]
        - clearence (float): TDC clearence [m]
        - cylArea (float): cylinder cross section [m^2]
        - pistonArea (float): piston surface area [m^2]
        - headArea (float): cylinder head area [m^2]
        - Vs (float): Displacement volume [m^3]
        - Vmin (float): Mimimum volume [m^3]
        - Vmax (float): Maximum volume [m^3]
        - patches (list[str]): List of patches names
    """
    
    _CR:float
    """The compression ratio"""
    _D:float
    """Bore [m]"""
    _S:float
    """Stroke [m]"""
    _l:float
    """connecting-rod length [m]"""
    _pinOffset:float=0.0
    """Piston pin offset [m]"""
    _clearence:float=None
    """TDC clearence [m]"""
    _pistonCylAreaRatio:float=1.0
    """piston surf. area / cyl. section"""
    _headCylAreaRatio:float=1.0
    """head surf. area / cyl. section"""
    
    _patches: ClassVar[Iterable[str]] = ["liner", "piston", "head"]
    """List of patches names"""
    
    #########################################################################
    #Properties:
    @property
    def CR(self) -> float:
        """Compression ratio [-]"""
        return self._CR

    @property
    def D(self) -> float:
        """Bore [m]"""
        return self._D

    @property
    def S(self) -> float:
        """Stroke [m]"""
        return self._S

    @property
    def l(self) -> float:
        """Connecting-rod length [m]"""
        return self._l

    @property
    def pinOffset(self) -> float:
        """Piston pin offset [m]"""
        return self._pinOffset

    @property
    def clearence(self) -> float:
        """TDC clearance [m]"""
        return self._clearence

    @property
    def pistonCylAreaRatio(self) -> float:
        """Piston surface area / cylinder section"""
        return self._pistonCylAreaRatio

    @property
    def headCylAreaRatio(self) -> float:
        """Head surface area / cylinder section"""
        return self._headCylAreaRatio
    
    @property
    def patches(self) -> Iterable[str]:
        """
        Returns the list of patches names.

        Returns:
            Iterable[str]: List of patches names
        """
        return self._patches[:]
    
    #Since the class is frozen, variables are computed only once and stored
    @property
    def lam(self) -> float:
        """lambda = R/L"""
        if not hasattr(self, '_lam'):
            self._lam = 0.5 * self.S / self.l
        return self._lam

    @property
    def delta(self) -> float:
        """delta = PO/R"""
        if not hasattr(self, '_delta'):
            self._delta = self.pinOffset / (0.5 * self.S)
        return self._delta

    @property
    def cylArea(self) -> float:
        """Cylinder cross section area [m^2]"""
        if not hasattr(self, '_cylArea'):
            self._cylArea = pi * self.D**2 / 4.0
        return self._cylArea

    @property
    def pistonArea(self) -> float:
        """Piston surface area [m^2]"""
        if not hasattr(self, '_pistonArea'):
            self._pistonArea = self.cylArea * self.pistonCylAreaRatio
        return self._pistonArea

    @property
    def headArea(self) -> float:
        """Cylinder head area [m^2]"""
        if not hasattr(self, '_headArea'):
            self._headArea = self.cylArea * self.headCylAreaRatio
        return self._headArea

    @property
    def Vs(self) -> float:
        """Displacement volume [m^3]"""
        if not hasattr(self, '_Vs'):
            self._Vs = self.cylArea * self.S
        return self._Vs

    @property
    def Vmin(self) -> float:
        """Minimum volume [m^3]"""
        if not hasattr(self, '_Vmin'):
            self._Vmin = self.Vs / (self.CR - 1.0)
        return self._Vmin

    @property
    def Vmax(self) -> float:
        """Maximum volume [m^3]"""
        if not hasattr(self, '_Vmax'):
            self._Vmax = self.Vs + self.Vmin
        return self._Vmax
    
    #########################################################################
    #Construct from dictionary
    @classmethod
    def fromDictionary(cls,inputDict:dict):
        """
        Construct from dictionary containing the following parameters:
        - CR (float): Compression ratio [-]
        - bore (float): Bore [m]
        - stroke (float): Stroke [m]
        - conRodLen (float): connecting-rod length [m]
        - pinOffset (float): Piston pin offset [m]
        - clearence (float): TDC clearence [m] (optional)
        - pistonCylAreaRatio (float): piston surf. area / cyl. section (optional)
        - headCylAreaRatio (float): head surf. area / cyl. section (optional)
        
        Args:
            inputDict (dict): Dictionary containing the parameters
        """
        return cls(**inputDict)
    
    #########################################################################
    #Dunder methods:
    def __str__(self):
        STR = super(self.__class__, self).__str__()
        STR += "\n{:15s} {:10.3f} {:15s}".format("CR", self.CR,"[-]")
        STR += "\n{:15s} {:10.3f} {:15s}".format("delta = PO/R", self.delta,"[-]")
        STR += "\n{:15s} {:10.3f} {:15s}".format("lambda = R/L", self.lam,"[-]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("pistonCylAreaRatio", self.pistonCylAreaRatio,"[-]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("headCylAreaRatio", self.headCylAreaRatio,"[-]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("bore (2*R)", self.D,"[m]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("stroke (S)", self.S,"[m]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("conRodLen (L)", self.l,"[m]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("Pin-offset (PO)", self.pinOffset,"[m]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("clearence", self.clearence,"[m]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("cylArea", self.cylArea,"[m^2]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("pistonArea", self.pistonArea,"[m^2]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("headArea", self.headArea,"[m^2]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("Vs", self.Vs,"[m^3]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("Vmin", self.Vmin,"[m^3]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("Vmax", self.Vmax,"[m^3]")
        
        return STR
    
    ################################
    #hash
    def __hash__(self):
        return hash((self.CR, self.D, self.S, self.l, self.pinOffset, self.clearence, self.pistonCylAreaRatio, self.headCylAreaRatio))
    
    #########################################################################
    #Constructor:
    def __init__(self, *,
                 bore:float, 
                 stroke:float, 
                 conRodLen:float, 
                 CR:float, 
                 pinOffset:float=0.0, 
                 clearence:float=None, 
                 pistonCylAreaRatio:float=1.0, 
                 headCylAreaRatio:float=1.0
                 ):
        """
        Constructor for ConRodGeometry class.
        
        Args:
            bore (float): Bore [m]
            stroke (float): Stroke [m]
            conRodLen (float): connecting-rod length [m]
            CR (float): Compression ratio [-]
            pinOffset (float, optional): Piston pin offset [m]. Default is 0.0.
            clearence (float, optional): TDC clearence [m]. Default is None. If None, it is computed as Vmin/cylArea.
            pistonCylAreaRatio (float): piston surf. area / cyl. section. Default is 1.0.
            headCylAreaRatio (float): head surf. area / cyl. section. Default is 1.0.    
        """
        self.checkType(bore, float, "bore")
        self.checkType(stroke, float, "stroke")
        self.checkType(conRodLen, float, "conRodLen")
        self.checkType(CR, float, "CR")
        self.checkType(pinOffset, float, "pinOffset")
        self.checkType(pistonCylAreaRatio, float, "pistonCylAreaRatio")
        self.checkType(headCylAreaRatio, float, "headCylAreaRatio")
        
        self._D = bore #Bore [m]
        self._S = stroke #Stroke [m]
        self._l = conRodLen #connecting-rod length [m]
        self._pinOffset = pinOffset  #Piston pin offset [m]
        self._CR = CR #Compression ratio [-]
        self._pistonCylAreaRatio = pistonCylAreaRatio #piston surf. area / cyl. section
        self._headCylAreaRatio = headCylAreaRatio #head surf. area / cyl. section
        
        #Clearence
        if clearence is None:
            clearence = self.Vmin/self.cylArea
        else:
            self.checkType(clearence, float, "clearence")
        self._clearence = clearence
    
    #########################################################################
    #Piston position:
    def s(self,CA:float|Iterable[float]) -> float|np.ndarray:
        """
        Returns the piston position at CA [m] (reference to TDC)

        Args:
            CA (float | Iterable[float]): Time in CA

        Returns:
            float|np.ndarray: Piston position [m]
        """
        return pistonPosition(CA, S=self.S, lam=self.lam, delta=self.delta)
    
    ###################################
    #Instant. cylinder volume:
    def V(self,CA:float|Iterable[float]) -> float|np.ndarray:
        return self.Vmin + pistonPosition(CA, S=self.S, lam=self.lam, delta=self.delta) * self.cylArea
    
    ###################################
    #Time (in CA) derivative of cyl. position:
    def dsdCA(self,CA:float|Iterable[float]) -> float|np.ndarray:
        """
        Returns the time (in CA) derivative of instantaneous piston position at CA [m/CA].
        Args:
            CA (float | Iterable[float]): Time in CA

        Returns:
            float|np.ndarray: ds/dCA [m/CA]
        """
        return pistonPosDerivative(CA, S=self.S, lam=self.lam, delta=self.delta)
    
    ###################################
    #Time (in CA) derivative of cyl. volume:
    def dVdCA(self,CA:float|Iterable[float]) -> float|np.ndarray:
        return self.dsdCA(CA) * self.cylArea
    
    ###################################
    #Instant. liner area:
    def linerArea(self,CA:float|Iterable[float]) -> float|np.ndarray:
        """
        Returns the liner area at CA [m^2].
        Args:
            CA (float | Iterable): Time in CA

        Returns:
            float|np.ndarray: [m^2]
        """
        checkType(CA, (float, Iterable), "CA")
        return (self.s(CA) + self.clearence) * pi * self.D
    
    ###################################
    def A(self,CA:float|Iterable[float]) -> float|np.ndarray:
        return self.linerArea(CA) + self.pistonArea + self.headArea

    ###################################
    def areas(self,CA:float|Iterable) -> pd.DataFrame:
        data = \
        {
            "CA":CA if isinstance(CA, Iterable) else [CA], 
            "liner":self.linerArea(CA) if isinstance(CA, Iterable) else [self.linerArea(CA)],
            "piston":[self.pistonArea for _ in CA] if isinstance(CA, Iterable) else [self.pistonArea],
            "head":[self.headArea for _ in CA] if isinstance(CA, Iterable) else [self.headArea],
        }
        return pd.DataFrame.from_dict(data, orient="columns")
    
#########################################################################
#Add to selection table:
EngineGeometry.addToRuntimeSelectionTable(ConRodGeometry)