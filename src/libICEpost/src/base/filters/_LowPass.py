#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino (federico.ramognino@polimi.it)
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

#load the base class
from ._Filter import Filter

#Other imports
import numpy as np
import scipy as sp
from scipy.signal import butter, filtfilt, freqz

import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from libICEpost import Dictionary
from libICEpost.src.base.Functions.typeChecking import checkType

from typing import Iterable

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class LowPass(Filter):
    """
    A Butterworth low-pass filter with a given cutoff frequency and order.
    """
    
    #########################################################################
    #Properties:
    @property
    def cutoff(self) -> float:
        """
        Cut-off frequency

        Returns:
            float
        """
        return self._cutoff
    
    @property
    def order(self) -> int:
        """
        Order of the filter

        Returns:
            int
        """
        return self._order
    
    #########################################################################
    #Class methods and static methods:
    @classmethod
    def fromDictionary(cls, dictionary):
        """
        Create from dictionary with the following entries:
            - `cutoff` (`float`): the cutoff frequency
            - `order` (`int`, optional): the order of the filter. Defaults to 5.
        
        Args:
            dictionary (dict): the dictionary with the entries
        
        Returns:
            `LowPass`: the LowPass object
        """
        #Cast the dictionary to a Dictionary object
        dictionary = Dictionary(**dictionary)
        
        #Constructing this class with the specific entries
        data = {"cutoff":dictionary.lookup("cutoff")}
        if "order" in dictionary: data["order"] = dictionary.lookup("order")
        
        return cls(**data)
    
    #########################################################################
    def __init__(self, cutoff:float, *, order:int=5):
        """
        Create a low-pass filter with a given cutoff frequency and order.
        
        Args:
            cutoff (float): The cur-off frequency
            order (int, optional): The order of the filter. Defaults to 5.
        """
        #Argument checking:
        #Type checking
        checkType(cutoff, float, "cutoff")
        checkType(order, int, "order")

        if cutoff <= 0:
            raise ValueError(f"cutoff must be positive. Got {cutoff}")
        if order <= 0:
            raise ValueError(f"order must be positive. Got {order}")
        
        self._cutoff = cutoff
        self._order = order
    
    #########################################################################
    #Dunder methods:
    def __call__(self, xp:Iterable[float], yp:Iterable[float])-> tuple[np.ndarray[float], np.ndarray[float]]:
        #Type checking and recasting to numpy arrays
        xp, yp = Filter.__call__(self, xp, yp)
        
        #Resample on uniform grid with step equal to the minimum step
        res_x, res_y, delta = self._preProcess(xp, yp)
        
        #Apply filter:
        filt_y = self._butter_lowpass_filter(res_y, self.cutoff, 1./delta, self.order).T
        
        return res_x, filt_y
    
    ###################################
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(cutoff:{self.cutoff}, order:{self.order})"
    
    def __str__(self) -> str:
        return self.__repr__()
    
    #########################################################################
    #Methods:
    def _butter_lowpass(self, cutoff:float, fs:float, order:int=5):
        """
        Compute the Butterworth low-pass filter coefficients (b,a) for a given cutoff frequency and order.
        
        Args:
            cutoff (float): The cutoff frequency
            fs (float): The sampling frequency
            order (int, optional): The order of the filter. Defaults to 5.
        
        Returns:
            tuple[np.ndarray[float], np.ndarray[float]]: The filter coefficients (b,a)
        """
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a
    
    ###################################
    def _butter_lowpass_filter(self, data:Iterable[float], cutoff:float, fs:float, order:int=5):
        """
        Apply the Butterworth low-pass filter to a given data array.
        
        Args:
            data (Iterable[float]): The data to filter
            cutoff (float): The cutoff frequency
            fs (float): The sampling frequency
            order (int, optional): The order of the filter. Defaults to 5.
            
        Returns:
            np.ndarray[float]: The filtered data
        """
        #Data should be already checked by the __call__ method
        checkType(cutoff, float, "cutoff")
        checkType(fs, float, "fs")
        checkType(order, int, "order")
        
        #Get the filter coefficients
        b, a = self._butter_lowpass(cutoff, fs, order=order)
        
        #Remove nan
        where = np.invert(np.isnan(data))
        data_no_nan = data[where]
        
        #Filter
        y = np.array(data)
        y[where] = filtfilt(b, a, data_no_nan)
        return y
    
    ###################################
    def _preProcess(self, xp:Iterable[float], yp:Iterable[float])-> tuple[Iterable[float],Iterable[float],float]:
        """
        Pre-process data to uniform time-step (equal to minimum time-step found in list), since the filter 
        requires a uniform grid.
        
        Returns:
            tuple[Iterable[float],Iterable[float],float]: The resampled x and y data and the delta-x
        """
        #Cast to numpy array
        xp = np.array(xp)
        yp = np.array(yp)
        
        delta = min(np.diff(xp))
        n = int((xp[-1] - xp[0]) / delta)
        res_x = np.linspace(xp[0],xp[-1], n)
        res_y = np.interp(res_x, xp, yp, float("nan"), float("nan"))
        
        return res_x, res_y, delta
    
    ###################################
    def plot(self, xp:Iterable[float], yp:Iterable[float], *, 
             xName:str=None,
             yName:str=None,
             freqUnits:str=None
             ) -> tuple[Figure, Iterable[Axes]]:
        """
        Plot the frequency and time domain of the original and filtered data, with the filter FRF.
        
        Args:
            xp (Iterable[float]): The x data
            yp (Iterable[float]): The y data
            xName (str, optional): The x-axis label in the time domain. Defaults to None.
            yName (str, optional): The y-axis label in the time domain. Defaults to None.
            freqUnits (str, optional): The frequency units. Defaults to None.
        
        Returns:
            tuple[Figure, np.ndarray[Axes]]: The figure and axes
        """
        #Cast to numpy array and check
        xp, yp = Filter.__call__(self, xp, yp)
        
        fig, ax = plt.subplots(2,1, figsize=(8,8))
        
        ax1 = ax[0]
        ax2 = ax[1]
        
        x, y, delta = self._preProcess(xp, yp)
        fs = 1./delta
        
        #Filter
        b, a = self._butter_lowpass(self.cutoff, 1./delta, order=self.order)
        w, h = freqz(b, a, worN=8000)
        
        #Original FT
        RMS = np.sqrt(np.mean(y**2.))
        yf_Orig = sp.fftpack.fft(y)
        xf_Orig = np.linspace(0.0, 1.0/(2./fs), len(y)//2)
        
        #Filter data:
        xNew, yNew = self(xp, yp)
        
        #Remove nan
        IDs = np.array(np.invert(np.isnan(yNew)))
        xNew, yNew = xNew[IDs], yNew[IDs]
        
        #Filtered FT:
        RMS = np.sqrt(np.mean(yNew**2.))
        deltaNew = min(np.diff(xNew))
        fsNew = 1./deltaNew
        yf = sp.fftpack.fft(yNew)
        xf = np.linspace(0.0, 1.0/(2./fsNew), len(yNew)//2)
        
        #Frequency domain plots:
        ax1.plot(0.5*fs*w/np.pi, np.abs(h), c="blue", label="Filter FRF")
        ax1.plot(xf_Orig, 2.0/len(y) * 20*np.abs(yf_Orig[:len(y)//2])/RMS, c="grey", label="Original $\\mathcal{F}[y(x)]$")
        ax1.plot(xf, 2.0/len(yNew) * 20*np.abs(yf[:len(yNew)//2])/RMS, color="k", label="Filtered $\\mathcal{F}[y(x)]$")
        ax1.axvline(self.cutoff, color='k', linestyle="dashed", label="_no")
        
        #Time domain:
        ax2.plot(xp, yp, 'grey', label='Original')
        ax2.plot(xNew, yNew, 'k', label='Filtered')
        
        #Axes:
        ax1.set_xlim(1/xp[-1], 0.5*fs)
        ax1.set_ylim((1e-5,1e2))
        
        ax1.set_title("Frequency domain")
        ax1.set_xlabel("Frequency" + (f"[{freqUnits}]" if not freqUnits is None else ""))
        ax1.set_ylabel('Amplitude/RMS [-]')
        ax1.set_yscale('log')
        ax1.set_xscale('log')
        ax1.legend()
        
        ax2.set_title("Time domain")
        ax2.set_xlabel(xName)
        ax2.set_ylabel(yName)
        ax2.legend()
        
        fig.tight_layout()
        
        return fig, ax

#########################################################################
#Add to selection table of Base
Filter.addToRuntimeSelectionTable(LowPass)
