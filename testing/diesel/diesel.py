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
    thisPath, _ = os.path.split(__file__)
    print(f"thisPath = {thisPath}")
    os.chdir(thisPath)
    
    # Source constrol dictionary
    controlDict = Dictionary.fromFile("./controlDict.py")
    # print("Control dictionary:")
    # print(controlDict)
        
    # Build engine model
    engineModelType:str = controlDict.lookup("engineModelType")
    engineModelDict:Dictionary = controlDict.lookup(engineModelType + "Dict")
    model:EngineModel = EngineModel.selector("SparkIgnitionEngine", engineModelDict)
    
    model.process()
    
    from matplotlib import pyplot as plt
    model.data.data.plot(x="CA", y="ahrr")
    plt.show()
    
if __name__ == "__main__":
    main()