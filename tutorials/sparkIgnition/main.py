#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testing solver for post-processing of CFD results from spark-ignition simulations
"""

#Importing
import os
import traceback
import shutil
from libICEpost.src.engineModel.EngineModel.EngineModel import EngineModel
from libICEpost.src.base.dataStructures.Dictionary import Dictionary

#To disable the warning from the janaf7 module of out of bound temperature
#from libICEpost.src.thermophysicalModels.specie.thermo.Thermo.janaf7 import janaf7
#janaf7.__WARNING__ = False

#Define function for simpify loading:
def loadModel(path:str, controlDictName:str="controlDict.py") -> EngineModel|None:
    """
    Convenient function for loading the engineModel from the constrolDict.py file at specific 'path'.

    Args:
        path (str): The path where to find the controlDict.py file

    Returns:
        EngineModel: The engine model.
    """
    
    try:
        #Load the constrol dictionary
        print(f"Loading engine model from {path}/{controlDictName}")
        controlDict = Dictionary.fromFile(f"{path}/{controlDictName}")
        
        #Lookup engine model type and its dictionary
        engineModelType:str = controlDict.lookup("engineModelType")
        engineModelDict:Dictionary = controlDict.lookup(engineModelType + "Dict")
        
        #Construct from run-time selector
        model:EngineModel = EngineModel.selector(engineModelType, engineModelDict)
        return model
    
    except BaseException as err:
        print(f"Failed loading model from {path}:\n\t{err}")
        print(traceback.format_exc())
    

#Getting the current path (needed when running in debug mode)
thisPath, _ = os.path.split(__file__)
print(f"thisPath = {thisPath}")
os.chdir(thisPath)  #Move here if in debug

#Load the model
model = loadModel("./dictionaries/")

#Process the data in the engine model
model.process()

############################################################
# Combined plot of pressure trace and rate of heat release #
############################################################
#Importing matplotlib and pyplot
from matplotlib import pyplot as plt

#Setting plotting parameters
plt.rcParams.setdefault

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
    'figure.figsize':(6,6),
    #'figure.dpi':10
})

#Example of plotting and general output
#Plotting pressure-ROHR
axP, axRohr = model.plotP_ROHR(label="CFD", legend=True, c="k", figsize=(6,8))

#Adjust axes, limits, legend
axP.set_xlim((-30,30))  #x axis
axP.set_ylim((-10,40))  #pressure
axRohr.set_ylim((0,100)) #ROHR
axP.legend(loc="upper left")
plt.tight_layout()

#Plotting p-V diagram
ax = model.plotPV(label="CFD", timingsParams={"markersize":120, "linewidth":2})
plt.tight_layout()

#Output of the data to a csv file with comma as separator
#Check if the "output" folder exists, if not it creates it
#If it already exists, it removes it and creates a new one
output_folder = "output"
if os.path.exists(output_folder) and os.path.isdir(output_folder):
    # Remove the "output" folder
    shutil.rmtree(output_folder)
    print(f"Removed folder: {output_folder}")
    os.mkdir(output_folder)
    print(f"Created folder: {output_folder}")
else:
    print(f"Folder does not exist: {output_folder}")
    os.mkdir(output_folder)
    print(f"Created folder: {output_folder}")
    
model.data[:].to_csv(output_folder + "/Complete_processed_data.csv", sep=',', index=False)

#Save the pressure-ROHR plot
pressure_rohr_fig = axP.get_figure()
pressure_rohr_fig.savefig(output_folder + "/pressure_rohr_plot.png")

#Save the p-V diagram plot
pv_fig = ax.get_figure()
pv_fig.savefig(output_folder + "/pv_plot.png")

#Show the plots in matplotlib windows, note that this will not end the script
#until all matplotlib windows are closed
plt.show()