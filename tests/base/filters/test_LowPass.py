import pytest
import numpy as np
from libICEpost.src.base.filters._LowPass import LowPass

def test_lowpass_initialization():
    # Test initialization with valid cutoff and order
    lowpass = LowPass(cutoff=0.1, order=3)
    assert lowpass.cutoff == 0.1
    assert lowpass.order == 3

    # Test initialization with invalid cutoff
    with pytest.raises(TypeError):
        LowPass(cutoff="invalid", order=3)
    
    # Test initialization with invalid order
    with pytest.raises(TypeError):
        LowPass(cutoff=0.1, order="invalid")
    
    # Test initialization with negative cutoff
    with pytest.raises(ValueError):
        LowPass(cutoff=-0.1, order=3)
    
    # Test initialization with negative order
    with pytest.raises(ValueError):
        LowPass(cutoff=0.1, order=-3)

def test_lowpass_from_dictionary():
    # Test creation from dictionary
    dictionary = {"cutoff": 0.2, "order": 4}
    lowpass = LowPass.fromDictionary(dictionary)
    assert lowpass.cutoff == 0.2
    assert lowpass.order == 4

    # Test creation with missing order (default value)
    dictionary = {"cutoff": 0.2}
    lowpass = LowPass.fromDictionary(dictionary)
    assert lowpass.cutoff == 0.2
    assert lowpass.order == 5

    # Test creation with missing cutoff
    with pytest.raises(KeyError):
        LowPass.fromDictionary({"order": 4})

def test_lowpass_call():
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
    lowpass = LowPass(cutoff=5.0)
    xp = np.linspace(0, 20, 10000)
    yp = func(xp, A=A, f=f)

    x_filtered, y_filtered = lowpass(xp, yp)
    
    # Check that the signal is filtered (high-frequency components are removed)
    aNew = [a for a, f in zip(A, f) if f <= 5.0]
    fNew = [f for f in f if f <= 5.0]
    y_new = func(x_filtered, A=aNew, f=fNew)

    # Check if mean squared error is reduced
    mse_original = np.mean((func(x_filtered, A=A, f=f) - y_new) ** 2)
    mse_filtered = np.mean((y_filtered - y_new) ** 2)
    
    assert mse_filtered < mse_original
    assert mse_filtered < 1e-2

def test_lowpass_invalid_call():
    # Test invalid input types
    lowpass = LowPass(cutoff=0.1, order=3)
    with pytest.raises(TypeError):
        lowpass("invalid", [1, 2, 3])
    with pytest.raises(TypeError):
        lowpass([1, 2, 3], "invalid")
    with pytest.raises(ValueError):
        lowpass([1, 2, 3], [1, 2, 3, 4])

def test_lowpass_plot():
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
    lowpass = LowPass(cutoff=5.0)
    xp = np.linspace(0, 20, 1000)
    yp = func(xp, A=A, f=f)

    # Generate the plot
    fig, axes = lowpass.plot(xp, yp, xName="Time [s]", yName="Amplitude", freqUnits="Hz")

    # Check if the figure and axes are created
    assert isinstance(fig, plt.Figure)
    assert len(axes) == 2