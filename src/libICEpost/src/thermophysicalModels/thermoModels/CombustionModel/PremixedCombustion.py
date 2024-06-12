#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: <N. Surname>       <e-mail>
Last update:        DD/MM/YYYY
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from __future__ import annotations

#load the base class
from .CombustionModel import CombustionModel

#Other imports
from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture
from libICEpost.src.thermophysicalModels.thermoModels.thermoMixture.ThermoMixture import ThermoMixture
from libICEpost.src.thermophysicalModels.specie.reactions.ReactionModel.functions import computeAlphaSt

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class PremixedCombustion(CombustionModel):
    """
    Premixted combustion model
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        attr1:  <type>
            Description
    """
    
    _phi:float
    
    #########################################################################
    #Properties:
    @property
    def alpha(self) -> float:
        """
        The current air-to fuel ratio.

        Returns:
            float
        """
        return self.alphaSt*self.Lambda
    
    #######################################
    @property
    def alphaSt(self) -> float:
        """
        The current stoichiometric air-to fuel ratio.

        Returns:
            float
        """
        return computeAlphaSt(self.air.mix, self.fuel.mix)
    
    #######################################
    @property
    def phi(self) -> float:
        """
        The current fuel-to-air equivalence ratio.
        
        Returns:
            float
        """
        return self._phi
    
    #######################################
    @property
    def Lambda(self) -> float:
        """
        The current air-to-fuel equivalence ratio.
        
        Returns:
            float
        """
        return 1./max(self._phi, 1e-12)
    
    #########################################################################
    #Class methods and static methods:
    @classmethod
    def fromDictionary(cls, dictionary):
        """
        Create from dictionary.
        {
            air (Mixture): Air
            fuel (Mixture): The fuel composition
            phi (float): the air-to-fuel equivalence ratio
            thermo (Dictionary): Information for thermodynamic properties of mixtures
            egrModel (str, optional): Model for computation of EGR. Defaults to "EgrModel", i.e., no EGR.
            reactionModel (str, optional): Model handling reactions. defaults to "Stoichiometry".
            state (dict[str:float], optional): Giving current state to manage state-dependend 
                combustion models(e.g. equilibrium). Defaults to {}.
        }
        """
        try:
            #Constructing this class with the specific entries
            out = cls\
                (
                    **dictionary
                )
            return out
        
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed construction from dictionary", err)
    
    #########################################################################
    def __init__(self, /, *, 
                 fuel:Mixture, 
                 phi:float, 
                 **kwargs):
        """
        Construct combustion model from fuel composition and equivalence ratio. 
        Other keyword arguments passed to base class CombustionModel.
        
        Args:
            fuel (Mixture): The fuel composition
            phi (float): the air-to-fuel equivalence ratio
        """
        #Argument checking:
        try:
            #Type checking
            self.checkType(fuel, Mixture, "fuel")
            self.checkType(phi, float, "phi")

        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        try:
            #Initialize base class
            super().__init__(**kwargs)

            #Other stuff to initialize specific of PremixedCombustion
            self._fuel = ThermoMixture(fuel.copy(), **self.thermo)
            
            #Initialize unburnt mixture
            self.update(xb=0.0, phi=phi)

        except BaseException as err:
            self.fatalErrorInClass(self.__init__, f"Failed construction of {self.__class__.__name__}", err)
    
    #########################################################################
    #Dunder methods:
    
    #########################################################################
    #Methods:
    def update(self, 
               xb:float,
               *,
               phi:float=None,
               fuel:Mixture=None,
               **state:dict[str:float],
               ) -> PremixedCombustion:
        """
        Update mixture composition based on progress variable, equivalence ratio, and fuel composition.
        
        NOTE: phi and fuel are added in case there is multi-fuel combustion or direct-injection.

        Args:
            xb (float): the burned mass fraction
            phi (float, optional): update equivalence ratio. Defaults to None.
            fuel (Mixture, optional): update fuel composition. Defaults to None.
            **state (dict[str:float], optional): the state variables of the system (needed to 
                update the combustion model - e.g. equilibrium)

        Returns:
            PremixedCombustion: self
        """
        #Check if needed to be updated fresh mixture
        if not phi is None:
            self._phi = phi
            update = True
        
        if not fuel is None:
            self._fuel.update(fuel)
            update = True
        
        #Update the state
        update = super().update(**state)
        
        #Update fresh mixture if needed
        if update:
            #Reset fresh mixture to air mixture
            self._freshMixture.update(self.air.mix.copy())
            newFreshMix = self._freshMixture.mix
            self._appliedEGR = False
            
            #Apply EGR
            super().update()
            
            #Dilute with fuel
            #alpha = m_a/m_f
            #egr = m_egr/(m_a + m_egr)
            #y_f = m_f/(m_a + m_egr + m_f)
            
            yf = (1. - self.egrModel.egr)/(self.alpha + 1. - self.egrModel.egr) #Mass fraction of fuel in air+fuel mixture, removing egr
            newFreshMix.dilute(self.fuel.mix, yf, "mass")
            
            #Update reaction model
            self._reactionModel.update(reactants=self._freshMixture.mix, **self.state)
            
        #Update reaction model if only the state changed
        self._reactionModel.update(**self.state)
        
        #Update combustion products
        self._combustionProducts.update(self._reactionModel.products)
        
        #Update current state based on combustion progress variable
        newMix = self.freshMixture.mix.copy()
        newMix.dilute(self.combustionProducts.mix, xb, "mass")
        self._mixture.update(newMix)
        
        return self

#########################################################################
#Add to selection table of Base
CombustionModel.addToRuntimeSelectionTable(PremixedCombustion)
