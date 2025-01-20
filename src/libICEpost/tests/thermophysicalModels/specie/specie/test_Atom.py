import pytest

from .....src.thermophysicalModels.specie.specie.Atom import Atom
from .....src.thermophysicalModels.specie.specie.Molecule import Molecule

def test_atom_initialization():
    atom = Atom("H", 1.008)
    assert atom.name == "H"
    assert atom.mass == 1.008

def test_atom_initialization_invalid_name():
    with pytest.raises(TypeError):
        Atom(123, 1.008)

def test_atom_initialization_invalid_mass():
    with pytest.raises(TypeError):
        Atom("H", "1.008")

def test_atom_name_property():
    atom = Atom("H", 1.008)
    assert atom.name == "H"

def test_atom_mass_property():
    atom = Atom("H", 1.008)
    assert atom.mass == 1.008

def test_atom_equality():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("H", 1.008)
    assert atom1 == atom2

def test_atom_inequality():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("He", 4.0026)
    assert atom1 != atom2

def test_atom_less_than():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("He", 4.0026)
    assert atom1 < atom2

def test_atom_greater_than():
    atom1 = Atom("He", 4.0026)
    atom2 = Atom("H", 1.008)
    assert atom1 > atom2

def test_atom_less_than_or_equal():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("He", 4.0026)
    assert atom1 <= atom2
    assert atom1 <= atom1

def test_atom_greater_than_or_equal():
    atom1 = Atom("He", 4.0026)
    atom2 = Atom("H", 1.008)
    assert atom1 >= atom2
    assert atom1 >= atom1

def test_atom_addition():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("H", 1.008)
    molecule = atom1 + atom2
    assert isinstance(molecule, Molecule)

def test_atom_multiplication():
    atom = Atom("H", 1.008)
    molecule = atom * 2.0
    assert isinstance(molecule, Molecule)

def test_atom_representation():
    atom = Atom("H", 1.008)
    assert repr(atom) == "{'name': 'H', 'mass': 1.008}"
    
def test_atom_comparison_same_name_different_mass():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("H", 2.016)
    with pytest.raises(ValueError):
        atom1 + atom2
        
def test_atom_hash():
    atom = Atom("H", 1.008)
    assert isinstance(hash(atom), int)
    
def test_atom_copy():
    atom1 = Atom("H", 1.008)
    atom2 = atom1.copy()
    assert atom1 == atom2
    assert atom1 is not atom2
    
def test_atom_addition_same_atom():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("H", 1.008)
    molecule = atom1 + atom2
    assert isinstance(molecule, Molecule)
    assert molecule.name == "H2"
    assert molecule.atoms == [atom1]
    assert molecule.numberOfAtoms == [2]
    
def test_atom_addition_different_atoms():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule = atom2 + atom1
    assert isinstance(molecule, Molecule)
    assert molecule.name == "OH"
    assert molecule.atoms == [atom2, atom1]
    assert molecule.numberOfAtoms == [1, 1]
    
def test_atom_addition_same_name_different_properties():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("H", 2.016)
    with pytest.raises(ValueError):
        atom1 + atom2
        
def test_atom_addition_with_molecule():
    atom = Atom("H", 1.008)
    molecule = Molecule("H2", [atom], [2])
    new_molecule = atom + molecule
    assert isinstance(new_molecule, Molecule)
    assert new_molecule.name == "H3"
    assert new_molecule.atoms == [atom]
    assert new_molecule.numberOfAtoms == [3]
    
def test_atom_right_multiplication():
    atom = Atom("H", 1.008)
    molecule = 2.0 * atom
    assert isinstance(molecule, Molecule)
    assert molecule.name == "H2"
    assert molecule.atoms == [atom]
    assert molecule.numberOfAtoms == [2]