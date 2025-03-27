import pytest
import numpy as np
from libICEpost.src.base.filters._Resample import Resample

def test_resample_initialization():
    # Test initialization with valid delta
    resample = Resample(delta=0.5)
    assert resample.delta == 0.5

    # Test initialization with invalid delta
    with pytest.raises(TypeError):
        Resample(delta="invalid")
    
    # Test initialization with negative delta
    with pytest.raises(ValueError):
        Resample(delta=-0.5)

def test_resample_from_dictionary():
    # Test creation from dictionary
    dictionary = {"delta": 0.1, "not_used": 0.2}
    resample = Resample.fromDictionary(dictionary)
    assert resample.delta == 0.1

    # Test creation with missing delta
    with pytest.raises(KeyError):
        Resample.fromDictionary({"not_used": 0.1})

def test_resample_call():
    # Test resampling functionality
    resample = Resample(delta=0.5)
    xp = [0, 1, 2, 3, 4]
    yp = [0, 1, 4, 9, 16]

    x_resampled, y_resampled = resample(xp, yp)

    # Check if x_resampled is a uniform grid
    assert np.allclose(x_resampled, np.arange(0, 4.5, 0.5))

    # Check if y_resampled is interpolated correctly
    expected_y = np.interp(x_resampled, xp, yp)
    assert np.allclose(y_resampled, expected_y)

def test_resample_invalid_call():
    # Test invalid input types
    resample = Resample(delta=0.5)
    with pytest.raises(TypeError):
        resample("invalid", [1, 2, 3])
    with pytest.raises(TypeError):
        resample([1, 2, 3], "invalid")
    with pytest.raises(ValueError):
        resample([1, 2, 3], [1, 2, 3, 4])
