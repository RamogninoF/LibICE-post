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

from pylab import math, cos, sin, sqrt, radians, degrees

from src.base.Utilities import Utilities

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class engineGeometry(Utilities):
    """
    Base class for handling engine geometrical parameters during cycle.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        
        [Variable] | [Type]     | [Unit] | [Description]
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
        -----------|------------|--------|-------------------------
        IVC        | float      | CA     | Inlet valve closing
        EVO        | float      | CA     | Inlet valve closing
        -----------|------------|--------|-------------------------
        n          | float      | rpm    | Rotational speed
        omega      | float      | rad/s  | 
        upMean     | float      | m/s    | Mean piston speed
    """
    
    #########################################################################
    #Constructor:
    def __init__(self,inputDict={}, **argv):
        """
        Construct from dictionary or keyword arguments containing the following parameters:
        
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
        ------------------|--------|-----------|--------|----------------------------------
        IVC               | float  | -         | CA     | Inlet valve closing
        EVO               | float  | -         | CA     | Inlet valve closing
        ------------------|--------|-----------|--------|----------------------------------
        speed             | float  | -         | rpm    | Rotational speed
        
        """
        mandatoryEntries = ["CR", "bore", "stroke", "conRodLen", "IVC", "EVO", "speed"]
        
        defaultDict = \
            {
                "CR"               : float('nan'),
                "bore"             : float('nan'),
                "stroke"           : float('nan'),
                "conRodLen"        : float('nan'),
                "pistCylAreaRatio" : 1.0,
                "headCylAreaRatio" : 1.0,
                "IVC"              : float('nan'),
                "EVO"              : float('nan'),
                "speed"            : float('nan'),
            }
        
        #Argument checking:
        try:
            for entry in mandatoryEntries:
                if not entry in mandatoryEntries:
                    raise ValueError(f"Entry '{entry}' not found in contruction dictionary.")
            
            Dict = Utilities.updateKeywordArguments(inputDict, defaultDict)
            Dict = Utilities.updateKeywordArguments(argv, defaultDict)
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        try:
            #[-]
            self.CR = Dict["CR"]
            self.lam = .5*Dict["stroke"]/Dict["conRodLen"]
            #[m]
            self.D = Dict["bore"]
            self.S = Dict["stroke"]
            self.l = Dict["conRodLen"]
            #[m^2]
            self.cylArea = math.pi * Dict["bore"]**2 / 4.0
            self.pistonArea = self.cylArea * Dict["pistCylAreaRatio"]
            self.headArea = self.cylArea * Dict["headCylAreaRatio"]
            #[m^3]
            self.Vs = math.pi * Dict["bore"]**2 / 4.0 * Dict["stroke"]
            self.Vmin = self.Vs/(Dict["CR"] - 1.0)
            self.Vmax = self.Vs + self.Vmin
            
            #[other]
            self.n = Dict["speed"]
            self.omega = Dict["speed"] / 60.0 * 2.0 * math.pi
            self.upMean = 2.0 * Dict["stroke"] * Dict["speed"] / 60.
            self.IVC = Dict["IVC"]
            self.EVO = Dict["EVO"]
        except BaseException as err:
            self.fatalErrorIn(self.__init__, "Construction failed", err)
    
    #########################################################################
    #Piston position:
    def s(self,CA):
        """
        s(CA):
            CA:     float / list<float/int>
                Crank angle
            
            Returns the piston position at CA (reference to TDC)
        """
        def f(angle):
            return self.S/2.0 * (1.0 + 1.0 / self.lam - cos(1.*angle) - 1.0/self.lam * sqrt(1.0 - self.lam**2 * sin(1.*angle)**2))
        
        try:
            if isinstance(CA, list):
                return [f(radians(ca)) for ca in CA]
            else:
                return f(radians(ca))
        except BaseException as err:
            self.fatalErrorIn(self.s, "", err)
    
    ###################################
    #Instant. cylinder volume:
    def V(self,CA):
        """
        V(CA):
            CA:     float / list<float/int>
                Crank angle
            
            Returns the instantaneous in-cylinder volume at CA
        """
        def f(ca):
            return self.Vmin + self.s(ca)*self.cylArea
        
        try:
            if isinstance(CA, list):
                return [f(ca) for ca in CA]
            else:
                return f(CA)
        except BaseException as err:
            self.fatalErrorIn(self.V, "", err)
    
    ###################################
    #Time (in CA) derivative of cyl. volume:
    def dVdCA(self,CA):
        """
        dVdCA(CA):
            CA:     float / list<float/int>
                Crank angle
            
            Returns the time (in CA) derivative of instantaneous in-cylinder at CA
        """
        def f(angle):
            return 0.5 * self.Vs * (sin(1.*angle)+(self.lam*sin(2.0*angle))/(2.0 * sqrt(1.0 - self.lam**2 * sin(1.*angle)**2)))
        
        try:
            if isinstance(CA, list):
                return [f(radians(ca)) for ca in CA]
            else:
                return f(radians(CA))
        except BaseException as err:
            self.fatalErrorIn(self.dVdCA, "", err)
    
    ###################################
    #Instant. liner area:
    def linerArea(self,CA):
        """
        linerArea(CA):
            CA:     float / list<float/int>
                Crank angle
            
            Returns the liner area at CA
        """
        try:
            if isinstance(CA, list):
                return [s * math.pi * self.D for s in self.s(ca)]
            else:
                return self.s(CA) * math.pi * self.D
        except BaseException as err:
            self.fatalErrorIn(self.linerArea, "", err)
    
    ###################################
    #CA to Time:
    def CA2Time(self,CA):
        """
        CA2Time(CA):
            CA:     float / list<float/int>
                Crank angle
            
            Converts CA to time [s]
        """
        try:
            if isinstance(t, list):
                return [ca / (self.n * 6.0) for ca in CA]
            else:
                return CA / (self.n * 6.0)
        except BaseException as err:
            self.fatalErrorIn(self.CA2Time, "", err)
    
    ###################################
    #Time to CA:
    def Time2CA(self,t):
        """
        Time2CA(CA):
            CA:     float / list<float/int>
                Crank angle
            
            Converts time [s] to CA
        """
        try:
            if isinstance(t, list):
                return [T * self.n * 6.0 for T in t]
            else:
                return t * self.n * 6.0
        except BaseException as err:
            self.fatalErrorIn(self.Time2CA, "", err)
