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
    def __init__(self, mix:Mixture):
        """
        mix: Mixture
            The mixture
        Construct from Mixture.
        """
        try:
            self._EoS = EquationOfState.selector(self.EoSType, {"Rgas":mix.Rgas})
            
            super().__init__(mix)
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, "Failed construction", err)
            
    #########################################################################
    #Operators:
    
    #########################################################################
    def _update(self, mix:Mixture=None):
        """
        Equation of state of perfect gas mixture depend only on R*, which needs to be updated.
        
        Pv/R*T = 1
        """
        if super()._update(mix):
            return True
        self._EoS.Rgas = self.mix.Rgas
        return False

#########################################################################
#Add to selection table:
EquationOfStateMixing.addToRuntimeSelectionTable(PerfectGasMixing)