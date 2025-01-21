"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023

Global parameters of the pakage.
"""

__CACHE_SIZE__:int = 256
"""Size of the cache for cached functions"""

__ERROR_RECURSION__ = 0
"""The recursion level for errors"""

__VERBOSITY_LEVEL__:int = 1
"""
Verbosity levels for warnings:
    0:  Do not display any runtime message
    1:  Display runtime warnings
    2:  Base verbosity (TODO)
    3:  Advanced debug verbosity (TODO)
"""

__CUSTOM_ERROR_MESSAGE__:bool = False
"""Use custom error messages?"""

__TYPE_CHECKING__:bool = True
"""If need to perform type-checking"""

__SAFE_ITERABLE_CHECKING__:bool = True
"""If type-checking is enabled, check for all elements of an iterable? Otherwise, check only the first element"""