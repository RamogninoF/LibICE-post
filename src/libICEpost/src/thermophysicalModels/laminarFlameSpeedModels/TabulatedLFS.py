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

from __future__ import annotations

from typing import Iterable, Any

from libICEpost.src.base.dataStructures.Tabulation.OFTabulation import OFTabulation, FoamStringParser
from .LaminarFlameSpeedModel import LaminarFlameSpeedModel

from libICEpost.src.base.dataStructures.Dictionary import Dictionary

from libICEpost.src.base.dataStructures.Tabulation.Tabulation import Tabulation

import numpy as np 
import copy as cp

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Laminar flame speed computation with Gulder correlation:
class TabulatedLFS(OFTabulation,LaminarFlameSpeedModel):
    """
    Class for computation of unstained laminar flame speed from tabulation
    """
    #########################################################################
    #Class data:
    __inputNames:list[str] = ["pValues", "TuValues", "eqvrValues", "egrValues"]
    __order:list[str] = ["p", "Tu", "phi", "egr"]
    __files:dict[str,str] = {"Su":"laminarFlameSpeedTable", "deltaL":"deltaLTable"}
    
    #########################################################################
    #Class methods:
    @classmethod
    def fromFile(cls, path:str, readLaminarFlameThickness:bool=True, noWrite=True, **kwargs) -> TabulatedLFS:
        """
        Construct a table from files stored in an OpenFOAM-LibICE tabulation locted at 'path'.
        Directory structure as follows: \\
           path                         \\
           |-tableProperties            \\
           |---constant                 \\
           |   |-Su                     \\
           |   |-deltaL                 \\
           |---system                   \\
               |-controlDict            \\
               |-fvSchemes              \\
               |-fvSolutions

        Args:
            path (str): The master path where the tabulation is stored.
            readLaminarFlameThickness (bool, optional): Is the laminar flame thickness to be loaded? (in case it was not tabulated). Defaults to True.
            noWrite (bool, optional): Handle to prevent write access of this class to the tabulation (avoid overwrite). Defaults to True.
            **kwargs: Optional keyword arguments of Tabulation.__init__ method of each Tabulation object.
            
        Returns:
            TabulatedLFS: the tabulation
        """
        cls.checkType(path, str, "path")
        cls.checkType(noWrite, bool, "noWrite")
        cls.checkType(readLaminarFlameThickness, bool, "readLaminarFlameThickness")
        
        order = cls.__order[:]
        inputNames = cls.__inputNames[:]
        files = cp.deepcopy(cls.__files)
        
        #Read table properties to see if EGR is present
        with open(path + "/tableProperties", "r") as file:
            tabProps = FoamStringParser(file.read(), noVectorOrTensor=True).getData()
            #Remove EGR entries if not found
            if not "egrValues" in tabProps:
                del order[-1]
                del inputNames[-1]
                
        return super().fromFile(
            path=path,
            order=order,
            files=files,
            inputNames={var:inputNames[ii] for ii,var in enumerate(order)},
            noRead=(None if readLaminarFlameThickness else ["deltaL"]),
            noWrite=noWrite,
            **kwargs)
    
    ###################################
    #Class methods:
    @classmethod
    def fromDictionary(cls, dictionary:dict) -> TabulatedLFS:
        """
        Construct from dictionary containing:
            path (str): The master path where the tabulation is stored.
            readLaminarFlameThickness (bool, optional): Is the laminar flame thickness to be loaded? (in case it was not tabulated). Defaults to True.
            noWrite (bool, optional): Handle to prevent write access of this class to the tabulation (avoid overwrite). Defaults to True.
            kwargs (dict, optional): The optional keyword arguments to pass to Tabulation instance for construction. Defaults to dict().
        
        Args:
            dictionary (dict): The input dictionary.

        Returns:
            TabulatedLFS
        """
        cls.checkType(dictionary, dict, "dictionary")
        dictionary = Dictionary(**dictionary)
        
        return cls.fromFile(
            path=dictionary.lookup("path", varType=str),
            readLaminarFlameThickness=dictionary.lookupOrDefault("readLaminarFlameThickness", default=True),
            noWrite=dictionary.lookupOrDefault("noWrite", default=True),
            **dictionary.lookupOrDefault("kwargs", default=dict()),
            )
    
    #########################################################################
    #Constructor:
    def __init__(
        self, 
        *,
        Su:Iterable[float],
        deltaL:Iterable[float]=None,
        pRange:Iterable[float],
        TuRange:Iterable[float],
        phiRange:Iterable[float],
        egrRange:Iterable[float]=None,
        path:str=None, 
        noWrite:bool=True,
        tablePropertiesParameters:dict[str,Any]=None, 
        **kwargs):
        """Construct a tabulation from sampling points and unwrapped list of data-points for each variable to tabulate.
        
        Args:
            Su (Iterable[float]): The data at the sampling points for laminar flame speed [m/s]. Data can be stored as 1-D array or n-D matrix.
            deltaL (Iterable[float], optional): The data at the sampling points for laminar flame thickness [m] (if stored). Data can be stored as 1-D array or n-D matrix. Defaults to None.
            pRange (Iterable[float]): The sampling points of pressure [Pa].
            TuRange (Iterable[float]): The sampling points of unburnt-gas temperature [K].
            phiRange (Iterable[float]): The sampling points of equivalence ratio.
            egrRange (Iterable[float], optional): The sampling points of mass fraction of recirculated exhaust-gasses (if tabulated). Defaults to None.
            path (str, optional): The path where to save the tabulation. Defaults to None.
            noWrite (bool, optional): Forbid writing (prevent overwrite). Defaults to True.
            tablePropertiesParameters (dict[str,Any], optional): Additional parameters to store in the tableProperties. Defaults to None.
            **kwargs: Optional keyword arguments of Tabulation.__init__ method of each Tabulation object.
        """
        #LFS and LFT
        self.checkType(Su, Iterable, "Su")
        if not deltaL is None:
            self.checkType(deltaL, Iterable, "deltaL")
        data = {"Su":Su, "deltaL":deltaL}
        
        #Ranges and order
        ranges = dict()
        order = self.__order[:]
        inputNames = self.__inputNames[:]
        files = cp.deepcopy(self.__files)
        
        #Pressure
        self.checkType(pRange, Iterable, "pRange")
        ranges["p"] = pRange[:]
        
        #Temperature
        self.checkType(pRange, Iterable, "TuRange")
        ranges["Tu"] = TuRange[:]
        
        #Phi
        self.checkType(phiRange, Iterable, "pRange")
        ranges["phi"] = phiRange[:]
        
        #EGR
        if not egrRange is None:
            self.checkType(egrRange, Iterable, "egrRange")
            ranges["egr"] = egrRange[:]
        else:
            #Remove from order
            del order[-1]
            del inputNames[-1]
        
        super().__init__(
            ranges=ranges,
            data=data,
            order=order,
            inputNames={var:inputNames[ii] for ii,var in enumerate(order)},
            path=path,
            files=files,
            noWrite=noWrite,
            tablePropertiesParameters=tablePropertiesParameters,
            **kwargs
        )
    
    #########################################################################
    #Get SuTable:
    def SuTable(self) -> Tabulation:
        """
        The tabulation of laminar flame speed (read-only)
        """
        return self.tables["Su"]
    
    ################################
    #Get deltaLTable:
    def deltaLTable(self) -> Tabulation|None:
        """
        The tabulation of laminar flame tickness (read-only)
        """
        return self.tables["deltaL"]
    
    #########################################################################
    #Cumpute laminar flame speed:
    def Su(self,p:float,T:float,phi:float,EGR=None, **kwargs):
        """
        Interpolate laminar flame speed from tabulation.

        Args:
            p (float): Pressure [Pa].
            T (float): Unburnt gas temperature [K]
            phi (float): Equivalence ratio [-].
            EGR (float, optional): (optional) mass fraction of recirculated exhaust gasses. Defaults to None.
            **kwargs: The key-word arguments to pass to Tabulation.__call__ method.

        Returns:
            float|np.ndarray[float]: The computed laminar flame speed [m/s].
        """
        #Check arguments:
        LaminarFlameSpeedModel.Su(self,p,T,phi,EGR)
        
        vars = (p,T,phi,EGR) if "egr" in self.order else (p,T,phi)
        return self("Su", *vars, **kwargs)
    
    ################################
    #Cumpute laminar flame tickness:
    def deltaL(self,p,T,phi,EGR=None, **kwargs):
        """
        Interpolate laminar flame thickness from tabulation.

        Args:
            p (float): Pressure [Pa].
            T (float): Unburnt gas temperature [K]
            phi (float): Equivalence ratio [-].
            EGR (float, optional): (optional) mass fraction of recirculated exhaust gasses. Defaults to None.
            **kwargs: The key-word arguments to pass to Tabulation.__call__ method.

        Returns:
            float|np.ndarray[float]: The computed laminar flame thickness [m].
        """
        #Check arguments:
        LaminarFlameSpeedModel.deltaL(self,p,T,phi,EGR)
        
        vars = (p,T,phi,EGR) if "egr" in self.order else (p,T,phi)
        return self("deltaL", *vars, **kwargs)
    
#############################################################################
LaminarFlameSpeedModel.addToRuntimeSelectionTable(TabulatedLFS)
