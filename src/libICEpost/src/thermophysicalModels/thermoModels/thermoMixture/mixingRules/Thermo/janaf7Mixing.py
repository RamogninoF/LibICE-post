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

from .ThermoMixing import ThermoMixing

from .....specie.specie.Mixture import Mixture
from .....specie.thermo.Thermo import Thermo

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class janaf7Mixing(ThermoMixing):
    """
    Class handling mixing of multi-component mixture: thermodynamic data in janaf7 definition.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        ThermoType: str
            Type of thermodynamic data for which it is implemented
        
        Thermo: Thermo
            The Thermo of the mixture
    """
    
    ThermoType = "janaf7"
    #########################################################################
    #NOTE:
    # In this case the implementation is slight different because it is not possible to define
    # the average properies of the mixture with a new janaf7 class with a mass-weighted average
    # set of coefficients. Hence, it is necessary to introduce a new class here defined consistenty
    # with Thermo implementation, and then use the properties of each component and averaging them.

    class _ThermoClass(Thermo):
        """
        Thermodynamic data of janaf7 mixture consistent with Thermo class.
        """

        ###################################
        @classmethod
        def fromDictionary(cls, dictionary:dict):
            """
            Not to be used!
            """
            raise NotImplementedError
        
        ###################################
        def __init__(self, mix:Mixture):
            self._mix = mix

        ###################################
        def _combineMethod(self, func:str, *fargs, **fkwargs):
            """
            Method for macro-ization of combination of properties based on mixture composition
            
            Args:
                func (str): the name of the method to combine

            Returns:
                Thermo.func@ReturnType: returns sum(y_i * thermo[specie_i].func(*fargs, **fkwargs))
            """
            vals = []
            weigths = []
            for specie in self._mix:
                if not specie.specie.name in janaf7Mixing.thermos[janaf7Mixing.ThermoType]:
                    raise ValueError(f"Thermo.{janaf7Mixing.ThermoType} data not found in database for specie {specie['specie'].name}.\n{janaf7Mixing.thermos}")
                th = janaf7Mixing.thermos[janaf7Mixing.ThermoType][specie.specie.name]
                
                weigths.append(self._mix.Y[self._mix.index(specie.specie)])
                vals.append(th.__getattribute__(func)(*fargs, **fkwargs))

            return (sum([weigths[ii]*v for ii, v in enumerate(vals)]))

        ###################################
        def cp(self, p:float, T:float) -> float:
            super().cp(p, T)
            return self._combineMethod("cp", p, T)
        
        ###################################
        def dcpdT(self, p:float, T:float) -> float:
            super().dcpdT(p, T)
            return self._combineMethod("dcpdT", p, T)
        
        ###################################
        def hs(self, p:float, T:float) -> float:
            #Argument checking
            try:
                super(self.__class__,self).hs(p,T)
            except NotImplementedError:
                pass
            return self._combineMethod("hs", p, T)
        
        ###################################
        def hf(self) -> float:
            return self._combineMethod("hf")
        
        ###################################
        def ha(self, p:float, T:float) -> float:
            #Argument checking
            try:
                super(self.__class__,self).ha(p,T)
            except NotImplementedError:
                pass
            return self._combineMethod("ha", p, T)
        
        ###################################
        def update(self, mix:Mixture=None)-> None:
            if not mix is None:
                self._mix = mix

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
            self._Thermo = self._ThermoClass(mix)
            super().__init__(mix)
            
        except BaseException as err:
            self.fatalErrorInClass(self.__init__, "Failed construction", err)
            
    #########################################################################
    #Operators:
    
    #########################################################################
    def _update(self, mix:Mixture=None):
        """
        Not class data to be updated
        """
        self._Thermo.update(mix)
        return super()._update(mix)

#########################################################################
#Add to selection table
ThermoMixing.addToRuntimeSelectionTable(janaf7Mixing)