
#####################################################################
#                                 DOC                               #
#####################################################################

"""
Defines abstract classes that are used for inheritance checking
in the solvers for checking consistency of sub-models (for example,
geometries and engines that are designed for engine simulations)

Content of the package:
    - `Engine` (`class`): Abstract base-class for engine-compatible models.

@author: F. Ramognino       <federico.ramognino@polimi.it>
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from abc import ABCMeta, abstractmethod

#####################################################################
#                           MAIN CLASSES                            #
#####################################################################

class Engine(metaclass=ABCMeta):
    """
    Base class for marking engine-compatible models.
    All classes that are compatible with the engine model should
    inherit from this class.
    """
    @abstractmethod
    def __init__(self):
        """
        Not contructable.
        """
        pass