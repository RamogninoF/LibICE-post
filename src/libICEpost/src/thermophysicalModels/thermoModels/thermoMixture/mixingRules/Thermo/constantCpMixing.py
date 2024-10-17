#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        30/01/2024
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from .ThermoMixing import ThermoMixing

from .....specie.specie.Mixture import Mixture
from .....specie.thermo.Thermo import Thermo

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class constantCpMixing(ThermoMixing):
    """
    Class handling mixing of multi-component mixture: thermodynamic data in constantCp definition.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        ThermoType: str
            Type of thermodynamic data for which it is implemented
        
        Thermo: Thermo
            The Thermo of the mixture
    """
    
    ThermoType = "constantCp"
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
            #Initialize to nan and then set with update method in base class __init__
            self._Thermo = Thermo.selector\
                (
                    self.ThermoType,
                    {
                        "Rgas":float('nan'),
                        "cp":float('nan'),
                    }
                )
            super().__init__(mix)
            
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, "Failed construction", err)
            
    #########################################################################
    #Operators:
    def _update(self, mix:Mixture=None):
        """
        Compute new properties as mass-weighted from individual specie in mixture.
        """
        #Update of base class, return if already updated
        if super()._update(mix):
            return True

        #Update
        cp = []
        hf = []
        weigths = []
        for specie in self.mix:
            if not specie.specie.name in self.thermos[self.ThermoType]:
                raise ValueError(f"Thermo.{self.ThermoType} data not found in database for specie {specie['specie'].name}.\n{self.thermos}")
            th = self.thermos[self.ThermoType][specie.specie.name]
            
            weigths.append(self._mix.Y[self.mix.index(specie.specie)])
            cp.append(th._cp)
            hf.append(th._hf)
        
        self._Thermo._cp = (sum([weigths[ii]*v for ii, v in enumerate(cp)]))
        self._Thermo._hf = (sum([weigths[ii]*v for ii, v in enumerate(hf)]))

        return False

        

#########################################################################
#Add to selection table
ThermoMixing.addToRuntimeSelectionTable(constantCpMixing)