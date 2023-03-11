#####################################################################
#                               IMPORT                              #
#####################################################################

from src.base.Utilities import Utilities

from src.thermophysicalModels.specie.specie.Mixture import Mixture

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
#Chemical reaction:
class Reaction(Utilities):
    """
    Class handling chemical reactions (transformation of reactants into products).
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        reactants:  Mixture
            The reactants
        products:   Mixture
            The products
        atoms:      list<Atom>
            List of atomic specie involved in the reaction
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Methods:
        checkCompatibility():
            checks that the composition of reactants and products are
            compatible, i.e. the reaction can be balanced.
        checkConsistency():
            checks that the reactants and products are consistent, i.e. the
            total mass of each atomic specie is conserved throughout the 
            reaction. Raises ValueError if mass is not conserved for some
            atoic specie.
        update():
            computes the composition of reactants and products through mass
            balance of each atomic specie. If the chemical specie are not
            compatible to guarantee the balance it raises ValueError.
    """
    def __init__(self, reactants, products):
        """
        reactants:  Mixture or list<Molecule>
            Mixture (or list) of reactants. If list is given, the
            composition is automatically computed based on mass balances
            of atomic species
        products:   Mixture or list<Molecule>
            Mixture (or list) of products. If list is given, the
            composition is automatically computed based on mass balances
            of atomic species
        """
        raise NotImplementedError("Reactions not yet implemented.")
