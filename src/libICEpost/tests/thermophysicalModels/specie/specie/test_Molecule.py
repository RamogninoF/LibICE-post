import pytest
from .....src.thermophysicalModels.specie.specie.Molecule import Molecule, constants
from .....src.thermophysicalModels.specie.specie.Atom import Atom

def test_molecule_initialization():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    assert molecule.name == "H2O"
    assert molecule.atoms == [atom1, atom2]
    assert molecule.numberOfAtoms == [2.0, 1.0]

def test_molecule_initialization_invalid():
    atom1 = Atom("H", 1.008)
    with pytest.raises(ValueError):
        Molecule("H2O", [atom1], [2.0, 1.0])

def test_molecule_equality():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    molecule2 = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    assert molecule1 == molecule2

def test_molecule_inequality():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    molecule2 = Molecule("H2", [atom1], [2.0])
    assert molecule1 != molecule2

def test_molecule_less_than():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    assert molecule1 < molecule2

def test_molecule_greater_than():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("O2", [atom2], [2.0])
    molecule2 = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    assert molecule1 > molecule2

def test_molecule_addition():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O", [atom2], [1.0])
    molecule3 = molecule1 + molecule2
    assert molecule3.name == "H2O"
    assert molecule3.atoms == [atom1, atom2]
    assert molecule3.numberOfAtoms == [2.0, 1.0]

def test_molecule_brute_formula():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    assert molecule.bruteFormula() == "H2O"

    molecule = Molecule("", [atom1, atom2], [4./3, 1.0])
    molecule.name = molecule.bruteFormula()
    assert molecule.name == "H1.333O"

def test_molecule_hash():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    assert isinstance(hash(molecule), int)

def test_molecule_copy():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    molecule2 = molecule1.copy()
    assert molecule1 == molecule2
    assert molecule1 is not molecule2

def test_molecule_contains():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    assert atom1 in molecule
    assert "H" in molecule
    assert "C" not in molecule

def test_molecule_index():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    assert molecule.index(atom1) == 0
    assert molecule.index(atom2) == 1
    assert molecule.index("H") == molecule.index(atom1)
    with pytest.raises(ValueError):
        molecule.index("C")
    with pytest.raises(ValueError):
        molecule.index(Atom("C", 12.00))

def test_molecule_getitem():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    assert molecule[0].atom == atom1
    assert molecule["H"].atom == atom1
    assert molecule[atom2].atom == atom2

def test_molecule_len():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    assert len(molecule) == 2

def test_molecule_iter():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    atoms = [item.atom for item in molecule]
    assert atoms == [atom1, atom2]

def test_molecule_atomic_composition_matrix():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    assert (molecule.atomicCompositionMatrix() == [2.0, 1.0]).all()

def test_molecule_initialization_duplicate_atoms():
        atom1 = Atom("H", 1.008)
        atom2 = Atom("O", 16.00)
        molecule = Molecule("H2O", [atom1, atom1, atom2], [1.0, 1.0, 1.0])
        assert molecule.name == "H2O"
        assert molecule.atoms == [atom1, atom2]
        assert molecule.numberOfAtoms == [2.0, 1.0]

def test_molecule_addition_with_atom():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule = Molecule("H2", [atom1], [2.0])
    new_molecule = molecule + atom2
    assert new_molecule.name == "H2O"
    assert new_molecule.atoms == [atom1, atom2]
    assert new_molecule.numberOfAtoms == [2.0, 1.0]

def test_molecule_addition_with_molecule():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O", [atom2], [1.0])
    new_molecule = molecule1 + molecule2
    assert new_molecule.name == "H2O"
    assert new_molecule.atoms == [atom1, atom2]
    assert new_molecule.numberOfAtoms == [2.0, 1.0]

def test_molecule_addition_with_duplicate_atoms():
    atom1 = Atom("H", 1.008)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("H", [atom1], [1.0])
    new_molecule = molecule1 + molecule2
    assert new_molecule.name == "H3"
    assert new_molecule.atoms == [atom1]
    assert new_molecule.numberOfAtoms == [3.0]

def test_molecule_addition_with_conflicting_atoms():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("H", 2.016)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("H", [atom2], [1.0])
    with pytest.raises(ValueError):
        molecule1 + molecule2

def test_molecule_Rgas():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    expected_Rgas = constants.Rgas / (molecule.MM * 1e-3)
    assert molecule.Rgas == expected_Rgas

def test_molecule_getitem_invalid_atom():
        atom1 = Atom("H", 1.008)
        atom2 = Atom("O", 16.00)
        atom3 = Atom("C", 12.00)
        molecule = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
        with pytest.raises(ValueError):
            molecule["C"]
        with pytest.raises(ValueError):
            molecule[atom3]

def test_molecule_getitem_invalid_index():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    with pytest.raises(IndexError):
        molecule[3]

def test_empty_molecule_initialization():
    with pytest.raises(ValueError):
        Molecule("H2O", [], [])
    
    with pytest.raises(NotImplementedError):
        Molecule.empty()