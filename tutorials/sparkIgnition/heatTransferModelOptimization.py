#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testing solver for post-processing of CFD results from spark-ignition simulations
"""

#Importing
import numpy as np
import os
import traceback
from libICEpost.src.engineModel.EngineModel.EngineModel import EngineModel
from libICEpost.src.base.dataStructures.Dictionary import Dictionary
from matplotlib import pyplot as plt

from libICEpost import GLOBALS
GLOBALS.__TYPE_CHECKING__ = True
GLOBALS.__SAFE_ITERABLE_CHECKING__ = True

#Disable warnings from janaf7
from libICEpost.src.thermophysicalModels.specie.thermo.Thermo.janaf7 import janaf7
janaf7.__WARNING__ = False

#%% Functions
#Define function for simpify loading:
def loadModel(path:str, controlDictName:str="controlDict.py", verbose:bool=True, process:bool=True) -> EngineModel|None:
    """
    Convenient function for loading the engineModel from the constrolDict.py file at specific 'path'.

    Args:
        path (str): The path where to find the controlDict.py file

    Returns:
        EngineModel: The engine model.
    """
    
    try:
        # Load the constrol dictionary
        print(f"Loading engine model from {path}/{controlDictName}")
        controlDict = Dictionary.fromFile(f"{path}/{controlDictName}")
        
        # Lookup engine model type and its dictionary
        engineModelType:str = controlDict.lookup("engineModelType")
        engineModelDict:Dictionary = controlDict.lookup(engineModelType + "Dict")
        
        #Construct from run-time selector
        model:EngineModel = EngineModel.selector(engineModelType, engineModelDict)
        if process: model.process()
        return model
    
    except BaseException as err:
        print(f"Failed loading model from {path}:\n\t{err}")
        if verbose:
            print(traceback.format_exc())

# Convergend
from typing import Iterable
#function object for computing energy
def saveEnergy(model):
    #Current time
    from libICEpost.src.thermophysicalModels.specie.reactions.functions import computeMixtureEnergy
    #Current time
    CA = model.time.time
    index = model.data.index[model.data.loc[:,'CA'] == CA].tolist()
    model.data.loc[index, "reactantsEnergy"] = computeMixtureEnergy(model.CombustionModel.freshMixture)*model.data.loc[index,"m"]
    model.data.loc[index, "productsEnergy"] = computeMixtureEnergy(model.CombustionModel.combustionProducts)*model.data.loc[index,"m"]

def xbConvergence(model:EngineModel, *, firstGuess:float|Iterable[float]=1.0, threshold:float=1e-3, maxiter:int=4, plotConvergence:bool=False):
    # Compute xb from LHV
    
    if not saveEnergy in model.info["functionObjects"]:
        print("Adding functionObject")
        model.info["functionObjects"].append(saveEnergy)
    
    print("\n")
    print("".center(60,"="))
    print("Computing convergence on burnt mass fraction (xb)")
    print("".center(60,"="))
    print(f"Maximum relative error: {threshold:.2%}")
    print(f"Maximum iterations: {maxiter}")
    
    #If no start of combustion, set to 1, process, and return
    if model.time.startOfCombustion() is None:
        print("No start of combustion found. Setting xb to 0")
        model.data["xb"] = 0.0
        model.process()
        return model
    
    #Set initial xb to 1
    model.data.loc[:,"xb"] = firstGuess
    xbOld = model.data.loc[:,"xb"]
    
    if plotConvergence:
        _ = plt.figure()
        ax1 = plt.gca()
        ax1.set_title("xb")
        _ = plt.figure()
        ax2 = plt.gca()
        ax2.set_title("error")
    
    numIter = 0
    meanError = 1
    while (meanError > threshold) and (numIter < maxiter):
        print(f"Iteration {numIter}".center(60, "-"))
        
        #Process
        model.process()
        
        #Update xb
        xbOld = model.data["xb"]*1.0
        #Compute target energy
        #TODO: force timings to be always in CA range
        EVO = model.data["CA"][model.time.isClosedValves(model.data["CA"])].to_numpy()[-1]
        targetEnergy = model.data.reactantsEnergy(EVO) - model.data.productsEnergy(EVO)
        model.data.loc[:,"xb"] = [min(1., max(0., x)) for x in model.data["cumHR"]/targetEnergy]
        
        #Set 0 before start of combustion
        model.data.loc[:,"xb"][model.data.loc[:,"CA"] <= model.time.startOfCombustion()] = 0.0
        
        #Set to maximum after the maximum (xb cannot go down)
        combustionEfficiency = max(
            model.data["xb"][
            model.time.isCombustion(model.data["CA"])
            &
            model.time.isClosedValves(model.data["CA"])]
            )
        maxXbID = model.data.index[
            (model.data["xb"] == combustionEfficiency)
            &
            model.time.isCombustion(model.data["CA"])
            &
            model.time.isClosedValves(model.data["CA"])
            ].to_numpy()[0]
        model.data.loc[maxXbID:,"xb"] = combustionEfficiency
        
        #Compute error
        meanError = (np.mean(abs(xbOld - model.data["xb"])))/np.mean(model.data["xb"])
        print(f"Mean error: {meanError:.2%}")
        print(f"Computed combustion efficiency: {combustionEfficiency:.2%}")
        print(f"Computed target energy: {targetEnergy:.2f}")
        
        #Plot
        if plotConvergence:
            ax1 = model.data.plot("CA", "xb", label=f"Iteration {numIter+1} (e = {meanError:.2%})", ax=ax1)
            ax2.plot(model.data["CA"], abs(xbOld - model.data["xb"]), label=f"Iteration {numIter+1} (e = {meanError:.2%})")
    
        # Update index
        numIter += 1
    
    if plotConvergence:
        ax1.legend()
        ax2.legend()
    
    print("COMPLETED".center(60, "-"))
    print(f"Number of iterations: {numIter} (max = {maxiter})")
    print(f"Mean relative error: {meanError:.2%}")
    print(f"Computed combustion efficiency: {combustionEfficiency:.2%}")
    return model

from functools import lru_cache

def heatTransferCoeffOptimizer(model:EngineModel, *, heatTransferModel:str, freeVariables:list[str], combustionEfficiency:float, tol:float=1e-4, maxiter:int=4, plotConvergence=None, xbConvergenceParams:dict=None, delta0Rel:float=1e-3, delta0Abs:float=1e-5, weights=[0.9, 0.01, 0.09], bounds:Iterable[tuple[float|None,float|None]]):
    #Set heat transfer model
    from libICEpost.src.engineModel.HeatTransferModel.HeatTransferModel import HeatTransferModel
    htm = HeatTransferModel.selector(heatTransferModel, {}) #Start from default parameters
    model.HeatTransferModel = htm
    
    #Get initial conditions of heat transfer model
    coeffs = {c:float('nan') for c in freeVariables}
    for c in freeVariables:
        if not c in htm.coeffs:
            raise ValueError(f"Coefficient {c} not a parameter of heat transfer model {heatTransferModel}")
        coeffs[c] = htm.coeffs[c]
    
    #Parameters for xb convergence analysis
    params = {}
    params.update(threshold=1e-3, maxiter=1, plotConvergence=False)
    if not xbConvergenceParams is None:
        params.update(**{v:xbConvergenceParams[v] for v in xbConvergenceParams if v in params})
    
    print("\n")
    print("".center(60,"="))
    print("Computing convergence on heat transfer model parameters")
    print("".center(60,"="))
    print(f"Heat transfer model: {heatTransferModel}")
    print(f"Tuning parameters:\n\t" + "\n\t".join(f"{p:<15}: {coeffs[p]} in range {bounds[ii]}" for ii, p in enumerate(coeffs)))
    print(f"Target combustion efficiency: {combustionEfficiency:.2%}")
    print(f"Tolerance: {tol:.2%}")
    print(f"Maximum iterations: {maxiter}")
    print(f"Parameters for xb convergence analysis:\n\t" + "\n\t".join(f"{p:<15}: {params[p]}" for p in params))
    
    #Updating function, returning the xb at EVO
    class updater:
        def __init__(self, model, coeffs, plotConvergence, combustionEfficiency, weights):
            self.model = model
            self.coeffs = {c:coeffs[c] for c in coeffs}
            self.combustionEfficiency = combustionEfficiency
            self.weights = weights[:]
            self.numIter = 0
            self.error = 1
            if plotConvergence:
                _ = plt.figure()
                self.ax1 = plt.gca()
                self.ax1.set_title("AHRR")
                self.ax1.set_xlabel("CA [°]")
                self.ax1.set_ylabel("[J/°]")
                _ = plt.figure()
                self.ax2 = plt.gca()
                self.ax2.set_title("ROHR")
                self.ax2.set_xlabel("CA [°]")
                self.ax2.set_ylabel("[J/°]")
                _ = plt.figure()
                self.ax3 = plt.gca()
                self.ax3.set_title("Heat losses")
                self.ax3.set_xlabel("CA [°]")
                self.ax3.set_ylabel("[J/°]")
                _ = plt.figure()
                self.ax4 = plt.gca()
                self.ax4.set_title("$x_b$")
                self.ax4.set_xlabel("CA [°]")
                self.ax4.set_ylabel("[-]")
        
        def __hash__(self):
            return hash(f"self.__class__.__name__({self.model.__class__.__name__},{self.coeffs.keys()},{self.combustionEfficiency})")
        
        def plot(self):
            if plotConvergence:
                self.model.data.plot("CA", "AHRR", ax=self.ax1, label=f"It {self.numIter+1} - {self.coeffs}")
                self.model.data.plot("CA", "ROHR", ax=self.ax2, label=f"It {self.numIter+1} - {self.coeffs}")
                self.model.data.plot("CA", "dQwalls", ax=self.ax3, label=f"It {self.numIter+1} - {self.coeffs}")
                self.model.data.plot("CA", "xb", ax=self.ax4, label=f"It {self.numIter+1} - {self.coeffs}")
        
        def __call__(self, x):
            #Rounding to prevent small steps
            x = tuple(float(f"{xx:.5g}") for xx in x)
            return self.cachedCall(x)
        
        @lru_cache(maxsize=200)
        def cachedCall(self, x):
            print(f"Iteration {self.numIter}".center(60, "-"))
            
            x = np.array(x)
            #Update heat transfer model
            self.model.HeatTransferModel.coeffs.update(**{var:xx for var,xx in zip(self.coeffs.keys(), x)})
            
            #Update model with xb convergence
            xbConvergence(self.model, **params, firstGuess=self.model.data["xb"])
            
            #Compute error
            #Error function with target
            #1) max(cumHR) aiming to combustionEfficiency*releasableEnergy
            e1 = 0.0
            EVO = model.data["CA"][model.time.isClosedValves(model.data["CA"])].to_numpy()[-1]
            avEn = self.model.data.reactantsEnergy(EVO) - self.model.data.productsEnergy(EVO)
            if not self.model.time.startOfCombustion() is None:
                cumHrMax = max(self.model.data["cumHR"][
                    self.model.time.isClosedValves(self.model.data["CA"]) &
                    self.model.time.isCombustion(self.model.data["CA"])])
                e1 = abs(cumHrMax - avEn*self.combustionEfficiency)/(avEn*self.combustionEfficiency)
            print(f"e1: {e1:.2%} (w = {self.weights[0]:.2%})")
            #2) |ROHR| before start of combustion minimuzed
            rohrMot = self.model.data["ROHR"][
                self.model.time.isClosedValves(self.model.data["CA"]) &
                np.invert(self.model.time.isCombustion(self.model.data["CA"]))]
            e2 = np.mean(abs(rohrMot))/((avEn**0.1) if (avEn*self.combustionEfficiency > 0) else 1.0)
            print(f"e2: {e2:.2%} (w = {self.weights[1]:.2%})")
            #3) cumHR strictly increasing (constant after its maximum)
            e3 = 0.0
            if not model.time.startOfCombustion() is None:
                whereMax = self.model.data.loc[self.model.data["cumHR"] == cumHrMax].index.to_numpy()[0]
                hrAfertMax = self.model.data["cumHR"][
                    self.model.time.isClosedValves(self.model.data["CA"]) &
                    self.model.time.isCombustion(self.model.data["CA"]) &
                    (self.model.data.index >= whereMax)]
                e3 = np.max(abs(hrAfertMax - cumHrMax))/(avEn*self.combustionEfficiency)
            print(f"e3: {e3:.2%} (w = {self.weights[2]:.2%})")
            
            #Update error
            self.error = 0.0
            errors = [e1, e2, e3]
            self.error = sum([w*e if not np.isnan(e*w) and not np.isinf(e) else 0.0 for w, e in zip(self.weights, errors)])
            
            #Final stuff
            self.coeffs.update({c:self.model.HeatTransferModel.coeffs[c] for c in self.coeffs})
            print(f"Current coefficients:\n\t" + "\n\t".join(f"{p:<15}: {self.coeffs[p]}" for p in self.coeffs))
            print(f"Relative error: {self.error:.2%}")
            print(f"Computed combustion efficiency: {up.model.data.xb(EVO):.2%}")
            self.plot()
            self.numIter += 1
            
            return self.error
    
    from scipy.optimize import minimize
    x0 = np.array([coeffs[c] for c in coeffs])
    up = updater(model, coeffs, plotConvergence, combustionEfficiency, weights=weights)
    delta0 = np.array([max(abs(x*delta0Rel), delta0Abs) for x in x0])
    finalCoeffs = minimize(up, x0, tol=tol, method="L-BFGS-B", bounds=bounds, options={"maxfun":maxiter, "maxiter":maxiter, "disp":False, "xrtol":tol, "eps":delta0})
    
    #Update with parameters
    up(finalCoeffs.x)
    
    if plotConvergence:
        up.ax1.legend()
        up.ax2.legend()
        up.ax3.legend()
        up.ax4.legend()
    
    EVO = model.data["CA"][model.time.isClosedValves(model.data["CA"])].to_numpy()[-1]
    
    print("COMPLETED".center(60, "-"))
    print(f"Number of iterations: {up.numIter} (max = {maxiter})")
    print(f"Initial coefficients:\n\t" + "\n\t".join(f"{p:<15}: {coeffs[p]}" for p in coeffs))
    print(f"Final coefficients:\n\t" + "\n\t".join(f"{p:<15}: {up.coeffs[p]}" for p in up.coeffs))
    print(f"Target combustion efficiency: {combustionEfficiency:.2%}")
    print(f"Final combustion efficiency: {up.model.data.xb(EVO):.2%}")
    print(f"Relative error: {up.error:.2%}")
    return model

# %% Loading
#Getting the current path (needed when running in debug mode)
thisPath, _ = os.path.split(__file__)
print(f"thisPath = {thisPath}")
os.chdir(thisPath)  #Move here if in debug

#The path where to load the model
modelPath = f"{thisPath}/dictionaries"

modelBaseline:EngineModel = loadModel(modelPath)

modelConverged:EngineModel = loadModel(modelPath, process=False)
heatTransferCoeffOptimizer(
    modelConverged,
    heatTransferModel="Woschni",
    freeVariables=["C1"],
    bounds=[(0, None)],
    combustionEfficiency= 0.78,
    plotConvergence=False,
    maxiter=10,
    xbConvergenceParams={"maxiter":1},
    delta0Abs=0.0,
    delta0Rel=0.1,
    weights=[0.8, 0.001, 0.2],
    )

#%% Plotting

ax = None
ax = modelBaseline.data.plot("CA", "AHRR", label="AHRR", ax=ax)
ax = modelConverged.data.plot("CA", "AHRR", ls="-.", label="_no", ax=ax, c=ax.lines[-1].get_color())
ax = modelBaseline.data.plot("CA", "ROHR", label="ROHR", ax=ax)
ax = modelConverged.data.plot("CA", "ROHR", ls="-.", label="_no", ax=ax, c=ax.lines[-1].get_color())
ax = modelBaseline.data.plot("CA", "dQwalls", label="dQ", ax=ax)
ax = modelConverged.data.plot("CA", "dQwalls", ls="-.", label="_no", ax=ax, c=ax.lines[-1].get_color())

ax.set_ylabel("[J]")
ax.set_xlim(modelBaseline.time.IVC, modelBaseline.time.EVO)
ax.axhline(0,c="k")

l1 = ax.legend(loc="upper left")
p = [0]*3
p[0], = ax.plot([0],[0], "k-")
p[1], = ax.plot([0],[0], "k-.")
p[2], = ax.plot([0],[0], "k--")
ax.legend(p, ["Default", "Convergence"], loc="upper right")
ax.add_artist(l1)


plt.show()