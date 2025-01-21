#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: <N. Surname>       <e-mail>
Last update:        DD/MM/YYYY
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

#load the base class
from .Filter import Filter

#Other imports
import numpy as np
import scipy as sp
from scipy.signal import butter, filtfilt, freqz

import matplotlib as mpl
from matplotlib import pyplot as plt

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class LowPass(Filter):
    """
    Apply low-pass filter
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        cutoff:float
            Cutoff frequency
        
        order:int
            Order of the filter
    """
    
    #########################################################################
    #Properties:
    @property
    def cutoff(self) -> float:
        """
        cutoff frequency

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
        Create from dictionary.

        {
            cutoff (float): cutoff frequency
            order (int): order of the filter
        }
        """
        #Create the dictionary for construction
        Dict = {}
        
        entryList = ["cutoff"]
        for entry in entryList:
            if not entry in dictionary:
                raise ValueError(f"Mandatory entry '{entry}' not found in dictionary.")
            #Set the entry
            Dict[entry] = dictionary[entry]
        
        #Constructing this class with the specific entries
        out = cls(**Dict)
        return out
    
    #########################################################################
    def __init__(self, cutoff:float, *, order=5):
        """
        cutoff (float): The cur-off frequency
        order (int): The order of the filter (default:5)
        """
        #Argument checking:
        #Type checking
        self.checkType(cutoff, float, "cutoff")
        self.checkType(order, int, "order")

        self._cutoff = cutoff
        self._order = order
    
    #########################################################################
    #Dunder methods:
    def __call__(self, xp:"list[float]", yp:"list[float]")-> "tuple[list[float],list[float]]":
        """
        Filter an array of x,y data with low-pass filter
        """
        #Resample on uniform grid with step equal to the minimum step
        res_x, res_y, delta = self._preProcess(xp, yp)
        
        #Apply filter:
        filt_y = self._butter_lowpass_filter(res_y, self.cutoff, 1./delta, self.order).T
        filt_x = np.linspace(xp[0],xp[len(xp)-1], len(filt_y))
        
        return filt_x, filt_y
    
    ###################################
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(cutoff:{self.cutoff}, order:{self.order})"
    
    #########################################################################
    #Methods:
    def _butter_lowpass(self, cutoff:float, fs:float, order:int=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a
    
    ###################################
    def _butter_lowpass_filter(self, data:"list[float]", cutoff:float, fs:float, order:int=5):
        b, a = self._butter_lowpass(cutoff, fs, order=order)
        y = filtfilt(b, a, data)
        return y
    
    ###################################
    def _preProcess(self, xp:"list[float]", yp:"list[float]")-> "tuple[list[float],list[float],float]":
        """
        Pre-process data to uniform time-step (equal to minimum time-step found in list).
        
        Returns:
            tuple[list[float],list[float],float]: [resampled x, resampled y, delta]
        """
        #Cast to numpy array
        xp = np.array(xp)
        yp = np.array(yp)
        
        delta = min(np.diff(xp))
        res_x = np.arange(xp[0],xp[-1], delta)
        res_y = np.interp(res_x, xp, yp, float("nan"), float("nan"))
        
        return res_x, res_y, delta
    
    ###################################
    def plot(self, xp:"list[float]", yp:"list[float]", *, xName:"str|None"=None, yName:"str|None"=None, freqUnits:"str|None"=None, c="b", **kwargs) -> "tuple[mpl.Figure, np.ndarray[mpl.axes.Axes]]":
        """TODO"""
        #Cast to numpy array
        xp = np.array(xp)
        yp = np.array(yp)
        
        fig, ax = plt.subplots(2,1, figsize=(8,8))
        
        ax1 = ax[0]
        ax2 = ax[1]
        
        x, y, delta = self._preProcess(xp, yp)
        fs = 1./delta
        
        #Filter
        b, a = self._butter_lowpass(self.cutoff, 1./delta, order=self.order)
        w, h = freqz(b, a, worN=8000)
        ax1.plot(0.5*fs*w/np.pi, np.abs(h), c=c, label="Filter FRF")
        
        #Original FT
        RMS = np.sqrt(np.mean(y**2.))
        yf = sp.fftpack.fft(y)
        xf = np.linspace(0.0, 1.0/(2./fs), len(y)//2)
        ax1.plot(xf, 2.0/len(y) * 20*np.abs(yf[:len(y)//2])/RMS, c="grey", label="Original $\\mathcal{F}[y(x)]$")
        
        #Filter data:
        xNew, yNew = self(xp, yp)
        
        #Remove nan
        IDs = np.array([not v for v in np.isnan(yNew)])
        xNew, yNew = xNew[IDs], yNew[IDs]
        
        #Filtered FT:
        RMS = np.sqrt(np.mean(yNew**2.))
        deltaNew = min(np.diff(xNew))
        fsNew = 1./deltaNew
        yf = sp.fftpack.fft(yNew)
        xf = np.linspace(0.0, 1.0/(2./fsNew), len(yNew)//2)
        
        ax1.plot(xf, 2.0/len(yNew) * 20*np.abs(yf[:len(yNew)//2])/RMS, color="k", label="Filtered $\\mathcal{F}[y(x)]$")
        
        #Time domain:
        ax2.plot(xp, yp, 'grey', label='Original')
        ax2.plot(xNew, yNew, 'k', label='Filtered')
        
        #Axes:
        ax1.axvline(self.cutoff, color='k', linestyle="dashed", label="_no")
        
        ax1.set_xlim(1/xp[-1], 0.5*fs)
        ax1.set_ylim((1e-5,1e2))
        ax2.set(**kwargs)
        
        ax1.set_title("Frequency domain",fontsize=24)
        ax1.set_xlabel("Frequency" + (f"[{freqUnits}]" if not freqUnits is None else ""),fontsize=20)
        ax1.set_ylabel('Amplitude/RMS [-]',fontsize=20)
        ax1.set_yscale('log')
        ax1.set_xscale('log')
        ax1.legend(fontsize=20,fancybox=False).get_frame().set(edgecolor="k", alpha=1)
        
        ax2.set_title("Time domain",fontsize=24)
        ax2.set_xlabel(xName, fontsize=20)
        ax2.set_ylabel(yName,fontsize=20)
        ax2.legend(fontsize=20,fancybox=False).get_frame().set(edgecolor="k", alpha=1)
        
        fig.tight_layout()
        
        return fig, ax

#########################################################################
#Add to selection table of Base
Filter.addToRuntimeSelectionTable(LowPass)
