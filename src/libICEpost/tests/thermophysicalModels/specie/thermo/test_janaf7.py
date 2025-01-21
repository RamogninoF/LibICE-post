import pytest
from .....src.thermophysicalModels.specie.thermo.Thermo.janaf7 import janaf7

Rgas = 8.314
cpLow = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
cpHigh = [7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]
Tth = 1000.0
Tlow = 300.0
Thigh = 2000.0

@pytest.fixture
def thermo():
    return janaf7(Rgas, cpLow, cpHigh, Tth, Tlow, Thigh)

@pytest.fixture
def thermo_dict():
    return {
        "Rgas": Rgas,
        "cpLow": cpLow,
        "cpHigh": cpHigh,
        "Tth": Tth,
        "Tlow": Tlow,
        "Thigh": Thigh
    }

def test_janaf7_initialization_valid(thermo):
    assert thermo.Rgas == Rgas
    assert thermo.cpLow == cpLow
    assert thermo.cpLow is not cpLow
    assert thermo.cpHigh == cpHigh
    assert thermo.cpHigh is not cpHigh
    assert thermo.Tth == Tth
    assert thermo.Tlow == Tlow
    assert thermo.Thigh == Thigh

def test_janaf7_initialization_invalid_cpLow_length():
    Rgas = 8.314
    cpLow = [1.0, 2.0, 3.0]  # Invalid length
    cpHigh = [7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]
    Tth = 1000.0
    Tlow = 300.0
    Thigh = 2000.0

    with pytest.raises(ValueError):
        janaf7(Rgas, cpLow, cpHigh, Tth, Tlow, Thigh)

def test_janaf7_initialization_invalid_cpHigh_length():
    Rgas = 8.314
    cpLow = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    cpHigh = [7.0, 6.0, 5.0]  # Invalid length
    Tth = 1000.0
    Tlow = 300.0
    Thigh = 2000.0

    with pytest.raises(ValueError):
        janaf7(Rgas, cpLow, cpHigh, Tth, Tlow, Thigh)

def test_janaf7_initialization_invalid_Tth_type():
    Rgas = 8.314
    cpLow = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    cpHigh = [7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]
    Tth = "1000.0"  # Invalid type
    Tlow = 300.0
    Thigh = 2000.0

    with pytest.raises(TypeError):
        janaf7(Rgas, cpLow, cpHigh, Tth, Tlow, Thigh)

def test_janaf7_initialization_invalid_Tlow_type():
    Rgas = 8.314
    cpLow = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    cpHigh = [7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]
    Tth = 1000.0
    Tlow = "300.0"  # Invalid type
    Thigh = 2000.0

    with pytest.raises(TypeError):
        janaf7(Rgas, cpLow, cpHigh, Tth, Tlow, Thigh)

def test_janaf7_initialization_invalid_Thigh_type():
    Rgas = 8.314
    cpLow = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    cpHigh = [7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]
    Tth = 1000.0
    Tlow = 300.0
    Thigh = "2000.0"  # Invalid type

    with pytest.raises(TypeError):
        janaf7(Rgas, cpLow, cpHigh, Tth, Tlow, Thigh)

def test_janaf7_copy(thermo):
    thermo_copy = thermo.copy()
    assert thermo_copy.Rgas == Rgas
    assert thermo_copy.cpLow == cpLow
    assert thermo_copy.cpHigh == cpHigh
    assert thermo_copy.Tth == Tth
    assert thermo_copy.Tlow == Tlow
    assert thermo_copy.Thigh == Thigh
    assert thermo_copy is not thermo

def test_janaf7_coeffs_below_Tth(thermo):
    coeffs = thermo.coeffs(500.0)
    assert coeffs == cpLow
    
def test_janaf7_coeffs_above_Tth(thermo):
    coeffs = thermo.coeffs(1500.0)
    assert coeffs == cpHigh

def test_janaf7_cp(thermo):
    # Test above Tth
    cp = thermo.cp(0,1500.0)
    cp_expected = 0.0
    for i in range(5):
        cp_expected += cpHigh[i] * (1500.0)**i
    assert cp == cp_expected*Rgas

    # Test below Tth
    cp = thermo.cp(0,500.0)
    cp_expected = 0.0
    for i in range(5):
        cp_expected += cpLow[i] * (500.0)**i
    assert cp == cp_expected*Rgas

def test_janaf7_ha(thermo):
    # Test above Tth
    ha = thermo.ha(0,1500.0)
    ha_expected = cpHigh[5]
    for i in range(5):
        ha_expected += cpHigh[i] * (1500.0)**(i+1) / (i+1)
    assert ha == ha_expected*Rgas

    # Test below Tth
    ha = thermo.ha(0,500.0)
    ha_expected = cpLow[5]
    for i in range(5):
        ha_expected += cpLow[i] * (500.0)**(i+1) / (i+1)
    assert ha == ha_expected*Rgas

def test_janaf7_hs(thermo):
    # Test above Tth
    hs = thermo.hs(0, 1500.0)
    ha_expected = cpHigh[5]
    for i in range(5):
        ha_expected += cpHigh[i] * (1500.0)**(i+1) / (i+1)
    ha_expected *= Rgas
    hs_expected = ha_expected - thermo.hf()
    assert hs == hs_expected

    # Test below Tth
    hs = thermo.hs(0, 500.0)
    ha_expected = cpLow[5]
    for i in range(5):
        ha_expected += cpLow[i] * (500.0)**(i+1) / (i+1)
    ha_expected *= Rgas
    hs_expected = ha_expected - thermo.hf()
    assert hs == hs_expected

def test_janaf7_dcpcT(thermo):
    # Test above Tth
    dcpdT = thermo.dcpdT(0,1500.0)
    dcpdT_expected = 0.0
    for i in range(1,5):
        dcpdT_expected += i * cpHigh[i] * (1500.0)**(i - 1)
    dcpdT_expected *= Rgas
    assert dcpdT == dcpdT_expected

    # Test below Tth
    dcpdT = thermo.dcpdT(0,500.0)
    dcpdT_expected = 0.0
    for i in range(1,5):
        dcpdT_expected += i * cpLow[i] * (500.0)**(i - 1)
    dcpdT_expected *= Rgas
    assert dcpdT == dcpdT_expected

def test_janaf7_fromDictionary_valid(thermo_dict):
    thermo = janaf7.fromDictionary(thermo_dict)
    assert thermo.Rgas == Rgas
    assert thermo.cpLow == cpLow
    assert thermo.cpLow is not cpLow
    assert thermo.cpHigh == cpHigh
    assert thermo.cpHigh is not cpHigh
    assert thermo.Tth == Tth
    assert thermo.Tlow == Tlow
    assert thermo.Thigh == Thigh

def test_janaf7_fromDictionary_invalid_key(thermo_dict):
    thermo_dict.pop("Rgas")
    with pytest.raises(KeyError):
        janaf7.fromDictionary(thermo_dict)

def test_janaf7_fromDictionary_invalid_value_type(thermo_dict):
    thermo_dict["Rgas"] = "8.314"  # Invalid type
    with pytest.raises(TypeError):
        janaf7.fromDictionary(thermo_dict)

def test_janaf7_ua(thermo):
    with pytest.raises(NotImplementedError):
        thermo.ua(0, 300)

def test_janaf7_str(thermo):
    str_output = str(thermo)

def test_janaf7_repr(thermo):
    repr_output = repr(thermo)