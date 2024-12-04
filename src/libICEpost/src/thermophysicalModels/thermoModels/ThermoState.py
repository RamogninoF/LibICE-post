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

from libICEpost.src.base.BaseClass import BaseClass
from libICEpost.src.base.dataStructures.Dictionary import Dictionary

try:
    from dataclasses import dataclass
    #Test python version
    @dataclass(kw_only=True)
    class __test_Dataclass:
        pass
    del __test_Dataclass
    
except:
    #Python < 3.10
    from pydantic.dataclasses import dataclass

from collections.abc import Mapping

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#DataClass for thermodynamic state of the system
@dataclass(kw_only=True, match_args=True)
class ThermoState(Mapping, BaseClass):
    """
    DataClass storing the thermodynamic state of the system
        
    Attributes:
        p (float): pressure [Pa]
        T (float): temperature [T]
        V (float): volume [m^3]
        rho (float): density [kg/m^3]
        m (float): mass [kg]
    """
    p:float = float("nan")
    """pressure [Pa]"""
    T:float = float("nan")
    """temperature [T]"""
    m:float = float("nan")
    """Volume [m^3]"""
    V:float = float("nan")
    """density [kg/m^3]"""
    rho:float = float("nan")
    """mass [kg]"""
    
    #Construct from dictionary
    @classmethod
    def fromDictionary(cls, dictionary:dict):
        """
        Construct from dictionary.

        Args:
            dictionary (dict): The constructor dictionary

        Returns:
            ThermoState: An instance of this class constructed from dictionary
        """
        dictionary = Dictionary(**dictionary)
        vars = cls().__dict__.keys()
        return cls(**{v:dictionary.lookup(v) for v in vars if v in dictionary})
    
    #Allow unpacking with ** operator
    def __len__(self):
        return len(self.__dict__)
    
    def __getitem__(self, ii:str) -> float:
        if not ii in self.__dict__.keys():
            raise KeyError(f"Entry '{ii}' not stored in {self.__class__.__name__} class.")
        return self.__dict__[ii]
    
    def __iter__(self):
        vars = self.__dict__.keys()
        return iter(vars)

#############################################################################
ThermoState.createRuntimeSelectionTable()

#############################################################################
#                                 THERMO STATES                             #
#############################################################################
#DataClass for thermodynamic state of the system
@dataclass(kw_only=True, match_args=True)
class PsiPsiuThermoState(ThermoState):
    """
    DataClass storing the thermodynamic state of the system with burnt and unburnt properties:
        
    Attributes:
        p (float): avg. pressure [Pa]
        T (float): avg. temperature [T]
        V (float): tot. volume [m^3]
        rho (float): avg. density [kg/m^3]
        m (float): tot. mass [kg]
        Tu (float): unburnt gas temperature [T]
        Vu (float): unburnt gas volume [m^3]
        rhou (float): unburnt gas density [kg/m^3]
        mu (float): unburnt gas mass [kg]
        Tb (float): burnt gas temperature [T]
        Vb (float): burnt gas volume [m^3]
        rhob (float): burnt gas density [kg/m^3]
        mb (float): burnt gas mass [kg]
    """
    Tu:float = float("nan")
    """unburnt gas temperature [T]"""
    mu:float = float("nan")
    """unburnt gas Volume [m^3]"""
    Vu:float = float("nan")
    """unburnt gas density [kg/m^3]"""
    rhou:float = float("nan")
    """unburnt gas mass [kg]"""
    
    Tb:float = float("nan")
    """burnt gas temperature [T]"""
    mb:float = float("nan")
    """burnt gas Volume [m^3]"""
    Vb:float = float("nan")
    """burnt gas density [kg/m^3]"""
    rhob:float = float("nan")
    """burnt gas mass [kg]"""

#############################################################################
ThermoState.addToRuntimeSelectionTable(PsiPsiuThermoState)