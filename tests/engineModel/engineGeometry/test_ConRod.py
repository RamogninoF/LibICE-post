import pytest
from libICEpost.src.engineModel.EngineGeometry.ConRod import ConRodGeometry, pistonPosition, pistonPosDerivative
import numpy as np

@pytest.fixture
def conrod_geometry():
    return ConRodGeometry(
        bore=0.1,
        stroke=0.1,
        conRodLen=0.15,
        CR=10.0,
        pinOffset=0.01,
        clearence=0.002,
        pistonCylAreaRatio=2.0,
        headCylAreaRatio=3.0
    )

def test_conrod_geometry_initialization(conrod_geometry):
    assert conrod_geometry.D == 0.1
    assert conrod_geometry.S == 0.1
    assert conrod_geometry.l == 0.15
    assert conrod_geometry.CR == 10.0
    assert conrod_geometry.pinOffset == 0.01
    assert conrod_geometry.clearence == 0.002
    assert conrod_geometry.pistonCylAreaRatio == 2.0
    assert conrod_geometry.headCylAreaRatio == 3.0

def test_conrod_geometry_lam(conrod_geometry):
    assert conrod_geometry.lam == 0.5 * conrod_geometry.S / conrod_geometry.l

def test_conrod_geometry_delta(conrod_geometry):
    assert conrod_geometry.delta == conrod_geometry.pinOffset / (0.5 * conrod_geometry.S)

def test_conrod_geometry_cylArea(conrod_geometry):
    assert conrod_geometry.cylArea == pytest.approx(0.007854, rel=1e-3)

def test_conrod_geometry_pistonArea(conrod_geometry):
    assert conrod_geometry.pistonArea == conrod_geometry.cylArea * conrod_geometry.pistonCylAreaRatio

def test_conrod_geometry_headArea(conrod_geometry):
    assert conrod_geometry.headArea == conrod_geometry.cylArea * conrod_geometry.headCylAreaRatio

def test_conrod_geometry_Vs(conrod_geometry):
    assert conrod_geometry.Vs == conrod_geometry.cylArea * conrod_geometry.S

def test_conrod_geometry_Vmin(conrod_geometry):
    assert conrod_geometry.Vmin == conrod_geometry.Vs / (conrod_geometry.CR - 1.0)

def test_conrod_geometry_Vmax(conrod_geometry):
    assert conrod_geometry.Vmax == conrod_geometry.Vs + conrod_geometry.Vmin

def test_conrod_geometry_s(conrod_geometry):
    CA = 0.0
    assert conrod_geometry.s(CA) == pistonPosition(CA, S=conrod_geometry.S, lam=conrod_geometry.lam, delta=conrod_geometry.delta)

def test_conrod_geometry_V(conrod_geometry):
    CA = 0.0
    assert conrod_geometry.V(CA) == conrod_geometry.Vmin + pistonPosition(CA, S=conrod_geometry.S, lam=conrod_geometry.lam, delta=conrod_geometry.delta) * conrod_geometry.cylArea

def test_conrod_geometry_dsdCA(conrod_geometry):
    CA = 0.0
    assert conrod_geometry.dsdCA(CA) == pistonPosDerivative(CA, S=conrod_geometry.S, lam=conrod_geometry.lam, delta=conrod_geometry.delta)

def test_conrod_geometry_dVdCA(conrod_geometry):
    CA = 0.0
    assert conrod_geometry.dVdCA(CA) == conrod_geometry.dsdCA(CA) * conrod_geometry.cylArea

def test_conrod_geometry_linerArea(conrod_geometry):
    CA = 0.0
    assert conrod_geometry.linerArea(CA) == (conrod_geometry.s(CA) + conrod_geometry.clearence) * 3.141592653589793 * conrod_geometry.D

def test_conrod_geometry_A(conrod_geometry):
    CA = 0.0
    assert conrod_geometry.A(CA) == conrod_geometry.linerArea(CA) + conrod_geometry.pistonArea + conrod_geometry.headArea

def test_conrod_geometry_areas(conrod_geometry):
    CA = [0.0, 180.0]
    areas_df = conrod_geometry.areas(CA)
    assert list(areas_df.columns) == ["CA"] + conrod_geometry.patches
    assert len(areas_df) == 2
    assert areas_df["CA"].tolist() == CA
    assert areas_df["piston"].tolist() == [conrod_geometry.pistonArea, conrod_geometry.pistonArea]
    assert areas_df["head"].tolist() == [conrod_geometry.headArea, conrod_geometry.headArea]
    assert areas_df["liner"].tolist() == conrod_geometry.linerArea(CA).tolist()

def test_pistonPosition_array(conrod_geometry):
    CA = np.array([0.0, 90.0, 180.0])
    expected_positions = [pistonPosition(ca, S=conrod_geometry.S, lam=conrod_geometry.lam, delta=conrod_geometry.delta) for ca in CA]
    assert np.allclose(pistonPosition(CA, S=conrod_geometry.S, lam=conrod_geometry.lam, delta=conrod_geometry.delta), expected_positions)

def test_pistonPosDerivative_array(conrod_geometry):
    CA = np.array([0.0, 90.0, 180.0])
    expected_derivatives = [pistonPosDerivative(ca, S=conrod_geometry.S, lam=conrod_geometry.lam, delta=conrod_geometry.delta) for ca in CA]
    assert np.allclose(pistonPosDerivative(CA, S=conrod_geometry.S, lam=conrod_geometry.lam, delta=conrod_geometry.delta), expected_derivatives)

def test_conrod_geometry_s_array(conrod_geometry):
    CA = np.array([0.0, 90.0, 180.0])
    expected_positions = [pistonPosition(ca, S=conrod_geometry.S, lam=conrod_geometry.lam, delta=conrod_geometry.delta) for ca in CA]
    assert np.allclose(conrod_geometry.s(CA), expected_positions)

def test_conrod_geometry_V_array(conrod_geometry):
    CA = np.array([0.0, 90.0, 180.0])
    expected_volumes = [conrod_geometry.Vmin + pistonPosition(ca, S=conrod_geometry.S, lam=conrod_geometry.lam, delta=conrod_geometry.delta) * conrod_geometry.cylArea for ca in CA]
    assert np.allclose(conrod_geometry.V(CA), expected_volumes)

def test_conrod_geometry_dsdCA_array(conrod_geometry):
    CA = np.array([0.0, 90.0, 180.0])
    expected_derivatives = [pistonPosDerivative(ca, S=conrod_geometry.S, lam=conrod_geometry.lam, delta=conrod_geometry.delta) for ca in CA]
    assert np.allclose(conrod_geometry.dsdCA(CA), expected_derivatives)

def test_conrod_geometry_dVdCA_array(conrod_geometry):
    CA = np.array([0.0, 90.0, 180.0])
    expected_dVdCA = [conrod_geometry.dsdCA(ca) * conrod_geometry.cylArea for ca in CA]
    assert np.allclose(conrod_geometry.dVdCA(CA), expected_dVdCA)

def test_conrod_geometry_linerArea_array(conrod_geometry):
    CA = np.array([0.0, 90.0, 180.0])
    expected_liner_areas = [(conrod_geometry.s(ca) + conrod_geometry.clearence) * 3.141592653589793 * conrod_geometry.D for ca in CA]
    assert np.allclose(conrod_geometry.linerArea(CA), expected_liner_areas)

def test_conrod_geometry_A_array(conrod_geometry):
    CA = np.array([0.0, 90.0, 180.0])
    expected_A = [conrod_geometry.linerArea(ca) + conrod_geometry.pistonArea + conrod_geometry.headArea for ca in CA]
    assert np.allclose(conrod_geometry.A(CA), expected_A)

def test_conrod_geometry_str(conrod_geometry):
    str(conrod_geometry)

def test_conrod_geometry_hash(conrod_geometry):
    assert isinstance(hash(conrod_geometry), int)