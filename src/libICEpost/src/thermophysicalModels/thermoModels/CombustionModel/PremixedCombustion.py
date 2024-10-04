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
from libICEpost.src.thermophysicalModels.specie.reactions.ReactionModel.functions import computeAlphaSt, computeAlpha
from libICEpost.src.base.dataStructures.Dictionary import Dictionary

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class PremixedCombustion(CombustionModel):
    """
    Premixted combustion model
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
    """
    _fuel:Mixture
    _air:Mixture
    _alphaSt:float
    _xb:float
    
    #########################################################################
    #Properties:
    @property
    def air(self) -> Mixture:
        """
        The air mixture
        
        Returns:
            Mixture
        """
        return self._air
    
    ################################
    @property
    def fuel(self) -> Mixture:
        """
        The current fuel mixture
        
        Returns:
            Mixture
        """
        return self._fuel
    
    ################################
    @property
    def alpha(self) -> float:
        """
        The current air-to fuel ratio.

        Returns:
            float
        """
        return self.Lambda*self.alphaSt
    
    #######################################
    @property
    def alphaSt(self) -> float:
        """
        The current stoichiometric air-to fuel ratio.

        Returns:
            float
        """
        return self._alphaSt
    
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
    def fromDictionary(cls, dictionary:dict|Dictionary):
        """
        Create from dictionary.
        {
            air (Mixture): Air
            fuel (Mixture): The fuel composition
            reactants (Mixture): The reactants composition
            
            reactionModel (str, optional): Model handling reactions. defaults to "Stoichiometry".
            <ReactionModel>Dict (dict, optional): the dictionary for construction of the specific ReactionModel.
            
            state (ThermoState, optional): Giving current state to manage state-dependend 
                combustion models(e.g. equilibrium). Defaults to empty state ThermoState().
        }
        """
        try:
            #Cast to Dictionary
            cls.checkTypes(dictionary,(dict, Dictionary),"dictionary")
            if isinstance(dictionary, dict):
                dictionary = Dictionary(**dictionary)
                
            #Constructing this class with the specific entries
            out = cls\
                (
                    **dictionary,
                )
            return out
            
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed construction from dictionary", err)
    
    #########################################################################
    def __init__(self, /, *, 
                 air:Mixture,
                 fuel:Mixture,
                 xb:float=0.0,
                 **kwargs):
        """
        Construct combustion model from fuel and reactants. 
        Other keyword arguments passed to base class CombustionModel.
        
        Args:
            air (Mixture): The fuel composition
            fuel (Mixture): The fuel composition
        """
        #Argument checking:
        try:
            #Type checking
            self.checkType(air, Mixture, "air")
            self.checkType(fuel, Mixture, "fuel")

        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        try:
            #Initialize base class
            super().__init__(**kwargs)

            #Other stuff to initialize specific of PremixedCombustion
            self._air = air.copy()
            self._fuel = fuel.copy()
            
            #Initialize unburnt mixture
            self._xb = -1   #Enforce first update
            self.update(xb=xb)

        except BaseException as err:
            self.fatalErrorInClass(self.__init__, f"Failed construction of {self.__class__.__name__}", err)
    
    #########################################################################
    #Dunder methods:
    
    #########################################################################
    #Methods:
    def update(self, 
               xb:float=None,
               *,
               air:Mixture=None,
               fuel:Mixture=None,
               **kwargs,
               ) -> bool:
        """
        Update mixture composition based on progress variable, fuel, and reactants composition.
        
        Args:
            xb (float, None): the burned mass fraction. Defaults to None (no update).
            air (Mixture, optional): update air composition. Defaults to None.
            fuel (Mixture, optional): update fuel composition. Defaults to None.
            reactants (Mixture, optional): update reactants composition. Defaults to None.

        Returns:
            bool: if something changed
        """
        try:
            update = False
            
            #Update air
            if not air is None:
                self.checkType(air, Mixture, "air")
                old = self._air
                self._air = air
                if old != self.air:
                    update = True
                    
            #Update fuel
            if not fuel is None:
                self.checkType(fuel, Mixture, "fuel")
                old = self._fuel
                self._fuel = fuel
                if old != self.fuel:
                    update = True
            
            #Xb
            if not xb is None:
                if xb != self._xb:
                    self._xb = xb
                    update = True
                
            #Update the state and air composition
            update = update or super().update(**kwargs)
            
            #Update
            if update:
                #Update reaction model
                self._reactionModel.update(reactants=self._freshMixture, **self.state)
                
                #Update phi and alphaSt
                alpha = computeAlpha(air=self.air, fuel=self.fuel, reactants=self.freshMixture)
                self._alphaSt = computeAlphaSt(self.air, self.fuel)
                self._phi = self.alphaSt/alpha
                
            #Update combustion products
            self._combustionProducts = self._reactionModel.products
            
            #Update current state based on combustion progress variable
            newMix = self.freshMixture.copy()
            newMix.dilute(self.combustionProducts, self._xb, "mass")
            self._mixture = newMix
            
            return self
        except BaseException as err:
            self.fatalErrorInClass(self.update, f"Failed updating combustion model state.", err)

#########################################################################
#Add to selection table of Base
CombustionModel.addToRuntimeSelectionTable(PremixedCombustion)
