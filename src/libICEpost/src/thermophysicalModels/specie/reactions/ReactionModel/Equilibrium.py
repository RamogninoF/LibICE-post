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

import numpy as np
from typing import Iterable, Literal
import cantera as ct

from enum import Enum

from libICEpost.src.base.dataStructures.Dictionary import Dictionary
from .ReactionModel import ReactionModel
from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture

from libICEpost.src.thermophysicalModels.thermoModels.ThermoState import ThermoState

from libICEpost.src.base.Functions.runtimeWarning import runtimeWarning

from libICEpost.Database import database

#############################################################################
class _equilibriumComputationMethods(Enum):
    average = "average"
    burntGas = "burntGas"
    adiabatiFlame = "adiabaticFlame"

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class Equilibrium(ReactionModel):
    """
    Reaction model based on computation of chemical equilibrium which CANTERA.
    
    Attributes:
        oxidiser (Molecule): The oxidiser
        reactants (Mixture):The mixture of the reactants
        products (Mixture): The mixture of products of the reaction
        specie (list[Molecule]): The molecules to consider in the equilibrium
        mechanism (str): The path where the mechanism in yaml is stored
    """
    _ReactionType:str = None
    """The type for reactions to lookup for in the database"""
    
    _reactor:ct.Solution
    """The ractor used to compute equilibrium in CANTERA"""
    
    _mechamism:str
    """The path of the mechanism"""
    
    #########################################################################
    @classmethod
    def fromDictionary(cls, dictionary:dict):
        """
        Constructs from dictionary
        
        Args:
            dictionary (dict): The dictionary from which constructing:
                reactants (Mixture): the mixture of reactants
                mechanism (str): The path where is stored the chemical mechanism to use (yaml)
        """
        cls.checkType(dictionary, dict, "dictionary")
        dictionary = Dictionary(**dictionary)
        
        out = cls(
            reactants=dictionary.lookup("reactants", varType=Mixture),
            mechanism=dictionary.lookup("mechanism", varType=str),
            method=dictionary.lookup("method", varType=str),
            state=(dictionary.lookupOrDefault("state", default=ThermoState()))
        )
        
        return out
    
    #########################################################################
    #Properties:
    @property
    def mechanism(self) -> str:
        """
        The path where the mechanism is stored.
        """
        return self._mechanism
    
    @property
    def method(self):
        """
        The method used to compute the equilibrium.
        """
        return self._method.value
    
    #########################################################################
    #Constructor:
    def __init__(self, reactants:Mixture, mechanism:str, *, method:Literal["average","adiabatiFlame","burntGas"], state:ThermoState):
        """
        Constuct from the reactants and the chemical mechanism to use for computation of equilibrium with cantera.
        
        Args:
            reactants (Mixture): the mixture of reactants
            mechanism (str): The path where is stored the chemical mechanism to use (yaml)
            method (Literal["average","adiabatiFlame","burntGas"]): Which method to use to compute the equilibrium:
                average: Use the average in-cylinder temperature T (equilibrate(TP))
                adiabaticFlame: Compute the equilibrium at adiabatic flame temperature (equilibrate(HP) at Tu)
                burntGas: Compute the equilibrium at burnt gas temperature (equilibrate(TP) at Tb)
            state (ThermoState): Thermodynamic state to update the reaction model.
        """
        
        self.checkType(mechanism, str, "mechanism")
        self._mechanism = mechanism
        
        self._method = _equilibriumComputationMethods(method)
        
        #Construct the reactor
        self._reactor = ct.Solution(self.mechanism)
        
        super().__init__(reactants, state=state)

    #########################################################################
    #Operators:
    
    #########################################################################
    #Methods:
    def _update(self, reactants:Mixture=None, *, state:ThermoState) -> bool:
        """
        Method to update the products.

        Args:
            reactants (Mixture, optional): Update mixture of reactants. Defaults to None.
            state (ThermoState): Thermodynamic state to update the reaction model.

        Returns:
            bool: wether the system was updated
        """
        #Update reactants and state, return False if nothing changed:
        if not super()._update(reactants, state=state):
            return False
        
        for s in self.reactants:
            if not s.specie.name in self._reactor.species_names:
                raise ValueError(
                    f"Cannot compute chemical equilibrium: " +
                    f"specie {s.specie.name} not found in mechanism. " +
                    f"Avaliable species are:\n\t" + "\n\t".join(self._reactor.species_names)
                    )
        
        #Update composition
        Y = np.zeros((len(self._reactor.species_names), 1))
        for s in self.reactants:
            Y[self._reactor.species_index(s.specie.name)] = s.Y
        self._reactor.Y = Y
        
        #Update thermo props
        if self._method == _equilibriumComputationMethods.adiabatiFlame:
            T, P = self._state["Tu"], self._state["p"]
        elif self._method == _equilibriumComputationMethods.burntGas:
            T, P = self._state["Tb"], self._state["p"]
        elif self._method == _equilibriumComputationMethods.average:
            T, P = self._state["T"], self._state["p"]
        
        if np.isnan(T):
            runtimeWarning("Equilibrium: found nan temperature. Setting to 300K.", stack=False)
            T = 300.
        if np.isnan(P):
            runtimeWarning("Equilibrium: found nan pressure. Setting to 1bar.", stack=False)
            P = 300.
        
        self._reactor.TP = T, P
        if self._method == _equilibriumComputationMethods.adiabatiFlame:
            self._reactor.equilibrate("HP")
        else:
            self._reactor.equilibrate("TP")
        
        #Update products
        mols = [database.chemistry.specie.Molecules[mol] for mol in self._reactor.species_names]
        Y = self._reactor.Y
        self._products.update(mols, Y, fracType="mass")
        
        #Updated
        return True
    
#########################################################################
#Add to selection table
ReactionModel.addToRuntimeSelectionTable(Equilibrium)