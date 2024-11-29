#!/usr/bin/env python3
"""
Generator for tabulation of laminar flame speed from CANTERA or OpenSMOKE for LibICE-OpenFOAM code.

Tabulation stores values of laminar flame speed and thickness with respect to variables:
    p:      Pressure
    Tu:     Unburnt gas temperature
    phi:    Equivalence ratio
    egr:    EGR mass fraction (optional)
Which are stored as a list.

DEFINITIONS:
    alpha = m_air/m_fuel
    phi = alpha_st/alpha
    egr = m_air/(m_air + m_egr + m_f)

The computation of LFS is strongly sensitive to inital conditions, so the 
operating points already computed are used to initialize new reactors in 
similar conditions. Therefore, the following computation procedure is used:
    1) The process starts computing the LFS for a set of initial conditions
    2) All adjacent nodes in the (p,Tu,phi,egr) space are identified
    3) List of adjacents are added to the pool of simulations to execute 
       with solution of the current reactor as initial conditions
    4) The procedure iterates until the full data-set is covered

Compatible with LibICE-8.

#Sample of input dictionary: 
    p = [1e5, 2e5, 3e5]   #Pressure points in [Pa]
    Tu = [300, 400, 500]  #Unburnt gas temperature in [K]
    phi = [0.5, 1.0, 2.0] #Equivalence ratios
    egr = [0., 0.1]       #Exhaust gas recirculation mass fractions (optional)
    
    #The initial point(s) where to start the tabulation. This can be either a single dictionary (1 initial point) or a list of dicts (multiple starting points)
    initialConditions = \
        {
            "p": p[3],
            "Tu":Tu[0],
            "phi":1.,
            "egr":0.
        }
    
    #Mixture porperties
    mechanism = "./mech.xml" #The chemical mechanism in .xml format
    fuel = {"H2": 1.0} #The fuel mass-fraction composition
    air = {"O2": 0.21, "N2":0.78} #The air mass-fraction composition
    
    meshType = "pressureAdaptive"
    #The type of mesh to use. Options are:
    #   pressureAdaptive
    #   pressureTemperatureAdaptive
    #   constantWidth
    #   userDefined
    
    pressureAdaptiveDict = \
        {
            "refLength": 0.014,     #Lenght at standard conditions
            "expCoeff":1.5
        }
    pressureTemperatureAdaptiveDict = \
        {
            "refLength": 0.0138,     #Lenght at standard conditions
            "pressCoeff":1.45,
            "tempCoeff":-1.6,
            "maxGridPoints":3000,   #Allow up to 3000 grid-points (default is 1000 in cantera)
        }
    userDefinedDict = \
        {
            "grid": np.linspace(0, 0.025, 20)
        }
    constantWidthDict = \
        {
            "width": 0.025
        }
        
    #Grid refinement parameters
    gridRefinementParams = \
        {
            "ratio": 2, 
            "slope":0.005, 
            "curve":0.005, 
            "prune":0.000,
        }

    #Miscellaneous
    loglevel = 0 #Verbosity level of solution (0 to 5). Default is 0.
    numberOfProcessors = 6 #Number of cores for parallelization

    #Restart from an old tabulation
    tableName = "tableGasoline"          #The name of the table to create
    debugFile = "./tempTable.csv"       #File for saving a debug '.csv' file (optional). Useful for restart.
    restartFile = "./tempTable.csv"     #Restart file used if '-restart' flag is used
    fileFormat = "ascii" #"binary"      #Want to write in binary or ascii?
    
    #debugLogFile = "debug.log"           #Debug log file (needed if running with -redirect_debug flag)
"""

#--------------------------------------------#
#                   Imports                  #
#--------------------------------------------#
import sys
import os
import argparse
import traceback
import logging

log = logging.getLogger("createLaminarFlameSpeedTable")

from typing import Iterable
from enum import StrEnum

from multiprocessing import Pool
from multiprocessing.pool import ApplyResult

from tqdm import tqdm
import time
processStart = time.time()

import numpy as np
import cantera as ct
import pandas as pd
from pandas import DataFrame

from libICEpost.src.base.dataStructures.Dictionary import Dictionary
from libICEpost.src.thermophysicalModels.specie.reactions.ReactionModel.functions import computeAlphaSt, Mixture, mixtureBlend
from libICEpost.src.thermophysicalModels.thermoModels.EgrModel.StoichiometricMixtureEGR import StoichiometricMixtureEGR

from libICEpost.Database.chemistry.specie.Molecules import Molecules

from libICEpost.src.base.Functions.runtimeWarning import enf
from libICEpost.src.base.Functions.typeChecking import checkType

from libICEpost.src.thermophysicalModels.laminarFlameSpeedModels.TabulatedLFS import TabulatedLFS

#--------------------------------------------#
#              Argument parsing              #
#--------------------------------------------#
def cmdline_args():
    # Make parser object
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    #Control dictionary
    p.add_argument("dictionary",
                   help="The python dictionary where information for generation of the table are stored.", type=str)
    
    #Overwrite
    p.add_argument("-overwrite", action="store_true",
                   help="Allow overwriting.")
    
    #Restart
    p.add_argument("-restart", action="store_true",
                   help="Restart computation from a partial table in 'csv' format ('restartFile' in control dictionary).")
    
    # #Verbosity
    p.add_argument("-v", "--verbosity", choices=("DEBUG", "INFO", "ERROR"), default='INFO',
                   help="Increase output verbosity (default: %(default)s)")
    
    # #Verbosity
    p.add_argument("-redirect_debug", action="store_true",
                   help="Redirect debug output to 'debugLogFile' entry")

    return(p.parse_args())

#--------------------------------------------#
#                   Logging                  #
#--------------------------------------------#
#Formatter for logging
class MyFormatter(logging.Formatter):
    info_fmt = "%(msg)s"
    debug_fmt = enf(enf("DEBUG", "warning"),"bold") + " [%(module)s:%(lineno)s]: %(msg)s"
    err_fmt = enf(enf("ERROR", "fail"),"bold") + ": %(msg)s"
    warning_fmt = enf(enf("WARNING", "fail"),"warning") + ": %(msg)s"
    
    def _update(self,string:str):
        self._fmt = string
        self._style._fmt = string
    
    def format(self, record):
        
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._fmt

        # Info
        if record.levelno == logging.INFO:
            self._update(self.info_fmt)
        if record.levelno == logging.DEBUG:
            self._update(self.debug_fmt)
        if record.levelno == logging.ERROR:
            self._update(self.err_fmt)
        if record.levelno == logging.WARNING:
            self._update(self.warning_fmt)

        # Call the original formatter class to do the grunt work
        result = super().format(record)

        # Restore the original format configured by the user
        self._update(format_orig)

        return result

#--------------------------------------------#
#                  Aux func                  #
#--------------------------------------------#
#Mesh parameters
class MeshType(StrEnum):
    pressureAdaptive = "pressureAdaptive"
    pressureTemperatureAdaptive = "pressureTemperatureAdaptive"
    userDefined = "userDefined"
    constantWidth = "constantWidth"

#File format
class FileFormat(StrEnum):
    binary = "binary"
    ascii = "ascii"

#Flame description
def describe(input, flame):
    """Print a short description of the input conditions and flame, with a few properties."""
    # Using single string to prevent mixing of output in parallel computation
    s = ""
    s += f"Pressure             = {input['p']*1e-5} bar\n"
    s += f"Temperature          = {input['Tu']} K\n"
    s += f"Equivalence ratio    = {input['phi']}\n"
    s += f"Exhaust gas          = {input['egr']*100.:.2f}%\n"
    s += f"Flame speed          = {flame.velocity[0] * 100 :.2f} cm/s\n"
    s += f"Flame thickness      = {(flame.T[-1] - flame.T[0])/max(np.gradient(flame.T, flame.grid))*1e3 :.3f} mm\n"
    s += f"Maximum temperature  = {flame.T.max() :.0f} K\n"
    s += f"Solved with {flame.grid.size} grid points\n"
    log.debug(s)

#--------------------------------------------#
#                Computing LFS               #
#--------------------------------------------#
#Computation of lfs:
def computeLFS(p:float,
               Tu:float, 
               mixture:dict[str,float], 
               *, 
               mechanism:str, 
               meshType:MeshType, 
               meshTypeDict:dict, 
               gridRefinementParams:dict=dict(),
               loglevel:int=1,
               firstGuess:DataFrame=None
               ) -> ct.FreeFlame:
    
    #The mixture state
    engineFuel:ct.Solution = ct.Solution(mechanism)
    engineFuel.TPY = Tu, p, mixture
    
    #Create the mesh
    log.debug("Creating the mesh for 1D reactor")
    meshTypeDict = Dictionary(**meshTypeDict)
    if meshType == MeshType.pressureAdaptive:
        #Pressure dependend
        expCoef = meshTypeDict.lookup("expCoeff", varType=float)
        refLen = meshTypeDict.lookup("refLength", varType=float)
        width = refLen*(1e5/p)**expCoef
        flame = ct.FreeFlame(engineFuel, width=width)
    if meshType == MeshType.pressureTemperatureAdaptive:
        #Pressure and temperature dependent
        pressCoeff = meshTypeDict.lookup("pressCoeff", varType=float)
        tempCoeff = meshTypeDict.lookup("tempCoeff", varType=float)
        refLen = meshTypeDict.lookup("refLength", varType=float)
        width = refLen*(1e5/p)**pressCoeff*(Tu/300.)**tempCoeff
        flame = ct.FreeFlame(engineFuel, width=width)
    elif meshType == MeshType.userDefined:
        #User defined grid
        grid = meshTypeDict.lookup("grid")
        flame = ct.FreeFlame(engineFuel, grid=grid)
        width = grid[-1]
    if meshType == MeshType.constantWidth:
        #Constant width
        width = meshTypeDict.lookup("width", varType=float)
        flame = ct.FreeFlame(engineFuel, width=width)
    log.debug(f"Width of grid: {width}")
    
    #Setting maximum grid-points
    if "maxGridPoints" in meshTypeDict:
        maxGridPoints = meshTypeDict.lookup("maxGridPoints", varType=int)
        flame.set_max_grid_points(flame.flame,maxGridPoints)
        log.debug(f"Setting maximum grid points to {maxGridPoints}")
    
    #Set initial guess
    if not firstGuess is None:
        firstGuess["grid"] *= flame.grid[-1]/firstGuess["grid"][len(firstGuess)-1]
        log.debug(f"Setting initial guess for flame\n{firstGuess.iloc[::2]}")
        
        flame.set_initial_guess(data=firstGuess.iloc[::4])
    
    #Set parameteres
    log.debug("Setting additional parameters")
    flame.set_refine_criteria(**gridRefinementParams)
    flame.transport_model = "unity-Lewis-number"
    flame.soret_enabled = False
    
    #Solve
    flame.solve(loglevel=loglevel, refine_grid=True, auto=False)
    
    return flame

#Running asyncronous
def asyncRun(input, *, firstGuess=None, alphaSt, air, fuel, mechanism, meshType, meshParams, gridRefinementParams, loglevel) -> tuple[DataFrame,DataFrame|None]:
    results = DataFrame(data={i:[input[i]] for i in input})
    results[["Su", "deltaL"]] = float("nan")
    results["completed"] = False
    
    #Create the initial mixture
    alpha = alphaSt/input["phi"]
    yf = 1./(alpha + 1.)
    log.debug(f"alpha: {alpha}")
    log.debug(f"yf: {yf}")
    
    mixture = air.copy()    #Start from air
    mixture.dilute(fuel, yf, fracType="mass")    #Dilute with fuel
    if input["egr"] > 0:
        egrModel = StoichiometricMixtureEGR(air=air, fuel=fuel, egr=input["egr"])
        mixture.dilute(egrModel.EgrMixture, egrModel.egr, fracType="mass")    #Dilute air with egr
        log.debug(f"EGR: {egrModel.egr}")
        log.debug(f"EGR mixture: {[(s.specie.name, s.Y) for s in egrModel.EgrMixture]}")
    
    log.debug(f"mixture: {[(s.specie.name, s.Y) for s in mixture]}")
    
    try:
        flame = computeLFS(
            input["p"], 
            input["Tu"], 
            {s.specie.name:s.Y for s in mixture}, 
            mechanism=mechanism, 
            meshType=meshType, 
            meshTypeDict=meshParams, 
            gridRefinementParams=gridRefinementParams, 
            loglevel=loglevel,
            firstGuess=firstGuess)
        
        describe(input, flame)
        
        #Compute flame speed and thickness
        Su = flame.velocity[0]
        deltaL = (flame.T[-1] - flame.T[1])/max(np.gradient(flame.T, flame.grid))
        
        #Append to dataframe
        results.iloc[0] = [input[ii] for ii in input] + [Su, deltaL, True]
        return results, flame.to_pandas()
        
    except Exception as err:
        log.error("Failed computation for conditions:\n\t" + "\n\t".join([f"{c}: {input[c]}" for c in input]))
        log.debug(traceback.format_exc())
        return results, None

#Auxiliary function to wrap parallelization of function with kwargs with Pool.map method
def worker_wrapper(arg):
    ii, args, kwargs = arg
    return ii, asyncRun(*args, **kwargs)

#--------------------------------------------#
#                     Run                    #
#--------------------------------------------#
#Running the program
def run(dictName:str, *, overwrite=False, restart=False) -> None:
    """
    Main running function for generation of the tabulation.

    Args:
        dictName (str): name of input dictionary file.
        overwirte (bool, optional): Overwrite if found. Defaults to False.
    """

    #---------------------------------------------------------------------------#
    #Input dictionary
    log.info(f"Input dictionary: {dictName}")
    log.debug(f"Loading dictionary")
    inputDict = Dictionary.fromFile(dictName)
    log.debug(inputDict)
    
    #Table name
    tableName = inputDict['tableName']
    log.info(f"Table name: {tableName}")
    
    #Check for overwrite option
    if not overwrite:
        #Debug file
        if (False if not "debugFile" in inputDict else os.path.exists(inputDict["debugFile"])):
            log.error(f"Debug file '{inputDict['debugFile']}' already exists. Run with -overwrite option for overwriting results.")
            exit()
        if os.path.exists(tableName):
            log.error(f"Table '{tableName}' already exists. Run with -overwrite option for overwriting results.")
            exit()
    else:
        log.warning("Running in '-overwrite' mode.")
        time.sleep(1)
    
    #File format
    format = FileFormat(inputDict.lookupOrDefault("fileFormat", default="ascii").lower())
    
    #Load data
    pList = np.array(inputDict.lookup("p", varType=Iterable))
    TuList = np.array(inputDict.lookup("Tu", varType=Iterable))
    phiList = np.array(inputDict.lookup("phi", varType=Iterable))
    egrList = np.array(inputDict.lookupOrDefault("egr", default=np.array([0.0])))
    tabulatedEgr = "egr" in inputDict #Check if EGR is tabulated
    
    #Total number of conditions
    numEl = len(pList)*len(TuList)*len(phiList)*len(egrList)
    
    log.info("")
    log.info(f"Sampling points ({numEl}):")
    log.info(f"p({len(pList)}): {pList}")
    log.info(f"Tu({len(TuList)}): {TuList}")
    log.info(f"phi({len(phiList)}): {phiList}")
    log.info(f"EGR({len(egrList)}): {egrList}")
    log.info("")
    
    #Mesh parameters
    meshType = MeshType(inputDict.lookup("meshType", varType=str))
    meshParams = inputDict.lookup(meshType + "Dict", varType=dict)
    
    log.info(f"Mesh type: {meshType}")
    log.info("Mesh parameters: \n" + "\n".join(['{'] + [f"\t{p}: {meshParams[p]}" for p in meshParams] + ['}']))
    log.info("")
    
    #Mixture properties
    mechanism = inputDict.lookup("mechanism", varType=str)
    fuelMix = inputDict.lookup("fuel", varType=dict)
    airMix = inputDict.lookup("air", varType=dict)
    
    fuel = Mixture([Molecules[s] for s in fuelMix], [fuelMix[s] for s in fuelMix], fracType="mass")
    air = Mixture([Molecules[s] for s in airMix], [airMix[s] for s in airMix], fracType="mass")
    alphaSt = computeAlphaSt(air, fuel)
    
    log.info(f"fuel: {fuelMix}")
    log.info(f"air: {airMix}")
    log.info(f"alphaSt: {alphaSt}")
    log.info("")
    
    #Misellaneous
    gridRefinementParams = inputDict.lookupOrDefault("gridRefinementParams", default=dict())
    loglevel = inputDict.lookupOrDefault("loglevel", default=1)
    
    log.info("Grid refinement parameters: \n" + "\n".join(['{'] + [f"\t{p}: {gridRefinementParams[p]}" for p in gridRefinementParams] + ['}']))
    log.info(f"loglevel: {loglevel}")
    log.info("")
    
    #---------------------------------------------------------------------------#
    #Computation of the table of initial conditions, all combinations of (p,Tu,phi, EGR)
    inputList = []
    for p in pList:
        for t in TuList:
            for phi in phiList:
                for egr in egrList:
                    inputList.append({"p":p, "Tu":t, "phi":phi, "egr":egr})
    
    #Check for restart
    if restart:
        try:
            log.warning("Running in '-restart' mode.")
            log.info(f"Reading from file '{inputDict['restartFile']}'")
            time.sleep(1)
            
            #Read dataframe
            results = pd.read_csv(inputDict["restartFile"])
            log.debug(f"Restarting from:\n{results}")
            
            #Length
            if not len(results) == numEl:
                raise ValueError(f"Length of data inconsistent with sampling points ({len(results)}!={numEl})")
            
            #Check that all sampling points are present in table
            iptTab = [(v["p"], v["Tu"], v["phi"], v["egr"]) for _,v in results.iterrows()] #Sampling points in restart table
            for ipt in inputList:
                if not (ipt["p"], ipt["Tu"], ipt["phi"], ipt["egr"]) in iptTab:
                    raise ValueError("Data-points of restart tabulation are inconsistent with those in control dictionary. Not fount\n\t" + "\n\t".join([f"{c}: {ipt[c]}" for c in ipt]))
        
        except Exception as err:
            log.error(f"Failed restarting tabulation from backup file.")
            log.debug(traceback.format_exc())
            exit()
            
        
    else: 
        #Dataframe for output
        results = DataFrame(
            {
                "p":[float("nan")]*numEl, 
                "Tu":[float("nan")]*numEl, 
                "phi":[float("nan")]*numEl, 
                "egr":[float("nan")]*numEl, 
                "Su":[float("nan")]*numEl, 
                "deltaL":[float("nan")]*numEl,
                "completed":[False]*numEl,
            })
        
        #Filling input points
        ii = 0
        for p in pList:
            for t in TuList:
                for phi in phiList:
                    for egr in egrList:
                        results.iloc[ii,:4] = [p, t, phi, egr]
                        ii += 1
    
    
    log.info("Starting iteration")
    #Parallelization strategy:
    #   The computation of LFS is strongly sensitive to inital 
    #   conditions, so the operating points already computed are 
    #   used to initialize new reactors in similar conditions
    #   1) The process starts computing the LFS for an initial condition
    #   2) All adjacent nodes in the (p,Tu,phi) space are identified
    #   3) List of adjacents are added to the pool of simulations to execute 
    #      (childs), with solution of the current reactor as initial conditions
    #   4) The procedure iterates until the full data-set is covered
    
    #Initial conditions
    initialConditions:dict|Iterable = inputDict.lookup("initialConditions", varType=(dict, Iterable))
    #Check for single point
    if isinstance(initialConditions, dict):
        initialConditions = [initialConditions]
        
    firstIndex = []
    for ii, ic in enumerate(initialConditions):
        checkType(ic, dict, f"initialConditions[{ii}]")
        
        if not ((ic["p"] in pList) and (ic["Tu"] in TuList) and (ic["phi"] in phiList)):
            raise ValueError("Initial conditions not in tabulation dataset.\n\t" + "\n\t".join([f"{c}: {ic[c]}" for c in ic]))
        firstIndex.append(
            results.index[
                (results["Tu"] == ic["Tu"])
                &
                (results["p"] == ic["p"])
                &
                (results["phi"] == ic["phi"])
            ][0])
    
    completed = 0   #Number of conditions covered
    failed = 0  #Number of conditions failed
    successful = 0 #Numbre of conditions successful
    childs = {id:None for id in firstIndex}  #Table of childs to process, with relative IC
    
    #Parallelization
    numProc = inputDict.lookup("numberOfProcessors", varType=int) #Number of processors
    log.info(f"Parallelization on {numProc} processors")
    
    #Common kwargs
    kwargs = dict(alphaSt=alphaSt,
            air=air,
            fuel=fuel,
            mechanism=mechanism,
            meshType=meshType,
            meshParams=meshParams,
            gridRefinementParams=gridRefinementParams,
            loglevel=loglevel)
    
    #Progress bar
    progressBar = tqdm(initial=completed,total=numEl,unit="condition",file=sys.stdout)
    
    processorPool:dict[int,ApplyResult] = {}
    with Pool(processes=numProc) as pool:
        while (len(processorPool) > 0) or (len(childs) > 0):
            log.debug(f"Processing: {list(processorPool.keys())}")
            log.debug(f"In queue: {list(childs.keys())}")
            
            #Send to the pool of processes, while creating a progress bar
            sentToPool = []
            for c in childs:
                #Double check that the child was not already successfully processed (it might have been added while already processing but not completed yet)
                if results.iloc[c]["completed"] == True:
                    sentToPool.append(c) #Add to list of childs to remove
                    continue    #Skip
                
                #To send it to the pool, the child must satisfy the following requirements:
                #   1) Pool must have places avaliable
                #   2) Child should not be already part of the pool
                if (len(processorPool) < numProc) and (not c in processorPool):
                    processorPool[c] = pool.apply_async(worker_wrapper, args=((c, (inputList[c],), {**kwargs, "firstGuess":childs[c]}),))
                    sentToPool.append(c)
            
            #Removed childs sent to the pool
            for c in sentToPool:
                del childs[c]
            
            #Wait a bit
            time.sleep(1)
            
            #Retrieve outputs
            outputs = {}
            for p in processorPool:
                proc = processorPool[p]
                if proc.ready():
                    try:
                        out = proc.get()
                        outputs[out[0]] = out[1]
                        #Upgrade progress bar
                        progressBar.update(1)
                        log.debug(f"Completed {out[0]}")
                        log.debug(f"Value:\n{out[1]}")
                        completed += 1
                    except TimeoutError:
                        #Not ready yet
                        pass
                else:
                    log.debug(f"Process '{p}' not ready yet")
            
            #Display progress bar (in case no output was computed)
            progressBar.display()
            
            #Remove completed
            processorPool = {p:processorPool[p] for p in processorPool if not p in outputs}
            
            #Merge results
            for ii in outputs:
                results.iloc[ii] = outputs[ii][0]
                
                ## Compute adjacent operating conditions that were not processed
                #This point
                pID = [p for p in pList].index(inputList[ii]["p"])
                tID = [t for t in TuList].index(inputList[ii]["Tu"])
                phiID = [phi for phi in phiList].index(inputList[ii]["phi"])
                egrID = [egr for egr in egrList].index(inputList[ii]["egr"])
                #Adjacents
                adjacents = results[
                    (results["p"] >= pList[max(pID-1,0)])
                    &
                    (results["p"] <= pList[min(pID+1,len(pList)-1)])
                    &
                    (results["Tu"] >= TuList[max(tID-1,0)])
                    &
                    (results["Tu"] <= TuList[min(tID+1,len(TuList)-1)])
                    &
                    (results["phi"] >= phiList[max(phiID-1,0)])
                    &
                    (results["phi"] <= phiList[min(phiID+1,len(phiList)-1)])
                    &
                    (results["egr"] >= egrList[max(egrID-1,0)])
                    &
                    (results["egr"] <= egrList[min(egrID+1,len(egrList)-1)])
                ]
                #Remove completed and this point
                adjacents = adjacents[
                    (adjacents["completed"] == False) 
                    &
                    np.invert(
                        (adjacents["Tu"] == inputList[ii]["p"])
                        &
                        (adjacents["p"] == inputList[ii]["p"])
                        &
                        (adjacents["phi"] == inputList[ii]["p"])
                        &
                        (adjacents["egr"] == inputList[ii]["egr"])
                    )
                    ]
                
                #Add those that were completed as new child conditions to be computed
                if not outputs[ii][1] is None:
                    childs.update({adj:outputs[ii][1] for adj in adjacents.index})
                    successful += 1
                else:
                    failed += 1
    
    #Stop progress bar
    progressBar.close()
    
    #Conditions successfully completed
    conditionsCompleted = sum(int(v) for v in results['completed'].to_numpy())
    
    log.info("Completed computation.")
    log.info("")
    
    nFill = 80
    #Statistics on conditions tabulated
    log.info(" Statistics ".center(nFill,"="))
    log.info(f"\tOperating conditons:         {numEl}")
    log.info(f"\tConditions completed:        {conditionsCompleted}/{numEl} [{conditionsCompleted/numEl*100:.2f}%]")
    log.info("")
    
    #Stats on flames computed
    log.info(f"\tFlames computed:             {completed}")
    log.info(f"\tFlames successful:           {successful}/{completed} [{successful/completed*100:.2f}%]")
    log.info(f"\tFlames failed:               {failed}/{completed} [{failed/completed*100:.2f}%]")
    
    #Stats of time reqired
    log.info(" Time ".center(nFill,"="))
    hours, rem = divmod(time.time() - processStart, 3600)
    minutes, seconds = divmod(rem, 60)
    log.info(f"\tElapsed time:                {hours:0>2}h {minutes:0>2}min {seconds:05.2f}s")
    hours, rem = divmod((time.time() - processStart)/completed, 3600)
    minutes, seconds = divmod(rem, 60)
    log.info(f"\tTime per flame:              {hours:0>2}h {minutes:0>2}min {seconds:05.2f}s")
    hours, rem = divmod((time.time() - processStart)/conditionsCompleted, 3600)
    minutes, seconds = divmod(rem, 60)
    log.info(f"\tTime per condition:          {hours:0>2}h {minutes:0>2}min {seconds:05.2f}s")
    log.info("".center(nFill,"="))
    log.info("")
    
    log.info(" Results ".center(nFill,"="))
    log.info(f"\n{results}")
    log.info("".center(nFill,"="))
    
    #Save to csv as debug file to restart partially-failed tabulations
    if "debugFile" in inputDict:
        debugFileName = inputDict["debugFile"]
        log.info(f"Saving to csv state {debugFileName}")
        results.to_csv(debugFileName, index=False)
    
    #Additional information for the user
    tabProp = Dictionary(
            alphaSt=alphaSt,
            air=[s.specie.name for s in air],
            airY=[s.Y for s in air],
            fuel=[s.specie.name for s in fuel],
            fuelY=[s.Y for s in fuel])
    
    #Create OpenFOAM table
    tableOF = TabulatedLFS(
    Su=results["Su"].to_numpy(),
    deltaL=results["deltaL"].to_numpy(),
    pRange=pList,
    TuRange=TuList,
    phiRange=phiList,
    egrRange=egrList if tabulatedEgr else None,
    path=tableName,
    noWrite=False,
    tablePropertiesParameters=tabProp,
    )
    
    #Write the table
    log.info(f"Saving tabulation to {tableName}")
    tableOF.write(binary=format)
    
#--------------------------------------------#
#                     Main                   #
#--------------------------------------------# 
#Main
def main() -> None:
    try:
        #Parsing
        args = cmdline_args()
        
        #Logging
        hdlrs = []
        
        #stdout
        hdlr = logging.StreamHandler(sys.stdout)
        hdlr.setFormatter(MyFormatter())
        hdlr.setLevel(args.verbosity.upper())
        
        #Redirecting debug
        if args.redirect_debug:
            if args.verbosity.upper() == "DEBUG":
                hdlr.setLevel("INFO")
            
            controlDict = Dictionary.fromFile(args.dictionary)
            
            hdlr_file = logging.FileHandler(controlDict.lookup("debugLogFile", varType=str), mode="w")
            hdlr_file.setFormatter(MyFormatter())
            hdlr_file.setLevel("DEBUG")
            
            hdlrs.append(hdlr_file)
        
        hdlrs.append(hdlr)
        logging.basicConfig(level=args.verbosity.upper() if not args.redirect_debug else "DEBUG",handlers=hdlrs)
        
        #Running the program
        run(dictName=args.dictionary, overwrite=args.overwrite, restart=args.restart)
        
    except BaseException as err:
        if not isinstance(err,SystemExit):
            print(f'Failed generation of laminar flame speed table: {err}')
            print(traceback.format_exc())

if __name__ == '__main__':
    main()