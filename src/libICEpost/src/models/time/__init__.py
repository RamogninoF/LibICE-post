"""
Time classes used to handle time in post-processing models.

## Content of the module

###Base classes
- `Time` (`class`): Base class for handling time in a post-processing model.

###Spark ignition
- `createSparkIgnitionTime` (`function`): A factory function to create a 
    spark-ignition derivation from a given `Time` class.
- `SparkIgnitionTime` (`class`): SI derivation of `Time` class.

### engine (module)
Time classes designed for time in internal combustion engines.

@author: F. Ramognino       <federico.ramognino@polimi.it>
"""

from ._Time import Time
from ._si import createSparkIgnitionTime

from . import engine

#Create all the time classes:
SparkIgnitionTime = createSparkIgnitionTime(Time)

#Add to the selection tables:
Time.addToRuntimeSelectionTable(SparkIgnitionTime)