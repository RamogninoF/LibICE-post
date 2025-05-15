#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testing solver for post-processing of CFD results from spark-ignition simulations
"""

#%%Importing and defining functions
import os
from libICEpost.src.engineModel.EngineModel.EngineModel import EngineModel

#To disable the warning from the janaf7 module of out of bound temperature
from libICEpost.src.thermophysicalModels.specie.thermo.Thermo.janaf7 import janaf7
janaf7.__WARNING__ = False

# Function for loading a dictionary and an engine model
from libICEpost.src.base.Functions.userInterface import loadDictionary
from libICEpost.src.engineModel.functions import loadModel

#%% Loading the data
#Getting the current path (needed when running in debug mode)
thisPath, _ = os.path.split(__file__)
print(f"thisPath = {thisPath}")
os.chdir(thisPath)  #Move here if in debug

#Parameters for loading the data
masterPath = os.path.join(thisPath, "dicts") #Path where the dictionaries are stored
reload = True #Reload the data if already loaded?

# Data structure for the dictionaries to load and (optionally) their templates
dictsPath:str = "./dicts/"
cases:dict[str,tuple[str,...]] = {
    "exp_A_25":("A/A25.py", "A.py", "exp.py", "base/controlDict.py"), #Select the dictionaries to load, from the most specific to the most general
    "exp_A_50":("A/A50.py", "A.py", "exp.py", "base/controlDict.py"),
    "exp_A_75":("A/A75.py", "A.py", "exp.py", "base/controlDict.py"),
    "exp_A_100":("A/A100.py", "A.py", "exp.py", "base/controlDict.py"),
}

# --------------------------------------------------
# Load data
# --------------------------------------------------
#Data structure for the models
if not "data" in locals():
    data:dict[str, EngineModel] = {}  #Dictionary to store the models

for case in cases:
    #Load the model
    print(f"Loading case {case}")
    
    #Get the control dictionary
    controlDict = loadDictionary(*[f"{dictsPath}/{c}" for c in cases[case]])
    
    #Load the model
    model = loadModel(controlDict, fatal=False)
    
    #If the model was not loaded correctly, skip the case
    if model is None:
        print(f"Failed loading model for case {case}")
        continue
        
    #Process the model
    model.process()
        
    #Store the model in the dictionary
    data[case] = model

############################################################
#%% Combined plot of pressure trace and rate of heat release #
############################################################
#Importing matplotlib and pyplot
from matplotlib import pyplot as plt
import matplotlib.colors as mcols
side_size = 8
line_width = 3
marker_size = 10
axis_size = 30
label_size = axis_size - 2
tick_size = axis_size - 2
tick_width = 2
tick_length = 8
dpi = 300
plt.rcParams.update(
{
    "text.usetex": True,
    "font.family": "Computer Modern",
    "font.size": axis_size,
    "lines.linewidth": line_width,
    "lines.markersize": marker_size,
    "xtick.major.width": tick_width,
    "xtick.major.size": tick_length,
    "ytick.major.width": tick_width,
    "ytick.major.size": tick_length,
    "xtick.labelsize": tick_size,
    "xtick.direction": 'in',
    "ytick.labelsize": tick_size,
    "ytick.direction": 'in',
    "axes.linewidth": tick_width,
    "axes.titlepad": 15,
    "legend.fontsize": tick_size - 7,
    "legend.loc": "upper left",
    "legend.fancybox": False,
    "legend.facecolor": "inherit",
    "legend.edgecolor": "black",
    "figure.figsize": (side_size, side_size),
    "figure.dpi": dpi,
    "contour.linewidth": 1,
    'contour.negative_linestyle': 'solid',
    "image.cmap": "turbo",
    'legend.framealpha': 1.0,
    "hatch.linewidth": 5,
})

# --------------------------------------------------
# Parameters for plotting
# --------------------------------------------------
#Parameters for the plot

#Cases to plot
casesToPlot:dict[str, dict[str, str]] = {
    "exp_A_25":
        {
            "color": "blue",
            "label": r"A-25",
        },
    "exp_A_50":
        {
            "color": "green",
            "label": r"A-50",
        },
    "exp_A_75":
        {
            "color": "orange",
            "label": r"A-75",
        },
    "exp_A_100":
        {
            "color": "red",
            "label": r"A-100",
        },
}

#Parameters for the plot
title = "Experimental data"
xLimit = (-40, 40)  #CAD

yLimits:dict[str, tuple[float, float]|None] = {
    "p": (-100, 250),  # [bar]
    "rohr": (-10, 1000),  # [J/kg]
}

figsize = (side_size, side_size*1.1)  #Figure size

# ----------------------------------------------------
# Plotting
# ----------------------------------------------------

#Axes
axes = (None, None)  #Axes for the plot

for case in casesToPlot:
    #Get the model
    model = data[case]
    
    #Get the color and label for the case
    color = casesToPlot[case].get("color", None)
    label = casesToPlot[case].get("label", None)
    
    #Plot the data
    axes = model.plotP_ROHR(label=label, color=color, axes=axes, figsize=figsize)
    
    #Get the limits
    axes[0].set_ylim(yLimits.get("p", None))
    axes[0].set_xlim(xLimit)
    axes[1].set_ylim(yLimits.get("rohr", None))
    
    
#Set the title
axes[0].set_title(title)
plt.tight_layout()

axes[0].legend(loc="lower left")

#Show the plot
plt.show()

# %%
