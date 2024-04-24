"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        9/03/2023

Package with useful classes and function for pre/post processing of data in the context of internal combustion engines and CFD simulations"
    ->  Processing of experimental measurements on ICEs
    ->  Processing of results of CFD simulations
    ->  Computation of mixture compositions (external/internal EGR, thermophysical properties)
    ->  Processing of laminar flame speed correlations and OpenFOAM tabulations
    ->  Handling, reading/writing, and assessment of OpenFOAM tabulations

Content of the package
    GLOBALS
        Global variables that are used from the package
        NOTE: Some variables are not defined within this file but added sub-packages, as they are related to their operations

    base (package)
        Basic functions and classes or data-structures that are useful for the overall package
    
    thermophysicalModels (package)
        Classess used to handle:
            Composition of mixtures of perfect gasses (atoms, molecules, mixtures)
            Thermophysical properties of mixtures and molecules
            Laminar flame speed correlations
"""
