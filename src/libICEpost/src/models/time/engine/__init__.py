"""
Time classes designed for time in internal combustion engines.

Content of the module:
- `EngineTime` (`class`): Base class for handling time in an internal combustion engine.
    Time is measured in crank angle degrees (CAD) and the class provides methods
    for converting between CAD (user time) and seconds (physical time).
    The specific timings (IVC, EVO, etc...) are defined in the derived classes.
    (e.g. `TwoStrokeTime`, `FourStrokeTime`, etc...).
- `FourStrokeEngineTime` (`class`): Four-stroke engine time class. This defines the timings
    IVO, IVC, EVO, EVC.
- `TwoStrokeEngineTime` (`class`): Two-stroke engine time class. This defines the timings
    IVO, IVC, EVO, EVC.

@author: F. Ramognino       <federico.ramognino@polimi.it>
"""

# EngineTime classes:
from .._Time import Time
from ._EngineTime import EngineTime
from ._FourStrokeEngineTime import FourStrokeEngineTime
from ._TwoStrokeEngineTime import TwoStrokeEngineTime

# Spark-ignition time classes:
from .._si import createSparkIgnitionTime

# Create all the time classes:
SparkIgnitionFourStrokeEngineTime = createSparkIgnitionTime(FourStrokeEngineTime)
SparkIgnitionTwoStrokeEngineTime = createSparkIgnitionTime(TwoStrokeEngineTime)

# Add to the selection tables:
Time.addToRuntimeSelectionTable(SparkIgnitionFourStrokeEngineTime)
Time.addToRuntimeSelectionTable(SparkIgnitionTwoStrokeEngineTime)
EngineTime.addToRuntimeSelectionTable(SparkIgnitionFourStrokeEngineTime)
EngineTime.addToRuntimeSelectionTable(SparkIgnitionTwoStrokeEngineTime)