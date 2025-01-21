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

from typing import Iterable, Literal
from libICEpost.src.thermophysicalModels.specie.specie.Molecule import Molecule
from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture, _fracType

from libICEpost import Dictionary
from .DissociationModel import DissociationModel
from libICEpost.src.thermophysicalModels.thermoModels.ThermoState import ThermoState

from  libICEpost.src.thermophysicalModels.specie.reactions.Reaction.StoichiometricReaction import StoichiometricReaction

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class ConstantDissociationFraction(DissociationModel):
    """
    Dissociation of a molecule based on a constant mass/mole fraction of the dissociated specie.
    """
    
    _fraction:float
    """The mass/mole fraction to dissociate"""
    
    _fracType:str
    """The method to compure the fraction to dissociate (mass or mole)"""
    
    _molecule:Molecule
    """The molecule to dissociate"""
    
    _reaction:StoichiometricReaction
    """The reaction used to compute the dissociation"""
    
    #########################################################################
    @property
    def fraction(self) -> float:
        """The mass/mole fraction to dissociate"""
        return self._fraction

    @property
    def fracType(self) -> str:
        """The method to compure the fraction to dissociate (mass or mole)"""
        return self._fracType
    
    @property
    def molecule(self) -> Molecule:
        """The molecule to dissociate"""
        return self._molecule
    
    @property
    def reaction(self) -> StoichiometricReaction:
        """The reaction used to compute the dissociation"""
        return self._reaction
    
    #########################################################################
    @classmethod
    def fromDictionary(cls, dictionary:dict):
        """
        Construct from dictionary

        Args:
            dictionary (dict): Dictionary containing:
                molecule (Molecule): The molecule to dissociate.
                products (Iterable[Molecule]): The molecules in which this dissociates (balance automatically computed).
                fraction (float): The mass/mole fraction of this molecule that dissociates.
                fracType (Literal[&quot;mass&quot;, &quot;mole&quot;], optional): How to compute the dissociation fraction. Defaults to "mass".
            

        Returns:
            ConstantDissociationFraction: Instance of this class.
        """
        dictionary = Dictionary(**dictionary)
        
        return cls(**dictionary)
    
    #########################################################################
    #Constructor:
    def __init__(self, molecule:Molecule, products:Iterable[Molecule], fraction:float, *, fracType:Literal["mass", "mole"]="mass", state:ThermoState=None):
        """_summary_

        Args:
            molecule (Molecule): The molecule to dissociate.
            products (Iterable[Molecule]): The molecules in which this dissociates (balance automatically computed).
            fraction (float): The mass/mole fraction of this molecule that dissociates.
            fracType (Literal[&quot;mass&quot;, &quot;mole&quot;], optional): How to compute the dissociation fraction. Defaults to "mass".
            state (ThermoState, optional): Thermodynamic state to update the reaction model. Defaults to None.
        """
        #Check arguments
        self.checkType(molecule, Molecule, "molecule")
        self.checkArray(products, Molecule, "products")
        self.checkType(fraction, float, "fraction")
        self.checkType(fracType, str, "fracType")
        _fracType(fracType) #Check value
        
        self._fraction = fraction
        self._fracType = fracType
        self._molecule = molecule
        self._reaction = StoichiometricReaction(reactants=[molecule], products=products)
        
        self.update(state=state)
    
    #########################################################################
    def _update(self, *, state:ThermoState=None) -> bool:
        """
        Method to update the model (implementation).
        
        Args:
            state (ThermoState): Thermodynamic state to update the model.
            
        Returns:
            bool: if something changed
        """
        #Nothing to do
        return super()._update(state=state)
        
    #####################################
    def apply(self, mixture:Mixture, *, inplace:bool=True) -> Mixture|None:
        """
        Apply the dissociation model to the mixture. In-place update the mixture composition. If inplace=False, return the changed mixture.

        Args:
            mixture (Mixture): The mixture to manipulate to impose the dissociation
            inplace (bool, optional): If inplace is True, change mixture and return None, else update mixture compositon. Defaults to True.
        """
        self.checkType(mixture, Mixture, "mixture")
        
        #Check if present
        if not self._molecule in mixture:
            return mixture
        
        #Remove the molecule
        cleanMix = mixture.extract([mol.specie for mol in mixture if not (mol.specie == self._molecule)])
        
        #Diluting mixture
        dilMix = Mixture([self._molecule], [1.])
        dilMix.dilute(self._reaction.products, self._fraction, fracType=self._fracType)
        
        #Dilute
        cleanMix.dilute(dilMix, mixture[self._molecule].Y, fracType="mass")
        
        #Update the mixture
        if inplace:
            mixture.update(cleanMix.species, cleanMix.Y, fracType="mass")
            
            print(mixture)
        else:
            return cleanMix
            
#########################################################################
#Create selection table
DissociationModel.addToRuntimeSelectionTable(ConstantDissociationFraction)