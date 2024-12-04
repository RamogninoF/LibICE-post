"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        9/03/2023

Package with useful classes and executables and function for pre/post processing of data in the context of internal combustion engines and CFD simulations"
    ->  Processing of experimental measurements on ICEs
    ->  Processing of results of CFD simulations
    ->  Computation of mixture compositions (external/internal EGR, thermophysical properties)
    ->  Processing of laminar flame speed correlations and OpenFOAM tabulations
    ->  Handling, reading/writing, and assessment of OpenFOAM tabulations
    
    Content of the package:
    TODO: Add description
"""

#Useful staff to have pre-loaded here
from .Database import database
from .src.base.BaseClass import BaseClass
from .src.base.dataStructures.Dictionary import Dictionary

# from .src.base.Logging.Logging import logger