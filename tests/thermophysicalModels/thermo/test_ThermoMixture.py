import pytest
from libICEpost.src.thermophysicalModels.thermoModels.thermoMixture.ThermoMixture import ThermoMixture
from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture
from libICEpost.src.thermophysicalModels.specie.thermo.EquationOfState.EquationOfState import EquationOfState
from libICEpost.src.thermophysicalModels.specie.thermo.Thermo.Thermo import Thermo

from libICEpost.src.thermophysicalModels.specie.thermo.EquationOfState.PerfectGas import PerfectGas
from libICEpost.src.thermophysicalModels.specie.thermo.Thermo.janaf7 import janaf7
from libICEpost.Database import database
import itertools

@pytest.fixture
def sample_mixture():
    # Create a sample Mixture instance
    O2 = database.chemistry.specie.Molecules.O2
    N2 = database.chemistry.specie.Molecules.N2
    return Mixture(specieList=[O2, N2], composition=[0.21, 0.79])

#Check all possible combinations of Thermo and EoS types
ThermoTypes = ["constantCp", "janaf7"]
EoSTypes = ["PerfectGas"]
thermo_eos_pairs = list(itertools.product(ThermoTypes, EoSTypes))

@pytest.mark.parametrize("thermoType, eosType", thermo_eos_pairs)
def test_thermo_mixture_parametric(thermoType, eosType, sample_mixture):
    thermoTypeDict = {"Thermo": thermoType, "EquationOfState": eosType}
    thermo_mixture = ThermoMixture(sample_mixture, thermoTypeDict)
    assert thermo_mixture._Thermo.__class__.__name__.startswith(thermoType)
    assert thermo_mixture._EoS.__class__.__name__.startswith(eosType)

@pytest.fixture
def thermo_mixture(sample_mixture):
    # Create a sample ThermoMixture instance
    thermoType = {"Thermo": "janaf7", "EquationOfState": "PerfectGas"}
    return ThermoMixture(sample_mixture, thermoType)

def test_db_property(thermo_mixture):
    assert thermo_mixture.db is database.chemistry.thermo

@pytest.mark.parametrize("thermoType, eosType", thermo_eos_pairs)
def test_update_mixture(thermoType, eosType, sample_mixture):
    thermoTypeDict = {"Thermo": thermoType, "EquationOfState": eosType}
    thermo_mixture = ThermoMixture(sample_mixture, thermoTypeDict)
    new_mixture = Mixture(specieList=[database.chemistry.specie.Molecules.CO2], composition=[1.0])
    thermo_mixture.update(new_mixture)
    assert thermo_mixture.mix == new_mixture
    assert thermo_mixture._Thermo.mix == new_mixture
    assert thermo_mixture._EoS.mix == new_mixture

@pytest.mark.parametrize("thermoType, eosType", thermo_eos_pairs)
def test_thermoMixture_str(thermoType, eosType, sample_mixture):
    thermoTypeDict = {"Thermo": thermoType, "EquationOfState": eosType}
    thermo_mixture = ThermoMixture(sample_mixture, thermoTypeDict)
    assert thermoType in str(thermo_mixture)
    assert eosType in str(thermo_mixture)
    assert str(sample_mixture) in str(thermo_mixture)


@pytest.mark.parametrize("thermoType, eosType", thermo_eos_pairs)
def test_thermoMixture_repr(thermoType, eosType, sample_mixture):
    thermoTypeDict = {"Thermo": thermoType, "EquationOfState": eosType}
    thermo_mixture = ThermoMixture(sample_mixture, thermoTypeDict)
    assert thermoType in repr(thermo_mixture)
    assert eosType in repr(thermo_mixture)
    assert repr(sample_mixture) in repr(thermo_mixture)

def test_dcpdT(thermo_mixture):
    assert isinstance(thermo_mixture.dcpdT(101325, 300), float)

def test_ha(thermo_mixture):
    assert isinstance(thermo_mixture.ha(101325, 300), float)

def test_hs(thermo_mixture):
    assert isinstance(thermo_mixture.hs(101325, 300), float)

def test_ua(thermo_mixture):
    assert isinstance(thermo_mixture.ua(101325, 300), float)

def test_us(thermo_mixture):
    assert isinstance(thermo_mixture.us(101325, 300), float)

def test_cp(thermo_mixture):
    assert isinstance(thermo_mixture.cp(101325, 300), float)

def test_cv(thermo_mixture):
    assert isinstance(thermo_mixture.cv(101325, 300), float)

def test_gamma(thermo_mixture):
    assert isinstance(thermo_mixture.gamma(101325, 300), float)