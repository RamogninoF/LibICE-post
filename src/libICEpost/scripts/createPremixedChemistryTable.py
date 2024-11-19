#!/usr/bin/env python3
"""
Generator for tabulation of laminar flame speed 
from CANTERA or OpenSMOKE for LibICE-OpenFOAM code.

Tabulation of chemical composition of reactants and products of premixed 
combustion (0 and 1 progress variable respectively) with respect to variables:
    p:      Pressure
    Tu:     Unburnt gas temperature
    phi:    Equivalence ratio
    egr:    EGR mass fraction (optional)
Which are stored as a list.

Chemical compositions are computed both under assumption of chemical 
equilibrium (Y<specie>Eq)and at the adiabatic flame temperature from 
unburnt-gas temperature (Y<specie>Adf)

Compatible with LibICE-8.

#Sample of input dictionary: 
    p = [1e5, 2e5, 3e5]   #Pressure points in [Pa]
    Tu = [300, 400, 500]  #Unburnt gas temperature in [K]
    phi = [0.5, 1.0, 2.0] #Equivalence ratios
    egr = [0., 0.1]       #Exhaust gas recirculation mass fractions (optional)
    
    #Mixture porperties
    mechanism = "./mech.xml" #The chemical mechanism in .xml format
    fuel = {"H2": 1.0} #The fuel mass-fraction composition
    air = {"O2": 0.21, "N2":0.78} #The air mass-fraction composition
    
    #Miscellaneous
    numberOfProcessors = 6 #Number of cores for parallelization
    tableName = "tableGasoline"          #The name of the table to create
    fileFormat = "ascii" #"binary"      #Want to write in binary or ascii?
"""

#--------------------------------------------#
#                   Imports                  #
#--------------------------------------------#
import sys
import os
import argparse
import traceback
import logging

log = logging.getLogger("createPremixedChemistryTable")

from typing import Iterable
from enum import StrEnum

from multiprocessing import Pool

from tqdm import tqdm
import time
processStart = time.time()

import numpy as np
import cantera as ct
import pandas as pd
from pandas import DataFrame

from libICEpost.src.base.dataStructures.Dictionary import Dictionary
from libICEpost.src.thermophysicalModels.specie.reactions.ReactionModel.functions import computeAlphaSt, Mixture
from libICEpost.src.thermophysicalModels.thermoModels.EgrModel.StoichiometricMixtureEGR import StoichiometricMixtureEGR

from libICEpost.Database.chemistry.specie.Molecules import Molecules

from libICEpost.src.base.Functions.runtimeWarning import enf

from libICEpost.src.base.dataStructures.Tabulation.OFTabulation import OFTabulation

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
    
    #Verbosity
    p.add_argument("-v", "--verbosity", choices=("DEBUG", "INFO", "ERROR"), default='INFO',
                   help="Increase output verbosity (default: %(default)s)")
    
    # Redirect debug
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

#File format
class FileFormat(StrEnum):
    binary = "binary"
    ascii = "ascii"

#Flame description
def describe(ipt:dict[str,float], reactor, condition:str):
    """Print a short description of the input conditions."""
    # Using single string to prevent mixing of output in parallel computation
    s = ""
    s += f"{'Condition':<30s} = {condition}\n"
    s += f"{'Pressure':<30s} = {ipt['p']*1e-5} bar\n"
    s += f"{'Temperature':<30s} = {ipt['tu']} K\n"
    s += f"{'Equivalence ratio':<30s} = {ipt['phi']}\n"
    s += f"{'Exhaust gas':<30s} = {ipt['egr']*100.:.2f}%\n"
    
    relevantSpecie = ["CO", "CO2", "OH"]
    for specie in relevantSpecie:
        #Check if found:
        try:
            s += f"{'y(' + specie + ')':<30s} = {reactor.species_index(specie)*100:.2f}%\n"
        except ValueError:
            pass
        
    log.debug(s)

#--------------------------------------------#
#                Computing flame             #
#--------------------------------------------#

#Running asyncronous
def computeChemistry(ipt:dict[str,float], *, alphaSt:float, air:Mixture, fuel:Mixture, mechanism:str):
    #Create the initial mixture
    egrModel = StoichiometricMixtureEGR(air=air, fuel=fuel, egr=ipt["egr"])
    alpha = alphaSt/ipt["phi"]
    yf = 1./(alpha + 1.)
    
    mixture = air.copy()    #Start from air
    mixture.dilute(fuel, yf, fracType="mass")    #Dilute with fuel
    mixture.dilute(egrModel.EgrMixture, egrModel.egr, fracType="mass")    #Dilute with egr
    
    log.debug(f"alpha: {alpha}")
    log.debug(f"yf: {yf}")
    log.debug(f"mixture: {[(s.specie.name, s.Y) for s in mixture]}")
    
    #Reference conditions
    Tref = 298.
    Pref = 1e5
    
    #Create the cantera reactors
    reactants = ct.Solution(mechanism)
    equilibrium = ct.Solution(mechanism)
    adf = ct.Solution(mechanism)
    ref = ct.Solution(mechanism)
    
    Tmax = 1500. #NOTE: Limit the temperature for adf computation to prevent numerical problems 
    ref.TPY = Tref, Pref, {s.specie.name:s.Y for s in mixture}
    reactants.TPY = min(ipt["tu"], Tmax), ipt["p"], {s.specie.name:s.Y for s in mixture}
    equilibrium.TPY = ipt["tu"], ipt["p"], {s.specie.name:s.Y for s in mixture}
    adf.TPY = min(ipt["tu"], Tmax), ipt["p"], {s.specie.name:s.Y for s in mixture}
    
    #Reactants
    describe(ipt, reactants, "reactants")
    
    # Equilibrium
    equilibrium.equilibrate("TP")
    describe(ipt, equilibrium, "equilibrium")
    
    # Adiabati flame temperature
    describe(ipt, adf, "Adiabatic flame")
    adf.equilibrate("HP")
    
    #Progress variable
    c0 = reactants.h - ref.h
    cMax = adf.h - ref.h
    
    #Dataframe of results
    specie = reactants.species_names
    results = DataFrame({**{v:([ipt[v], ipt[v]] if v != "c" else [ipt[v], 1.0]) for v in ipt}, **{f"Y{s}Eq":[0., 0.] for s in specie}, **{f"Y{s}Adf":[0., 0.] for s in specie} , "c0":[0., 0.], "cMax":[0., 0.]})
    results.iloc[0] = [ipt[v] for v in ipt] + [reactants.Y[reactants.species_index(s)] for s in specie] + [reactants.Y[reactants.species_index(s)] for s in specie] + [c0, cMax]
    ipt.update(c=1.) #Cange c = 1
    results.iloc[1] = [ipt[v] for v in ipt] + [equilibrium.Y[equilibrium.species_index(s)] for s in specie] + [adf.Y[adf.species_index(s)] for s in specie] + [c0, cMax]
    
    #Reindex results
    return results

#Auxiliary function to wrap parallelization of function with kwargs with Pool.map method
def worker_wrapper(arg):
    ii, args, kwargs = arg
    return ii, computeChemistry(*args, **kwargs)

#--------------------------------------------#
#                     Run                    #
#--------------------------------------------#
#Running the program
def run(dictName:str, *, overwrite=False) -> None:
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
    
    #Mixture properties
    mechanism = inputDict.lookup("mechanism", varType=str)
    fuelMix = inputDict.lookup("fuel", varType=dict)
    airMix = inputDict.lookup("air", varType=dict)
    
    fuel = Mixture([Molecules[s] for s in fuelMix], [fuelMix[s] for s in fuelMix], fracType="mass")
    air = Mixture([Molecules[s] for s in airMix], [airMix[s] for s in airMix], fracType="mass")
    alphaSt = computeAlphaSt(air, fuel)
    specie = ct.Solution(mechanism).species_names
    specieW = ct.Solution(mechanism).molecular_weights
    
    log.info(f"fuel: {fuelMix}")
    log.info(f"air: {airMix}")
    log.info(f"alphaSt: {alphaSt}")
    log.info(f"specie: {specie}")
    log.info("")
    
    #---------------------------------------------------------------------------#
    #Computation of the table of initial conditions, all combinations of (p,Tu,phi, EGR)
    inputList = []
    for p in pList:
        for t in TuList:
            for phi in phiList:
                for egr in egrList:
                    inputList.append({"p":p, "tu":t, "phi":phi, "egr":egr, "c":0.0})
    
    #Dataframe for results
    results = DataFrame(
        {
            "p":[float("nan")]*numEl*2, 
            "tu":[float("nan")]*numEl*2, 
            "phi":[float("nan")]*numEl*2, 
            "egr":[float("nan")]*numEl*2,
            "c":[float("nan")]*numEl*2,
            **{f"Y{s}Eq":[float("nan")]*numEl*2 for s in specie}, 
            **{f"Y{s}Adf":[float("nan")]*numEl*2 for s in specie},
            "c0":[float("nan")]*numEl*2, 
            "cMax":[float("nan")]*numEl*2,
        })
    
    #Default kwargs
    kwargs = dict(alphaSt=alphaSt,
                    air=air,
                    fuel=fuel,
                    mechanism=mechanism)
    
    log.info("Starting iteration")
    numProc = inputDict.lookup("numberOfProcessors")
    log.info(f"Parallelizing on {numProc} processors")
    with Pool(processes=numProc) as pool:
        for r in tqdm(
            pool.imap_unordered(worker_wrapper, [(ii, (ipt,), {**kwargs})  for ii,ipt in enumerate(inputList)]),
            file=sys.stdout,
            total=numEl,
            initial=0,
            unit="condition"):
            #Store the output
            results.iloc[(2*r[0]):(2*r[0] + 2)] = r[1].iloc[:]
            
    log.info("Completed computation.")
    log.info("")
    
    nFill = 80
    #Stats of time reqired
    log.info(" Time ".center(nFill,"="))
    hours, rem = divmod(time.time() - processStart, 3600)
    minutes, seconds = divmod(rem, 60)
    log.info(f"\tElapsed time:                {hours:0>2}h {minutes:0>2}min {seconds:05.2f}s")
    hours, rem = divmod((time.time() - processStart)/numEl, 3600)
    minutes, seconds = divmod(rem, 60)
    log.info(f"\tTime per condition:          {hours:0>2}h {minutes:0>2}min {seconds:05.2f}s")
    log.info("".center(nFill,"="))
    log.info("")
    
    log.info(" Results ".center(nFill,"="))
    log.info(f"\n{results}")
    log.info("".center(nFill,"="))
    
    # results.to_csv("results.csv")
    
    #Construct the tables
    order = ["p", "tu", "phi", "egr", "c"]
    fields = [c for c in results.columns if not c in order]
    ranges = \
        {
            "p":pList,
            "tu":TuList,
            "phi":phiList,
            "egr":egrList,
            "c":[0.0, 1.0],
        }
    inputNames = {o:o+"Values" for o in order}
    data = {var:results[var].to_numpy() for var in results.columns if var in fields}
    tabProp = Dictionary(
            assumeMixingLine=False,
            includeFuelEvaporation=False,
            TFuelMixingLine=300.,
            alphaSt=alphaSt,
            stoichiometricMixtureFraction=(1. - egrList)/(1. + alphaSt), #Stoichiometric mixture fraction
            species=specie,
            specieW=specieW,
            air=[s.specie.name for s in air],
            airY=[s.Y for s in air],
            fuel=[s.specie.name for s in fuel],
            fuelY=[s.Y for s in fuel],
            tValues=TuList,
            tbValues=TuList,)
    
    #Create OpenFOAM table
    tableOF = OFTabulation(
        data=data,
        ranges=ranges,
        inputNames=inputNames,
        tablePropertiesParameters=tabProp,
        order=order,
        path=tableName,
        noWrite=False
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
        run(dictName=args.dictionary, overwrite=args.overwrite)
        
    except BaseException as err:
        if not isinstance(err,SystemExit):
            print(f'Failed generation of table: {err}')
            print(traceback.format_exc())

if __name__ == '__main__':
    main()