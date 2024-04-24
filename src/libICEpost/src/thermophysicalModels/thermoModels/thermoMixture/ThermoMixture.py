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

from libICEpost.src.base.Utilities import Utilities

from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture
from . import mixingRules

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class ThermoMixture(Utilities):
    """
    Class for computing thermodynamic data of a mixture.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        _mix:    Mixture
            The composition of the mixture.
        
        _EoS: mixingRules.EquationOfState
            The mixing rule used for computation of the equation of state of the mixture.

        _Thermo: mixingRules.Thermo
            The mixing rule used for computation of the thermo of the mixture.
    """
    
    #########################################################################
    #Properties:

    @property
    def mix(self):
        """
        The composition of the mixture (Mixture).
        """
        return self._mix
    
    ################################
    @property
    def db(self):
        """
        Database of thermodynamic data (reference to database.chemistry.thermo)
        """
        return self._db
    
    ################################
    @property
    def Thermo(self):
        """
        Thermodynamic data of this mixture.
        """
        return self._Thermo.Thermo
    
    ################################
    @property
    def EoS(self):
        """
        The equation of state of this mixture.
        """
        return self._EoS.EoS

    #########################################################################
    #Constructor:
    def __init__(self, mixture: Mixture, ThermoType: str, EoSType: str, ThermoDict=None, EoSDict=None):
        """
        mixture:    ThermoTable
            The composition of the mixture.
        
        ThermoType: str
            There MixingRules.Thermo type to use
        
        EoSType: str
            There MixingRules.EquationOfState type to use
        
        Construct new instance of thermodynamic model of mixture from the mixture composition and mixingRule
        """
        from libICEpost.Database.chemistry.thermo import database

        try:
            self.checkType(mixture, Mixture, "mixture")
            self.checkType(ThermoType, str, "ThermoType")
            self.checkType(EoSType, str, "EoSType")

            self._db = database.chemistry.thermo
            self._mix = mixture
            
            #Set the dictionaries
            if ThermoDict is None:
                ThermoDict = {"mixture":mixture}
            else:
                ThermoDict["mixture"] = mixture
            
            if EoSDict is None:
                EoSDict = {"mixture":mixture}
            else:
                EoSDict["mixture"] = mixture
                
            self._Thermo = mixingRules.ThermoMixing.selector(ThermoType + "Mixing", ThermoDict)
            self._EoS = mixingRules.EquationOfStateMixing.selector(EoSType + "Mixing", EoSDict)
                
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, "Failed construction", err)
        
    #########################################################################
    #Operators:
    
    #########################################################################
    #Member functions:
    #NOTE: the derivatives of thermodynamic quantities (p,T,rho) 
    # are defined only in the equation of state, as they are not 
    # affected by the specific thermo. Similarly, hf is only in 
    # thermo.
    
    ################################
    def dcpdT(self, p, T):
        """
        dcp/dT [J/kg/K^2]
        """
        return self.Thermo.dcpdT(p, T) + self.EoS.dcpdT(p, T)
        
    
    ################################
    def ha(self, p, T):
        """
        Absolute enthalpy [J/kg]
        """
        return self.Thermo.ha(p, T) + self.EoS.h(p, T)
    
    ################################
    def cp(self, p, T):
        """
        Constant pressure heat capacity [J/kg/K]
        """
        return self.Thermo.cp(p, T) + self.EoS.cp(p, T)
    
    ################################
    def cv(self, p, T):
        """
        Constant volume heat capacity [J/kg/K]
        """
        return self.cp(p, T) - self.EoS.cpMcv(p, T)
    
    ################################
    def gamma(self, p, T):
        """
        Heat capacity ratio cp/cv [-]
        """
        return self.cp(p, T)/self.cv(p, T)