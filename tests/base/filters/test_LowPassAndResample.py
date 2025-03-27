import pytest
import numpy as np
from libICEpost.src.base.filters._LowPassAndResample import LowPassAndResample

def test_lowpassandresample_initialization():
    # Test initialization with valid cutoff and order
    lowpassandresample = LowPassAndResample(cutoff=0.1, order=3, delta=0.5)
    assert lowpassandresample.cutoff == 0.1
    assert lowpassandresample.order == 3
    assert lowpassandresample.delta == 0.5

    # Test initialization with invalid cutoff
    with pytest.raises(TypeError):
        LowPassAndResample(cutoff="invalid", order=3, delta=0.5)
    
    # Test initialization with invalid order
    with pytest.raises(TypeError):
        LowPassAndResample(cutoff=0.1, order="invalid", delta=0.5)
        
    # Test initialization with invalid delta
    with pytest.raises(TypeError):
        LowPassAndResample(cutoff=0.1, order=3, delta="invalid")

def test_lowpassandresample_from_dictionary():
    # Test creation from dictionary
    dictionary = {"cutoff": 0.2, "order": 4, "delta": 0.5}
    lowpassandresample = LowPassAndResample.fromDictionary(dictionary)
    assert lowpassandresample.cutoff == 0.2
    assert lowpassandresample.order == 4
    assert lowpassandresample.delta == 0.5

    # Test creation with missing order (default value)
    dictionary = {"cutoff": 0.2, "delta": 0.5}
    lowpassandresample = LowPassAndResample.fromDictionary(dictionary)
    assert lowpassandresample.cutoff == 0.2
    assert lowpassandresample.order == 5
    assert lowpassandresample.delta

    # Test creation with missing cutoff and delta
    with pytest.raises(KeyError):
        LowPassAndResample.fromDictionary({"order": 4})

def test_lowpassandresample_call():
    # Test low-pass filtering functionality
    def func(x, *, A:list[float], f:list[float]):
        """
        Function to generate a signal with multiple frequencies and amplitudes.
        
        Args:
            x (np.ndarray): The x values
            A (list[float]): The amplitudes of the signals
            f (list[float]): The frequencies of the signals
        """
        y = np.zeros_like(x)
        for a, F in zip(A, f):
            y += a * np.sin(2 * np.pi * F * x)
        return y
    
    A = [5., 1., 2., 3., 4.]
    f = [0.0, 0.1, 0.5, 1.0, 15.0]
    lowpassandresample = LowPassAndResample(cutoff=5.0, delta=0.5)
    xp = np.linspace(0, 20, 10000)
    yp = func(xp, A=A, f=f)

    x_filtered, y_filtered = lowpassandresample(xp, yp)

def test_lowpassandresample_plot():
    # Test the plot method
    import matplotlib.pyplot as plt

    def func(x, *, A:list[float], f:list[float]):
        """
        Function to generate a signal with multiple frequencies and amplitudes.
        
        Args:
            x (np.ndarray): The x values
            A (list[float]): The amplitudes of the signals
            f (list[float]): The frequencies of the signals
        """
        y = np.zeros_like(x)
        for a, F in zip(A, f):
            y += a * np.sin(2 * np.pi * F * x)
        return y

    A = [5., 1., 2., 3., 4.]
    f = [0.0, 0.1, 0.5, 1.0, 15.0]
    lowpassandresample = LowPassAndResample(cutoff=5.0, delta=0.01)
    xp = np.linspace(0, 20, 1000)
    yp = func(xp, A=A, f=f)

    # Generate the plot
    fig, axes = lowpassandresample.plot(xp, yp, xName="Time [s]", yName="Amplitude", freqUnits="Hz")

    # Check if the figure and axes are created
    assert isinstance(fig, plt.Figure)
    assert len(axes) == 2