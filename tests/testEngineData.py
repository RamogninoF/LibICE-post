# -*- coding: utf-8 -*-
"""
Testing EngineData class
"""

import traceback
import numpy as np
import pandas as pd
from libICEpost.src.base.dataStructures.EngineData.EngineData import EngineData


CA1 =  [0, 1,   2.2, 2.2, 3 ]
var1 = [0, 1.1, 3,   4,   5 ]

CA2 =  [-1, -0.5, 0, 1,   2.2, 2.2, 3, 4, 5.5]
var2 = [6,  12.1, 0, 1.1, 3,   4,   5, 6, 1  ]

CA3 =  [3, 4, 5, 5.5]
var3 = [7, 8, 9, 10]

CA4 =  [4.5,  5.25, 6,  7]
var4 = [11,   12,   13, 10]

CA5 =  [-10,  10]
var5 = [-10,  10]

def createTestData(CA, var):
    d = \
        {
            "list of tuples":([(ca, var[ii]) for ii,ca in enumerate(CA)], {"dataFormat":"column"}),
            "list of lists":([CA, var], {"dataFormat":"row"}),
            "numpy.array horizontal":(np.array([CA, var]), {"dataFormat":"row"}),
            "numpy.array vertical":(np.array([CA, var]).T, {"dataFormat":"column"}),
            "pandas.DataFrame":(pd.DataFrame({"CA":CA, "var":var}), {"dataFormat":"column"}),
            "pandas.DataFrame":(pd.DataFrame([CA, var]), {"dataFormat":"row"}),
        }
    return d

test1 = createTestData(CA1, var1)
test2 = createTestData(CA2, var2)
test3 = createTestData(CA3, var3)
test4 = createTestData(CA4, var4)
test5 = createTestData(CA5, var5)

#Testing:
for t in test1:
    try:
        print("---------------------------")
        print(f"test: {t}")
        
        print("Loading v1")
        print(f"data:\n{test1[t][0]}")
        ed = EngineData()
        ed.loadArray(test1[t][0], varName="var1", **test1[t][1])
        print(f"EngineData:\n{ed}")
        print()
        
        print("Loading v2")
        print(f"data:\n{test2[t][0]}")
        ed.loadArray(test2[t][0], varName="var2", **test2[t][1])
        print(f"EngineData:\n{ed}")
        print()
        
        print("Extending v1 without interpolation")
        print(f"data:\n{test3[t][0]}")
        ed.loadArray(test3[t][0], varName="var1", **test3[t][1])
        print(f"EngineData:\n{ed}")
        print()
        
        print("Extending v2 with interpolation")
        print(f"data:\n{test4[t][0]}")
        ed.loadArray(test4[t][0], varName="var2", **test4[t][1], interpolate=True)
        print(f"EngineData:\n{ed}")
        print()
        
        print("Loading v3 with interpolation")
        print(f"data:\n{test5[t][0]}")
        ed.loadArray(test5[t][0], varName="var3", **test5[t][1], interpolate=True)
        print(f"EngineData:\n{ed}")
        print()
        
    except BaseException as err:
        print("FAILED.")
        print(traceback.format_exc())