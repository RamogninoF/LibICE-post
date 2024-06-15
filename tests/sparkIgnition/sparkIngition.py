# -*- coding: utf-8 -*-
"""
Testing spark ignition solver
"""
def main():
    from libICEpost.src.base.Functions.runtimeWarning import GLOBALS
    GLOBALS.CUSTOM_ERROR_MESSAGE = False
    
    from libICEpost.src.engineModel.EngineModel.EngineModel import EngineModel
    from libICEpost.src.base.dataStructures.Dictionary import Dictionary

    import os
    thisPath = "/".join(__file__.split("/")[:-1])
    print(f"thisPath = {thisPath}")
    os.chdir(thisPath)
    
    # Source constrol dictionary
    controlDict = Dictionary.fromFile("./controlDict.py")
    print("Control dictionary:")
    # print(controlDict)
    
    # Build engine model
    engineModelType:str = controlDict.lookup("engineModelType")
    engineModelDict:Dictionary = controlDict.lookup(engineModelType + "Dict")
    dataDict:Dictionary = controlDict.lookup("data")
    model:EngineModel = EngineModel.selector("SparkIgnitionEngine", engineModelDict)
    
    #load pressure
    print("Loading data:")
    path = dataDict.lookupOrDefault("path", "./")
    
    pressureData:Dictionary = dataDict.lookup("pressure")
    dataFormat:str = pressureData.lookup("format")
    data:Dictionary = pressureData.lookup("data")
    
    if (dataFormat == "file"):
        fileName = data.lookup("fileName")
        opts:Dictionary = data.lookupOrDefault("opts", Dictionary())
        model.loadFile(f"{path if fileName[0] != '/' else ''}/{fileName}" , "p", **opts)
        
    elif (dataFormat == "array"):
        raise NotImplementedError()
    
    #load other data
    #TODO
    
    # Filtering data
    from libICEpost.src.base.Filter import Filter
    preProcessingDict = dataDict.lookup("preProcessing")
    filterType = preProcessingDict.lookup("FilterType")
    filter:Filter = Filter.selector(filterType, preProcessingDict.lookup(f"{filterType}Dict"))
    model.filterData(filter)
    
    #Construction of model for handling thermophysical properties and reaction
    #   Domain is split into zones (cylinder, prechamber, etc...). 
    #   Each zone is a thermodynamic model and their interaction will be controlled by the specific EngineModel
    
    #Dictionary for definition of thermophysical properties
    thermophysicalProperties:Dictionary = engineModelDict.lookup("thermophysicalProperties")
    
    #Dictionary for definition of combustion properties
    # Solver for premixed spark-ignition engine
    combustionProperties:Dictionary = engineModelDict.lookup("combustionProperties")
    
    combustionModelType = "PremixedCombustion"
    combustionModelDict = combustionProperties.lookup(combustionModelType + "Dict")
    combustionModelDict.update(thermo=thermophysicalProperties)
    
    #Compute composition through reaction model to compute reactants/products
    from libICEpost.src.thermophysicalModels.thermoModels.CombustionModel.CombustionModel import CombustionModel
    combustionModel = CombustionModel.selector(combustionModelType, combustionModelDict)
    
    print("air")
    print(combustionModel.air.mix)
    
    print("EGR")
    print(combustionModel.egrModel.EgrMixture)
    
    print("fresh mixture")
    print(combustionModel.freshMixture.mix)
    
    print("combustion products")
    print(combustionModel.combustionProducts.mix)
    
    # Set initial/boundary conditions
    #   Set initial conditions for all zones in the model (cylinder, prechamber, etc...). 
    # model.initializeThemodynamicModels(\
    #     cylinder=\
    #     {
    #         "pressure":"p",
    #         "mass":540e-6,
    #         "volume":"@geometry.V"
    #     })
    pass
    
if __name__ == "__main__":
    main()