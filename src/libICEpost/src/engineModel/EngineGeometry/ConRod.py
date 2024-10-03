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

from .EngineGeometry import EngineGeometry

from collections.abc import Iterable

import numpy as np
from numpy import cos, sin, sqrt, radians, pi

import pandas as pd

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class ConRodGeometry(EngineGeometry):
    """
    Geometry for simple engine piston.
    
    NOTE: Crank angles are defined with 0 CAD at TDC
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        
        Variable   | Type       | Unit   | Description
        -----------|------------|--------|-------------------------
        CR         | float      | -      | Compression ratio
        lam        | float      | -      | conRodLen/crankRadius
        -----------|------------|--------|-------------------------
        D          | float      | m      | Bore
        S          | float      | m      | Stroke
        l          | float      | m      | connecting-rod length
        -----------|------------|--------|-------------------------
        cylArea    | float      | m^2    | cylinder cross section
        pistonArea | float      | m^2    | piston surface area
        headArea   | float      | m^2    | cylinder head area
        -----------|------------|--------|-------------------------
        Vs         | float      | m^3    | Displacement volume
        Vmin       | float      | m^3    | Mimimum volume
        Vmax       | float      | m^3    | Maximum volume
    """
    
    #########################################################################
    #Construct from dictionary
    @classmethod
    def fromDictionary(cls,inputDict):
        """
        Construct from dictionary containing the following parameters:
        
        [Variable]        | [Type] | [Default] | [Unit] | [Description]
        ------------------|--------|-----------|--------|----------------------------------
        CR                | float  | -         | -      | Compression ratio
        ------------------|--------|-----------|--------|----------------------------------
        bore              | float  | -         | m      | Bore
        stroke            | float  | -         | m      | Stroke
        conRodLen         | float  | -         | m      | connecting-rod length
        ------------------|--------|-----------|--------|----------------------------------
        pistCylAreaRatio  | float  | 1         | -      | piston surf. area / cyl. section
        headCylAreaRatio  | float  | 1         | -      | head surf. area / cyl. section
        
        """
        mandatoryEntries = ["CR", "bore", "stroke", "conRodLen"]
        defaultDict = \
            {
                "CR"               : float('nan'),
                "bore"             : float('nan'),
                "stroke"           : float('nan'),
                "conRodLen"        : float('nan'),
                "pistCylAreaRatio" : 1.0,
                "headCylAreaRatio" : 1.0
            }
        
        #Argument checking:
        try:
            for entry in mandatoryEntries:
                if not entry in inputDict:
                    raise ValueError(f"Entry '{entry}' not found in contruction dictionary.")
            
            Dict = cls.updateKeywordArguments(inputDict, defaultDict)
            
            return cls(Dict["CR"], Dict["bore"], Dict["stroke"], Dict["conRodLen"], Dict["pistCylAreaRatio"], Dict["headCylAreaRatio"])
            
        except BaseException as err:
            cls.fatalErrorInClass(cls.__init__, "Failed constructing from dictionary", err)
        
    #########################################################################
    def __str__(self):
        STR = super(self.__class__, self).__str__()
        STR += "\n{:15s} {:10.3f} {:15s}".format("CR", self.CR,"[-]")
        STR += "\n{:15s} {:10.3f} {:15s}".format("delta = PO/R", self.delta,"[-]")
        STR += "\n{:15s} {:10.3f} {:15s}".format("lambda = R/L", self.lam,"[-]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("bore (2*R)", self.D,"[m]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("stroke (S)", self.S,"[m]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("conRodLen (L)", self.l,"[m]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("Pin-offset (PO)", self.pinOffset,"[m]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("cylArea", self.cylArea,"[m^2]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("pistonArea", self.pistonArea,"[m^2]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("headArea", self.headArea,"[m^2]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("Vs", self.Vs,"[m^3]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("Vmin", self.Vmin,"[m^3]")
        STR += "\n{:15s} {:10.3e} {:15s}".format("Vmax", self.Vmax,"[m^3]")
        
        return STR
    
    #########################################################################
    #Constructor:
    def __init__(self, /, CR:float, bore:float, stroke:float, conRodLen:float, pistonCylAreaRatio:float=1.0, headCylAreaRatio:float=1.0, pinOffset=0.0):
        """
        [Variable]        | [Type] | [Default] | [Unit] | [Description]
        ------------------|--------|-----------|--------|----------------------------------
        CR                | float  | -         | -      | Compression ratio
        ------------------|--------|-----------|--------|----------------------------------
        bore              | float  | -         | m      | Bore
        stroke            | float  | -         | m      | Stroke
        conRodLen         | float  | -         | m      | connecting-rod length
        pinOffset         | float  | 0.0       | m      | Piston pin offset
        ------------------|--------|-----------|--------|----------------------------------
        pistCylAreaRatio  | float  | 1         | -      | piston surf. area / cyl. section
        headCylAreaRatio  | float  | 1         | -      | head surf. area / cyl. section
        """
        inputDict = \
            {
                "CR"               : CR,
                "bore"             : bore,
                "stroke"           : stroke,
                "conRodLen"        : conRodLen,
                "pistCylAreaRatio" : 1.0,
                "headCylAreaRatio" : 1.0,
                "pinOffset"        : 0.0
            }
        
        defaultDict = \
            {
                "CR"               : float('nan'),
                "bore"             : float('nan'),
                "stroke"           : float('nan'),
                "conRodLen"        : float('nan'),
                "pistCylAreaRatio" : 1.0,
                "headCylAreaRatio" : 1.0,
                "pinOffset"        : 0.0
            }
        
        #Argument checking:
        try:
            Dict = self.updateKeywordArguments(inputDict, defaultDict)
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        try:
            #[-]
            self.CR = Dict["CR"]
            self.lam = 0.5*Dict["stroke"]/Dict["conRodLen"]
            self.delta = Dict["pinOffset"]/(.5*Dict["stroke"])
            #[m]
            self.D = Dict["bore"]
            self.S = Dict["stroke"]
            self.l = Dict["conRodLen"]
            self.pinOffset = Dict["pinOffset"]
            #[m^2]
            self.cylArea = pi * Dict["bore"]**2 / 4.0
            self.pistonArea = self.cylArea * Dict["pistCylAreaRatio"]
            self.headArea = self.cylArea * Dict["headCylAreaRatio"]
            #[m^3]
            self.Vs = self.cylArea * Dict["stroke"]
            self.Vmin = self.Vs/(Dict["CR"] - 1.0)
            self.Vmax = self.Vs + self.Vmin
            
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, "Construction failed", err)
    
    #########################################################################
    #Piston position:
    def s(self,CA:float|Iterable) -> float|np.ndarray:
        """
        Returns the piston position at CA (reference to TDC)

        Args:
            CA (float | Iterable): Time in CA

        Returns:
            float|np.ndarray[float]: Piston position [m]
        """
        def f(angle):
            return self.S/2.0 * (1.0 - cos(1.*angle) + 1.0/self.lam *(1. - cos(np.arcsin((sin(1.*angle) + self.delta)*self.lam))))
        
        try:
            if isinstance(CA, list):
                return np.array([f(radians(ca)) for ca in CA])
            else:
                return f(radians(CA))
        except BaseException as err:
            self.fatalErrorInClass(self.s, "Failed computing piston position", err)
    
    ###################################
    #Instant. cylinder volume:
    def V(self,CA:float|Iterable) -> float|np.ndarray:
        """
        Returns the instantaneous in-cylinder volume at CA

        Args:
            CA (float | Iterable): Time in CA

        Returns:
            float|np.ndarray[float]: In-cylinder volume [m^3]
        """
        def f(ca):
            return self.Vmin + self.s(ca)*self.cylArea
        
        try:
            if isinstance(CA, list):
                return np.array([f(ca) for ca in CA])
            else:
                return f(CA)
        except BaseException as err:
            self.fatalErrorInClass(self.V, "Failed computing in-cylinder volume", err)
    
    ###################################
    #Time (in CA) derivative of cyl. position:
    def dsdCA(self,CA:float|Iterable) -> float|np.ndarray:
        """
        Returns the time (in CA) derivative of instantaneous piston position at CA
        Args:
            CA (float | Iterable): Time in CA

        Returns:
            float|np.ndarray[float]: ds/dCA [m/CA]
        """
        def f(angle):
            return 0.5 * self.S * (self.lam*cos(1.*angle)*(self.delta + sin(1.*angle))/sqrt(1. - (self.lam**2.)*((self.delta + sin(1.*angle))**2.)) + sin(1.*angle))
        
        try:
            if isinstance(CA, list):
                return np.array([f(radians(ca))*pi/180. for ca in CA])
            else:
                return f(radians(CA))*pi/180.
        except BaseException as err:
            self.fatalErrorInClass(self.dsdCA, "Failed computing ds/dCA", err)
    
    ###################################
    #Time (in CA) derivative of cyl. volume:
    def dVdCA(self,CA:float|Iterable) -> float|np.ndarray:
        """
        Returns the time (in CA) derivative of instantaneous in-cylinder volume at CA
        Args:
            CA (float | Iterable): Time in CA
        
        Returns:
            float|np.ndarray[float]: dV/dCA [m^3/CA]
        """
        return self.dsdCA(CA) * self.cylArea
    
    ###################################
    #Instant. liner area:
    def linerArea(self,CA:float|Iterable) -> float|np.ndarray:
        """
        Returns the liner area at CA
        Args:
            CA (float | Iterable): Time in CA

        Returns:
            float|np.ndarray[float]: [m^2]
        """
        try:
            if isinstance(CA, list):
                return np.array([s * pi * self.D for s in self.s(CA)])
            else:
                return self.s(CA) * pi * self.D
        except BaseException as err:
            self.fatalErrorInClass(self.linerArea, "Failed computing liner area", err)
    
    ###################################
    def A(self,CA:float|Iterable) -> float|np.ndarray:
        """
        Returns the chamber area at CA
        Args:
            CA (float | Iterable): Time in CA

        Returns:
            float|np.ndarray[float]: [m^2]
        """
        try:
            return self.linerArea(CA) + self.pistonArea + self.headArea
        except BaseException as err:
            self.fatalErrorInClass(self.linerArea, "Failed computing chamber area", err)

    ###################################
    def areas(self,CA:float|Iterable) -> pd.DataFrame:
        """
        CA:     float / list<float/int>
            Crank angle
        
        Returns a pandas.Dataframe with area of all patches at CA
        
        Args:
            CA (float | Iterable): Time in CA

        Returns:
            pandas.Dataframe: DataFrame of areas [m^2] at CA. Columns are patch names and CA.
        """
        try:
            data = \
            {
                "CA":CA if isinstance(CA, Iterable) else [CA], 
                "liner":self.linerArea(CA) if isinstance(CA, Iterable) else [self.linerArea(CA)],
                "piston":[self.pistonArea for _ in CA] if isinstance(CA, Iterable) else [self.pistonArea],
                "head":[self.headArea for _ in CA] if isinstance(CA, Iterable) else [self.headArea],
            }
            return pd.DataFrame.from_dict(data, orient="columns")
            
        except BaseException as err:
            self.fatalErrorInClass(self.linerArea, "Failed computing patch areas", err)
    
#########################################################################
#Add to selection table:
EngineGeometry.addToRuntimeSelectionTable(ConRodGeometry)