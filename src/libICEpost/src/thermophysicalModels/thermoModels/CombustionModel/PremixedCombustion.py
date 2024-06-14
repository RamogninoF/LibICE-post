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
from .EgrModel.EgrModel import EgrModel
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
        return self.Lambda*self.alphaSt
    
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
    def fromDictionary(cls, dictionary:dict|Dictionary):
        """
        Create from dictionary.
        {
            air (Mixture): Air
            fuel (Mixture): The fuel composition
            phi (float, optional): the air-to-fuel equivalence ratio (supply either this or alpha)
            alpha (float, optional): the air/fuel ratio (supply either this or phi)
            
            thermo (Dictionary): Information for thermodynamic properties of mixtures
            
            egrModel (str, optional): Model for computation of EGR. Defaults to "EgrModel", i.e., no EGR.
            <EgrModel>Dict (dict, optional): the dictionary for construction of the specific EgrModel.
            
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
                
            #Manipulate the dictionary to supply the correct informations to the egrModel dictionary (air, fuel, alpha/phi)
            egrModelType = dictionary.lookupOrDefault("egrModel", "EgrModel")
            egrModelDict = dictionary.lookupOrDefault(egrModelType + "Dict", Dictionary())
            egrModelDict.update(
                                fuel=dictionary.lookup("fuel"),
                                air=dictionary.lookup("air"),
                                phi=dictionary.lookupOrDefault("phi", None, fatal=False),
                                alpha=dictionary.lookupOrDefault("alpha", None, fatal=False)
                            )
            
            egrModel = EgrModel.selector(egrModelType, egrModelDict)
            dictionary.update(egrModel=egrModel)
            
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
                 fuel:Mixture,
                 phi:float=None,
                 alpha:float=None,
                 **kwargs):
        """
        Construct combustion model from fuel composition and equivalence ratio. 
        Other keyword arguments passed to base class CombustionModel.
        
        Args:
            fuel (Mixture): The fuel composition
            phi (float, optional): the air-to-fuel equivalence ratio (supply either this or alpha)
            alpha (float, optional): the air/fuel ratio (supply either this or phi)
        """
        #Argument checking:
        try:
            #Type checking
            self.checkType(fuel, Mixture, "fuel")
            if (not phi is None) and (alpha is None):
                self.checkType(phi, float, "phi")
            elif (not alpha is None) and (phi is None):
                self.checkType(alpha, float, "alpha")
            else:
                raise ValueError("One of either phi or alpha must be given")

        except BaseException as err:
            self.fatalErrorInArgumentChecking(self.__init__, err)
        
        try:
            #Initialize base class
            super().__init__(**kwargs)

            #Other stuff to initialize specific of PremixedCombustion
            self._fuel = ThermoMixture(fuel.copy(), **self.thermo)
            
            #Get phi from alpha
            if phi is None:
                phi = self.alphaSt/(alpha + 1e-12)
            
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
               alpha:float=None,
               fuel:Mixture=None,
               **kwargs,
               ) -> PremixedCombustion:
        """
        Update mixture composition based on progress variable, equivalence ratio, and fuel composition.
        
        NOTE: phi and fuel are added in case there is multi-fuel combustion or direct-injection.

        Args:
            xb (float): the burned mass fraction
            phi (float, optional): update equivalence ratio. Defaults to None.
            alpha (float, optional): update air/fuel ratio. Defaults to None.
            fuel (Mixture, optional): update fuel composition. Defaults to None.

        Returns:
            PremixedCombustion: self
        """
        try:
            #Update fuel
            if not fuel is None:
                self.checkType(fuel, Mixture, "fuel")
                self._fuel.update(fuel)
                update = True
            
            #Update mixture composition
            if (not phi is None) and (alpha is None):
                self.checkType(phi, float, "phi")
                self._phi = phi
                update = True
            elif (phi is None) and (not alpha is None):
                self.checkType(alpha, float, "alpha")
                self._phi = self.alphaSt/(alpha + 1e-12)
                update = True
            elif (not phi is None) and (not alpha is None):
                raise ValueError("Only one of phi or alpha can be supplied.")
            
            #Update the state
            update = super().update(**kwargs)
            
            #Update reactants and products
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
        except BaseException as err:
            self.fatalErrorInClass(self.update, f"Failed updating combustion model state.", err)

#########################################################################
#Add to selection table of Base
CombustionModel.addToRuntimeSelectionTable(PremixedCombustion)
