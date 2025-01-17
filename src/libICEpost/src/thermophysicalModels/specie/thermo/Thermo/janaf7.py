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

from libICEpost.Database.chemistry.constants import database
Tstd = database.chemistry.constants.Tstd

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class janaf7(Thermo):
    """
    Class for computation of thermophysical properties with NASA (janaf) 7-coefficient polynomials.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        Rgas: float
            The mass specific gas constant
        
        cpLow:  list<float>
            List of polynomial coefficients to compute cp of the specie
            in the range of temperature below Tth
            
        cpHigh: list<float>
            List of polynomial coefficients to compute cp of the specie
            in the range of temperature above Tth
            
        Tth:    float
            Threshold temperature to change polynomial coefficient to
            be used to compute the cp of the specie
            
        Tlow:   float
            Lower limit of the range of valodity of the polynomial
            coefficients for computation of cp
            
        Thigh:   float
            Higher limit of the range of valodity of the polynomial
            coefficients for computation of cp
    """
    
    #########################################################################
    
    numCoeffs = 7
    """Number of coefficients"""
    
    cpLow:list[float]
    """Low-temperature coefficients"""
    
    cpHigh:list[float]
    """High-temperature coefficients"""
    
    Tlow:float
    """Lower-limit of validity"""
    
    Thigh:float
    """Higher-limit of validity"""
    
    Tth:float
    """Threshold temperature for changing between low-T and high-T coefficients"""
    
    #########################################################################
    #Constructor:
    def __init__(self, Rgas:float, cpLow:Iterable[float], cpHigh:Iterable[float], Tth:float, Tlow:float, Thigh:float):
        """
        Rgas: float
            The mass specific gas constant
        cpLow:  list<float>
            List of polynomial coefficients to compute cp of the specie
            in the range of temperature below Tth
        cpHigh: list<float>
            List of polynomial coefficients to compute cp of the specie
            in the range of temperature above Tth
        Tth:    float
            Threshold temperature to change polynomial coefficient to
            be used to compute the cp of the specie
        Tlow:   float
            Lower limit of the range of valodity of the polynomial
            coefficients for computation of cp
        Thigh:   float
            Higher limit of the range of valodity of the polynomial
            coefficients for computation of cp
        """
        #Argument checking:
        super().__init__(Rgas)
        self.checkType(cpLow, Iterable, entryName="cpLow")
        self.checkType(cpHigh, Iterable, entryName="cpHigh")
        [self.checkType(c, float, entryName=f"cpLow[{ii}]") for ii, c in enumerate(cpLow)]
        [self.checkType(c, float, entryName=f"cpHigh[{ii}]") for ii, c in enumerate(cpHigh)]
        self.checkType(Tth, float, entryName="Tth")
        self.checkType(Tlow, float, entryName="Tlow")
        self.checkType(Thigh, float, entryName="Thigh")
        
        if not(len(cpLow) == self.numCoeffs) or not(len(cpHigh) == self.numCoeffs):
            raise ValueError("Required lists of 7 coefficients for 'cpLow' and 'cpHigh'.")
        
        self.cpLow = cpLow[:]
        self.cpHigh = cpHigh[:]
        self.Tth = Tth
        self.Tlow = Tlow
        self.Thigh = Thigh
        
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
        R = eval(super(self.__class__,self).__repr__())
        R["cpLow"]   = self.cpLow 
        R["cpHigh"]  = self.cpHigh 
        R["Tth"]     = self.Tth    
        R["Tlow"]    = self.Tlow   
        R["Thigh"]   = self.Thigh  
                       
        return R.__repr__()
    
    #########################################################################
    #Member functions:
    def coeffs(self, T:float) -> float:
        """
        Get coefficients, depending on temperature range.
        """
        # if (T < self.Tlow) or (T > self.Thigh):
        #     self.__class__.runtimeWarning("Temperature outside of range ["+ "{:.3f}".format(self.Tlow) + ","+ "{:.3f}".format(self.Thigh) + "] (T = "+ "{:.3f}".format(T) + " [K])")
        
        if T < self.Tth:
            return self.cpLow
        else:
            return self.cpHigh
    
    ################################
    def cp(self, p:float, T:float) -> float:
        """
        Constant pressure heat capacity [J/kg/K].
        If the temperature is not within Tlow and Thigh, a
        warning is displayed.
            
        cp(T) = sum_{i=0,4} ( a_{i} * T^i )
        """
        #Argument checking
        super().cp(p,T)
        
        coeffs = self.coeffs(T)
        
        cp = 0.0
        for nn in [0, 1, 2, 3, 4]:
            cp += coeffs[nn] * (T **nn)
        
        return cp*self.Rgas
    
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
        
        ha = coeffs[5]
        for nn in [0, 1, 2, 3, 4]:
            ha += coeffs[nn] * (T ** (nn + 1)) / (nn + 1.0)
        
        return ha*self.Rgas
    
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
        
        dcpdT = 0.0
        for nn in [1, 2, 3, 4]:
            dcpdT += nn * coeffs[nn] * (T ** (nn - 1))
        
        return dcpdT*self.Rgas
    
    #########################################################################
    @classmethod
    def fromDictionary(cls,dictionary):
        """
        Create from dictionary.

        {
            Rgas: float
                The mass specific gas constant
            cpLow:  list<float>
                List of polynomial coefficients to compute cp of the specie
                in the range of temperature below Tth
            cpHigh: list<float>
                List of polynomial coefficients to compute cp of the specie
                in the range of temperature above Tth
            Tth:    float
                Threshold temperature to change polynomial coefficient to
                be used to compute the cp of the specie
            Tlow:   float
                Lower limit of the range of valodity of the polynomial
                coefficients for computation of cp
            Thigh:   float
                Higher limit of the range of valodity of the polynomial
                coefficients for computation of cp
        }
        """
        entryList = ["specie", "cpLow", "cpHigh", "Tth", "Tlow", "Thigh"]
        for entry in entryList:
            if not entry in dictionary:
                raise ValueError(f"Mandatory entry '{entry}' not found in dictionary.")
        
        out = cls\
            (
                dictionary["specie"], 
                dictionary["cpLow"], 
                dictionary["cpHigh"], 
                dictionary["Tth"], 
                dictionary["Tlow"], 
                dictionary["Thigh"]
            )
        return out
    
#############################################################################
Thermo.addToRuntimeSelectionTable(janaf7)

#############################################################################
#Load database:
import libICEpost.Database.chemistry.thermo.Thermo.janaf7