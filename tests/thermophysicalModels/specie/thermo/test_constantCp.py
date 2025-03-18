import pytest
from libICEpost.src.thermophysicalModels.specie.thermo.Thermo.constantCp import constantCp, Tstd

@pytest.fixture
def model():
    Rgas = 287.0
    cp = 1005.0
    hf = 50000.0
    return constantCp(Rgas, cp, hf)

def test_constantCp_cp(model):
    assert model.cp(0, 300) == model._cp

def test_constantCp_ha(model):
    T = 300.0
    expected_ha = model._cp * (T - Tstd) + model._hf
    assert model.ha(0, T) == expected_ha

def test_constantCp_hf(model):
    expected_hf = model.ha(0, Tstd)
    assert model.hf() == expected_hf

def test_constantCp_dcpdT(model):
    assert model.dcpdT(0, 300) == 0.0

def test_constantCp_hs(model):
    T = 300.0
    expected_hs = model.ha(0, T) - model.hf()
    assert model.hs(0, T) == expected_hs

def test_constantCp_construction():
    Rgas = 287.0
    cp = 1005.0
    hf = 50000.0
    model = constantCp(Rgas, cp, hf)
    assert model._cp == cp
    assert model._hf == hf
    assert model.Rgas == Rgas

def test_constantCp_construction_without_hf():
    Rgas = 287.0
    cp = 1005.0
    model = constantCp(Rgas, cp)
    assert model._cp == cp
    assert model._hf != model._hf  # NaN check
    assert model.Rgas == Rgas

def test_constantCp_fromDictionary():
    dictionary = {
        "Rgas": 287.0,
        "cp": 1005.0,
        "hf": 50000.0
    }
    model = constantCp.fromDictionary(dictionary)
    assert model._cp == dictionary["cp"]
    assert model._hf == dictionary["hf"]
    assert model.Rgas == dictionary["Rgas"]

def test_constantCp_fromDictionary_without_hf():
    dictionary = {
        "Rgas": 287.0,
        "cp": 1005.0
    }
    model = constantCp.fromDictionary(dictionary)
    assert model._cp == dictionary["cp"]
    assert model._hf != model._hf  # NaN check
    assert model.Rgas == dictionary["Rgas"]

def test_constantCp_type_checking():
    with pytest.raises(TypeError):
        constantCp("287.0", 1005.0, 50000.0)
    with pytest.raises(TypeError):
        constantCp(287.0, "1005.0", 50000.0)
    with pytest.raises(TypeError):
        constantCp(287.0, 1005.0, "50000.0")

def test_constantCp_fromDictionary_missing_Rgas():
    dictionary = {
        "cp": 1005.0,
        "hf": 50000.0
    }
    with pytest.raises(KeyError):
        constantCp.fromDictionary(dictionary)

def test_constantCp_fromDictionary_missing_cp():
    dictionary = {
        "Rgas": 287.0,
        "hf": 50000.0
    }
    with pytest.raises(KeyError):
        constantCp.fromDictionary(dictionary)

def test_constantCp_ua(model):
    with pytest.raises(NotImplementedError):
        model.ua(0, 300)

def test_constantCp_str(model):
    str(model)

def test_constantCp_repr(model):
    repr(model)
