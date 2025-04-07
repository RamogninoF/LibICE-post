# Changelog

## v0.10.2 (7/04/2025)

### Enhancements
- Added `src._utils` module for managing external package dependencies.
- Introduced a custom version of `PyFoam` at `src._utils.PyFoam` with fixes to ensure compatibility with Windows.

### Changes
- Remove `pyfoam` dependency
- Remove `PyFoam` patches and from `libICEpost-applyPatches` script