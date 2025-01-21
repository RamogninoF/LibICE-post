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

from typing import Iterable

from .Thermo import Thermo

from libICEpost import Dictionary
from libICEpost.Database.chemistry.constants import database
Tstd = database.chemistry.constants.Tstd

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class janaf7(Thermo):
    """
    Class for computation of thermophysical properties with NASA (janaf) 7-coefficient polynomials.
        cp(T) = sum_{i=0,4} ( a_{i} * T^i )
        ha(T) = sum_{i=0,4} ( a_{i}/(i + 1) * T^i )*T + a_{5}
        s(T) = sum_{i=0,4} ( a_{i}/(i + 1) * T^i ) + a_{5} * ln(T) + a_{6}
    
    Attibutes:
        - Rgas (float): The mass specific gas constant.
        - cpLow (Iterable[float]): List of polynomial coefficients to compute cp of the specie in the range of temperature below Tth.
        - cpHigh (Iterable[float]): List of polynomial coefficients to compute cp of the specie in the range of temperature above Tth.
        - Tth (float): Threshold temperature to change polynomial coefficient to be used to compute the cp of the specie.
        - Tlow (float): Lower limit of the range of validity of the polynomial coefficients for computation of cp.
        - Thigh (float): Higher limit of the range of validity of the polynomial coefficients for computation of cp.
    """
    
    #########################################################################
    
    __WARNING__ = False
    """If True, a warning is displayed when the temperature is outside of the range of validity."""
    
    numCoeffs = 7
    """Number of coefficients"""
    
    _cpLow:list[float]
    """Low-temperature coefficients"""
    
    _cpHigh:list[float]
    """High-temperature coefficients"""
    
    _Tlow:float
    """Lower-limit of validity"""
    
    _Thigh:float
    """Higher-limit of validity"""
    
    _Tth:float
    """Threshold temperature for changing between low-T and high-T coefficients"""

    #########################################################################
    #Properties:
    @property
    def cpLow(self) -> list[float]:
        """Low-temperature coefficients"""
        return self._cpLow[:]

    @property
    def cpHigh(self) -> list[float]:
        """High-temperature coefficients"""
        return self._cpHigh[:]

    @property
    def Tlow(self) -> float:
        """Lower-limit of validity"""
        return self._Tlow

    @property
    def Thigh(self) -> float:
        """Higher-limit of validity"""
        return self._Thigh

    @property
    def Tth(self) -> float:
        """Threshold temperature for changing between low-T and high-T coefficients"""
        return self._Tth
    
    #########################################################################
    #Class methods:
    def copy(self):
        """
        Create a copy with the same coefficients.
        
        Returns:
            janaf7: The copied object.
        """
        return janaf7(self.Rgas, self.cpLow, self.cpHigh, self.Tth, self.Tlow, self.Thigh)
    
    #########################################################################
    #Constructor:
    def __init__(self, Rgas:float, cpLow:Iterable[float], cpHigh:Iterable[float], Tth:float, Tlow:float, Thigh:float):
        """
        Initializes the thermo model with specific gas constant and polynomial coefficients.
        Args:
            Rgas (float): The mass specific gas constant.
            cpLow (Iterable[float]): List of polynomial coefficients to compute cp of the specie
                in the range of temperature below Tth.
            cpHigh (Iterable[float]): List of polynomial coefficients to compute cp of the specie
                in the range of temperature above Tth.
            Tth (float): Threshold temperature to change polynomial coefficient to
                be used to compute the cp of the specie.
            Tlow (float): Lower limit of the range of validity of the polynomial
                coefficients for computation of cp.
            Thigh (float): Higher limit of the range of validity of the polynomial
                coefficients for computation of cp.
        Raises:
            ValueError: If the length of cpLow or cpHigh is not equal to the required number of coefficients.
        """
        #Argument checking:
        super().__init__(Rgas)
        self.checkArray(cpLow, float, entryName="cpLow")
        self.checkArray(cpHigh, float, entryName="cpHigh")
        self.checkType(Tth, float, entryName="Tth")
        self.checkType(Tlow, float, entryName="Tlow")
        self.checkType(Thigh, float, entryName="Thigh")
        
        if not(len(cpLow) == self.numCoeffs) or not(len(cpHigh) == self.numCoeffs):
            raise ValueError("Required lists of 7 coefficients for 'cpLow' and 'cpHigh'.")
        
        self._cpLow = cpLow[:]
        self._cpHigh = cpHigh[:]
        self._Tth = Tth
        self._Tlow = Tlow
        self._Thigh = Thigh
        
    #########################################################################
    #Operators:
    
    ################################
    #Print:
    def __str__(self):
        StrToPrint = Thermo.__str__(self)
        
        hLine = lambda a: (("-"*(len(a)-1)) + "\n")
        
        template1 = "| {:10s}| "
        template2 = "{:10s}   "
        template3 = "{:.3e}"
        
        title = template1.format("Coeffs")
        for ii in range(len(self.cpLow)):
            title += template2.format("c_" + str(ii))
        title += "|\n"
        
        StrToPrint += hLine(title)
        StrToPrint += title
        StrToPrint += hLine(title)
        
        StrToPrint += template1.format("High")
        for ii in range(len(self.cpLow)):
            if (len(self.cpHigh) > ii):
                StrToPrint += template2.format(template3.format(self.cpHigh[ii]))
            else:
                StrToPrint += template2.format("")
        StrToPrint += "|\n"
        
        StrToPrint += template1.format("Low")
        for ii in range(len(self.cpLow)):
            if (len(self.cpHigh) > ii):
                StrToPrint += template2.format(template3.format(self.cpHigh[ii]))
            else:
                StrToPrint += template2.format("")
        StrToPrint += "|\n"
        
        StrToPrint += hLine(title)
        
        template = "| {:10} | {:10} | {:10}|\n"
        StrToPrint += hLine(template.format("","",""))
        StrToPrint += template.format("Tlow", "Thigh", "Tth")
        StrToPrint += hLine(template.format("","",""))
        StrToPrint += template.format(self.Tlow, self.Thigh, self.Tth)
        StrToPrint += hLine(template.format("","",""))
        
        return StrToPrint
    
    ##############################
    #Representation:
    def __repr__(self):
        R = {}
        R["Rgas"]    = self.Rgas
        R["cpLow"]   = self.cpLow 
        R["cpHigh"]  = self.cpHigh 
        R["Tth"]     = self.Tth    
        R["Tlow"]    = self.Tlow   
        R["Thigh"]   = self.Thigh  
                       
        return f"{self.TypeName}{R.__repr__()}"
    
    #########################################################################
    #Member functions:
    def coeffs(self, T:float) -> Iterable[float]:
        """
        Get coefficients, depending on temperature range.
        - If T < Tth, returns cpLow
        - If T >= Tth, returns cpHigh
        
        Args:
            T (float): Temperature [K].
        
        Returns:
            Iterable[float]: The coefficients to be used for the computation of cp.
        """
        if (T < self.Tlow) or (T > self.Thigh) and self.__class__.__WARNING__:
            self.runtimeWarning("Temperature outside of range ["+ "{:.3f}".format(self.Tlow) + ","+ "{:.3f}".format(self.Thigh) + "] (T = "+ "{:.3f}".format(T) + " [K])")
        
        if T < self.Tth:
            return self.cpLow
        else:
            return self.cpHigh
    
    ################################
    def cp(self, p:float, T:float) -> float:
        """
        Constant pressure heat capacity [J/kg/K].
        If the temperature is not within Tlow and Thigh, 
        and janaf7.__WARNING__ is True a warning is displayed.
        
        cp(T) = sum_{i=0,4} ( a_{i} * T^i )
        """
        #Argument checking
        super().cp(p,T)
        
        coeffs = self.coeffs(T)
        return sum(coeffs[nn] * (T ** nn) for nn in [0, 1, 2, 3, 4])*self.Rgas
    
    ################################
    def ha(self, p:float, T:float) -> float:
        """
        Absolute enthalpy [J/kg]
        If the temperature is not within Tlow and Thigh, a
        warning is displayed.
        
                
        ha(T) = sum_{i=0,4} ( a_{i}/(i + 1) * T^i )*T + a_{5}
        """
        #Argument checking
        try:
            super().ha(p,T)
        except NotImplementedError:
            #Passed the check of p and T
            pass
        
        coeffs= self.coeffs(T)
        return (coeffs[5] + sum(coeffs[nn] * (T ** (nn + 1)) / (nn + 1.0) for nn in [0, 1, 2, 3, 4]))*self.Rgas
    
    ##################################
    def hf(self) -> float:
        """
        Enthalpy of formation [J/kg]
        
        hf = ha(Tstd)
        """
        return self.ha(0.,Tstd)
    
    ################################
    def dcpdT(self, p:float, T:float) -> float:
        """
        dcp/dT [J/kg/K^2]
        If the temperature is not within Tlow and Thigh, a
        warning is displayed.
            
        dcp/dT(T) = sum_{i=1,4}(i * a_{i} * T^(i - 1))
        """
        #Check arguments
        super().dcpdT(p,T)
        
        coeffs = self.coeffs(T)
        return sum(nn * coeffs[nn] * (T ** (nn - 1)) for nn in [1, 2, 3, 4])*self.Rgas
    
    #########################################################################
    @classmethod
    def fromDictionary(cls,dictionary):
        """
        Create from dictionary with the following entries:
            - Rgas (float): The mass specific gas constant.
            - cpLow (Iterable[float]): List of polynomial coefficients to compute cp of the specie in the range of temperature below Tth.
            - cpHigh (Iterable[float]): List of polynomial coefficients to compute cp of the specie in the range of temperature above Tth.
            - Tth (float): Threshold temperature to change polynomial coefficient to be used to compute the cp of the specie.
            - Tlow (float): Lower limit of the range of validity of the polynomial coefficients for computation of cp.
            - Thigh (float): Higher limit of the range of validity of the polynomial coefficients for computation of cp.
        
        Args:
            dictionary (dict): Dictionary for construction.
        
        Returns:
            janaf7: The constructed object.
        """
        dictionary = Dictionary(**dictionary)
        #Here check only the presence of the keys, argument checking is done in the constructor
        return cls(
            dictionary.lookup("Rgas"),
            dictionary.lookup("cpLow"),
            dictionary.lookup("cpHigh"),
            dictionary.lookup("Tth"),
            dictionary.lookup("Tlow"),
            dictionary.lookup("Thigh")
            )
    
#############################################################################
Thermo.addToRuntimeSelectionTable(janaf7)

#############################################################################
#Load database:
import libICEpost.Database.chemistry.thermo.Thermo.janaf7