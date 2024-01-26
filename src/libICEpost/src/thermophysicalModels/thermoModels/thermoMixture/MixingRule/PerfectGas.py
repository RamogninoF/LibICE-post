#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        17/10/2023
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from .MixingRule import MixingRule
from ....specie.thermo.EquationOfState import EquationOfState

from ....specie.specie.Mixture import Mixture

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class PerfectGas(MixingRule):
    """
    Class handling mixing rule of multi-component mixture of perfect gasses.
    
    Defines a moethod to generate the equation of state of a mixture of gasses.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        EoSType: str
            Type of equation of state for which it is implemented
        
        EoS: EquationOfState
            The eqation of state of the mixture
    """
    
    EoSType = "PerfectGas"
    #########################################################################
    @classmethod
    def fromDictionary(cls, dictionary):
        """
        Create from dictionary.
        """
        try:
            entryList = ["mixture"]
            for entry in entryList:
                if not entry in dictionary:
                    raise ValueError(f"Mandatory entry '{entry}' not found in dictionary.")
            
            out = cls\
                (
                    dictionary["mixture"]
                )
            return out
            
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed construction from dictionary", err)
    
    #########################################################################
    #Constructor:
    # No overloading, calling the base-class constructor
            
    #########################################################################
    #Operators:
    
    #########################################################################
    def _update(self, mix:Mixture):
        """
        Method to update the equation of state based on the mixture composition (implementation).
        """
        #Equation of state of perfect gas mixture depend only on R*, which needs to be updated.
        #
        # Pv/R*T = 1

        self._Eos.Rgas = Mixture.Rgas