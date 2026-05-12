#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        27/04/2026
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from libICEpost.src.base.Functions.typeChecking import checkType
from .EngineGeometry import EngineGeometry

from collections.abc import Iterable

import numpy as np
from numpy import pi
import scipy.integrate as integrate

import pandas as pd
from typing import ClassVar

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class WankelGeometry(EngineGeometry):
    """
    Geometry for Wankel rotary engine.

    Attributes:
        - R (float): Rotor generating radius [m]
        - e (float): Eccentricity [m]
        - a (float): Parallel transfer housing [m]
        - cl (float): Clearance [m]
        - b (float): Rotor width [m]
        - vMinAdd (float): Additional dead volume (spark plug holes, rotor recess) [m^3]
        - vMinTheo (float): Theoretical dead volume [m^3]
        - Vmin (float): Actual minimum volume (vMinTheo + vMinAdd) [m^3]
        - Vs (float): Displacement volume per rotor [m^3]
        - Vmax (float): Maximum volume [m^3]
        - Vconst (float): Volume law amplitude term [m^3]
        - CR (float): Compression ratio [-]
        - TC (float): Trochoid constant R/e [-]
        - TDC (float): Top dead center crank angle [deg]
        - patches (list[str]): List of patch names
    """
    
    _patches: ClassVar[list[str]] = ["rotor", "housing", "side"]
    """List of patches names"""

    #########################################################################
    # Properties
    @property
    def R(self) -> float:
        """Rotor generating radius [m]"""
        return self._R

    @property
    def e(self) -> float:
        """Eccentricity [m]"""
        return self._e

    @property
    def a(self) -> float:
        """Parallel transfer housing [m]"""
        return self._a

    @property
    def cl(self) -> float:
        """Clearance [m]"""
        return self._cl

    @property
    def b(self) -> float:
        """Rotor width [m]"""
        return self._b

    @property
    def vMinAdd(self) -> float:
        """Additional dead volume [m^3]"""
        return self._vMinAdd

    @property
    def patches(self) -> list[str]:
        """
        Returns the list of patches names.

        Returns:
            list[str]: List of patches names
        """
        return self._patches[:]

    # Cached derived properties
    @property
    def TC(self) -> float:
        """Trochoid constant R/e [-]"""
        return self._TC

    @property
    def a_prime(self) -> float:
        """Parallel transfer rotor: a - cl [m]"""
        return self._a_prime

    @property
    def R1(self) -> float:
        """Actual housing radius R + a [m]"""
        return self._R1

    @property
    def R2(self) -> float:
        """Actual rotor radius R + a_prime [m]"""
        return self._R2

    @property
    def phiMax(self) -> float:
        """Max oscillation angle [rad]"""
        return self._phiMax

    @property
    def vMinTheo(self) -> float:
        """Theoretical dead volume [m^3]"""
        return self._vMinTheo

    @property
    def Vconst(self) -> float:
        """Volume law amplitude term: sqrt(3)/2 * e * (2*R1 + R2) * b [m^3]"""
        return self._Vconst

    @property
    def Vs(self) -> float:
        """Displacement volume per rotor [m^3]"""
        return self._Vs

    @property
    def Vmin(self) -> float:
        """Minimum volume [m^3]"""
        return self._Vmin

    @property
    def Vmax(self) -> float:
        """Maximum volume [m^3]"""
        return self._Vmax

    @property
    def CR(self) -> float:
        """Compression ratio [-]"""
        return self._CR

    @property
    def TDC(self) -> float:
        """Top dead center crank angle [deg]"""
        return self._TDC
    
    @property
    def S(self) -> float:
        """Equivalent stroke [m]"""
        return self._Vs / self._rotorArea
    
    @property
    def D(self) -> float:
        """Equivalent bore [m]"""
        return 2.0 * np.sqrt(self._rotorArea / np.pi)
    
    #########################################################################
    # Construct from dictionary
    @classmethod
    def fromDictionary(cls, inputDict: dict):
        """
        Construct from dictionary containing:
        - rotorRadius (float): Rotor generating radius [m]
        - eccentricity (float): Eccentricity [m]
        - parallelTransfer (float): Parallel transfer housing [m]
        - clearance (float): Clearance [m]
        - rotorWidth (float): Rotor width [m]
        - TDC (float, optional): Top dead center crank angle [deg]. Default 90.0.
        - vMinAdd (float, optional): Additional dead volume [m^3]. Default 0.0.
        - VolumeLaw (array-like, optional): (N,2) array of [CA, V] for lookup. Default None.
        - AreaLaw (array-like, optional): (N,2) array of [CA, A] for lookup. Default None.

        Args:
            inputDict (dict): Dictionary containing the parameters
        """
        return cls(**inputDict)

    #########################################################################
    # Dunder methods
    def __str__(self):
        STR = super(self.__class__, self).__str__()
        STR += "\n{:25s} {:10.3f} {:15s}".format("CR", self.CR, "[-]")
        STR += "\n{:25s} {:10.3f} {:15s}".format("TC = R/e", self.TC, "[-]")
        STR += "\n{:25s} {:10.3e} {:15s}".format("rotorRadius (R)", self.R, "[m]")
        STR += "\n{:25s} {:10.3e} {:15s}".format("eccentricity (e)", self.e, "[m]")
        STR += "\n{:25s} {:10.3e} {:15s}".format("parallelTransfer (a)", self.a, "[m]")
        STR += "\n{:25s} {:10.3e} {:15s}".format("clearance (cl)", self.cl, "[m]")
        STR += "\n{:25s} {:10.3e} {:15s}".format("TDC", self.TDC, "[deg]")
        STR += "\n{:25s} {:10.3e} {:15s}".format("rotorWidth (b)", self.b, "[m]")
        STR += "\n{:25s} {:10.3e} {:15s}".format("vMinTheo", self.vMinTheo, "[m^3]")
        STR += "\n{:25s} {:10.3e} {:15s}".format("vMinAdd", self.vMinAdd, "[m^3]")
        STR += "\n{:25s} {:10.3e} {:15s}".format("Vmin", self.Vmin, "[m^3]")
        STR += "\n{:25s} {:10.3e} {:15s}".format("Vs (per rotor)", self.Vs, "[m^3]")
        STR += "\n{:25s} {:10.3e} {:15s}".format("Vmax", self.Vmax, "[m^3]")
        return STR

    #########################################################################
    # Constructor
    def __init__(self, *,
                 rotorRadius: float,
                 eccentricity: float,
                 parallelTransfer: float,
                 clearance: float,
                 rotorWidth: float,
                 vMinAdd: float = 0.0,
                 TDC: float = -90.0,
                 ):
        """
        Constructor for WankelGeometry.

        Args:
            rotorRadius (float): Rotor generating radius [m]
            eccentricity (float): Eccentricity [m]
            parallelTransfer (float): Parallel transfer housing [m]
            clearance (float): Clearance [m]
            rotorWidth (float): Rotor width [m]
            vMinAdd (float, optional): Additional dead volume (spark plug holes, rotor
                recess) [m^3]. Default 0.0. If 0.0, use imposeCR() to set it from a
                target compression ratio.
            TDC (float, optional): Top dead center crank angle [deg]. Default 90.0.
        """
        self.checkType(rotorRadius, float, "rotorRadius")
        self.checkType(eccentricity, float, "eccentricity")
        self.checkType(parallelTransfer, float, "parallelTransfer")
        self.checkType(clearance, float, "clearance")
        self.checkType(rotorWidth, float, "rotorWidth")
        self.checkType(vMinAdd, float, "vMinAdd")
        self.checkType(TDC, float, "TDC")

        self._R = rotorRadius
        self._e = eccentricity
        self._a = parallelTransfer
        self._cl = clearance
        self._b = rotorWidth
        self._vMinAdd = vMinAdd
        self._TDC = TDC
        
        # Derived properties
        self._TC = self._R / self._e
        self._a_prime = self._a - self._cl
        self._R1 = self._R + self._a
        self._R2 = self._R + self.a_prime
        self._phiMax = np.arcsin(3.0 * self._e / self._R)
        
        self._R_x = self._R - self._e + 3.0 * self._e * self._R / (self._R - 4.0 * self._e)
        self._beta: float = np.arctan(np.sqrt(3.0)*self._R/(6.0*self._e*self._R/(self._R - 4.0*self._e) + (self._R + 2.0*self._e)))
        
        R1, R2, e, b = self.R1, self.R2, self._e, self._b
        phiMax = self.phiMax
        self._vMinTheo: float = (
            np.pi/3.0 * e**2
            + (R1**2 - R2**2) / (3*np.pi)
            + 2.0 * e * R2 * np.cos(phiMax)
            + (2.0/9.0 * R2**2 + 4.0 * e**2) * phiMax
            - np.sqrt(3)/2.0 * e * (2.0*R1 + R2)
        ) * b
        
        self._Vconst = np.sqrt(3)/2.0 * e * (2.0*R1 + R2) * b
        self._Vs = 2.0 * self._Vconst
        self._Vmin = self.vMinTheo + self._vMinAdd
        self._Vmax = self._Vmin + self._Vs
        self._CR = self._Vmax / self._Vmin
        
        self._rotorArea = self._R_x * 2 * self._beta * self._b

    #########################################################################
    # Volume
    def V(self, CA: float | Iterable[float]) -> float | np.ndarray:
        """
        Returns the instantaneous chamber volume at CA [m^3].

        Uses VolumeLaw lookup table if provided, otherwise the analytical formula:
            V = Vmin + Vconst * (1 - sin(2/3 * CA_rad + pi/6))

        Args:
            CA (float | Iterable[float]): Crank angle [deg]

        Returns:
            float|np.ndarray: Chamber volume [m^3]
        """
        if isinstance(CA, Iterable) and not isinstance(CA, np.ndarray):
            CA = np.array(CA)
        angle = np.radians(CA - self._TDC)  # Shift CA so that TDC is at 0 deg for the formula
        return self._Vmin + self._Vconst * (1.0 - np.sin(2.0/3.0 * angle + np.pi/6.0))

    def dVdCA(self, CA: float | Iterable[float]) -> float | np.ndarray:
        """
        Returns the time (in CA) derivative of instantaneous chamber volume [m^3/deg].

        Analytical derivative of the volume formula (always used, ignoring VolumeLaw).

        Args:
            CA (float | Iterable[float]): Crank angle [deg]

        Returns:
            float|np.ndarray: dV/dCA [m^3/deg]
        """
        if isinstance(CA, Iterable) and not isinstance(CA, np.ndarray):
            CA = np.array(CA)
        angle = np.radians(CA - self._TDC)  # Shift CA so that TDC is at 0 deg for the formula
        return -self._Vconst * (2.0/3.0) * np.cos(2.0/3.0 * angle + np.pi/6.0) * (np.pi/180.0)

    #########################################################################
    def housingArea(self, CA: float | Iterable[float]) -> float | np.ndarray:
        """
        Returns the area of the housing in contact with the chamber at CA [m^2].

        Args:
            CA (float | Iterable[float]): Crank angle [deg]

        Returns:
            float|np.ndarray: Housing area [m^2]
        """
        if isinstance(CA, Iterable) and not isinstance(CA, np.ndarray):
            CA = np.array(CA)
        angle = np.radians(CA - self._TDC)  # Shift CA so that TDC is at 0 deg for the formula
        
        e = self._e
        R = self._R
        phiMax = self.phiMax
        
        def ds_base(alpha):
            ds_base_sq = \
                e**2 + \
                R**2 / 9.0 + \
                2.0 * e * R / 3.0 * np.cos(2.0/3.0 * alpha)
            return np.sqrt(ds_base_sq)

        def curv_num(alpha):
            cn = \
                e ** 2.0 + \
                R**2 / 27.0 + \
                4.0 * e * R / 9.0 * np.cos(2.0/3.0 * alpha)
            return cn
        
        def kappa(alpha):
            k = curv_num(alpha) / ds_base(alpha)**3.0
            return k
        
        def integrand(alpha):
            return ds_base(alpha) * np.abs(1.0 + kappa(alpha) * self._a)
        
        num_points = 100
        if isinstance(CA, Iterable):
            # Vectorized integration from angle to angle + 2*pi
            alpha_ranges = angle[:, np.newaxis] + np.linspace(0, 2.0 * np.pi, num_points)
            housing_area = np.array([integrate.simpson(integrand(alpha_ranges[i]), alpha_ranges[i]) for i in range(len(angle))]) * self._b
            return housing_area
        else:
            alpha_range = np.linspace(angle, angle + 2.0 * np.pi, num_points)
            return integrate.simpson(integrand(alpha_range), alpha_range) * self._b
    
    def rotorArea(self, CA: float | Iterable[float]) -> float | np.ndarray:
        """
        Returns the area of the rotor in contact with the chamber at CA [m^2].

        Args:
            CA (float | Iterable[float]): Crank angle [deg]

        Returns:
            float|np.ndarray: Rotor area [m^2]
        """
        if isinstance(CA, Iterable) and not isinstance(CA, np.ndarray):
            CA = np.array(CA)
        if isinstance(CA, Iterable):
            return np.full_like(CA, self._rotorArea) # Rotor area is constant, so return an array of the same shape as CA
        else:
            return self._rotorArea
                
    def sideArea(self, CA: float | Iterable[float]) -> float | np.ndarray:
        """
        Returns the area of the side in contact with the chamber at CA [m^2].

        Args:
            CA (float | Iterable[float]): Crank angle [deg]

        Returns:
            float|np.ndarray: Side area [m^2]
        """
        if isinstance(CA, Iterable) and not isinstance(CA, np.ndarray):
            CA = np.array(CA)
        angle = np.radians(CA - self._TDC)  # Shift CA so that TDC is at 0 deg for the formula
        
        e = self._e
        R = self._R
        phiMax = self.phiMax
        
        return 2*((pi/3.0)*e**2 + e*R*(2.0*np.cos(phiMax) - 3.0/2.0*np.sqrt(3.0) * np.sin(2.0/3.0 * angle + pi/6.0)) + (2.0/9.0 * R**2 + 4.0 * e**2) * phiMax)
    
    def A(self,CA:float|Iterable[float]) -> float|np.ndarray:
        return self.housingArea(CA) + self.rotorArea(CA) + self.sideArea(CA)
    
    ###################################
    def areas(self,CA:float|Iterable) -> pd.DataFrame:
        data = \
        {
            "CA":CA if isinstance(CA, Iterable) else [CA], 
            "housing":self.housingArea(CA) if isinstance(CA, Iterable) else [self.housingArea(CA)],
            "rotor":self.rotorArea(CA) if isinstance(CA, Iterable) else [self.rotorArea(CA)],
            "side":self.sideArea(CA) if isinstance(CA, Iterable) else [self.sideArea(CA)],
        }
        return pd.DataFrame.from_dict(data, orient="columns")

    #########################################################################
    # Utility
    def imposeCR(self, CR: float) -> None:
        """
        Adjust vMinAdd so that the geometry achieves the target compression ratio.

        Updates Vmin, Vmax, CR, and vMinAdd accordingly.

        Args:
            CR (float): Target compression ratio [-]
        """
        self.checkType(CR, float, "CR")
        new_Vmin = self.Vs / (CR - 1.0)
        self._vMinAdd = new_Vmin - self.vMinTheo
        for attr in ("_Vmin", "_Vmax", "_CR"):
            if hasattr(self, attr):
                delattr(self, attr)

#########################################################################
#Add to selection table:
EngineGeometry.addToRuntimeSelectionTable(WankelGeometry)
