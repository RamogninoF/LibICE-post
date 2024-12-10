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

from .EquationOfStateMixing import EquationOfStateMixing
from .....specie.thermo.EquationOfState import EquationOfState
from .....specie.specie.Mixture import Mixture

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class PerfectGasMixing(EquationOfStateMixing):
    """
    Class handling mixing rule of multi-component mixture of perfect gasses.
    
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
        entryList = ["mixture"]
        for entry in entryList:
            if not entry in dictionary:
                raise ValueError(f"Mandatory entry '{entry}' not found in dictionary.")
        
        out = cls\
            (
                dictionary["mixture"]
            )
        return out
    
    #########################################################################
    #Constructor:
    def __init__(self, mix:Mixture):
        """
        mix: Mixture
            The mixture
        Construct from Mixture.
        """
        self._EoS = EquationOfState.selector(self.EoSType, {"Rgas":mix.Rgas})
        super().__init__(mix)
        
    #########################################################################
    #Operators:
    
    #########################################################################
    def _update(self, mix:Mixture=None) -> bool:
        """
        Equation of state of perfect gas mixture depend only on R*. Update only the mixture composition.
        
        Pv/R*T = 1
        
        Returns:
            bool: if womething changed
        """
        super()._update(mix)
        self._EoS.Rgas = self.mix.Rgas
        return True

#########################################################################
#Add to selection table:
EquationOfStateMixing.addToRuntimeSelectionTable(PerfectGasMixing)