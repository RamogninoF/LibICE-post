# Changelog
## v0.0.3 (16/10/2024)

- First releases.

## v0.10.0 (23/4/2025)
First release introducing testing (coverege around 70%).

Tested packages/functions:
### Tabulation and OFTabulation
- Refactored `concat` methods for performance improvements.
- Optimized `toPandas` and `concat` functions.
- Fixed `insertDimension` for consistent access between sub-classes.
- Bug fix in `plot`, `squeeze`, and handling of oxidation reaction in `ReactionModel::Stoichiometry` when not already in database.
- Changed backend in `computeAlphaSt` to use `cantera` for alphaSt calculation.
- Added comments for stoichiometric ratio calculation in `computeAlphaSt` function.
- Accept single float values as ranges in `slice` methods.
- Accept empty iso for tables with only 2 variables in `plot`.
### Enhancements
### Dictionary
- Improved error outputs in `Dictionary.fromFile` by compiling the content before execution.
- Relying on `checkType` backend for type-checking `lookup` and `lookupOrDefault` methods.
- Enhanced `checkArray` function: improved type checking for numpy arrays and added tests for mixed types and pandas DataFrame.
- Added `allowEmpty` parameter to `checkArray`.
- `checkArray`: add `allowEmpty` parameter and optimized type checking for numpy arrays.
### Tutorials
- Added tutorial for using `loadDictionary` function with templetized dictionary structure (handling multiple conditions with similar configurations).
- Streamlined model loading by integrating `loadDictionary` and removing redundant `loadModel` function.
- `Tabulation`, `OFTabulation`: Optimized `toPandas` methods.
### User Interface
- Created `userInterface` module for user interface functionalities.
- Added `loadDictionary` function for loading a dictionary from a sequence of templates.

### Engine Models
- Added `loadModel` function for loading engine models from control dictionaries.
### Changes
### readOFscalarList
- Changed backend to `foamlib` for improved performance in reading files.
- `OFTabulation(slice)` and `Tabulation(slice)`: accept single float values as ranges.
### Documentation
- Updated README documentation for installation and setup of conda.
- Fixed typos and improved comments in README and `dataDict.py`.
- Fixed typo in docstring for `OFTabulation` class constructor.
- `Tabulation(plot)`: Accept also empty iso for tables with only 2 variables.
### Tests
- Updated test structure for functions and added tests for `userInterface`.

## v0.10.1.post1 (26/03/2025)

### Fixes
- `makeEquilibriumMechanism`: Fixed conversion of data to builtin classes to ensure correct conversion to YAML format
  
## v0.10.2 (7/04/2025)

### Enhancements
- Added `src._utils` module for managing external package dependencies.
- Introduced a custom version of `PyFoam` at `src._utils.PyFoam` with fixes to ensure compatibility with Windows.

### Changes
- Remove `pyfoam` dependency
- Remove `PyFoam` patches and from `libICEpost-applyPatches` script

## v0.10.3 (12/09/2025)
This version mostly improves the functionalities and efficiency of tabulated classes.

### Tabulated classes
#### Fixes
- Refactored `concat` and `toPandas` methods in `Tabulation` and `OFTabulation` for performance improvements.
- Fixed `insertDimension` in `Tabulation` for consistent access between sub-classes.

#### Changes
- Changed backend of `readOFscalarList` to `foamlib` for improved performance in reading files.

### Other
#### Fixes
- Bug fix in `ReactionModel::Stoichiometry` when oxidation reaction is not already in database.

#### Changes
- Changed backend in `computeAlphaSt` to use `cantera` for alphaSt calculation.
- `Dictionary.fromFile`: Improved error outputs when loading from file by compiling the content of the dictionary before execution.
- Relying on `checkType` backend for type-checking `lookup` and `lookupOrDefault` methods in `Dictionary`.
- Enhanced `checkArray` function: improved type checking for numpy arrays and added tests for mixed types and pandas DataFrame.

#### Enhancements
- Streamlined model loading in tutorials by integrating `loadDictionary`.
- Added tutorial for using `loadDictionary` function with templetized dictionary structure (handling multiple conditions with similar configurations).
- Created `userInterface` module for user interface functionalities; added `loadDictionary` function for loading a dictionary from a sequence of templates.
- Updated test structure for functions and added tests for `userInterface`.