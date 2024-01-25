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

from .Thermo import Thermo

from Database.chemistry.constants import Tstd
from numpy import math

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class janaf7(Thermo):
    """
    Class for computation of thermophysical properties with janaf 7 coefficient polynomials.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        specie: Molecule
            Chemical specie for which the thermodynamic properties are defined
        
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
    
    #########################################################################
    #Constructor:
    def __init__(self, specie, cpLow, cpHigh, Tth, Tlow, Thigh):
        """
        specie: Molecule
            Chemical specie for which the thermodynamic properties are defined
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
        super(self.__class__, self).__init__(specie)
        try:
            self.checkInstanceTemplate(cpLow, [1.0], entryName="cpLow")
            self.checkInstanceTemplate(cpHigh, [1.0], entryName="cpHigh")
            self.checkType(Tth, float, entryName="Tth")
            self.checkType(Tlow, float, entryName="Tlow")
            self.checkType(Thigh, float, entryName="Thigh")
            
            if not(len(cpLow) == self.numCoeffs) or not(len(cpHigh) == self.numCoeffs):
                raise ValueError("Required lists of 7 coefficients for 'cpLow' and 'cpHigh'.")
        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
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
    def coeffs(self, T):
        """
        Get coefficients, depending on temperature range.
        """
        if (T < self.Tlow) or (T > self.Thigh):
            self.__class__.runtimeWarning("Temperature outside of range ["+ "{:.3f}".format(self.Tlow) + ","+ "{:.3f}".format(self.Thigh) + "] for specie " + self.specie.name + "(T = "+ "{:.3f}".format(T) + " [K])")
        
        if T < self.Tth:
            return self.cpLow
        else:
            return self.cpHigh
    
    ################################
    def cp(self, p, T):
        """
        Constant pressure heat capacity [J/kg/K].
        If the temperature is not within Tlow and Thigh, a
        warning is displayed.
            
        cp(T) = sum_{i=0,4} ( a_{i} * T^i )
        """
        
        #Argument checking
        super(self.__class__,self).cp(p,T)
        
        coeffs = self.coeffs(T)
        
        cp = 0.0
        for nn in [0, 1, 2, 3, 4]:
            cp += coeffs[nn] * (T **nn)
        
        return cp*self.specie.Rgas()
    
    ##################################
    #Constant volume heat capacity
    def cv(self,p,T):
        """
        Constant volume heat capacity [J/kg/K].
        If the temperature is not within Tlow and Thigh, a
        warning is displayed.
        
        cv(p,T) = cp(p,T) - R
        """
        #Argument checking
        super(self.__class__,self).cv(p,T)
        
        return (self.cp(p,T) - self.specie.Rgas())
    
    ##################################
    #Gamma
    def gamma(self,p,T):
        """
        Heat capacity ratio cp/cv [-]. 
        If the temperature is not within Tlow and Thigh, a warning is 
        displayed.
        
        gammma(T) = cp(T)/cv(T)
        """
        #Argument checking
        super(self.__class__,self).gamma(p,T)
        
        return (self.cp(p,T) / self.cv(p,T))
    
    ################################
    def ha(self, p, T):
        """
        Absolute enthalpy [J/kg]
        If the temperature is not within Tlow and Thigh, a
        warning is displayed.
        
                
        ha(T) = sum_{i=0,4} ( a_{i}/(i + 1) * T^i )*T + a_{5}
        """
        
        #Argument checking
        super(self.__class__,self).ha(p,T)
        
        coeffs= self.coeffs(T)
        
        ha = coeffs[5]
        for nn in [0, 1, 2, 3, 4]:
            ha += coeffs[nn] * (T ** (nn + 1)) / (nn + 1.0)
        
        return ha*self.specie.Rgas()
    
    ##################################
    def hf(self):
        """
        Enthalpy of formation [J/kg]
        
        hf = ha(Tstd)
        """
        return self.ha(0.,Tstd)
    
    ################################
    def dcpdT(self, p, T):
        """
        dcp/dT [J/kg/K^2]
        If the temperature is not within Tlow and Thigh, a
        warning is displayed.
            
        dcp/dT(T) = sum_{i=1,4}(i * a_{i} * T^(i - 1))
        """
        super(self.__class__,self).dcpdT(p,T)
        
        coeffs = self.coeffs(T)
        
        dcpdT = 0.0
        for nn in [1, 2, 3, 4]:
            dcpdT += nn * coeffs[nn] * (T ** (nn - 1))
        
        return dcpdT*self.specie.Rgas()
    
    #########################################################################
    @classmethod
    def fromDictionary(cls,dictionary):
        """
        Create from dictionary.
        """
        try:
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
            
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed construction from dictionary", err)
    
#############################################################################
janaf7.addToRuntimeSelectionTable("janaf7")

