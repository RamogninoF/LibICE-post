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
    
    NOTE: Crank angles are defined with 0 CAD at FIRING TDC
    
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
                if not entry in mandatoryEntries:
                    raise ValueError(f"Entry '{entry}' not found in contruction dictionary.")
            
            Dict = Utilities.updateKeywordArguments(inputDict, defaultDict)
            
            return cls(Dict["CR"], Dict["bore"], Dict["stroke"], Dict["conRodLen"], Dict["pistCylAreaRatio"], Dict["headCylAreaRatio"])
            
        except BaseException as err:
            cls.fatalErrorInClass(cls.__init__, "Failed constructing from dictionary", err)
        
    #########################################################################
    def __str__(self):
        STR = "{:15s} {:15.3f} {:15s}\n".format("CR", self.CR,"[-]")
        STR += "{:15s} {:15.3f} {:15s}\n".format("bore", self.D,"[m]")
        STR += "{:15s} {:15.3f} {:15s}\n".format("stroke", self.S,"[m]")
        STR += "{:15s} {:15.3f} {:15s}\n".format("conRodLen", self.l,"[m]")
        STR += "{:15s} {:15.3f} {:15s}\n".format("cylArea", self.cylArea,"[m^2]")
        STR += "{:15s} {:15.3f} {:15s}\n".format("pistonArea", self.pistonArea,"[m^2]")
        STR += "{:15s} {:15.3f} {:15s}\n".format("headArea", self.headArea,"[m^2]")
        STR += "{:15s} {:15.3f} {:15s}\n".format("Vs", self.Vs,"[m^3]")
        STR += "{:15s} {:15.3f} {:15s}\n".format("Vmin", self.Vmin,"[m^3]")
        STR += "{:15s} {:15.3f} {:15s}\n".format("Vmax", self.Vmax,"[m^3]")
        
        return STR
    
    #########################################################################
    #Constructor:
    def __init__(self, CR, bore, stroke, conRodLen, pistonCylAreaRatio=1.0, headCylAreaRatio=1.0):
        """
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
        inputDict = \
            {
                "CR"               : CR,
                "bore"             : bore,
                "stroke"           : stroke,
                "conRodLen"        : conRodLen,
                "pistCylAreaRatio" : 1.0,
                "headCylAreaRatio" : 1.0
            }
        
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
            Dict = Utilities.updateKeywordArguments(inputDict, defaultDict)
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
            
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, "Construction failed", err)
    
    #########################################################################
    #Piston position:
    def s(self,CA):
        """
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
            self.fatalErrorInClass(self.s, "", err)
    
    ###################################
    #Instant. cylinder volume:
    def V(self,CA):
        """
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
            self.fatalErrorInClass(self.V, "", err)
    
    ###################################
    #Time (in CA) derivative of cyl. volume:
    def dVdCA(self,CA):
        """
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
            self.fatalErrorInClass(self.dVdCA, "", err)
    
    ###################################
    #Instant. liner area:
    def linerArea(self,CA):
        """
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
            self.fatalErrorInClass(self.linerArea, "", err)
