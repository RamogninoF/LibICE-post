#####################################################################
#                               IMPORT                              #
#####################################################################

from src.thermophysicalModels.specie.thermo.Thermo import Thermo

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Laminar flame speed computation with Gulder correlation:
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
    
    #Name:
    typeName = "janaf7"
    
    numCoeffs = 7
    
    cpLow = [float("nan")]*numCoeffs
    cpHigh = [float("nan")]*numCoeffs
    Tth = float("nan")
    Tlow = float("nan")
    Thigh = float("nan")
    
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
            self.__class__.checkInstanceTemplate(cpLow, [1.0], entryName="cpLow")
            self.__class__.checkInstanceTemplate(cpHigh, [1.0], entryName="cpHigh")
            self.__class__.checkType(Tth, float, entryName="Tth")
            self.__class__.checkType(Tlow, float, entryName="Tlow")
            self.__class__.checkType(Thigh, float, entryName="Thigh")
            
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
    
    #########################################################################
    #Member functions:
    
    ################################
    def cp(self,T):
        self.__class__.cp.__doc__ = \
        """
        Returns the constant pressure heat capacity at temperature T of the 
        chemical specie. If the temperature is not within Tlow and Thigh, a
        warning is displayed.
            
                | sum_{i=0,n} ( a_{i,low} * T^i )     if T < Tth
        cp(T) = |
                | sum_{i=0,n} ( a_{i,high} * T^i )    if T >= Tth
        """
        self.__class__.cp.__doc__ += "\n\twith n = {}".format(self.numCoeffs-2)
        
        #Argument checking
        super(self.__class__,self).cp(T)
        
        if (T < self.Tlow) or (T > self.Thigh):
            self.__class__.runtimeWarning("Temperature outside of range ["+ "{:.3f}".format(self.Tlow) + ","+ "{:.3f}".format(self.Thigh) + "] for specie " + self.specie.name + "(T = "+ "{:.3f}".format(T) + " [K])")
        
        cp = 0.0
        if(T > self.Tth):
            for nn in range(self.numCoeffs-2):
                cp += self.cpHigh[nn] * (T **nn)
        else:
            for nn in range(self.numCoeffs-2):
                cp += self.cpLow[nn] * (T **nn)
        
        return cp*self.specie.Rgas()
    
    ##################################
    #Constant volume heat capacity
    def cv(self,T):
        """
        Returns the constant volume heat capacity at temperature T of the 
        chemical specie. If the temperature is not within Tlow and Thigh, a
        warning is displayed.
        
        cv(T) = cp(T) - R
        """
        #Argument checking
        super(self.__class__,self).cv(T)
        
        return (self.cp(T) - self.specie.Rgas())
    
    ##################################
    #Gamma
    def gamma(self,T):
        """
        Returns the ratio cp/cv at temperature T of the chemical specie. 
        If the temperature is not within Tlow and Thigh, a warning is 
        displayed.
        
        gammma(T) = cp(T)/cv(T)
        """
        #Argument checking
        super(self.__class__,self).gamma(T)
        
        return (self.cp(T) / self.cv(T))
        
