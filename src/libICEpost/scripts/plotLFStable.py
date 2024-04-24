#! /usr/bin/env python3

######################################################################
#Imports:
import argparse
import os
import shutil

import sys
# setting path
sys.path.append("/home/framognino/OpenFOAM/utilities/LibICE_postV3/")

from src.thermophysicalModels.laminarFlameSpeedModels import tabulatedLFS
from src.base.Functions.runtimeWarning import fatalError
import src.GLOBALS

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

######################################################################
GLOBALS = \
    {\
        "version":"1.0.0",
        "path":None,
    }

src.GLOBALS.VERBOSITY_LEVEL=0

######################################################################
#Check script arguments
def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser\
    (
        prog="plotLFStable",
        usage="%(prog)s [OPTIONS]",
        description="Python utility for visualization of a laminar flame speed tabulation in OpenFOAM format."
    )
    
    #Version
    parser.add_argument\
    (
        "-v", "--version",
        action="version",
        version = f"{parser.prog} version {GLOBALS['version']}"
    )
    
    #Case directory
    parser.add_argument\
    (
        "-case",
        action="store",
        default="./",
        help="The directory where the tabulation is stored",
        type=str
    )
    
    #xVar
    parser.add_argument\
    (
        "-xVar",
        action="store",
        default="p",
        help="Varaible of x axis (defauls: p)",
        type=str
    )
    
    #yVar
    parser.add_argument\
    (
        "-yVar",
        action="store",
        default="T",
        help="Varaible of y axis (defauls: T)",
        type=str
    )
    
    #isoPhi
    parser.add_argument\
    (
        "-isoPhi",
        action="store",
        default=[],
        help="Iso-surfaces to plot"
    )

    #isoEGR
    parser.add_argument\
    (
        "-isoEGR",
        action="store",
        default=[],
        help="Iso-surfaces to plot"
    )
    
    #xLims
    parser.add_argument\
    (
        "-xLims",
        action="store",
        default=[],
        help="Limits of x variable for plotting"
    )
    
    #xLims
    parser.add_argument\
    (
        "-yLims",
        action="store",
        default=[],
        help="Limits of y variable for plotting"
    )
    
    return parser

######################################################################
def readArguments():
    #Parse arguments:
    parser = init_argparse()
    args = parser.parse_args()
    
    print("Running",parser.prog,"utility\n")
    
    #Path
    GLOBALS["path"] = args.case
    
    if GLOBALS["path"][-1] != "/":
        GLOBALS["path"] += "/"
    
    if (GLOBALS["path"][0] == "/"):
        pass
    elif (len(GLOBALS["path"]) > 1):
        if (GLOBALS["path"][:2] == "./"):
            pass
        else:
            GLOBALS["path"] = "./" + GLOBALS["path"]
    else:
        pass
    
    return args

######################################################################
def ceckData(xVar, yVar, xLims, yLims, isoPhi, isoEGR):
    table = tabulatedLFS.fromFile(GLOBALS["path"], isLaminarFlameThickness=False, Fatal=False, extrapolate=False)
    
    if not(xVar in table.varOrder):
        raise ValueError(f"Variable '{xVar}' not present among fields of the tabulation. Available fields are {table.varOrder}")
    
    if not(yVar in table.varOrder):
        raise ValueError(f"Variable '{yVar}' not present among fields of the tabulation. Available fields are {table.varOrder}")
    
    if (xVar == yVar):
        raise ValueError("xVar and yVar cannot be the same.")
    
    if len(xLims) > 0:
        #TODO
        pass
    else:
        xLims = None
    
    if len(yLims) > 0:
        #TODO
        pass
    else:
        yLims = None
    
    isoSurfs = []
    if len(isoPhi) == 0:
        isoPhi = table.ranges()["phi"]
    else:
        isoPhi = isoPhi.split()
        if not(isinstance(isoPhi, list)):
            isoPhi = [isoPhi]
        for ii, item in enumerate(isoPhi):
            isoPhi[ii] = float(item)
    
    if not ("EGR" in table.varOrder):
        raise ValueError("Trying to impose isoEGR surfaces, but the tabulation does not containe EGR levels.")
    else:
        if len(isoEGR) == 0:
            isoEGR = table.ranges()["EGR"]
        else:
            isoEGR = isoEGR.split()
            if not(isinstance(isoEGR, list)):
                isoEGR = [isoEGR]
            for ii, item in enumerate(isoEGR):
                isoEGR[ii] = float(item)
            
    for ii, phi in enumerate(isoPhi):
        for jj, EGR in enumerate(isoEGR):
            isoSurfs.append({"phi":phi, "EGR":EGR})
    
    return table, xVar, yVar, xLims, yLims, isoSurfs
    
######################################################################
def plotTable(xVar, yVar, xLims, yLims, isoPhi, isoEGR):
    try:
        table, xVar, yVar, xLims, yLims, isoSurfs = ceckData(xVar, yVar, xLims, yLims, isoPhi, isoEGR)
        #xRange
        xRange = []
        for item in table.ranges()[xVar]:
            if not(xLims is None):
                if item <= xLims[0] or item >= xLim[1]:
                    xRange.append(item)
            else:
                xRange.append(item)
        
        #yRange
        yRange = []
        for item in table.ranges()[yVar]:
            if not(yLims is None):
                if item <= yLims[0] or item >= yLim[1]:
                    yRange.append(item)
            else:
                yRange.append(item)
        
        fig, ax = table.tables["Su"].plot(xVar,yVar,isoSurfs)
        plt.show()
    except BaseException as err:
        fatalError("Could not plot the laminar flame speed tabulation",err)

######################################################################
#The program
def main() -> None:
    #Arguments:
    args = readArguments()
    
    try:
        #Main program:
        plotTable(args.xVar, args.yVar, args.xLims, args.yLims, args.isoPhi, args.isoEGR)
        
    except BaseException as err:
        fatalError("Execution failed",err)
    
######################################################################
#Run
if __name__ == "__main__":
    main()
    print("End.")
