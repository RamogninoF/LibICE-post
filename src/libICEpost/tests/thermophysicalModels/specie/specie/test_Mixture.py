import pytest
from .....src.thermophysicalModels.specie.specie.Mixture import Mixture, mixtureBlend, constants, MixtureItem
from .....src.thermophysicalModels.specie.specie.Molecule import Molecule
from .....src.thermophysicalModels.specie.specie.Atom import Atom

def test_mixture_initialization():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    molecules = [molecule1, molecule2]
    
    #From mole fractions
    X = [0.5, 0.5]
    MMmix = sum([x*M.MM for x, M in zip(X, molecules)])
    Y = [x*MM/MMmix for x, MM in zip(X, [M.MM for M in molecules])]
    mixture = Mixture(molecules, X, "mole")
    assert mixture.species == [molecule1, molecule2]
    assert mixture.Y == pytest.approx(Y , abs=10.**(-Mixture._decimalPlaces+1))
    
    #From mass fractions
    mixture = Mixture([molecule1, molecule2], Y, "mass")
    assert mixture.species == [molecule1, molecule2]
    assert mixture.X == pytest.approx(X , abs=10.**(-Mixture._decimalPlaces+1))
    
    mixture = Mixture(molecules, X, "mole")
    assert mixture.species == molecules
    assert mixture.Y == pytest.approx(Y , abs=10.**(-Mixture._decimalPlaces+1))

def test_mixture_invalid_fraction_type():
    atom1 = Atom("H", 1.008)
    molecule1 = Molecule("H2", [atom1], [2.0])
    with pytest.raises(ValueError):
        Mixture([molecule1], [1.0], "invalid")

def test_mixture_getitem_invalid_specie():
    atom1 = Atom("H", 1.008)
    molecule1 = Molecule("H2", [atom1], [2.0])
    mixture = Mixture([molecule1], [1.0], "mass")
    with pytest.raises(ValueError):
        mixture["O2"]

def test_mixture_getitem_invalid_index():
    atom1 = Atom("H", 1.008)
    molecule1 = Molecule("H2", [atom1], [2.0])
    mixture = Mixture([molecule1], [1.0], "mass")
    with pytest.raises(ValueError):
        mixture[1]

def test_mixture_getitem_with_name():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    mixture = Mixture([molecule1, molecule2], [0.5, 0.5], "mass")
    assert mixture["H2"] == mixture[0]
    assert mixture["O2"] == mixture[1]

def test_mixture_getitem_with_molecule():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    molecules = [molecule1, molecule2]
    X = [0.5, 0.5]
    mixture = Mixture([molecule1, molecule2], X, "mole")
    
    for ii,mol in enumerate(molecules):
        assert mixture[ii] == mixture[mol]

def test_mixture_delitem_with_name():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    molecule3 = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    mixture = Mixture([molecule1, molecule2, molecule3], [1./3, 1./3, 1./3], "mass")
    del mixture["H2"]
    assert mixture.species == [molecule2, molecule3]
    assert mixture.Y == pytest.approx([0.5, 0.5] , abs=10.**(-Mixture._decimalPlaces+1))

def test_mixture_delitem_with_molecule():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    molecule3 = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    mixture = Mixture([molecule1, molecule2, molecule3], [1./3, 1./3, 1./3], "mass")
    del mixture[molecule2]
    assert mixture.species == [molecule1, molecule3]
    assert mixture.Y == pytest.approx([0.5, 0.5] , abs=10.**(-Mixture._decimalPlaces+1))

def test_mixture_delitem_with_index():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    molecule3 = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    mixture = Mixture([molecule1, molecule2, molecule3], [1./3, 1./3, 1./3], "mass")
    del mixture[1]
    assert mixture.species == [molecule1, molecule3]
    assert mixture.Y == pytest.approx([0.5, 0.5] , abs=10.**(-Mixture._decimalPlaces+1))

def test_mixture_delitem_invalid_specie():
    atom1 = Atom("H", 1.008)
    molecule1 = Molecule("H2", [atom1], [2.0])
    mixture = Mixture([molecule1], [1.0], "mass")
    with pytest.raises(ValueError):
        del mixture["O2"]

def test_mixture_delitem_invalid_index():
    atom1 = Atom("H", 1.008)
    molecule1 = Molecule("H2", [atom1], [2.0])
    mixture = Mixture([molecule1], [1.0], "mass")
    with pytest.raises(ValueError):
        del mixture[1]

def test_mixture_dilute_invalid_fraction():
    atom1 = Atom("H", 1.008)
    molecule1 = Molecule("H2", [atom1], [2.0])
    mixture = Mixture([molecule1], [1.0], "mass")
    with pytest.raises(ValueError):
        mixture.dilute(mixture, -0.1)

def test_mixture_dilute_with_molecule():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    mixture = Mixture([molecule1, molecule2], [0.5, 0.5], "mass")
    new_molecule = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    diluted_mixture = mixture.dilute(new_molecule, 0.1)
    assert new_molecule in diluted_mixture.species
    assert diluted_mixture.Y[-1] == 0.1

def test_mixture_dilute_with_empty_mixture():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    mixture = Mixture([molecule1, molecule2], [0.5, 0.5], "mass")
    empty_mixture = Mixture([], [], "mass")
    diluted_mixture = mixture.dilute(empty_mixture, 0.1)
    assert diluted_mixture.species == mixture.species
    assert diluted_mixture.Y == mixture.Y

def test_dilute_empty_mixture():
    mix = Mixture.empty()
    
    atom1 = Atom("H", 1.008)
    molecule1 = Molecule("H2", [atom1], [2.0])
    mix.dilute(molecule1, 0.1) #Here dilution fraction is not used
    
    assert mix.species == [molecule1]
    assert mix.Y == [1.0]

def test_dilute_with_mixture_with_zero_fraction_specie():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    molecule3 = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    molecule4 = Molecule("H2O2", [atom1, atom2], [2.0, 2.0])
    
    mix = Mixture([molecule1], [1.0], "mass")
    mix.dilute(molecule2, 0.1)
    
    mix2 = Mixture([molecule3, molecule4], [1.0, 0.0], "mass")
    mix.dilute(mix2, 0.5)
    
    assert mix.species == [molecule1, molecule2, molecule3, molecule4]
    assert mix.Y ==  pytest.approx([0.45, 0.05, 0.5, 0.0] , abs=10.**(-Mixture._decimalPlaces+1))

def test_mixture_dilute_zero_dilution_fraction():
    atom1 = Atom("H", 1.008)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("H3", [atom1], [2.0])
    mixture = Mixture([molecule1], [1.0], "mass")
    mixture.dilute(molecule2, 0.9*10.0**(-Mixture._decimalPlaces))
    
    assert mixture.species == [molecule1, molecule2]
    assert mixture.Y == [1.0, 0.0]

def test_dilute_with_mole_fraction():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    
    mix = Mixture([molecule1], [1.0], "mass")
    mix.dilute(molecule2, 0.1, "mole")
    
    assert mix.species == [molecule1, molecule2]
    assert mix.X == [0.9, 0.1]
    
    mix.dilute(molecule1, 0.5, "mole")
    assert mix.X == [0.95, 0.05]

def test_mixture_extract_invalid_specie():
    atom1 = Atom("H", 1.008)
    molecule1 = Molecule("H2", [atom1], [2.0])
    mixture = Mixture([molecule1], [1.0], "mass")
    with pytest.raises(ValueError):
        mixture.extract([Molecule("O2", [atom1], [2.0])])

def test_mixture_extract():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    molecule3 = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    mixture = Mixture([molecule1, molecule2, molecule3], [0.3, 0.4, 0.3], "mass")
    extracted_mixture = mixture.extract([molecule1, molecule3])
    assert extracted_mixture.species == [molecule1, molecule3]
    assert extracted_mixture.Y == pytest.approx([0.5, 0.5] , abs=10.**(-Mixture._decimalPlaces+1))
    with pytest.raises(ValueError):
        extracted_mixture.extract([molecule2])
    with pytest.raises(ValueError):
        extracted_mixture.extract([])

def test_mixture_subtract_invalid_specie():
    atom1 = Atom("H", 1.008)
    molecule1 = Molecule("H2", [atom1], [2.0])
    mixture1 = Mixture([molecule1], [1.0], "mass")
    mixture2 = Mixture([Molecule("O2", [atom1], [2.0])], [1.0], "mass")
    yMix, remainder = mixture1.subtractMixture(mixture2)
    assert yMix == 0.0
    assert remainder == mixture1

def test_mixture_blend_invalid_composition():
    atom1 = Atom("H", 1.008)
    molecule1 = Molecule("H2", [atom1], [2.0])
    mixture1 = Mixture([molecule1], [1.0], "mass")
    with pytest.raises(ValueError):
        mixtureBlend([mixture1], [0.5, 0.5])

def test_mixture_blend_empty_composition():
    atom1 = Atom("H", 1.008)
    molecule1 = Molecule("H2", [atom1], [2.0])
    mixture1 = Mixture([molecule1], [1.0], "mass")
    with pytest.raises(ValueError):
        mixtureBlend([], [])

def test_mixture_blend_composition_not_adding_up_to_1():
    atom1 = Atom("H", 1.008)
    molecule1 = Molecule("H2", [atom1], [2.0])
    mixture1 = Mixture([molecule1], [1.0], "mass")
    with pytest.raises(ValueError):
        mixtureBlend([mixture1], [0.5])

def test_mixture_blend_composition_out_of_limits():
    atom1 = Atom("H", 1.008)
    molecule1 = Molecule("H2", [atom1], [2.0])
    mixture1 = Mixture([molecule1], [1.0], "mass")
    mixture2 = Mixture([molecule1], [1.0], "mass")
    with pytest.raises(ValueError):
        mixtureBlend([mixture1, mixture2], [1.1, -0.1])

def test_mixture_blend():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    mixture1 = Mixture([molecule1], [1.0], "mass")
    mixture2 = Mixture([molecule2], [1.0], "mass")
    mixture3 = Mixture([molecule1, molecule2], [0.5, 0.5], "mass")
    blended_mixture = mixtureBlend([mixture1, mixture2], [0.5, 0.5])
    assert blended_mixture.species == [molecule1, molecule2]
    assert blended_mixture.Y == [0.5, 0.5]
    
    blended_mixture2 = mixtureBlend([mixture1, mixture2, mixture3], [0.5, 0.5, 0.0])
    assert blended_mixture2.Y == blended_mixture.Y

def test_mixture_MM():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    X = [0.3, 0.7]
    mixture = Mixture([molecule1, molecule2], X, "mole")
    expected_MM = sum([x*M.MM for x, M in zip(X, [molecule1, molecule2])])
    assert mixture.MM == expected_MM

def test_mixture_Rgas():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    X = [0.3, 0.7]
    mixture = Mixture([molecule1, molecule2], X, "mole")
    expected_Rgas = constants.Rgas/(mixture.MM*1e-3)
    assert mixture.Rgas == expected_Rgas

def test_mixture_set_X():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    mixture = Mixture([molecule1, molecule2], [0.5, 0.5], "mole")
    new_X = [0.3, 0.7]
    mixture.X = new_X
    assert mixture.X == new_X

def test_mixture_set_Y():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    mixture = Mixture([molecule1, molecule2], [0.5, 0.5], "mass")
    new_Y = [0.3, 0.7]
    mixture.Y = new_Y
    assert mixture.Y == new_Y

def test_mixture_set_invalid_X():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    mixture = Mixture([molecule1, molecule2], [0.5, 0.5], "mole")
    with pytest.raises(ValueError):
        mixture.X = [0.3]
    with pytest.raises(TypeError):
        mixture.X = "invalid"

def test_mixture_set_invalid_Y():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    mixture = Mixture([molecule1, molecule2], [0.5, 0.5], "mass")
    with pytest.raises(ValueError):
        mixture.Y = [0.3]
    with pytest.raises(TypeError):
        mixture.Y = "invalid"

def test_mixture_empty_classmethod():
    empty_mixture = Mixture.empty()
    assert empty_mixture.species == []
    assert empty_mixture.Y == []
    assert empty_mixture.X == []

def test_mixture_contains():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    molecule3 = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    mixture = Mixture([molecule1, molecule2], [0.5, 0.5], "mass")
    assert "H2" in mixture
    assert molecule2 in mixture
    assert "CO2" not in mixture
    assert molecule3 not in mixture

def test_mixure_index():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    CO2 = Molecule("CO2", [atom1, atom2], [2.0, 1.0])
    
    mixture = Mixture([molecule1, molecule2], [0.5, 0.5], "mass")
    assert mixture.index(molecule1) == 0
    assert mixture.index("O2") == 1
    with pytest.raises(ValueError):
        mixture.index(CO2)
    with pytest.raises(ValueError):
        mixture.index("NH3")

def test_mixture_update_length_mismatch():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    mixture = Mixture([molecule1], [1.0], "mass")
    with pytest.raises(ValueError):
        mixture.update([molecule1, molecule2], [0.5])

def test_mixture_update_duplicate_species():
    atom1 = Atom("H", 1.008)
    molecule1 = Molecule("H2", [atom1], [2.0])
    mixture = Mixture([molecule1], [1.0], "mass")
    with pytest.raises(ValueError):
        mixture.update([molecule1, molecule1], [0.5, 0.5])

def test_mixture_update_composition_not_adding_up_to_1():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    mixture = Mixture([molecule1, molecule2], [0.5, 0.5], "mass")
    with pytest.raises(ValueError):
        mixture.update([molecule1, molecule2], [0.3, 0.6])

def test_mixture_update_fraction_out_of_range():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    mixture = Mixture([molecule1, molecule2], [0.5, 0.5], "mass")
    with pytest.raises(ValueError):
        mixture.update([molecule1, molecule2], [1.1, -0.1])

def test_mixture_remove_zeros():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    mixture = Mixture([molecule1, molecule2], [1.0, 0.0], "mass")
    mixture.removeZeros()
    assert mixture.species == [molecule1]
    assert mixture.Y == [1.0]

def test_mixture_subtract_mixture_equal_mixture():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    mixture1 = Mixture([molecule1, molecule2], [0.5, 0.5], "mass")
    mixture2 = Mixture([molecule1, molecule2], [0.5, 0.5], "mass")
    yMix, remainder = mixture1.subtractMixture(mixture2)
    assert yMix == 1.0
    assert remainder.species == []
    assert remainder.Y == []

def test_mixture_subtract_mixture():
    atom1 = Atom("H", 1.008)
    atom2 = Atom("O", 16.00)
    molecule1 = Molecule("H2", [atom1], [2.0])
    molecule2 = Molecule("O2", [atom2], [2.0])
    molecule3 = Molecule("H2O", [atom1, atom2], [2.0, 1.0])
    mixture1 = Mixture([molecule1, molecule2, molecule3], [0.4, 0.4, 0.2], "mass")
    mixture2 = Mixture([molecule1, molecule3], [0.5, 0.5], "mass")
    yMix, remainder = mixture1.subtractMixture(mixture2)
    assert yMix == 0.4
    assert remainder.species == [molecule1, molecule2]
    assert remainder.Y == pytest.approx([1./3, 2./3], abs=10.**(-Mixture._decimalPlaces+1))