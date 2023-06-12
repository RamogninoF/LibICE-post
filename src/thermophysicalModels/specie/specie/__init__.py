"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023

Classes for describing:
    -> Atomic specie
    -> Molecules
    -> Mixtures
"""

from Database import database
database["chemistry"]["specie"] = {}

from .Atom import Atom
from .Molecule import Molecule
from .Mixture import Mixture
