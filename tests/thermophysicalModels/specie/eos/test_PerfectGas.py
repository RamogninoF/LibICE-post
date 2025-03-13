import pytest
from libICEpost.src.thermophysicalModels.specie.thermo.EquationOfState.PerfectGas import PerfectGas

Rgas = 287.05

@pytest.fixture
def perfect_gas():
    return PerfectGas(Rgas)

def test_pressure(perfect_gas):
    rho = 1.2
    T = 300.
    assert perfect_gas.p(T, rho) == pytest.approx(Rgas*rho*T)

def test_temperature(perfect_gas):
    p = 101325.
    rho = 1.2
    assert perfect_gas.T(p, rho) == pytest.approx(p/(Rgas*rho))

def test_density(perfect_gas):
    p = 101325.
    T = 300.
    assert perfect_gas.rho(p, T) == pytest.approx(p/(Rgas*T))

def test_specific_gas_constant(perfect_gas):
    assert perfect_gas.Rgas == pytest.approx(Rgas)

def test_cp(perfect_gas):
    p = 101325.
    T = 300.
    assert perfect_gas.cp(p, T) == 0.0

def test_h(perfect_gas):
    p = 101325.
    T = 300.
    assert perfect_gas.h(p, T) == 0.0

def test_u(perfect_gas):
    p = 101325.
    T = 300.
    assert perfect_gas.u(p, T) == 0.0

def test_Z(perfect_gas):
    p = 101325.
    T = 300.
    assert perfect_gas.Z(p, T) == 1.0

def test_cpMcv(perfect_gas):
    p = 101325.
    T = 300.
    assert perfect_gas.cpMcv(p, T) == Rgas

def test_dcpdT(perfect_gas):
    p = 101325.
    T = 300.
    assert perfect_gas.dcpdT(p, T) == 0.0

def test_dpdT(perfect_gas):
    p = 101325.
    T = 300.
    assert perfect_gas.dpdT(p, T) == pytest.approx(perfect_gas.rho(p, T) * Rgas)

def test_dTdp(perfect_gas):
    p = 101325.
    T = 300.
    assert perfect_gas.dTdp(p, T) == pytest.approx(perfect_gas.rho(p, T) * Rgas)

def test_drhodp(perfect_gas):
    p = 101325.
    T = 300.
    assert perfect_gas.drhodp(p, T) == pytest.approx(1.0 / (Rgas * T))

def test_dpdrho(perfect_gas):
    p = 101325.
    T = 300.
    assert perfect_gas.dpdrho(p, T) == pytest.approx(Rgas * T)

def test_drhodT(perfect_gas):
    p = 101325.
    T = 300.
    assert perfect_gas.drhodT(p, T) == pytest.approx(-p / (Rgas * (T ** 2.0)))

def test_dTdrho(perfect_gas):
    p = 101325.
    T = 300.
    assert perfect_gas.dTdrho(p, T) == pytest.approx(-p / (Rgas * (perfect_gas.rho(p, T) ** 2.0)))

def test_hash(perfect_gas):
    hash(perfect_gas)

def test_repr(perfect_gas):
    repr(perfect_gas)

def test_str(perfect_gas):
    str(perfect_gas)
