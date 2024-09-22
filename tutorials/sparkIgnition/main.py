# -*- coding: utf-8 -*-
"""
Testing solver for post-processing of CFD results from spark-ignition simulations
"""

#Importing
import os
from libICEpost.src.engineModel.EngineModel.EngineModel import EngineModel
from libICEpost.src.base.dataStructures.Dictionary import Dictionary

#Getting the current path (needed when running in debug mode)
thisPath, _ = os.path.split(__file__)
print(f"thisPath = {thisPath}")
os.chdir(thisPath)  #Move here if in debug

# Load the constrol dictionary
controlDict = Dictionary.fromFile("./dictionaries/controlDict.py")

# Lookup engine model type and its dictionary
engineModelType:str = controlDict.lookup("engineModelType")
engineModelDict:Dictionary = controlDict.lookup(engineModelType + "Dict")

#Construct from run-time selector
model:EngineModel = EngineModel.selector(engineModelType, engineModelDict)

#Process the data in the engine model
model.process()

############################################################
# Combined plot of pressure trace and rate of heat release #
############################################################
#Importing matplotlib and pyplot
from matplotlib import pyplot as plt

#Setting plotting parameters
plt.rcParams.update({
    # "text.usetex": True,
    # "font.family": "serif",
    "font.monospace": ["Times"],
    "xtick.labelsize":22,
    "ytick.labelsize":22,
    'axes.labelsize': 28,
    'axes.titlesize': 24,
    "legend.fontsize":20,
    'lines.linewidth': 3,
    'axes.linewidth': 2,
    'figure.figsize':(6,12),
    # 'figure.dpi':10
})

#Create figure and combined axes (pressure lefr, ROHR right)
fig, axP = plt.subplots(1,1, figsize=(6,8))
axRohr = axP.twinx()

#Processed data are stored in the entry 'model.data' of type EngineData.
#This is a wrapper around a pandas.DataFrame data-structure, which is 
#the entry EngineModel.data. Hence we use the method DataFrame.plot, which 
#is a convenient interface for plotting of the data inside the DataFrame instance 

#Pressure
model.data.data.plot(\
    x="CA", y="pBar",                           #x and y variables 
    c="k", ylabel="p [bar]", xlabel="[CAD]",    #Formatting
    ax=axP,                                     #Axes
    legend=False)                               #No legend

#Rate of heat release (ROHR)
model.data.data.plot(\
    x="CA", y="ROHR",                           #x and y variables
    c="k", ls="--", ylabel="ROHR [J/CA]",       #Formatting
    ax=axRohr,                                  #Axes
    legend=False)                               #No legend

#Adjust axes and limits
plt.tight_layout()
axP.set_xlim((-30,30))  #x axis
axP.set_ylim((-10,40))  #pressure
axRohr.set_ylim((0,100)) #ROHR

#Show the figure
plt.show()