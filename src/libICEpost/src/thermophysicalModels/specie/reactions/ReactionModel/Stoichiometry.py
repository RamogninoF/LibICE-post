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

import math

from libICEpost import Dictionary

from .ReactionModel import ReactionModel
from ..Reaction.Reaction import Reaction
from ..Reaction.StoichiometricReaction import StoichiometricReaction
from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture, mixtureBlend
from libICEpost.src.thermophysicalModels.specie.specie.Molecule import Molecule

from libICEpost.src.thermophysicalModels.thermoModels.ThermoState import ThermoState

from libICEpost.Database import database

from typing import Iterable
from libICEpost.src.thermophysicalModels.specie.reactions.ReactionModel.DissociationModel.DissociationModel import DissociationModel

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class Stoichiometry(ReactionModel):
    """
    Reaction model of fuel combustion with infinitely fast chemistry
    
    TODO:
    Extend to handle a generic reaction set, where there might be more then one oxidizer
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Attributes:
        oxidiser:  Molecule
            The oxidiser

        reactants:  (Mixture)
            The mixture of the reactants
        
        products:  (Mixture)
            The mixture of products of the reaction
            
        reactions:  (_Database)
           Database of oxidation reactions. Reference to database.chemistry.reactions
    
    """
    _ReactionType:str = "StoichiometricReaction"
    """The type for reactions to lookup for in the database"""
    
    _productsPreDissociation:Mixture
    """The combustion products before applying the dissociation models"""
    
    dissociationModels:list[DissociationModel]
    """A list of the dissociation models to apply"""
    
    #########################################################################
    @property
    def fuel(self):
        """
        The sub-mixture of reactants with the fuels
        """
        self._updateFuels()
        return self.reactants.extract(self._fuels)
    
    ##############################
    @property
    def oxidizer(self):
        """
        The oxidizer
        """
        return self._oxidizer
    
    #########################################################################
    @classmethod
    def fromDictionary(cls, dictionary):
        """
        Construct from dictionary.
        
        Args:
            dictionary (dict): The dictionary from which constructing, containing:
                reactants (Mixture): the mixture of reactants
                oxidiser (Molecule): the oxidizer
                dissociationModels (dict[str:dict]): Construction dictionaries for dissociation models in the form:
                {
                    <DissociationModelType>: construction dictionary for the specific model
                    ...
                }
        """
        cls.checkType(dictionary,dict,"dictionary")
        dictionary = Dictionary(**dictionary)
        
        dissModels = dictionary.lookupOrDefault("dissociationModels", default={})
        
        out = \
        cls(
            reactants=dictionary.lookup("reactants"),
            oxidizer=dictionary.lookupOrDefault("oxidizer",default=database.chemistry.specie.Molecules.O2),
            dissociationModels=\
                [
                    DissociationModel.selector(d,dissModels[d])
                    for d in dissModels
                ]
        )
        return out
    
    #########################################################################
    #Properties:
    
    #########################################################################
    #Constructor:
    def __init__(self, reactants:Mixture, *, oxidizer:Molecule=database.chemistry.specie.Molecules.O2, dissociationModels:Iterable[DissociationModel]=None):
        """
        Args:
            reactants (Mixture): the mixture of reactants
            oxidizer (Molecule, optional): The oxidizing molecule. Defaults to database.chemistry.specie.Molecules.O2.
        """
        self.checkType(oxidizer, Molecule, "oxidizer")
        self._oxidizer = oxidizer
        if not dissociationModels is None:
            self.checkArray(dissociationModels, DissociationModel, "dissociationModels")
        else:
            dissociationModels = []
            
        #Dissociation models
        self.dissociationModels = dissociationModels[:]
        
        #Create the combustionProducts pre dissociation models
        self._productsPreDissociation = Mixture.empty()
        super().__init__(reactants)
        
    #########################################################################
    #Operators:
    
    #########################################################################
    #Methods:
    def _updateFuels(self):
        """
        Update list of fuels
        """
        fuels = []
        for s in self.reactants:
            if s.specie.name in database.chemistry.specie.Fuels:
                fuels.append(s.specie)
        self._fuels = fuels
        
        return self
        
    ###################################
    def _update(self, reactants:Mixture=None, *, state:ThermoState=None) -> bool:
        """
        Method to update the products.

        Args:
            reactants (Mixture, optional): Update mixture of reactants. Defaults to None.
            state (ThermoState, optional): Thermodynamic state to update the reaction model. (NOT USED)

        Returns:
            bool: if something changed
        """
        #Update reactants, return False if the reactants where not changed:
        if not super()._update(reactants):
            #Update the state, if only this has changed, update only the dissociation models:
            if super()._update(state=state):
                #Try updating all the dissociation models
                update = any([DM.update(state=state) for DM in self.dissociationModels])
                #If some dissociation model has changed, apply the dissociation models and return True:
                if update:
                    self._products.update(self._productsPreDissociation.species, self._products.Y, fracType="mass")
                    [DM.apply(self._products) for DM in self.dissociationModels]
                    return True
                else:
                    return False
            else:
                return False
        
        #The mixture has changed, compute combustion products
        self._updateFuels()
        
        #Splitting the computation into three steps:
        #1) Removing the non-reacting compounds
        #   ->  Identified as those not found in the reactants 
        #       of any reactions
        #2) Identification of the active reactions
        #   ->  Active reactions are those where all reactants are present
        #       in the mixture and at least one fuel and the oxidizer
        #3) Solve the balance
        
        #Look for the oxidation reactions for all fuels
        oxReactions = {}    #List of oxidation reactions
        for f in self._fuels:
            found = False
            for r in self.reactions:
                react = self.reactions[r]
                if (f in react.reactants) and (self.oxidizer in react.reactants):
                    found = True
                    oxReactions[f.name] = react
                    break
            if not found:
                #Create oxidation reaction
                oxReactions[f.name] = StoichiometricReaction.fromFuelOxidation(fuel=f, oxidizer=self.oxidizer)
                #Add to the database for later use
                reactions[ReactionType][oxReactions[f.name].name] = oxReactions[f.name]
                raise ValueError(f"Oxidation reaction not found in database 'rections.{self.ReactionType}' for the couple (fuel, oxidizer) = ({f.name, self.oxidizer.name})")
        
        #Identification of reacting compounds
        yReact = 0.0
        reactingMix = None
        activeReactions = []
        #Loop over specie of the reactants
        for specie in self.reactants:
            #Loop over all oxidation reactions to find the active reactions
            #TODO: loop over reducers to find also the reducers.
            found = False
            for r in oxReactions:
                react = oxReactions[r]
                #Check if the specie in the reactants of the reaction
                if specie.specie in react.reactants:
                    #Check that all reactants of the reaction are found in the mixture,
                    #otherwise the reaction does not take place
                    active = True
                    for sR in react.reactants:
                        if not (sR.specie in self.reactants):
                            active = False
                            break
                    
                    if not self.oxidizer in react.reactants:
                        active = False
                    if not any([mol in react.reactants for mol in self._fuels]):
                        active = False
                    
                    #If not active, skip to next reaction
                    if not active:
                        continue
                    
                    #If here, an active reaction was found
                    found = True
                    
                    #Check if already added to reactions
                    if not react in activeReactions:
                        #Add to active reactions
                        activeReactions.append(react)
                    
            #add the specie to the reacting mixture if an active reaction was found
            if found:
                if reactingMix is None:
                    reactingMix = Mixture([specie.specie], [1])
                elif specie.specie in reactingMix:
                    #skip
                    continue
                else:
                    reactingMix.dilute(specie.specie, specie.Y/(yReact + specie.Y), "mass")
                yReact += specie.Y
        
        #If reacting mixture still empty, products are equal to reactants:
        if reactingMix is None:
            self._products = self._reactants
            return False    #Updated
        
        #Removing inerts
        inerts = None
        yInert = 0.0
        for specie in self.reactants:
            if not specie.specie in reactingMix:
                if inerts is None:
                    inerts = Mixture([specie.specie], [1])
                else:
                    inerts.dilute(specie.specie, specie.Y/(yInert + specie.Y), "mass")
                yInert += specie.Y
        
        #To assess if lean or rich, mix the oxidation reactions based on the
        #fuel mole/mass fractions in the fuels-only mixture. If the concentration
        #of oxidizer is higher then the actual, the mixture is rich, else lean.
        
        #Get stoichiometric combustion products:
        #   -> Solving linear sistem of equations 
        #
        #   R0: c1*[f00*F0 + o0*Ox   ]          | Oxidation reaction fuel F0 (reactants)
        #   R1: c2*[f11*F1 + o1*Ox   ]          | Oxidation reaction fuel F1 (reactants)
        #   R2: c3*[f22*F2 + o2*Ox   ]          | Oxidation reaction fuel F2 (reactants)
        #   ----------------------------------
        #   Rtot: f(f1*F1 + f2*F2 + ...) + o*Ox | Overall reactants
        #
        #   Where (f1, f2, ...) is the composition of the fuel-only mixture (known)
        #   and (c1, c2, ..., f) are the unknowns
        #
        #   The equations are:
        #   sum(c_i * f_ii) = f*f_i for i in (1,...,n_fuels)
        #   sum(c_i) = 1 for i in (1,...,n_fuels)
        #
        #   Hence n_fuels+1 unknowns and n_fuel+1 equations
        #
        #   |f00  0   0  ... -f0| |c1| |0|
        #   | 0  f11  0  ... -f1|*|c2|=|0|
        #   |...                | |..| |.|
        #   | 1   1   1  ...  0 | |f | |1|
        #
        #   [M]*x = v
        #
        
        fuelMix = self.fuel
        
        M = self.np.diag([oxReactions[f.name].reactants[f.name].X for f in self._fuels])
        M = self.np.c_[M, [-fuelMix[f].X for f in self._fuels]]
        M = self.np.c_[M.T, [1.]*(len(fuelMix)) + [0.]].T
        v = self.np.c_[self.np.zeros((1,len(fuelMix))), [1]].T
        xStoich = self.np.linalg.solve(M,v).T[0][:-1]
        
        stoichReactingMix = mixtureBlend\
            (
                [oxReactions[f.name].reactants for f in self._fuels], 
                [xx for xx in xStoich],
                "mole"
            )
        
        xProd = [(xx * oxReactions[f.name].moleRatio) for xx in xStoich]
        prods = mixtureBlend\
            (
                [oxReactions[f.name].products for f in self._fuels], 
                [x/sum(xProd) for x in xProd],
                "mole"
            )
        
        #If the reaction is not stoichiometric, add the non-reacting part:
        # y_exc_prod = y_exc - y_def*(y_exc_st/y_def_st)
        
        if not math.isclose(stoichReactingMix[self.oxidizer].Y,reactingMix[self.oxidizer].Y):
            if (reactingMix[self.oxidizer].Y > stoichReactingMix[self.oxidizer].Y):
                #Excess oxidizer
                y_exc = reactingMix[self.oxidizer].Y
                y_exc_st = stoichReactingMix[self.oxidizer].Y
                excMix = Mixture([self.oxidizer],[1.])
            else:
                #Excess fuel
                y_exc = 1. - reactingMix[self.oxidizer].Y
                y_exc_st = 1. - stoichReactingMix[self.oxidizer].Y
                excMix = self.fuel
            #Add non-reacting compound
            
            y_def = 1 - y_exc
            y_def_st = 1. - y_exc_st
            y_exc_prod = y_exc - y_def*(y_exc_st/y_def_st)
            prods.dilute(excMix,y_exc_prod, "mass")
        
        #Add inherts:
        if not inerts is None:
            prods.dilute(inerts, yInert, "mass")
        
        #Save the combustion products pre-dissociation
        self._productsPreDissociation.update(prods.species, prods.Y, fracType="mass")
        
        #Apply dissociation models:
        for DM in self.dissociationModels:
            DM.update(state=state)
            DM.apply(prods)
        
        #Store post-dissociation
        self._products.update(prods.species, prods.Y, fracType="mass")
        
        #Updated
        return True
        
    ################################
    
    
#########################################################################
#Add to selection table
ReactionModel.addToRuntimeSelectionTable(Stoichiometry)