import importlib
import pytest
import sys
import os

#Generate the test for all the modules in the libICEpost package
def get_modules():
    #Base folder
    baseModule = "./src/libICEpost"
    modules:list[str] = []
    
    skip:list[str] = \
        [
            "./src/libICEpost/src/_utils/PyFoam"
        ]
    
    if not os.path.exists(baseModule):
        raise FileNotFoundError(f"Base module {baseModule} not found")
    
    #Walk the base folder, save all the folders containing a __init__.py file or even a .py files that are not __init__.py
    # Store the modelule name as its full path replacing the separator with a dot
    for root, dirs, files in os.walk(baseModule):
        # Skip the folders that are in the skip list
        if any([root.startswith(s) for s in skip]):
            continue
        for file in files:
            #Skip files that are in skip list
            if os.path.join(root, file) in skip:
                continue
            if file.endswith(".py") and not file == "__init__.py":
                modules.append(os.path.join(root, file).replace(os.sep, ".").replace(".py", ""))
            elif file == "__init__.py":
                modules.append(root.replace(os.sep, "."))

    #Remove trailing ...src
    return [m.removeprefix("..src.") for m in modules]

MODULES = get_modules()

print(MODULES)
@pytest.mark.parametrize('module', MODULES)
def test_import_module(module):
    splitModule = module.rsplit(".", 1)
    if len(splitModule) == 1:
        p, m = "", splitModule[0]
        exec(f"import {m}")
    else:
        p, m = splitModule
        exec(f"from {p} import {m}")