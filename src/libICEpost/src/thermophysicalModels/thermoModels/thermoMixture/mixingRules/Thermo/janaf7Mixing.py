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
from libICEpost import Dictionary

from .....specie.specie.Mixture import Mixture
from .....specie.thermo.Thermo import Thermo

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class janaf7Mixing(ThermoMixing):
    """
    Class handling mixing of multi-component mixture: thermodynamic data in janaf7 definition.

    Attributes:
        ThermoType (str): Type of thermodynamic data for which it is implemented
        Thermo (Thermo): The Thermo of the mixture
    """
    
    ThermoType = "janaf7"
    #########################################################################
    #NOTE:
    # In this case the implementation is slight different because it is not possible to define
    # the average properies of the mixture with a new janaf7 class with a mass-weighted average
    # set of coefficients. Hence, it is necessary to introduce a new class here defined consistenty
    # with Thermo implementation, and then use the properties of each component and averaging them.

    class janaf7(Thermo):
        """
        Thermodynamic data of mixture with NASA-7 polinomial coefficients consistent with janaf7 class.
        """

        ###################################
        @classmethod
        def fromDictionary(cls, dictionary:dict):
            """
            Not to be used!
            """
            raise NotImplementedError("Not to be used!")
        
        ###################################
        @property
        def Rgas(self):
            """The mass-specific gas constant [J/kgK]"""
            return self._mix.Rgas
        
        ###################################
        def __init__(self, mix:Mixture):
            self._mix = mix #Take as reference!

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
                self._mix.update(mix.species, mix.Y, fracType="mass")

    #########################################################################
    @classmethod
    def fromDictionary(cls, dictionary):
        """
        Create from dictionary.
        """
        dictionary = Dictionary(**dictionary)
        return cls(dictionary.lookup("mixture"))
    
    #########################################################################
    #Constructor:
    def __init__(self, mix:Mixture):
        """
        Construct from Mixture.
        
        Args:
            mix (Mixture): Mixture to which generate the thermodynamic data.
        """
        self._Thermo = self.janaf7(mix.copy())  #Start with copy
        super().__init__(mix)
        self._Thermo._mix = self._mix #Set the reference to the mixture
            
    #########################################################################
    #Operators:
    
    #########################################################################
    def _update(self, mix:Mixture=None) -> bool:
        """
        No class data to be updated.
        
        Args:
            mix (Mixture, optional): Change the mixture. Defaults to None.

        Returns:
            bool: If something changed
        """
        self._Thermo.update(mix)
        return super()._update(mix)

#########################################################################
#Add to selection table
ThermoMixing.addToRuntimeSelectionTable(janaf7Mixing)