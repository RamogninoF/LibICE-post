# Changelog

## v0.0.3 (16/10/2024)

- Beat releases.

## v0.10.0 (23/4/2025)
First release introducing testing (coverege around 70%).

Tested packages/functions:
- src (69%)
  - base (82%)
      - BaseClass (88%)
      - Utilities (88%)
      - Functions (88%)
      - dataStructures (87%)
        - Tabulation (93%)
        - Dictionary (96%)
  - thermophysicalModels (74%)
    - specie (76%)
      - specie (95%)
      - thermo (97%)
    - thermoModels (74%)
      - thermoMixture (94%)

## v0.10.1 (23/4/2025)

### Fixes
- Fix `sliceTable` function to use `_data` attribute for slicing (optimal).
- `Tabulation` and `OFTabulation`: Bug fixes in `plot`, `toPandas`, `squeeze`.
- `BaseTabulation`: removed duplicate method `slice`.
- `checkType`: checking multiple types (`tuple[type]`) among which a `_SpecialGenericAlias`.

### Enhancements
- `checkArray`: add `allowEmpty` parameter and optimized type checking for numpy arrays.
- `Tabulation`, `OFTabulation`: Optimized `toPandas` methods.

### Changes
- `OFTabulation(slice)` and `Tabulation(slice)`: accept single float values as ranges.
- `Tabulation(plot)`: Accept also empty iso for tables with only 2 variables.

## v0.10.1.post1 (26/03/2025)

### Fixes
- `makeEquilibriumMechanism`: Fixed conversion of data to builtin classes to ensure correct conversion to YAML format